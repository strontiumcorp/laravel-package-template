#!/usr/bin/env python3
"""Turn the template into a named package, in one go.

  scripts/configure.py --package laravel-support-sso [options]
  make configure ARGS="--package laravel-support-sso --title 'Support SSO'"

Replaces the placeholders across the tree (file contents and file names):

  strontiumcorp/laravel-package-template   -> VENDOR/PACKAGE   (Composer name, GitHub URLs)
  StrontiumCorp\\PackageTemplate            -> NAMESPACE        (also JSON-escaped)
  laravel-package-template                 -> PACKAGE          (repo name, vendor/ stub dir)
  PackageTemplate                          -> CLASS            (PackageTemplateServiceProvider, ...)
  package-template                         -> CONFIG_KEY       (config file, routes, publish tags)
  PACKAGE_TEMPLATE                         -> CONFIG_KEY in UPPER_SNAKE (env vars)
  Package Template                         -> TITLE            (`php artisan about`, docs)

and drops the template-only sections of README.md and CLAUDE.md (between
"template:start" and "template:end" markers). With --no-ui it also runs
scripts/remove-ui.py.

Idempotent: once configured, no placeholder is left, so running it again
changes nothing. Then run `composer dump-autoload` (or `make install`) and
`make ci`.
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).resolve()

SKIP_DIRS = {".git", "vendor", "node_modules", "build", ".phpunit.cache", "coverage", "__pycache__"}
SKIP_FILES = {"composer.lock"}

PLACEHOLDER_VENDOR = "strontiumcorp"
PLACEHOLDER_NAMESPACE_VENDOR = "StrontiumCorp"
PLACEHOLDER_TOKENS = ("PackageTemplate", "package-template", "PACKAGE_TEMPLATE", "Package Template")

TEMPLATE_BLOCK = re.compile(r"^[ \t]*<!-- template:start -->\n.*?^[ \t]*<!-- template:end -->\n", re.MULTILINE | re.DOTALL)

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAMESPACE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:\\[A-Z][A-Za-z0-9]*)+$")
CLASS = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def studly(kebab: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in kebab.split("-"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package", required=True, help="Composer package name without the vendor, e.g. laravel-support-sso")
    parser.add_argument("--vendor", default=PLACEHOLDER_VENDOR, help=f"Composer vendor and GitHub owner (default: {PLACEHOLDER_VENDOR})")
    parser.add_argument("--config-key", help="Config key, file and route prefix (default: PACKAGE without 'laravel-', e.g. support-sso)")
    parser.add_argument("--class", dest="class_name", help="Class-name prefix (default: CONFIG_KEY in StudlyCase, e.g. SupportSso)")
    parser.add_argument("--namespace", help="Root PHP namespace (default: StrontiumCorp\\CLASS, or the vendor in StudlyCase)")
    parser.add_argument("--title", help="Human name for `php artisan about` and the docs (default: CONFIG_KEY in Title Case)")
    parser.add_argument("--description", help="composer.json description")
    parser.add_argument("--no-ui", action="store_true", help="Also delete the optional frontend tooling (scripts/remove-ui.py)")
    parser.add_argument("--dry-run", action="store_true", help="List what would change; write nothing")
    args = parser.parse_args()

    for name in ("package", "vendor"):
        if not KEBAB.match(getattr(args, name)):
            parser.error(f"--{name} must be lowercase kebab-case, got: {getattr(args, name)}")

    args.config_key = args.config_key or args.package.removeprefix("laravel-")
    if not KEBAB.match(args.config_key):
        parser.error(f"--config-key must be lowercase kebab-case, got: {args.config_key}")

    args.class_name = args.class_name or studly(args.config_key)
    if not CLASS.match(args.class_name):
        parser.error(f"--class must be StudlyCase, got: {args.class_name}")

    vendor_ns = PLACEHOLDER_NAMESPACE_VENDOR if args.vendor == PLACEHOLDER_VENDOR else studly(args.vendor)
    args.namespace = (args.namespace or f"{vendor_ns}\\{args.class_name}").strip("\\")
    if not NAMESPACE.match(args.namespace):
        parser.error(f"--namespace must look like Vendor\\Package, got: {args.namespace}")

    args.title = args.title or " ".join(part.capitalize() for part in args.config_key.split("-"))

    # A new value holding a placeholder would be replaced again on the next run.
    for value in (args.package, args.config_key, args.class_name, args.namespace, args.title):
        if any(token.lower() in value.lower() for token in PLACEHOLDER_TOKENS):
            parser.error(f"{value!r} contains a template placeholder; pick another name")

    return args


def replacements(args: argparse.Namespace) -> list[tuple[str, str]]:
    """Longest, most specific first: each later token is a substring of an earlier one."""
    return [
        ("strontiumcorp/laravel-package-template", f"{args.vendor}/{args.package}"),
        ("StrontiumCorp\\\\PackageTemplate", args.namespace.replace("\\", "\\\\")),
        ("StrontiumCorp\\PackageTemplate", args.namespace),
        ("laravel-package-template", args.package),
        ("PackageTemplate", args.class_name),
        ("package-template", args.config_key),
        ("PACKAGE_TEMPLATE", args.config_key.upper().replace("-", "_")),
        ("Package Template", args.title),
    ]


def files() -> list[pathlib.Path]:
    found = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or path.name in SKIP_FILES or path == SELF:
            continue
        if path.is_file() and not path.is_symlink():
            found.append(path)
    return found


def apply(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def main() -> None:
    args = parse_args()
    pairs = replacements(args)
    changed: list[str] = []

    for path in files():
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary

        text = apply(original, pairs)
        if path.name in {"README.md", "CLAUDE.md"}:
            text = TEMPLATE_BLOCK.sub("", text)
        if args.description and path.name == "composer.json" and path.parent == ROOT:
            text = re.sub(r'("description": )"[^"]*"', lambda m: m.group(1) + '"' + args.description.replace('"', '\\"') + '"', text, count=1)

        if text != original:
            changed.append(f"edit    {path.relative_to(ROOT)}")
            if not args.dry_run:
                path.write_text(text, encoding="utf-8")

    # File and directory names, deepest first so parents are renamed last.
    for path in sorted(files() + [p for p in ROOT.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or path == SELF:
            continue
        new_name = apply(path.name, pairs)
        if new_name != path.name:
            changed.append(f"rename  {rel} -> {rel.parent / new_name}")
            if not args.dry_run:
                path.rename(path.with_name(new_name))

    if args.no_ui and (ROOT / "scripts/remove-ui.py").exists():
        changed.append("run     scripts/remove-ui.py")
        if not args.dry_run:
            subprocess.run([sys.executable, str(ROOT / "scripts/remove-ui.py")], check=True)

    if not changed:
        print("Nothing to change: the template is already configured.")
        return

    print("\n".join(changed))
    print()
    print(f"{'Would configure' if args.dry_run else 'Configured'} {args.vendor}/{args.package}: "
          f"namespace {args.namespace}, config key '{args.config_key}', class prefix {args.class_name}, title '{args.title}'.")
    if not args.dry_run:
        print("Next: composer dump-autoload (or make install), then make ci.")


if __name__ == "__main__":
    main()
