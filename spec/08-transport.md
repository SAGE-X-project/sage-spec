# 8. Transport envelope

Go sources: `pkg/agent/transport/wire.go`, `transport/http/client.go`,
`transport/http/server.go`. No dedicated vector; the envelope is covered
through the RFC 9421 vectors (headers) and JSON field names below.

## 1. WireMessage

```json
{
  "id": "<message id>",
  "context_id": "<optional handshake / session context>",
  "task_id": "<optional>",
  "payload": "<base64 bytes>",
  "did": "<sender DID>",
  "signature": "<base64 bytes>",
  "metadata": { "<key>": "<value>" },
  "role": "<optional>"
}
```

`payload` and `signature` are JSON strings holding standard base64 of the
raw bytes. `signature` is the sender's signature over `payload` with the
algorithm of `01-crypto.md` selected by the sender's registered key. The
envelope carries no protocol version member; the version is carried by the
labels inside the payload (`hpke/complete@v1`, `v: "v1"`).

## 2. WireResponse

```json
{ "success": true, "message_id": "<id>", "task_id": "<optional>", "data": "<base64>", "error": "<optional>" }
```

## 3. HTTP headers

| Header | Content |
|---|---|
| `X-SAGE-DID` | sender DID; MUST equal `did` in the body |
| `X-SAGE-Message-ID` | MUST equal `id` |
| `X-SAGE-Context-ID` | MUST equal `context_id` when present |
| `X-SAGE-Task-ID` | MUST equal `task_id` when present |
| `X-SAGE-Meta-<key>` | one header per `metadata` entry |

The HTTP server rejects a request whose headers disagree with the body.
When the transport is HTTP, the request and response are additionally
signed per `03-rfc9421.md`; `x-sage-did` is a covered component there, so
the DID cannot be changed without invalidating the signature.

## 4. WebSocket

The same `WireMessage` / `WireResponse` JSON objects are sent as text
frames; the `X-SAGE-*` headers are not used.
