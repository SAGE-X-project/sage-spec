// Inspect a future ABI artifact only. No RPC, contract or protocol execution.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"io"
	"math/big"
	"os"
	"reflect"
	"strings"
	"unicode/utf8"
)

const limit = 262144

var errorNames = strings.Fields("MalformedCall ValueNotAllowed WrongRegistryContext UnauthorizedCaller WrongRecordState PreviousVersionMismatch VersionExhausted ClaimUnavailable ClaimWindowInvalid ClaimMismatch IdentifierUnavailable KeyUnavailable KeyNameReused KeyMaterialReused InvalidKeyProof UnsupportedKeyAlgorithm InvalidEntry BoundsExceeded GrantUnavailable GrantAlreadyPresent HistoryUnavailable TimeInvalid")

type schema struct {
	Kind      string   `json:"kind"`
	Signature string   `json:"signature"`
	Layout    []string `json:"layout"`
}
type result struct {
	Scope      string            `json:"scope"`
	ABIHash    string            `json:"abi_sha256"`
	SchemaHash string            `json:"schemas_sha256"`
	Errors     int               `json:"errors"`
	Events     int               `json:"events"`
	Selectors  map[string]string `json:"error_selectors"`
	Topics     map[string]string `json:"event_topics"`
	Examples   int               `json:"normal_encoding_examples"`
	Execution  string            `json:"contract_execution"`
	Verdicts   int               `json:"new_conformance_verdicts"`
}

func ascii(s string) bool {
	for _, r := range s {
		if r < 32 || r > 126 {
			return false
		}
	}
	return true
}
func scan(d *json.Decoder, depth int) error {
	if depth > 16 {
		return errors.New("artifact nesting limit")
	}
	t, e := d.Token()
	if e != nil {
		return e
	}
	if s, ok := t.(string); ok && !ascii(s) {
		return errors.New("non-ASCII artifact text")
	}
	if t == json.Delim('{') {
		seen := map[string]bool{}
		for d.More() {
			k, e := d.Token()
			if e != nil {
				return e
			}
			s, ok := k.(string)
			if !ok || !ascii(s) || seen[s] {
				return errors.New("invalid or duplicate member")
			}
			seen[s] = true
			if e = scan(d, depth+1); e != nil {
				return e
			}
		}
		_, e = d.Token()
		return e
	}
	if t == json.Delim('[') {
		for d.More() {
			if e = scan(d, depth+1); e != nil {
				return e
			}
		}
		_, e = d.Token()
		return e
	}
	return nil
}
func decode(data []byte) (any, error) {
	if len(data) == 0 || len(data) > limit || !utf8.Valid(data) {
		return nil, errors.New("artifact length/UTF-8")
	}
	d := json.NewDecoder(bytes.NewReader(data))
	if e := scan(d, 0); e != nil {
		return nil, e
	}
	if _, e := d.Token(); e != io.EOF {
		return nil, errors.New("trailing JSON")
	}
	var v any
	e := json.Unmarshal(data, &v)
	return v, e
}
func object(v any, fields ...string) (map[string]any, error) {
	m, ok := v.(map[string]any)
	if !ok || len(m) != len(fields) {
		return nil, errors.New("closed object shape")
	}
	for _, n := range fields {
		if _, ok := m[n]; !ok {
			return nil, errors.New("missing exact member")
		}
	}
	return m, nil
}
func text(m map[string]any, n string) (string, error) {
	s, ok := m[n].(string)
	if !ok || s == "" {
		return "", errors.New("nonempty artifact text required")
	}
	return s, nil
}
func layout(v any, kind string) ([]string, error) {
	a, ok := v.([]any)
	if !ok {
		return nil, errors.New("non-null argument array required")
	}
	out := []string{}
	seen := map[string]bool{}
	topics := 0
	for _, v := range a {
		fields := []string{"name", "type"}
		if kind == "event" {
			fields = append(fields, "indexed")
		}
		m, e := object(v, fields...)
		if e != nil {
			return nil, e
		}
		n, e := text(m, "name")
		if e != nil || seen[n] {
			return nil, errors.New("argument name")
		}
		seen[n] = true
		t, e := text(m, "type")
		if e != nil {
			return nil, e
		}
		switch t {
		case "address", "bytes32", "uint64", "uint256", "string":
		default:
			return nil, errors.New("unsupported artifact type")
		}
		part := n + ":" + t
		if kind == "event" {
			b, ok := m["indexed"].(bool)
			if !ok {
				return nil, errors.New("exact indexed boolean required")
			}
			if b {
				topics++
				part += ":topic"
			} else {
				part += ":data"
			}
		}
		out = append(out, part)
	}
	if topics > 3 {
		return nil, errors.New("too many indexed arguments")
	}
	return out, nil
}
func schemas(data []byte) (map[string]schema, error) {
	raw, e := decode(data)
	if e != nil {
		return nil, e
	}
	m, ok := raw.(map[string]any)
	if !ok {
		return nil, errors.New("schema root")
	}
	out := map[string]schema{}
	for n, v := range m {
		if n == "" {
			return nil, errors.New("empty schema name")
		}
		o, e := object(v, "kind", "signature", "layout")
		if e != nil {
			return nil, e
		}
		k, e := text(o, "kind")
		if e != nil {
			return nil, e
		}
		sig, e := text(o, "signature")
		if e != nil {
			return nil, e
		}
		list, ok := o["layout"].([]any)
		if !ok {
			return nil, errors.New("schema layout array")
		}
		l := []string{}
		for _, v := range list {
			s, ok := v.(string)
			if !ok {
				return nil, errors.New("layout text")
			}
			l = append(l, s)
		}
		out[n] = schema{k, sig, l}
	}
	return out, nil
}
func examples(parsed abi.ABI) error {
	b, e := parsed.Events["ClaimCommitted"].Inputs.NonIndexed().Pack(big.NewInt(7))
	if e != nil {
		return e
	}
	expected := append(make([]byte, 31), 7)
	if !bytes.Equal(b, expected) {
		return errors.New("claim event data differs")
	}
	filled := func(v byte) (b [32]byte) {
		for i := range b {
			b[i] = v
		}
		return
	}
	args := parsed.Events["RecordChanged"].Inputs.NonIndexed()
	b, e = args.Pack("alpha", uint64(7), uint64(8), "activate", filled(0x11), filled(0x22), filled(0x33), uint64(123))
	if e != nil {
		return e
	}
	word := func(s string) string { return strings.Repeat("0", 64-len(s)) + s }
	expected, e = hex.DecodeString(word("100") + word("7") + word("8") + word("140") + strings.Repeat("11", 32) + strings.Repeat("22", 32) + strings.Repeat("33", 32) + word("7b") + word("5") + "616c706861" + strings.Repeat("00", 27) + word("8") + "6163746976617465" + strings.Repeat("00", 24))
	if e != nil {
		return e
	}
	if !bytes.Equal(b, expected) {
		return errors.New("record event data differs")
	}
	values, e := args.Unpack(expected)
	if e != nil {
		return e
	}
	if len(values) != 8 || values[0] != "alpha" || values[1] != uint64(7) || values[2] != uint64(8) || values[3] != "activate" || values[7] != uint64(123) {
		return errors.New("event example decode")
	}
	return nil
}
func inspect(data, manifest []byte) (result, error) {
	var out result
	raw, e := decode(data)
	if e != nil {
		return out, e
	}
	rows, ok := raw.([]any)
	if !ok {
		return out, errors.New("ABI array")
	}
	s, e := schemas(manifest)
	if e != nil {
		return out, e
	}
	expected := map[string]string{"ClaimCommitted": "event", "RecordChanged": "event"}
	for _, n := range errorNames {
		expected[n] = "error"
	}
	if len(rows) != len(expected) || len(s) != len(expected) {
		return out, errors.New("outcome inventory")
	}
	seen := map[string]bool{}
	for _, v := range rows {
		m, ok := v.(map[string]any)
		if !ok {
			return out, errors.New("ABI entry object")
		}
		k, e := text(m, "type")
		if e != nil {
			return out, e
		}
		fields := []string{"type", "name", "inputs"}
		if k == "event" {
			fields = append(fields, "anonymous")
		}
		m, e = object(v, fields...)
		if e != nil {
			return out, e
		}
		n, e := text(m, "name")
		if e != nil {
			return out, e
		}
		if seen[n] || expected[n] != k {
			return out, errors.New("outcome kind/name")
		}
		seen[n] = true
		if k == "event" {
			a, ok := m["anonymous"].(bool)
			if !ok || a {
				return out, errors.New("nonanonymous event required")
			}
		}
		l, e := layout(m["inputs"], k)
		if e != nil {
			return out, e
		}
		if k == "error" && len(l) != 0 {
			return out, errors.New("bounded no-argument errors required")
		}
		want, ok := s[n]
		if !ok || want.Kind != k || !reflect.DeepEqual(want.Layout, l) {
			return out, errors.New("outcome layout differs")
		}
	}
	parsed, e := abi.JSON(bytes.NewReader(data))
	if e != nil {
		return out, e
	}
	out.Selectors = map[string]string{}
	out.Topics = map[string]string{}
	ids := map[string]bool{}
	for n, k := range expected {
		if k == "error" {
			v, ok := parsed.Errors[n]
			if !ok || s[n].Signature != v.Sig {
				return out, errors.New("error signature differs")
			}
			id := hex.EncodeToString(v.ID[:4])
			if ids[id] {
				return out, errors.New("error selector collision")
			}
			ids[id] = true
			out.Selectors[n] = "0x" + id
		} else {
			v, ok := parsed.Events[n]
			if !ok || s[n].Signature != v.Sig {
				return out, errors.New("event signature differs")
			}
			id := v.ID.Hex()
			if ids[id] {
				return out, errors.New("event topic collision")
			}
			ids[id] = true
			out.Topics[n] = id
		}
	}
	if e = examples(parsed); e != nil {
		return out, e
	}
	a, b := sha256.Sum256(data), sha256.Sum256(manifest)
	out.Scope = "future error/event ABI and two normal data codecs only; no Registry execution"
	out.ABIHash = hex.EncodeToString(a[:])
	out.SchemaHash = hex.EncodeToString(b[:])
	out.Errors = len(errorNames)
	out.Events = 2
	out.Examples = 2
	out.Execution = "NOT_RUN"
	return out, nil
}
func read(name string) ([]byte, error) {
	f, e := os.Open(name)
	if e != nil {
		return nil, e
	}
	defer f.Close()
	b, e := io.ReadAll(io.LimitReader(f, limit+1))
	if e != nil {
		return nil, e
	}
	if len(b) > limit {
		return nil, errors.New("artifact too large")
	}
	return b, nil
}
func run(args []string, w io.Writer) error {
	f := flag.NewFlagSet("candidate-outcomes", flag.ContinueOnError)
	f.SetOutput(io.Discard)
	a := f.String("abi", "", "ABI file")
	s := f.String("schemas", "", "separately authored schemas file")
	if e := f.Parse(args); e != nil {
		return e
	}
	if *a == "" || *s == "" || f.NArg() != 0 {
		return errors.New("exact -abi and -schemas required")
	}
	b, e := read(*a)
	if e != nil {
		return e
	}
	m, e := read(*s)
	if e != nil {
		return e
	}
	out, e := inspect(b, m)
	if e != nil {
		return e
	}
	return json.NewEncoder(w).Encode(out)
}
func main() {
	if e := run(os.Args[1:], os.Stdout); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
