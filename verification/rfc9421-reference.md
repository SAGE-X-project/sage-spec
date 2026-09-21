# Local RFC 9421 reference assessment

User-designated path: `/Users/0xtopaz/work/github/sage-x-project/rfc9421`.
Reviewed 2026-09-13. Informative evidence for [chapter 03](../spec/03-rfc9421.md).

## Provenance and authority

HEAD is `a918cf61f0ec94efd75c58d62d952a348cc95bbd`, but the consulted RFC text,
Go module and implementation files are **untracked working-tree files**. That
commit does not identify their bytes. The SHA-256 inventory below pins the
consulted files; `.DS_Store` is excluded. No source files were modified.

`en.txt` contains local English RFC text; `kr.txt` and
`http_message_signatures.md` provide Korean/bilingual reading material.
The [official RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html) and applicable
verified errata remain authoritative. Local translations have not received a
complete translation audit or byte-equivalence certification.

## Implementation comparison

| Local source / observation | RFC or SAGE consequence | Existing inspector rule groups |
|---|---|---|
| `pkg/rfc9421/builder.go`: sorts header/parameter maps, emits unquoted field names and `(request-target)`, omits the final `@signature-params` line | RFC 9421 sections 2.3/2.5 require covered-component construction and signature metadata binding. Preserve the declared ordering; this builder is not a conforming reference base generator. | MSG-01, MSG-02, MSG-04 |
| `pkg/rfc9421/parser.go`: checks presence of Signature-Input but parses comma-separated Signature parameters and looks for a `signature` key | RFC sections 4.1/4.2 use related Structured Field dictionaries. Parse the declared label, inner list, parameters and signature byte sequence; a presence check is insufficient. | MSG-01, MSG-04 |
| Parser keeps its map across ParseHeaders calls | A reused parser can retain earlier values. Future implementations need isolated per-message parsing and duplicate/malformed-field rejection. | MSG-04 |
| `cmd/server/main.go`: signs form message bytes, sets both signature headers to GetSignatureInput, rather than signing the constructed HTTP base | The illustrated flow does not authenticate the RFC HTTP signature base. It supplies no conforming request-bound response evidence. | MSG-02, MSG-03, MSG-04 |
| `pkg/client/client.go`: submits a form and returns response bytes without signature verification | SAGE requires verification before accepting results; unsigned data is not an authenticated result. | MSG-03, MSG-04, MSG-06 |
| RSA PKCS1v1.5/SHA-256 and ECDSA P-256/SHA-256 signer sketches | RFC 9421 defines these algorithm families, but SAGE chapter 01 chooses a narrower set. P-256 is not SAGE's secp256k1/Keccak suite. Do not copy algorithm support by name alone. | MSG-01 |

The interface separation between signing, parsing/building, client and server is
useful implementation context. No interoperability or security equivalence is
inferred from that separation. The observations above refine review inputs for
the existing planned groups, without claiming new executed conformance cases.

## Build evidence

Executed in the reference repository with external dependency fetching disabled:

```sh
GOTOOLCHAIN=local GOPROXY=off GOCACHE=/private/tmp/sage-rfc9421-build-cache go test ./...
```

Exit status: **1, build failed**. Reported blockers include undefined
`MessageSigner` in parser.go, ECDSA receiver/result name collisions in ecdsa.go,
and passing `crypto.PublicKey` where `ed25519.PublicKey` is required in ed25519.go.
Packages that reached test discovery reported no test files. This is a failed
build check, not a completed RFC conformance test. No service was started.
Static inspection also shows a nil Curve dereference in the ECDSA verification
sketch; its runtime behaviour was not tested because the package does not build.

## Follow-up use

Use the local RFC documents while tracing chapter 03 to the official sections.
Use this implementation as historical design context and a source of regression
scenarios. Before adopting it as a library or comparison oracle, implementation
work must resolve build blockers and demonstrate RFC examples plus SAGE profile
cases in `sage-inspector`. That implementation work is outside this docs update.
The initial SAGE AST graph is unchanged; no RFC-project AST extraction is claimed.

## Consulted working-tree file hashes

| File | SHA-256 |
|---|---|
| `README.md` | `521ad078d2766c41e521329316b0e2cd3364d3f61804ff0dcf543be717c27a5a` |
| `go.mod` | `d5a8a7467948ffa831bb66f4e852c1a4bf713484217f8259b05bfaffb2f61c72` |
| `en.txt` | `bd168c908b3f436a9e63d7dae6341c933ca01bc628e91ad0770bd8e21e521097` |
| `kr.txt` | `1fa0fceed714d9e6e67e431f53a5c63fca366a8ea91bb6f39a41346a6e177976` |
| `http_message_signatures.md` | `7b7cd555b5ccb8212051b6e70e35f9896dadf1d19f5f455bcd82a731466d3e14` |
| `pkg/rfc9421/parser.go` | `4d5246a6dcb1f46d2ee2bbe220fa1444c7821baf126b211dad0e6b1ddfa6b6dc` |
| `pkg/rfc9421/builder.go` | `0fe2d630de5f05d5534680491fbfd83ce7775aea54bb00115a833e0a8e79d26f` |
| `pkg/interfaces/message.go` | `7064527d91a09ab6995d8a8f664d5e80bf8978857f6ceacc4bc4fd663c29be46` |
| `pkg/server/handler.go` | `327663db16f613bd5d8af32fbccb790ff75cdaa5ff172377b8dbb8744909b31d` |
| `pkg/server/signer.go` | `5b63bc2874036530b9639d0d791dd10757d9634ce7ff38a881bf484017d405a8` |
| `pkg/client/client.go` | `b60b8fab0aa71c1732b913d22b1d50fc1f36092911ba6510c7afdb6854a516d2` |
| `pkg/signers/ed25519.go` | `601cf250d416116b0abf2c5873b0efef9145e494145e53bff5d98143392c8fe4` |
| `pkg/signers/ecdsa.go` | `cf9911ec22aafb020644f670c6af7e0745da131a905e1176245a86e372877378` |
| `cmd/server/main.go` | `5b082396bd0d77c58526eaf843c6f4e16bc14bd4412f83d703cc75b2c7b37a61` |
