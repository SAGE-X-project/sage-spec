# Reproduce the stage-2 inventory

Use the pinned source revisions and sibling consumer revisions in
[`source-consumer-map.json`](source-consumer-map.json). Run the parsers against
those checkouts and write intermediate JSON outside the repositories:

```sh
cd /path/to/sage
go run /path/to/sage-spec/analysis/library-adoption-stage2/go-ast.go /path/to/sage > /tmp/sage-go-ast.json

CARGO_TARGET_DIR=/tmp/sage-stage2-target cargo run --locked --offline \
  --manifest-path /path/to/sage-spec/analysis/library-adoption-stage2/rust-ast/Cargo.toml -- \
  /path/to/rs-sage-core/src > /tmp/sage-rust-ast.json

cd /path/to/sage-spec
python3 -B analysis/library-adoption-stage2/build-map.py \
  --projects-root /path/to/sage-x-project \
  --go-ast /tmp/sage-go-ast.json --rust-ast /tmp/sage-rust-ast.json \
  > /tmp/sage-source-consumer-map.json
cmp analysis/library-adoption-stage2/source-consumer-map.json /tmp/sage-source-consumer-map.json
```

The Go parser records exported declarations and methods on exported receiver
types. The Rust parser records syntactically public declarations; it does not
resolve private-module or `cfg` reachability. The map builder keeps only files
tracked by Git and skips consumer test imports. Representative external build
probes and their limits are documented in the
[audit](../../architecture/library-adoption-stage2.md).
