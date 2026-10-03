package main

import (
	"bytes"
	"encoding/json"
	"go/ast"
	"go/parser"
	"go/printer"
	"go/token"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type row struct {
	File    string   `json:"file"`
	Package string   `json:"package"`
	Kind    string   `json:"kind"`
	Name    string   `json:"name"`
	Imports []string `json:"imports,omitempty"`
}

func exportedReceiver(expr ast.Expr) bool {
	switch value := expr.(type) {
	case *ast.Ident:
		return ast.IsExported(value.Name)
	case *ast.StarExpr:
		return exportedReceiver(value.X)
	case *ast.IndexExpr:
		return exportedReceiver(value.X)
	case *ast.IndexListExpr:
		return exportedReceiver(value.X)
	default:
		return false
	}
}

func main() {
	root := os.Args[1]
	var out []row
	if err := filepath.WalkDir(root, func(p string, d os.DirEntry, e error) error {
		if e != nil {
			return e
		}
		if d.IsDir() {
			if d.Name() == ".git" || d.Name() == "vendor" {
				return filepath.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(p, ".go") || strings.HasSuffix(p, "_test.go") {
			return nil
		}
		f, err := parser.ParseFile(token.NewFileSet(), p, nil, parser.ImportsOnly)
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(root, p)
		imports := []string{}
		for _, im := range f.Imports {
			imports = append(imports, strings.Trim(im.Path.Value, "\""))
		}
		sort.Strings(imports)
		out = append(out, row{File: rel, Package: f.Name.Name, Kind: "imports", Imports: imports})
		f, err = parser.ParseFile(token.NewFileSet(), p, nil, 0)
		if err != nil {
			return err
		}
		for _, decl := range f.Decls {
			switch v := decl.(type) {
			case *ast.FuncDecl:
				if ast.IsExported(v.Name.Name) {
					if v.Recv != nil && !exportedReceiver(v.Recv.List[0].Type) {
						continue
					}
					kind := "func"
					name := v.Name.Name
					if v.Recv != nil {
						kind = "method"
						var b bytes.Buffer
						_ = printer.Fprint(&b, token.NewFileSet(), v.Recv.List[0].Type)
						name = b.String() + "." + name
					}
					out = append(out, row{File: rel, Package: f.Name.Name, Kind: kind, Name: name})
				}
			case *ast.GenDecl:
				for _, spec := range v.Specs {
					switch s := spec.(type) {
					case *ast.TypeSpec:
						if ast.IsExported(s.Name.Name) {
							out = append(out, row{File: rel, Package: f.Name.Name, Kind: "type", Name: s.Name.Name})
						}
					case *ast.ValueSpec:
						for _, n := range s.Names {
							if ast.IsExported(n.Name) {
								out = append(out, row{File: rel, Package: f.Name.Name, Kind: "value", Name: n.Name})
							}
						}
					}
				}
			}
		}
		return nil
	}); err != nil {
		panic(err)
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].File != out[j].File {
			return out[i].File < out[j].File
		}
		if out[i].Kind != out[j].Kind {
			return out[i].Kind < out[j].Kind
		}
		return out[i].Name < out[j].Name
	})
	if err := json.NewEncoder(os.Stdout).Encode(out); err != nil {
		panic(err)
	}
}
