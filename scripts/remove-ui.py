#!/usr/bin/env python3
"""Delete the optional frontend tooling, for a package without React stubs.

  make remove-ui   (or: python3 scripts/remove-ui.py)

Deletes the React stubs, their Vitest tests, package.json, tsconfig.json,
vitest.config.ts, the ui-suite workflow and scripts/typecheck-stubs.sh, then
removes everything between "ui:start" and "ui:end" markers (Makefile,
workflows, .gitattributes, README.md, CLAUDE.md) and un-comments the
"ui:replace" lines. Finally it deletes itself. Idempotent.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent

DELETE = [
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "vitest.config.ts",
    "node_modules",
    "tests/js",
    "stubs/inertia-react",
    ".github/workflows/ui-suite.yml",
    "scripts/typecheck-stubs.sh",
]

EDIT = [
    "Makefile",
    ".gitattributes",
    ".github/workflows/tests.yml",
    ".github/workflows/full-matrix.yml",
    "README.md",
    "CLAUDE.md",
]

# Marker lines: "# ui:start" (Makefile, YAML, .gitattributes) or
# "<!-- ui:start -->" (Markdown), on a line of their own.
BLOCK = re.compile(r"^[ \t]*(?:#|<!--) ui:start(?: -->)?[ \t]*\n.*?^[ \t]*(?:#|<!--) ui:end(?: -->)?[ \t]*\n", re.MULTILINE | re.DOTALL)
# Inside a Markdown line: "text<!-- ui:start --> UI-only text<!-- ui:end -->".
INLINE = re.compile(r"<!-- ui:start -->.*?<!-- ui:end -->")
REPLACE = re.compile(r"^([ \t]*)# ui:replace (.*)$", re.MULTILINE)


def main() -> None:
    for rel in DELETE:
        path = ROOT / rel
        if path.is_dir():
            shutil.rmtree(path)
            print(f"deleted {rel}/")
        elif path.exists():
            path.unlink()
            print(f"deleted {rel}")

    stubs = ROOT / "stubs"
    if stubs.is_dir() and not any(stubs.iterdir()):
        stubs.rmdir()
        print("deleted stubs/")

    for rel in EDIT:
        path = ROOT / rel
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        text = REPLACE.sub(r"\1\2", INLINE.sub("", BLOCK.sub("", original)))
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"edited  {rel}")

    pathlib.Path(__file__).unlink()
    print("deleted scripts/remove-ui.py")
    print("Done. Run make ci to check.")


if __name__ == "__main__":
    main()
