#!/usr/bin/env python3
"""Rebuild the generated files from the skill source.

    python tools/build_dist.py

Writes:
  portable/pipeline-skill-prompt.md   one file with every instruction, for tools without skill support
  dist/pipeline-skill.zip             the skill folder, ready to upload
  examples/sample-report.md / .html   the sample report, rendered from examples/sample-report.json
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "pipeline-skill"

PARTS = [
    ("references/setup.md", "Setup wizard"),
    ("references/evidence-rules.md", "Evidence rules"),
    ("references/pipeline-review.md", "Pipeline review"),
    ("references/stale-deals.md", "Stale deals"),
    ("references/owes-and-chases.md", "Owes and chases"),
    ("references/report-format.md", "Report format"),
    ("assets/config-template.md", "Config template"),
]

HEADER = """# Pipeline Skill: portable prompt

This is the whole pipeline skill in one file, for AI tools that do not load skill folders.
It is generated from the skill source by `tools/build_dist.py`. Do not edit it by hand.

## How to use this file

Paste it into the instructions of a project, custom assistant, or gem in your AI tool, or attach
it at the start of a conversation and say "set up the pipeline skill."

## Notes for the assistant reading this

- Everything below is your instruction set. Part 1 is the main workflow. The other parts are the
  reference files it points to. Where the text says to read a file such as
  `references/setup.md`, use the part with that name below.
- The build script and the demo data are not included here. Build the report by hand using the
  markdown layout in the "Report format" part, and apply every length cap and evidence rule
  yourself, since no script will check them for you. Skip the HTML version.
- If asked for a demo, explain that the demo data ships with the full repository and offer to
  run setup instead.
"""


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        return text.split("---", 2)[2].lstrip("\n")
    return text


def build_portable() -> Path:
    out = [HEADER, "\n---\n\n# Part 1: Main workflow (SKILL.md)\n\n"]
    out.append(strip_frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8")))
    for number, (rel, title) in enumerate(PARTS, start=2):
        out.append(f"\n---\n\n# Part {number}: {title} (`{rel}`)\n\n")
        out.append((SKILL / rel).read_text(encoding="utf-8"))
    path = ROOT / "portable" / "pipeline-skill-prompt.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(out), encoding="utf-8")
    return path


def build_zip() -> Path:
    path = ROOT / "dist" / "pipeline-skill.zip"
    path.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(SKILL.rglob("*")):
            if file.is_file() and "__pycache__" not in file.parts and file.name != ".DS_Store":
                zf.write(file, Path("pipeline-skill") / file.relative_to(SKILL))
    return path


def build_sample() -> int:
    return subprocess.call(
        [sys.executable, str(SKILL / "scripts" / "build_report.py"), str(ROOT / "examples" / "sample-report.json"),
         "--out-dir", str(ROOT / "examples"), "--basename", "sample-report"]
    )


if __name__ == "__main__":
    print(f"Wrote {build_portable().relative_to(ROOT)}")
    print(f"Wrote {build_zip().relative_to(ROOT)}")
    sys.exit(build_sample())
