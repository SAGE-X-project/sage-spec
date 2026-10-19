package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func fixture(t *testing.T) ([]byte, []byte) {
	t.Helper()
	p := os.Getenv("SAGE_OUTCOMES_ROOT")
	if p == "" {
		t.Fatal("SAGE_OUTCOMES_ROOT required")
	}
	a, e := os.ReadFile(filepath.Join(p, "abi.json"))
	if e != nil {
		t.Fatal(e)
	}
	s, e := os.ReadFile(filepath.Join(p, "schemas.json"))
	if e != nil {
		t.Fatal(e)
	}
	return a, s
}
func TestFixedOutcomesAndCodecs(t *testing.T) {
	a, s := fixture(t)
	v, e := inspect(a, s)
	if e != nil {
		t.Fatal(e)
	}
	if v.Errors != 22 || v.Events != 2 || v.Examples != 2 || v.Execution != "NOT_RUN" || v.Verdicts != 0 || len(v.Selectors) != 22 || len(v.Topics) != 2 || len(v.ABIHash) != 64 || len(v.SchemaHash) != 64 {
		t.Fatalf("unexpected result %+v", v)
	}
	for _, id := range v.Selectors {
		if len(id) != 10 {
			t.Fatal(id)
		}
	}
}
func TestJSONBoundaries(t *testing.T) {
	for _, v := range [][]byte{nil, bytes.Repeat([]byte(" "), limit+1), {0xff}, []byte(`{"x":1,"x":2}`), []byte(`{"x":{"y":[],"y":[]}}`), []byte(`{"x":"\ud800"}`), []byte(`{"\ud800":1}`), []byte(`{"x":"\u0000"}`), []byte(`[] []`), []byte(`[`), []byte(`{"x":`), []byte(`{"x"`), []byte(strings.Repeat("[", 18) + strings.Repeat("]", 18))} {
		if _, e := decode(v); e == nil {
			t.Fatalf("accepted invalid JSON %q", v)
		}
	}
	if _, e := decode([]byte(`{"a":[true,null,4,"text"]}`)); e != nil {
		t.Fatal(e)
	}
}
func clone(t *testing.T, a []byte) []any {
	t.Helper()
	var v []any
	if e := json.Unmarshal(a, &v); e != nil {
		t.Fatal(e)
	}
	return v
}
func TestRefuseABIShapeAndRoleChanges(t *testing.T) {
	a, s := fixture(t)
	cases := []func([]any) []any{
		func(v []any) []any { return v[:len(v)-1] },
		func(v []any) []any { v[0] = nil; return v },
		func(v []any) []any { v[0].(map[string]any)["type"] = false; return v },
		func(v []any) []any { v[0].(map[string]any)["type"] = "function"; return v },
		func(v []any) []any { v[0].(map[string]any)["name"] = ""; return v },
		func(v []any) []any { v[0].(map[string]any)["extra"] = true; return v },
		func(v []any) []any { v[0].(map[string]any)["inputs"] = nil; return v },
		func(v []any) []any { v[1] = v[0]; return v },
		func(v []any) []any { v[22].(map[string]any)["anonymous"] = true; return v },
		func(v []any) []any { v[22].(map[string]any)["anonymous"] = 0; return v },
		func(v []any) []any {
			v[22].(map[string]any)["inputs"].([]any)[0].(map[string]any)["indexed"] = 0
			return v
		},
		func(v []any) []any {
			v[22].(map[string]any)["inputs"].([]any)[0].(map[string]any)["indexed"] = false
			return v
		},
		func(v []any) []any {
			v[22].(map[string]any)["inputs"].([]any)[0].(map[string]any)["name"] = "renamed"
			return v
		},
		func(v []any) []any {
			v[22].(map[string]any)["inputs"].([]any)[0].(map[string]any)["type"] = "uint8"
			return v
		},
		func(v []any) []any { v[22].(map[string]any)["inputs"].([]any)[0] = nil; return v },
	}
	for i, change := range cases {
		b, e := json.Marshal(change(clone(t, a)))
		if e != nil {
			t.Fatal(e)
		}
		if _, e = inspect(b, s); e == nil {
			t.Errorf("accepted ABI change %d", i)
		}
	}
	if _, e := inspect([]byte(`{}`), s); e == nil {
		t.Fatal("ABI root")
	}
	if _, e := inspect([]byte(`[`), s); e == nil {
		t.Fatal("invalid ABI JSON")
	}
	if _, e := inspect(a, []byte(`[`)); e == nil {
		t.Fatal("invalid schema JSON")
	}
}
func TestSchemaRefusals(t *testing.T) {
	a, s := fixture(t)
	for _, v := range []string{`[]`, `{"":{}}`, `{"x":{}}`, `{"x":{"kind":false,"signature":"X()","layout":[]}}`, `{"x":{"kind":"error","signature":false,"layout":[]}}`, `{"x":{"kind":"error","signature":"X()","layout":null}}`, `{"x":{"kind":"error","signature":"X()","layout":[1]}}`} {
		if _, e := schemas([]byte(v)); e == nil {
			t.Fatal(v)
		}
	}
	for _, change := range []func(map[string]any){func(v map[string]any) { delete(v, "MalformedCall") }, func(v map[string]any) { v["MalformedCall"].(map[string]any)["signature"] = "Other()" }, func(v map[string]any) {
		v["ClaimCommitted"].(map[string]any)["signature"] = "ClaimCommitted(address,bytes32,uint64)"
	}, func(v map[string]any) { v["MalformedCall"].(map[string]any)["kind"] = "event" }} {
		var v map[string]any
		if e := json.Unmarshal(s, &v); e != nil {
			t.Fatal(e)
		}
		change(v)
		b, _ := json.Marshal(v)
		if _, e := inspect(a, b); e == nil {
			t.Fatal("schema change accepted")
		}
	}
}
func TestArgumentRules(t *testing.T) {
	for _, v := range []any{nil, true, []any{nil}, []any{map[string]any{"name": "x", "type": "tuple"}}, []any{map[string]any{"name": "", "type": "address"}}, []any{map[string]any{"name": "x", "type": false}}, []any{map[string]any{"name": "x", "type": "address"}, map[string]any{"name": "x", "type": "address"}}} {
		if _, e := layout(v, "error"); e == nil {
			t.Fatalf("accepted %v", v)
		}
	}
	v := []any{}
	for _, n := range []string{"a", "b", "c", "d"} {
		v = append(v, map[string]any{"name": n, "type": "bytes32", "indexed": true})
	}
	if _, e := layout(v, "event"); e == nil {
		t.Fatal("four indexed fields")
	}
	if _, e := object(map[string]any{"a": true}, "b"); e == nil {
		t.Fatal("missing field")
	}
}
func TestNoArgumentErrorRule(t *testing.T) {
	a, s := fixture(t)
	v := clone(t, a)
	v[0].(map[string]any)["inputs"] = []any{map[string]any{"name": "x", "type": "address"}}
	b, _ := json.Marshal(v)
	if _, e := inspect(b, s); e == nil {
		t.Fatal("error arguments")
	}
}
func TestNormalExampleRefusals(t *testing.T) {
	a, _ := fixture(t)
	p, e := abi.JSON(bytes.NewReader(a))
	if e != nil {
		t.Fatal(e)
	}
	event := p.Events["ClaimCommitted"]
	event.Inputs = nil
	p.Events["ClaimCommitted"] = event
	if examples(p) == nil {
		t.Fatal("missing event data")
	}
	p, e = abi.JSON(bytes.NewReader(a))
	if e != nil {
		t.Fatal(e)
	}
	event = p.Events["RecordChanged"]
	event.Inputs[2].Type = p.Events["ClaimCommitted"].Inputs[0].Type
	p.Events["RecordChanged"] = event
	if examples(p) == nil {
		t.Fatal("wrong record argument type")
	}
}

type failingWriter struct{}

func (failingWriter) Write([]byte) (int, error) { return 0, errors.New("fixed output failure") }
func TestCLIAndBoundedFileReads(t *testing.T) {
	a, s := fixture(t)
	d := t.TempDir()
	ap, sp := filepath.Join(d, "abi.json"), filepath.Join(d, "schemas.json")
	if e := os.WriteFile(ap, a, 0600); e != nil {
		t.Fatal(e)
	}
	if e := os.WriteFile(sp, s, 0600); e != nil {
		t.Fatal(e)
	}
	args := []string{"-abi", ap, "-schemas", sp}
	var b bytes.Buffer
	if e := run(args, &b); e != nil {
		t.Fatal(e)
	}
	if !strings.Contains(b.String(), `"new_conformance_verdicts":0`) {
		t.Fatal(b.String())
	}
	if run(args, failingWriter{}) == nil {
		t.Fatal("lost output")
	}
	for _, v := range [][]string{nil, {"-unknown"}, {"-abi", ap, "-schemas", sp, "extra"}, {"-abi", d + "/missing", "-schemas", sp}, {"-abi", ap, "-schemas", d + "/missing"}, {"-abi", d, "-schemas", sp}} {
		if run(v, &b) == nil {
			t.Fatal(v)
		}
	}
	large := filepath.Join(d, "large")
	if e := os.WriteFile(large, bytes.Repeat([]byte(" "), limit+1), 0600); e != nil {
		t.Fatal(e)
	}
	if _, e := read(large); e == nil {
		t.Fatal("unbounded artifact")
	}
	if e := os.WriteFile(ap, []byte(`[]`), 0600); e != nil {
		t.Fatal(e)
	}
	if run(args, &b) == nil {
		t.Fatal("invalid artifact")
	}
}
