use std::{env, fs, path::Path};
use syn::{Item, Visibility};
fn walk(root: &Path, dir: &Path, out: &mut Vec<serde_json::Value>) {
    for e in fs::read_dir(dir).unwrap() {
        let p = e.unwrap().path();
        if p.is_dir() {
            walk(root, &p, out);
            continue;
        }
        if p.extension().is_none_or(|x| x != "rs") {
            continue;
        }
        let data = fs::read_to_string(&p).unwrap();
        let file = syn::parse_file(&data).unwrap_or_else(|error| panic!("{}: {error}", p.display()));
        let rel = p.strip_prefix(root).unwrap().to_string_lossy().to_string();
        for item in file.items {
            let (kind, name, pubvis) = match item {
                Item::Fn(x) => (
                    "fn",
                    x.sig.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Struct(x) => (
                    "struct",
                    x.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Enum(x) => (
                    "enum",
                    x.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Trait(x) => (
                    "trait",
                    x.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Type(x) => (
                    "type",
                    x.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Mod(x) => (
                    "mod",
                    x.ident.to_string(),
                    matches!(x.vis, Visibility::Public(_)),
                ),
                Item::Use(x) => ("use", String::new(), matches!(x.vis, Visibility::Public(_))),
                Item::Impl(x) => {
                    let owner = match x.self_ty.as_ref() {
                        syn::Type::Path(p) => p
                            .path
                            .segments
                            .last()
                            .map(|x| x.ident.to_string())
                            .unwrap_or_default(),
                        _ => String::new(),
                    };
                    for im in x.items {
                        if let syn::ImplItem::Fn(f) = im {
                            if matches!(f.vis, Visibility::Public(_)) {
                                out.push(serde_json::json!({"file":rel,"kind":"method","name":format!("{}.{}",owner,f.sig.ident)}));
                            }
                        }
                    }
                    continue;
                }
                _ => continue,
            };
            if pubvis {
                out.push(serde_json::json!({"file":rel,"kind":kind,"name":name}));
            }
        }
    }
}
fn main() {
    let root = env::args().nth(1).unwrap();
    let root = Path::new(&root);
    let mut out = Vec::new();
    walk(root, root, &mut out);
    out.sort_by_key(|v| {
        (
            v["file"].as_str().unwrap().to_owned(),
            v["kind"].as_str().unwrap().to_owned(),
            v["name"].as_str().unwrap().to_owned(),
        )
    });
    println!("{}", serde_json::to_string(&out).unwrap());
}
