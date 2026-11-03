import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from plan import TARGET_PATH, digest, plan, validate_manifest


class SyncPlannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.content = b"canonical skill"
        self.manifest = {
            "schema_version": 1,
            "skill_path": TARGET_PATH,
            "sha256": digest(self.content),
            "repositories": ["example/one"],
        }

    def test_missing_clone(self):
        self.assertEqual(plan(self.manifest, self.content, self.root)["targets"][0]["state"], "MISSING_CLONE")

    def test_missing_skill(self):
        (self.root / "example/one").mkdir(parents=True)
        self.assertEqual(plan(self.manifest, self.content, self.root)["targets"][0]["state"], "MISSING_SKILL")

    def test_in_sync(self):
        target = self.root / "example/one" / TARGET_PATH
        target.parent.mkdir(parents=True)
        target.write_bytes(self.content)
        self.assertEqual(plan(self.manifest, self.content, self.root)["targets"][0]["state"], "IN_SYNC")

    def test_drift(self):
        target = self.root / "example/one" / TARGET_PATH
        target.parent.mkdir(parents=True)
        target.write_bytes(b"changed")
        self.assertEqual(plan(self.manifest, self.content, self.root)["targets"][0]["state"], "DRIFT")

    def test_checksum_fails_closed(self):
        with self.assertRaises(ValueError):
            plan(self.manifest, b"tampered", self.root)

    def test_duplicate_rejected(self):
        self.manifest["repositories"].append("example/one")
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_bad_repo_rejected(self):
        self.manifest["repositories"] = ["../escape"]
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_symlink_rejected(self):
        target = self.root / "example/one" / TARGET_PATH
        target.parent.mkdir(parents=True)
        target.symlink_to(self.root / "outside")
        self.assertEqual(plan(self.manifest, self.content, self.root)["targets"][0]["state"], "BLOCKED_PATH")

    def test_no_target_writes(self):
        plan(self.manifest, self.content, self.root)
        self.assertFalse((self.root / "example").exists())


if __name__ == "__main__":
    unittest.main()
