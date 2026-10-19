package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/ethereum/go-ethereum/accounts/abi"
)

func fixture(t *testing.T) ([]byte, []byte) {
	t.Helper()
	root := os.Getenv("SAGE_CANDIDATE_ROOT")
	if root == "" {
		t.Fatal("SAGE_CANDIDATE_ROOT required")
	}
	a, err := os.ReadFile(filepath.Join(root, "contract-abi.json"))
	if err != nil {
		t.Fatal(err)
	}
	s, err := os.ReadFile(filepath.Join(root, "contract-signatures.json"))
	if err != nil {
		t.Fatal(err)
	}
	return a, s
}
func TestInspectCandidate(t *testing.T) {
	a, s := fixture(t)
	out, err := inspect(a, s)
	if err != nil {
		t.Fatal(err)
	}
	if out.Methods != 13 || out.NormalExamples != 2 || len(out.Selectors) != 13 || out.NewVerdicts != 0 || out.ContractExecution != "NOT_RUN" || len(out.ABIHash) != 64 || len(out.SignaturesHash) != 64 {
		t.Fatalf("incorrect inspection: %+v", out)
	}
}
func TestStrictJSON(t *testing.T) {
	cases := [][]byte{nil, bytes.Repeat([]byte{' '}, artifactLimit+1), {0xff}, []byte(`{"x":1,"x":2}`), []byte(`{"x":{"y":1,"y":2}}`), []byte(`[] []`), []byte(`[`), []byte(`{"x":`), []byte(`{"x"`), []byte(strings.Repeat("[", 66) + strings.Repeat("]", 66))}
	for i, b := range cases {
		var x any
		if strictJSON(b, &x) == nil {
			t.Errorf("invalid JSON %d accepted", i)
		}
	}
	var x any
	if err := strictJSON([]byte(`{"x":[true,null,"a",{}]}`), &x); err != nil {
		t.Fatal(err)
	}
	var typed struct {
		Name string `json:"name"`
	}
	if strictJSON([]byte(`{"unknown":1}`), &typed) == nil {
		t.Fatal("unknown member accepted")
	}
}
func TestArgumentRules(t *testing.T) {
	for _, v := range [][]argument{nil, {{Name: "", Type: "string"}}, {{Name: "x", Type: "string"}, {Name: "x", Type: "bool"}}, {{Name: "x", Type: "tuple"}}, {{Name: "x", Type: "string", Components: []argument{}}}, {{Name: "x", Type: "uint256"}}, {{Name: "x", Type: "tuple[]", Components: []argument{{Name: "a", Type: "unsupported"}}}}} {
		if argumentsValid(v) == nil {
			t.Fatalf("invalid arguments accepted: %+v", v)
		}
	}
	if err := argumentsValid([]argument{{Name: "x", Type: "tuple", Components: []argument{{Name: "a", Type: "bytes"}}}}); err != nil {
		t.Fatal(err)
	}
}
func TestInspectRejectsArtifactChanges(t *testing.T) {
	a, s := fixture(t)
	var original []method
	if err := json.Unmarshal(a, &original); err != nil {
		t.Fatal(err)
	}
	cases := []func([]method) []method{
		func(v []method) []method { return v[:len(v)-1] },
		func(v []method) []method { v[0].Type = "event"; return v },
		func(v []method) []method { v[1].Name = v[0].Name; return v },
		func(v []method) []method { v[0].Mutability = "payable"; return v },
		func(v []method) []method { v[0].Inputs = nil; return v },
		func(v []method) []method { v[0].Outputs = nil; return v },
		func(v []method) []method { v[0].Name = "unknownMethod"; return v },
		func(v []method) []method { v[0].Inputs[0].Type = "bytes"; return v },
		func(v []method) []method { v[10].Outputs = []argument{}; return v },
		func(v []method) []method { v[2].Outputs[0].Type = "bool"; return v },
		func(v []method) []method {
			v[12].Outputs[0], v[12].Outputs[1] = v[12].Outputs[1], v[12].Outputs[0]
			return v
		},
		func(v []method) []method { v[10].Outputs[0].Name = "exists"; return v },
		func(v []method) []method { v[12].Outputs = v[12].Outputs[:1]; return v },
		func(v []method) []method { v[1].Inputs[2].Components[0].Name = "renamed"; return v },
		func(v []method) []method {
			v[1].Inputs[2].Components[0], v[1].Inputs[2].Components[1] = v[1].Inputs[2].Components[1], v[1].Inputs[2].Components[0]
			return v
		},
	}
	for i, change := range cases {
		var v []method
		_ = json.Unmarshal(a, &v)
		b, _ := json.Marshal(change(v))
		if _, err := inspect(b, s); err == nil {
			t.Errorf("changed artifact %d accepted", i)
		}
	}
	for _, b := range [][]byte{[]byte(`{}`), []byte(`null`), []byte(`{"activate":"wrong"}`), []byte(`{"x":1}`)} {
		if _, err := inspect(a, b); err == nil {
			t.Fatal("bad signature inventory accepted")
		}
	}
	if _, err := inspect([]byte(`{}`), s); err == nil {
		t.Fatal("wrong ABI root accepted")
	}
	if _, err := inspect(a, []byte(`{`)); err == nil {
		t.Fatal("invalid signature JSON accepted")
	}
	var signatures map[string]methodSchema
	_ = json.Unmarshal(s, &signatures)
	schema := signatures["activate"]
	schema.Signature = "activate(string,uint256)"
	signatures["activate"] = schema
	b, _ := json.Marshal(signatures)
	if _, err := inspect(a, b); err == nil {
		t.Fatal("wrong signature accepted")
	}
}
func TestNormalExampleRejectsDifferentSignature(t *testing.T) {
	p, err := abi.JSON(strings.NewReader(`[{"type":"function","name":"activate","inputs":[{"name":"id","type":"bool"}],"outputs":[]}]`))
	if err != nil {
		t.Fatal(err)
	}
	if normalExamples(p) == nil {
		t.Fatal("different argument layout accepted")
	}
	p, err = abi.JSON(strings.NewReader(`[{"type":"function","name":"activate","inputs":[{"name":"id","type":"string"},{"name":"version","type":"uint32"}],"outputs":[]}]`))
	if err != nil {
		t.Fatal(err)
	}
	if normalExamples(p) == nil {
		t.Fatal("different integer type accepted")
	}
}

type failedWriter struct{}

func (failedWriter) Write([]byte) (int, error) { return 0, errors.New("write refused") }
func TestRun(t *testing.T) {
	a, s := fixture(t)
	dir := t.TempDir()
	ap, sp := filepath.Join(dir, "abi.json"), filepath.Join(dir, "signatures.json")
	if err := os.WriteFile(ap, a, 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(sp, s, 0600); err != nil {
		t.Fatal(err)
	}
	args := []string{"-abi", ap, "-signatures", sp}
	var out bytes.Buffer
	if err := run(args, &out); err != nil {
		t.Fatal(err)
	}
	var r result
	if json.Unmarshal(out.Bytes(), &r) != nil || r.Methods != 13 {
		t.Fatal("invalid output")
	}
	for _, v := range [][]string{nil, {"-unknown"}, {"-abi", ap}, {"-abi", ap, "-signatures", sp, "extra"}, {"-abi", dir + "/missing", "-signatures", sp}, {"-abi", ap, "-signatures", dir + "/missing"}} {
		if run(v, io.Discard) == nil {
			t.Fatal("invalid CLI accepted")
		}
	}
	if run(args, failedWriter{}) == nil {
		t.Fatal("output error ignored")
	}
	if err := os.WriteFile(ap, []byte(`[]`), 0600); err != nil {
		t.Fatal(err)
	}
	if run(args, io.Discard) == nil {
		t.Fatal("bad artifact accepted")
	}
}

// Fixed local data controls only: no client, chain or external service.
func TestClosedArtifactSchema(t *testing.T) {
	a, s := fixture(t)
	changes := []func([]map[string]any){
		func(v []map[string]any) { v[0]["Inputs"] = v[0]["inputs"]; delete(v[0], "inputs") },
		func(v []map[string]any) { v[0]["Name"] = "alias" },
		func(v []map[string]any) { v[0]["name"] = nil },
		func(v []map[string]any) { delete(v[0], "name") },
		func(v []map[string]any) { v[0]["inputs"] = nil },
		func(v []map[string]any) { v[0]["outputs"] = "" },
		func(v []map[string]any) { v[0]["inputs"] = []any{nil} },
		func(v []map[string]any) { v[0]["inputs"].([]any)[0].(map[string]any)["components"] = nil },
		func(v []map[string]any) { v[0]["inputs"].([]any)[0].(map[string]any)["Name"] = "alias" },
		func(v []map[string]any) { v[0]["inputs"].([]any)[0].(map[string]any)["name"] = false },
		func(v []map[string]any) { v[1]["inputs"].([]any)[2].(map[string]any)["components"] = nil },
		func(v []map[string]any) {
			v[1]["inputs"].([]any)[2].(map[string]any)["components"].([]any)[0].(map[string]any)["type"] = nil
		},
	}
	for i, change := range changes {
		var v []map[string]any
		if err := json.Unmarshal(a, &v); err != nil {
			t.Fatal(err)
		}
		change(v)
		b, err := json.Marshal(v)
		if err != nil {
			t.Fatal(err)
		}
		if _, err := inspect(b, s); err == nil {
			t.Errorf("closed ABI control %d accepted", i)
		}
	}
	for _, token := range []string{`"\ud800"`, `"\udfff"`, `"é"`, `"\u0000"`} {
		b := bytes.Replace(a, []byte(`"commitment"`), []byte(token), 1)
		if _, err := inspect(b, s); err == nil {
			t.Errorf("noncandidate text %s accepted", token)
		}
	}
	// An escaped ordinary ASCII member is decoded before duplicate detection.
	var x any
	if strictJSON([]byte(`{"name":1,"\u006eame":2}`), &x) == nil {
		t.Fatal("decoded duplicate accepted")
	}
	if err := strictJSON([]byte(`"\\ud800"`), &x); err != nil {
		t.Fatal("literal backslash ASCII text rejected", err)
	}
	changesManifest := []func(map[string]map[string]any){
		func(v map[string]map[string]any) {
			v["activate"]["Signature"] = v["activate"]["signature"]
			delete(v["activate"], "signature")
		},
		func(v map[string]map[string]any) { v["activate"]["signature"] = nil },
		func(v map[string]map[string]any) { v["activate"]["inputLayout"] = nil },
		func(v map[string]map[string]any) { v["activate"]["outputLayout"] = []any{false} },
		func(v map[string]map[string]any) { v["activate"]["mutability"] = "view" },
	}
	for i, change := range changesManifest {
		var v map[string]map[string]any
		if err := json.Unmarshal(s, &v); err != nil {
			t.Fatal(err)
		}
		change(v)
		b, err := json.Marshal(v)
		if err != nil {
			t.Fatal(err)
		}
		if _, err := inspect(a, b); err == nil {
			t.Errorf("closed manifest control %d accepted", i)
		}
	}
	for _, b := range []string{`{"activate":null}`, `{"activate":{}}`, `{"activate":{"signature":"x","mutability":"view","inputLayout":[],"outputLayout":null}}`} {
		if _, err := inspect(a, []byte(b)); err == nil {
			t.Fatal("bad manifest shape accepted")
		}
	}
}
