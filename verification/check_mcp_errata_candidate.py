"""Check the bounded descriptor vector in the non-HTTP MCP errata candidate."""

import base64
import hashlib
import json
from pathlib import Path

from check_mcp_adoption import verify as verify_adoption


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "proposals/non-http-mcp-errata/descriptor-digest.json"
DESCRIPTOR = ROOT / "profiles/non-http-mcp-tool.json"
EXPECTED_ID = "sage-mcp-non-http/0.10.0/mcp-2025-06-18"
EXPECTED_DIGEST = "sha256-jcs:f40nkKDT3hQs9poaxZxm8Bgw4hUV1f036fGMmIaKPtQ"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate descriptor member")
        result[key] = value
    return result


def restricted_jcs(raw):
    """Canonicalize only this descriptor's ASCII, integer-only JCS subset."""
    require(all(byte < 128 for byte in raw), "descriptor outside checked ASCII subset")

    def integer(token):
        require(token != "-0", "negative-zero descriptor integer")
        value = int(token)
        require(abs(value) <= 9007199254740991, "non-I-JSON descriptor integer")
        return value

    def unsupported_number(_token):
        raise ValueError("descriptor outside checked integer-only subset")

    value = json.loads(
        raw,
        object_pairs_hook=unique_pairs,
        parse_int=integer,
        parse_float=unsupported_number,
        parse_constant=unsupported_number,
    )

    def check(node):
        if isinstance(node, dict):
            for key, child in node.items():
                require(key.isascii(), "non-ASCII descriptor key")
                check(child)
        elif isinstance(node, list):
            for child in node:
                check(child)
        elif isinstance(node, str):
            require(node.isascii(), "non-ASCII descriptor string")
        elif type(node) is int:
            require(abs(node) <= 9007199254740991, "non-I-JSON descriptor integer")
        else:
            require(node is None or type(node) is bool, "unsupported JCS primitive")

    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_digest(manifest, raw):
    require(manifest["status"] == "NOT_NORMATIVE", "candidate status")
    require(manifest["binding_identifier"] == EXPECTED_ID, "binding identifier")
    require(manifest["descriptor"] == "../../profiles/non-http-mcp-tool.json", "descriptor path")
    require(hashlib.sha256(raw).hexdigest() == manifest["raw_file_sha256"], "descriptor file identity")
    canonical = restricted_jcs(raw)
    digest = hashlib.sha256(canonical).digest()
    require(len(canonical) == manifest["canonical_utf8_bytes"], "canonical length")
    require(digest.hex() == manifest["jcs_sha256_hex"], "JCS digest")
    encoded = "sha256-jcs:" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    require(encoded == manifest["descriptor_digest"] == EXPECTED_DIGEST, "encoded digest")
    return len(canonical)


def verify(root=ROOT):
    verify_adoption(root)
    manifest = json.loads((root / "proposals/non-http-mcp-errata/descriptor-digest.json").read_text())
    size = verify_digest(manifest, (root / "profiles/non-http-mcp-tool.json").read_bytes())
    candidate = (root / "proposals/non-http-mcp-errata/candidate.md").read_text()
    require("Status: **design candidate**" in candidate, "candidate status text")
    require(EXPECTED_ID in candidate and EXPECTED_DIGEST in candidate, "candidate constants")
    return {"binding_identifier": EXPECTED_ID, "jcs_bytes": size, "status": "NOT_NORMATIVE"}


if __name__ == "__main__":
    print("MCP errata candidate PASS: " + json.dumps(verify(), sort_keys=True))
