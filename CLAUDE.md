# CLAUDE.md — strontiumcorp/laravel-package-template

A Laravel package for Laravel 11, 12 and 13, PHP 8.2+. Composer `strontiumcorp/laravel-package-template`, namespace `StrontiumCorp\PackageTemplate`, config key `package-template`, repo `github.com/strontiumcorp/laravel-package-template` (installed as a VCS repository; not on Packagist). Maintainer: Mojahidul Islam (`@itsemon245`).

<!-- template:start -->
**This is the template itself**, not a package: it holds tooling only, no features. New packages start from it with `scripts/configure.py` (renames everything, then removes these template notes) and, without React stubs, `make remove-ui`; see the README. Changes here should stay generic: anything specific to one package belongs in that package. Keep `scripts/configure.py` working (run it in a scratch copy, then `make ci` there) when you add files or placeholders.

<!-- template:end -->
## Goal

Describe what the package does, which apps install it and anything they need from it. Keep this short; detail goes in `docs/`.

## Commands

`php` here is a Docker wrapper, so always go through the Makefile or `vendor/bin/*`. Run `make` to list the targets.

| Command | What it does |
|---|---|
| `make ci` | Pint (check), PHPStan level 6, the parallel Pest suite<!-- ui:start --> and `make test-js`<!-- ui:end -->. Run before every commit. |
| `make test PROCESSES=2` | The suite grouped the way CI groups it (CI has 2 workers; the local default is one per CPU). |
| `make test-filter FILTER="…"` | Run tests matching a name. |
| `make coverage` | Parallel coverage, fails under 85%. |
| `make test-matrix` | Laravel 11, 12 and 13, each with newest **and** lowest dependencies, in scratch copies. Run before pushing anything non-trivial. |
| `make test-laravel VERSION=11 [LOWEST=1]` | One cell of the matrix. |
| `make format` | Pint fix. |
| `make release ARGS="--dry-run"` | Preview the next release (see Git and releases). |
| `make release-pr` / `make release-tag` | For a protected `main`: open the release as a pull request, then tag it once merged. |
<!-- ui:start -->
| `make test-js` | `tsc` and Vitest for `stubs/inertia-react` (needs `npm ci`; `make install` does both). |
| `make typecheck-stubs APPS="../app-one ../app-two"` | Type-checks `stubs/inertia-react` against each app's real React/Inertia. Run after any stub change. |
| `make remove-ui` | Deletes the frontend tooling (for a package without React stubs). |
<!-- ui:end -->

**Never run mutation tests** (`pest --mutate`) as part of the normal loop: they are slow here, and `--parallel` reports false kills.

### Environment gotchas

- Perl can't open files in this repo; use `python3` for scripted edits.
- The shell is zsh: `$VAR` holding a command with arguments isn't word-split. Use env vars or write the command out.
- After `make format`, Pint may turn fully qualified names into `use` imports, so re-read a file before editing it again.
- Laravel 11 is EOL and every release carries advisories that Composer 2.9 blocks; `scripts/test-laravel.sh` and CI allow them only to verify compatibility.

## Git and releases

- Commits: focused, Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `ci:`, scopes like `fix(config):`, `!` for breaking). Short scannable subject; detail goes in extra `-m` paragraphs. **No `Co-Authored-By` or any other trailer.**
- Don't push unless asked. Pushing and tagging are the maintainer's call.
- Releasing (`scripts/release.sh` + `scripts/update-changelog.py`) infers the version from the commits (breaking → major, or minor below 1.0; `feat` → minor; else patch) and prepends grouped notes to `CHANGELOG.md`. `make release` runs only on a clean `main` that is up to date with `origin`, runs `make ci`, commits `chore: release vX.Y.Z`, creates an annotated tag with the notes, and pushes both atomically after you confirm. For a protected `main`, `make release-pr` opens that commit as a pull request from `release/vX.Y.Z` (based on `origin/main`) instead, and after it's merged (merge, squash or rebase; a squash must keep the title) `make release-tag` tags the merged commit and pushes only the tag. Both refuse while a pull-request release is untagged. Composer reads the version from the tag; no file holds a version. The tag push runs `full-matrix.yml`, whose last job publishes the GitHub Release from the tag's notes once all combinations pass (no Release for a red tag). Release only after CI on GitHub is green.
- CI layout: `.github/workflows/test-suite.yml` holds the test job once (reusable, takes a JSON matrix). `tests.yml` (every push/PR) runs static analysis plus 7 combinations<!-- ui:start --> and `ui-suite.yml`<!-- ui:end -->, under the plan's 20-concurrent-job limit so nothing queues. `full-matrix.yml` runs all 22 on `v*` tags, on demand, and nightly if `main` changed. Keep per-push jobs few so pushes stay under the concurrency limit. Runners are pinned to `ubuntu-24.04` (not `ubuntu-latest`, which moves to Ubuntu 26 from 2026-10-19); bump it deliberately, after a green run on the new image.

## Testing rules (each one learned the hard way)

- **Write the failing test first** for every bug, then fix it, then confirm the test fails without the fix (e.g. `git stash -- src/…`).
- **Never write into Testbench's `vendor/` skeleton.** Parallel workers share it; use a temp dir.
- **No process-global state in tests.** A parallel worker runs many test files in one PHP process, so a declared class, `class_alias` or `require`d class leaks into later files. Put fixtures under the `StrontiumCorp\PackageTemplate\Tests\` namespace (`tests/Fixtures/`) and use per-app state (e.g. set `app()->namespace` or `loadedProviders` by closure binding). Check with `make test PROCESSES=2`.
- **Freeze the clock** (`freezeSecond()`) in any test that asserts an exact time value. Two requests can straddle a second boundary on a slow runner.
- **Must pass on PHP 8.2** (CI's oldest): e.g. `class_alias()` of an internal class fails there.
- **Must pass on the lowest dependencies:** Laravel 11.x with Carbon 2 truncates `diffInSeconds()`. Compute whole-second waits from timestamps. Guzzle 7 (Laravel 11/12) and Guzzle 8 (Laravel 13) differ in their exceptions; handle both.
- SQLite foreign keys are on in `TestCase` (Testbench turns them off), so cascades and constraints behave as in production.
- Boot-time config (read while providers boot, e.g. `package-template.routes.enabled`) needs `$this->rebootWith([...])`.
- Never assert `null`/falsy on a response without asserting its status: a 500 can satisfy it.

## Invariants

- `config/package-template.php` is deep-merged with the app's published copy (`Support\ConfigMerge`), so new nested keys reach apps with old configs. Every new key needs its default in the config file; don't add `config('…', fallback)` defaults in code.
- Closures can't go in config (`config:cache`). Code-level rules are classes named in config that implement a contract, resolved per call.
- `env()` is read only in `config/` (an arch test enforces it).
- Octane: singletons hold no per-request state. Resolve the request and auth from the live container (`Container::getInstance()`), never from the container captured at boot.

## Where things live

- `src/PackageTemplateServiceProvider.php`: config merge and publishing, optional routes (`routes/package-template.php`) and migrations (`database/migrations/`), the `about` section.
- `tests/Feature`, `tests/Unit`, `tests/Arch`; `tests/TestCase.php`, `tests/Fixtures/` (models and migrations used only by tests).
<!-- ui:start -->
- `stubs/inertia-react/`: React components (and Inertia pages) published to apps, components under `components/vendor/laravel-package-template/`. Tests in `tests/js/` (Vitest, jsdom, Testing Library).
<!-- ui:end -->
- `.gitattributes` keeps tests, tooling and this file out of the Composer dist.
