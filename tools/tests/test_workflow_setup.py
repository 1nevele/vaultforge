"""Offline repository-configuration checks, not Claude skill execution tests."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUPERPOWERS = {
    "test-driven-development", "systematic-debugging", "verification-before-completion",
}
# Code review moved to the built-in /code-review and the Claude PR review workflow.
RETIRED_SUPERPOWERS = {"requesting-code-review", "receiving-code-review"}
SPECKIT = {
    "speckit-analyze", "speckit-checklist", "speckit-clarify", "speckit-constitution",
    "speckit-converge", "speckit-implement", "speckit-plan", "speckit-specify", "speckit-tasks",
}


def safe_file(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError("unsafe manifest path")
    target = root.joinpath(*path.parts)
    if any(p.is_symlink() for p in [target, *target.parents] if p != root.parent):
        raise ValueError("symlink in manifest path")
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("manifest path escapes root")
    return target


class WorkflowSetupTests(unittest.TestCase):
    def manifest(self):
        path = ROOT / "tools/provenance.json"
        self.assertTrue(path.is_file(), "native skill provenance has not been adopted")
        return json.loads(path.read_text())

    def test_native_inventory_is_bounded_and_complete(self):
        actual = {p.parent.name for p in (ROOT / ".claude/skills").glob("*/SKILL.md")}
        self.assertEqual(actual, SUPERPOWERS | SPECKIT)

    def test_retired_review_skills_are_absent(self):
        for name in RETIRED_SUPERPOWERS:
            self.assertFalse((ROOT / ".claude/skills" / name).exists(), name)

    def test_pins_and_unexercised_cloud_status(self):
        data = self.manifest()
        self.assertEqual(data["superpowers"]["commit"], "22f0b463e7a5e579904dd6211a520321035526f7")
        self.assertEqual(data["spec_kit"]["commit"], "99d10403a2681981be98bd372fa412045180d105")
        self.assertEqual(set(data["superpowers"]["skills"]), SUPERPOWERS)
        self.assertFalse(data["cloud_session_tested"])
        self.assertFalse(data["plugins_enabled"])

    def test_manifest_hashes_and_full_native_coverage(self):
        data = self.manifest()
        paths = []
        for section in (data["superpowers"]["files"], data["spec_kit"]["files"], data["licenses"]):
            for record in section:
                target = safe_file(ROOT, record["path"])
                self.assertTrue(target.is_file(), record["path"])
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), record["sha256"], record["path"])
                paths.append(record["path"])
        self.assertEqual(len(paths), len(set(paths)), "duplicate provenance record")
        actual = {str(p.relative_to(ROOT)) for p in (ROOT / ".claude/skills").rglob("*") if p.is_file()}
        recorded = {p for p in paths if p.startswith(".claude/skills/")}
        self.assertEqual(actual, recorded)

    def test_frontmatter_and_namespaces(self):
        for entry in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
            text = entry.read_text()
            self.assertTrue(text.startswith("---\n"), str(entry))
            header = text.split("---", 2)[1]
            match = re.search(r"^name:\s*[\"']?([^\n\"']+)", header, re.M)
            self.assertIsNotNone(match, str(entry))
            assert match is not None
            self.assertEqual(match.group(1).strip(), entry.parent.name)
            self.assertRegex(header, r"(?m)^description:\s*\S")
        for name in SUPERPOWERS:
            for file in (ROOT / ".claude/skills" / name).rglob("*.md"):
                self.assertNotRegex(file.read_text(), r"superpowers:[a-z][a-z-]+", str(file))

    def test_selected_skill_resources_exist(self):
        for name in SUPERPOWERS:
            for file in (ROOT / ".claude/skills" / name).rglob("*.md"):
                text = re.sub(r"```.*?```", "", file.read_text(), flags=re.S)
                for link in re.findall(r"\]\(([^\s)]+)\)", text):
                    if re.match(r"^(?:[a-z]+:|#)", link):
                        continue
                    self.assertTrue((file.parent / link.split("#", 1)[0]).is_file(), f"{file.name}: {link}")
        debug = ROOT / ".claude/skills/systematic-debugging"
        for name in ("root-cause-tracing.md", "defense-in-depth.md", "condition-based-waiting.md"):
            self.assertTrue((debug / name).is_file(), name)

    def test_official_speckit_skill_manifest(self):
        manifest = json.loads((ROOT / ".specify/integrations/claude.manifest.json").read_text())
        self.assertEqual(len(manifest["files"]), len(SPECKIT))
        for relative, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256(safe_file(ROOT, relative).read_bytes()).hexdigest(), digest)

    def test_no_automatic_plugins_or_bootstrap_installers(self):
        self.assertFalse((ROOT / ".claude/settings.json").exists())
        self.assertFalse((ROOT / ".claude/hooks").exists())
        self.assertFalse((ROOT / ".claude/scripts").exists())
        self.assertFalse((ROOT / ".claude-plugin").exists())
        self.assertFalse((ROOT / ".claude/skills/brainstorming").exists())
        for base in (ROOT / ".claude", ROOT / ".specify"):
            self.assertFalse(any(p.is_symlink() for p in base.rglob("*")))

    def test_entry_point_and_monorepo_links(self):
        for relative in ("README.md", "projects/sentinel/README.md"):
            file = ROOT / relative
            for link in re.findall(r"\]\(([^\s)]+)\)", file.read_text()):
                self.assertTrue((file.parent / link).is_file(), f"{relative}: {link}")
        text = (ROOT / "CLAUDE.md").read_text()
        for name in SUPERPOWERS:
            self.assertIn(name, text)
        self.assertIn("docs/claude-web-skill-smoke.md", text)

    def test_manifest_paths_reject_escape_and_absolute_paths(self):
        for bad in ("../outside", "/absolute", "a/../../outside", "a\\outside"):
            with self.assertRaises(ValueError, msg=bad):
                safe_file(ROOT, bad)

    def test_development_lock_targets_cloud_not_hermes(self):
        data = json.loads((ROOT / "development-tools.lock.json").read_text())
        self.assertIn("executor", data, "development lock still describes the historical Hermes setup")
        self.assertEqual(data["executor"], "claude-code-web")
        self.assertEqual(data["superpowers"]["distribution"], "native-project-skill-subset")
        self.assertFalse(data["cloud_session_tested"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
