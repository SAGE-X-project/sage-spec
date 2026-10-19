// ABI artifact inspection only. This program never connects to a chain.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"reflect"
	"strings"
	"unicode/utf8"

	"github.com/ethereum/go-ethereum/accounts/abi"
)

const artifactLimit = 262144

type argument struct {
	Name       string     `json:"name"`
	Type       string     `json:"type"`
	Components []argument `json:"components,omitempty"`
}
type method struct {
	Type       string     `json:"type"`
	Name       string     `json:"name"`
	Mutability string     `json:"stateMutability"`
	Inputs     []argument `json:"inputs"`
	Outputs    []argument `json:"outputs"`
}
type methodSchema struct {
	Signature    string   `json:"signature"`
	Mutability   string   `json:"mutability"`
	InputLayout  []string `json:"inputLayout"`
	OutputLayout []string `json:"outputLayout"`
}

type result struct {
	Scope             string            `json:"scope"`
	ABIHash           string            `json:"abi_sha256"`
	SignaturesHash    string            `json:"signatures_sha256"`
	Methods           int               `json:"methods"`
	Selectors         map[string]string `json:"selectors"`
	NormalExamples    int               `json:"normal_encoding_examples"`
	NewVerdicts       int               `json:"new_conformance_verdicts"`
	ContractExecution string            `json:"contract_execution"`
}

func uniqueValue(d *json.Decoder, depth int) error {
	if depth > 64 {
		return errors.New("JSON nesting exceeds artifact limit")
	}
	t, err := d.Token()
	if err != nil {
		return err
	}
	if v, ok := t.(string); ok && !artifactText(v) {
		return errors.New("artifact strings require printable ASCII")
	}
	switch t {
	case json.Delim('{'):
		seen := map[string]bool{}
		for d.More() {
			k, err := d.Token()
			if err != nil {
				return err
			}
			name, ok := k.(string)
			if !ok || !artifactText(name) {
				return errors.New("object key is not candidate ASCII text")
			}
			if seen[name] {
				return fmt.Errorf("duplicate JSON member %q", name)
			}
			seen[name] = true
			if err := uniqueValue(d, depth+1); err != nil {
				return err
			}
		}
		_, err = d.Token()
		return err
	case json.Delim('['):
		for d.More() {
			if err := uniqueValue(d, depth+1); err != nil {
				return err
			}
		}
		_, err = d.Token()
		return err
	}
	return nil
}

// Artifact identifiers/types/layouts use printable ASCII only. This rejects
// decoder replacement of escaped unpaired surrogates without claiming to be
// the protocol's general Unicode/JCS parser.
func artifactText(v string) bool {
	for _, r := range v {
		if r < 0x20 || r > 0x7e {
			return false
		}
	}
	return true
}
func closedObject(v any, fields ...string) (map[string]any, error) {
	obj, ok := v.(map[string]any)
	if !ok || len(obj) != len(fields) {
		return nil, errors.New("wrong artifact object shape")
	}
	for _, name := range fields {
		if _, ok := obj[name]; !ok {
			return nil, fmt.Errorf("missing exact member %s", name)
		}
	}
	return obj, nil
}
func textFields(obj map[string]any, names ...string) error {
	for _, name := range names {
		if _, ok := obj[name].(string); !ok {
			return fmt.Errorf("non-string artifact member %s", name)
		}
	}
	return nil
}
func rawArguments(v any) error {
	rows, ok := v.([]any)
	if !ok {
		return errors.New("argument array must be present and non-null")
	}
	for _, v := range rows {
		obj, ok := v.(map[string]any)
		if !ok {
			return errors.New("argument is not an object")
		}
		fields := []string{"name", "type"}
		if obj["type"] == "tuple" || obj["type"] == "tuple[]" {
			fields = append(fields, "components")
		}
		obj, err := closedObject(v, fields...)
		if err != nil {
			return err
		}
		if err := textFields(obj, "name", "type"); err != nil {
			return err
		}
		if len(fields) == 3 {
			if err := rawArguments(obj["components"]); err != nil {
				return err
			}
		}
	}
	return nil
}
func artifactShape(raw any, target any) error {
	switch target.(type) {
	case *[]method:
		rows, ok := raw.([]any)
		if !ok {
			return errors.New("ABI root must be an array")
		}
		for _, v := range rows {
			obj, err := closedObject(v, "type", "name", "stateMutability", "inputs", "outputs")
			if err != nil {
				return err
			}
			if err := textFields(obj, "type", "name", "stateMutability"); err != nil {
				return err
			}
			for _, name := range []string{"inputs", "outputs"} {
				if err := rawArguments(obj[name]); err != nil {
					return err
				}
			}
		}
	case *map[string]methodSchema:
		entries, ok := raw.(map[string]any)
		if !ok {
			return errors.New("schema root must be an object")
		}
		for _, v := range entries {
			obj, err := closedObject(v, "signature", "mutability", "inputLayout", "outputLayout")
			if err != nil {
				return err
			}
			if err := textFields(obj, "signature", "mutability"); err != nil {
				return err
			}
			for _, name := range []string{"inputLayout", "outputLayout"} {
				list, ok := obj[name].([]any)
				if !ok {
					return errors.New("layout must be a non-null array")
				}
				for _, item := range list {
					if _, ok := item.(string); !ok {
						return errors.New("layout member must be text")
					}
				}
			}
		}
	}
	return nil
}
func argumentLayout(args []argument, prefix string) []string {
	out := []string{}
	for _, a := range args {
		name := prefix + a.Name
		out = append(out, name+":"+a.Type)
		if a.Type == "tuple" || a.Type == "tuple[]" {
			child := name + "."
			if a.Type == "tuple[]" {
				child = name + "[]."
			}
			out = append(out, argumentLayout(a.Components, child)...)
		}
	}
	return out
}
func strictJSON(data []byte, target any) error {
	if len(data) == 0 || len(data) > artifactLimit || !utf8.Valid(data) {
		return errors.New("invalid artifact length or UTF-8")
	}
	scan := json.NewDecoder(bytes.NewReader(data))
	if err := uniqueValue(scan, 0); err != nil {
		return err
	}
	if _, err := scan.Token(); err != io.EOF {
		return errors.New("trailing JSON content")
	}
	var raw any
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	if err := artifactShape(raw, target); err != nil {
		return err
	}
	d := json.NewDecoder(bytes.NewReader(data))
	d.DisallowUnknownFields()
	return d.Decode(target)
}
func argumentsValid(args []argument) error {
	if args == nil {
		return errors.New("missing or null ABI argument array")
	}
	seen := map[string]bool{}
	for _, a := range args {
		if a.Name == "" || seen[a.Name] {
			return errors.New("empty or duplicate ABI argument name")
		}
		seen[a.Name] = true
		switch a.Type {
		case "tuple", "tuple[]":
			if len(a.Components) == 0 {
				return errors.New("empty tuple")
			}
			if err := argumentsValid(a.Components); err != nil {
				return err
			}
		case "string", "address", "bytes", "bytes32", "bool", "uint64":
			if a.Components != nil {
				return errors.New("components on a non-tuple")
			}
		default:
			return fmt.Errorf("unsupported candidate ABI type %q", a.Type)
		}
	}
	return nil
}
func normalExamples(parsed abi.ABI) error {
	// Independently authored argument bytes for activate("alpha", 7).
	expected, _ := hex.DecodeString("0000000000000000000000000000000000000000000000000000000000000040" +
		"0000000000000000000000000000000000000000000000000000000000000007" +
		"0000000000000000000000000000000000000000000000000000000000000005" +
		"616c706861000000000000000000000000000000000000000000000000000000")
	m := parsed.Methods["activate"]
	encoded, err := m.Inputs.Pack("alpha", uint64(7))
	if err != nil {
		return err
	}
	if !bytes.Equal(encoded, expected) {
		return errors.New("activate argument bytes differ from authored example")
	}
	decoded, err := m.Inputs.Unpack(expected)
	if err != nil {
		return err
	}
	if len(decoded) != 2 || decoded[0] != "alpha" || decoded[1] != uint64(7) {
		return errors.New("activate example decoded incorrectly")
	}
	// Solidity ABI 0.8.20's published baz(uint32,bool) example, not a Registry call.
	example, err := abi.JSON(strings.NewReader(`[{"type":"function","name":"baz","stateMutability":"pure","inputs":[{"name":"x","type":"uint32"},{"name":"y","type":"bool"}],"outputs":[]}]`))
	if err != nil {
		return err
	}
	call, err := example.Pack("baz", uint32(69), true)
	if err != nil {
		return err
	}
	published, _ := hex.DecodeString("cdcd77c0" + "0000000000000000000000000000000000000000000000000000000000000045" + "0000000000000000000000000000000000000000000000000000000000000001")
	if !bytes.Equal(call, published) {
		return errors.New("published Solidity example differs")
	}
	return nil
}
func inspect(data, signatureData []byte) (result, error) {
	var out result
	var rows []method
	if err := strictJSON(data, &rows); err != nil {
		return out, err
	}
	var signatures map[string]methodSchema
	if err := strictJSON(signatureData, &signatures); err != nil {
		return out, err
	}
	names := []string{"commitClaim", "revealClaim", "activate", "deactivate", "addKey", "revokeKey", "updateServices", "authorizeOperator", "revokeOperator", "registryId", "record", "activeGrants", "historyItem"}
	if len(rows) != len(names) || len(signatures) != len(names) {
		return out, errors.New("candidate method inventory differs")
	}
	views := map[string]bool{"registryId": true, "record": true, "activeGrants": true, "historyItem": true}
	seen := map[string]bool{}
	for _, row := range rows {
		if row.Type != "function" || seen[row.Name] {
			return out, errors.New("non-function or duplicate method")
		}
		seen[row.Name] = true
		want := "nonpayable"
		if views[row.Name] {
			want = "view"
		}
		if row.Mutability != want {
			return out, errors.New("candidate method mutability differs")
		}
		if err := argumentsValid(row.Inputs); err != nil {
			return out, err
		}
		if err := argumentsValid(row.Outputs); err != nil {
			return out, err
		}
		schema, ok := signatures[row.Name]
		if !ok || schema.Mutability != row.Mutability || !reflect.DeepEqual(schema.InputLayout, argumentLayout(row.Inputs, "")) || !reflect.DeepEqual(schema.OutputLayout, argumentLayout(row.Outputs, "")) {
			return out, fmt.Errorf("complete method schema mismatch for %s", row.Name)
		}
	}
	parsed, err := abi.JSON(bytes.NewReader(data))
	if err != nil {
		return out, err
	}
	selectors := map[string]string{}
	ids := map[string]bool{}
	for _, name := range names {
		m, ok := parsed.Methods[name]
		if !ok {
			return out, fmt.Errorf("missing method %s", name)
		}
		if signatures[name].Signature != m.Sig {
			return out, fmt.Errorf("signature mismatch for %s", name)
		}
		id := hex.EncodeToString(m.ID)
		if len(m.ID) != 4 || ids[id] {
			return out, errors.New("invalid or colliding selector")
		}
		ids[id] = true
		selectors[name] = "0x" + id
	}
	if err := normalExamples(parsed); err != nil {
		return out, err
	}
	a, b := sha256.Sum256(data), sha256.Sum256(signatureData)
	return result{Scope: "typed ABI and two normal encoding examples only; no Registry execution", ABIHash: hex.EncodeToString(a[:]), SignaturesHash: hex.EncodeToString(b[:]), Methods: len(names), Selectors: selectors, NormalExamples: 2, ContractExecution: "NOT_RUN"}, nil
}
func run(args []string, w io.Writer) error {
	f := flag.NewFlagSet("candidate-abi", flag.ContinueOnError)
	f.SetOutput(io.Discard)
	ap := f.String("abi", "", "candidate ABI file")
	sp := f.String("signatures", "", "authored signatures file")
	if err := f.Parse(args); err != nil {
		return err
	}
	if *ap == "" || *sp == "" || f.NArg() != 0 {
		return errors.New("exact -abi and -signatures paths required")
	}
	data, err := os.ReadFile(*ap)
	if err != nil {
		return err
	}
	sigs, err := os.ReadFile(*sp)
	if err != nil {
		return err
	}
	out, err := inspect(data, sigs)
	if err != nil {
		return err
	}
	return json.NewEncoder(w).Encode(out)
}
func main() {
	if err := run(os.Args[1:], os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
