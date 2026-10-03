#!/usr/bin/env python3
"""Build the stage 2 source/API and consumer inventory from parsed AST rows."""

import argparse
import json
import pathlib
import re
import subprocess


GO_FOCUS = (
    "pkg/agent/core/rfc9421",
    "pkg/agent/crypto",
    "pkg/agent/did",
    "pkg/agent/execution010",
    "pkg/agent/guard010",
    "pkg/agent/hpke",
    "pkg/agent/registry010",
    "pkg/agent/session",
    "pkg/agent/transport",
)
RUST_FOCUS = (
    "lib.rs", "core", "crypto", "did", "execution010", "ffi", "guard010",
    "hpke", "registry010", "rfc9421", "session",
)
CONSUMERS = (
    "sage-adk", "sage-a2a-go", "sage-gateway", "sage-proxy-server",
    "sage-registry-service", "sage-inspector",
)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def tracked(repo):
    return set(git(repo, "ls-files").splitlines())


def go_packages(repo, ast_rows):
    paths = tracked(repo)
    out = {}
    for row in ast_rows:
        path = pathlib.PurePosixPath(row["file"])
        if row["file"] not in paths or not any(
            str(path.parent) == p or str(path.parent).startswith(p + "/") for p in GO_FOCUS
        ):
            continue
        package = str(path.parent)
        item = out.setdefault(package, {"declarations": [], "internal_imports": []})
        if row["kind"] == "imports":
            item["internal_imports"].extend(
                x for x in row.get("imports", [])
                if x.startswith("github.com/sage-x-project/sage/")
            )
        else:
            item["declarations"].append([row["kind"], row["name"], row["file"]])
    for item in out.values():
        item["internal_imports"] = sorted(set(item["internal_imports"]))
        item["declarations"].sort()
    return dict(sorted(out.items()))


def rust_modules(repo, ast_rows):
    paths = tracked(repo)
    out = {}
    for row in ast_rows:
        path = "src/" + row["file"]
        module = row["file"].split("/")[0]
        if path not in paths or module not in RUST_FOCUS:
            continue
        out.setdefault(module, []).append([row["kind"], row["name"], path])
    for rows in out.values():
        rows.sort()
    return dict(sorted(out.items()))


def consumers(root):
    out = {}
    for name in CONSUMERS:
        repo = root / name
        paths = tracked(repo)
        imports = {}
        rust = []
        for path in sorted(paths):
            if path.endswith(".go") and not path.endswith("_test.go"):
                body = (repo / path).read_text(errors="replace")
                for match in re.findall(r'"(github\.com/sage-x-project/sage(?:/[^"\s]*)?)"', body):
                    imports.setdefault(match, []).append(path)
            elif path.endswith("Cargo.toml"):
                body = (repo / path).read_text(errors="replace")
                if re.search(r'\bsage_crypto_core\s*=', body):
                    rust.append(path)
        module = repo / "go.mod"
        declared = []
        if module.is_file():
            declared = re.findall(r'^\s*github\.com/sage-x-project/sage\s+([^\s]+)',
                                  module.read_text(), re.MULTILINE)
        out[name] = {
            "revision": git(repo, "rev-parse", "HEAD"),
            "declared_go_sage_versions": declared,
            "production_go_imports": dict(sorted(imports.items())),
            "rust_crate_manifests": rust,
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projects-root", type=pathlib.Path, required=True)
    p.add_argument("--go-ast", type=pathlib.Path, required=True)
    p.add_argument("--rust-ast", type=pathlib.Path, required=True)
    args = p.parse_args()
    root = args.projects_root
    go_repo, rust_repo = root / "sage", root / "rs-sage-core"
    result = {
        "status": "source inventory, not implementation conformance",
        "go_revision": git(go_repo, "rev-parse", "HEAD"),
        "rust_revision": git(rust_repo, "rev-parse", "HEAD"),
        "go_ast": go_packages(go_repo, json.loads(args.go_ast.read_text())),
        "rust_ast": rust_modules(rust_repo, json.loads(args.rust_ast.read_text())),
        "consumers": consumers(root),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
