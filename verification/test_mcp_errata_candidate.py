"""Check that changed descriptor bytes cannot inherit the candidate digest."""

import copy
import json
import unittest

from check_mcp_errata_candidate import DESCRIPTOR, MANIFEST, verify_digest


class DescriptorDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.raw = DESCRIPTOR.read_bytes()

    def test_pinned_descriptor(self):
        self.assertEqual(verify_digest(self.manifest, self.raw), 1141)

    def test_changed_descriptor_rejected(self):
        changed = self.raw.replace(b"sage_secure_call", b"sage_secure_check", 1)
        with self.assertRaisesRegex(ValueError, "descriptor file identity"):
            verify_digest(self.manifest, changed)

    def test_raw_file_digest_cannot_replace_jcs_digest(self):
        changed = copy.deepcopy(self.manifest)
        changed["jcs_sha256_hex"] = changed["raw_file_sha256"]
        with self.assertRaisesRegex(ValueError, "JCS digest"):
            verify_digest(changed, self.raw)

    def test_duplicate_members_rejected_before_jcs(self):
        changed = b'{"name":"sage_secure_call","name":"sage_secure_call"}'
        manifest = copy.deepcopy(self.manifest)
        import hashlib
        manifest["raw_file_sha256"] = hashlib.sha256(changed).hexdigest()
        with self.assertRaisesRegex(ValueError, "duplicate descriptor member"):
            verify_digest(manifest, changed)

    def test_negative_zero_is_not_normalized(self):
        changed = b'{"value":-0}'
        manifest = copy.deepcopy(self.manifest)
        import hashlib
        manifest["raw_file_sha256"] = hashlib.sha256(changed).hexdigest()
        with self.assertRaisesRegex(ValueError, "negative-zero"):
            verify_digest(manifest, changed)


if __name__ == "__main__":
    unittest.main()
