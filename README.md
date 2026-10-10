# laravel-package-template

A Laravel package for Laravel 11, 12 and 13 (PHP 8.2+).

Owned by [Strontium Corp](https://github.com/strontiumcorp). Maintained by [Mojahidul Islam](https://github.com/itsemon245).

<!-- template:start -->
## Using this template

This repository is the starting point for StrontiumCorp Laravel packages. It holds no features, only the tooling: Orchestra Testbench, Pest (parallel), PHPStan level 6 (Larastan), Pint, the CI layout, the release scripts and, optionally, Vitest and `tsc` for React stubs. `scripts/configure.py` removes this section.

1. Copy the template (GitHub "Use this template", or clone it and start a fresh history):

   ```bash
   git clone git@github.com:strontiumcorp/laravel-package-template.git laravel-support-sso
   ```

2. Rename everything in one go. Only `--package` is required; the rest is derived from it (shown with `--dry-run`):

   ```bash
   python3 scripts/configure.py --package laravel-support-sso --title "Support SSO" --description "Google sign-in for support staff."
   ```

   | Option | Default (for `laravel-support-sso`) | Replaces |
   |---|---|---|
   | `--vendor` | `strontiumcorp` | Composer vendor and GitHub owner |
   | `--config-key` | `support-sso` | `package-template`: config file and key, routes file, route prefix and names, publish tags |
   | `--class` | `SupportSso` | `PackageTemplate`: `SupportSsoServiceProvider`, … |
   | `--namespace` | `StrontiumCorp\SupportSso` | `StrontiumCorp\PackageTemplate` (tests: `…\Tests`) |
   | `--title` | `Support Sso` | `Package Template` (`php artisan about`, docs) |
   | `--no-ui` | off | also runs `make remove-ui` (below) |

   It edits file contents and renames files (`config/support-sso.php`, `src/SupportSsoServiceProvider.php`, …), env vars become `SUPPORT_SSO_*`. It is idempotent: a second run finds no placeholder and changes nothing. `make configure ARGS="…"` does the same.

3. No React stubs? Delete the frontend tooling in one step:

   ```bash
   make remove-ui
   ```

   It deletes `package.json`, `tsconfig.json`, `vitest.config.ts`, `stubs/inertia-react/`, `tests/js/`, `.github/workflows/ui-suite.yml` and `scripts/typecheck-stubs.sh`, and removes the `ui:start`/`ui:end` blocks from the Makefile, the workflows, `.gitattributes` and the docs.

4. Install and check:

   ```bash
   make install
   make ci
   ```

5. Commit (`chore: start from laravel-package-template`), create the GitHub repository, push, and make the first release with `make release` once CI is green.

Then replace the sample route (`routes/`), config keys and tests with the package's own, and rewrite this README and the Goal section of `CLAUDE.md`.

### What's inside

| Path | What |
|---|---|
| `src/PackageTemplateServiceProvider.php` | Deep-merges the config (`Support\ConfigMerge`), publishes it (`package-template-config`), loads `routes/package-template.php` and `database/migrations/` when they exist, adds an `about` section. |
| `config/package-template.php` | Sample config. Every key needs its default here. |
| `tests/TestCase.php` | Testbench base: SQLite with foreign keys on, `rebootWith()` for boot-time config, fixtures under `Tests\Fixtures`. |
| `Makefile` | `make` lists the targets (see CLAUDE.md). |
| `scripts/` | `release.sh` + `update-changelog.py` (releases), `test-laravel.sh` (matrix cells), `configure.py`, `remove-ui.py`, `typecheck-stubs.sh`. |
| `.github/workflows/` | `tests.yml` (every push), `full-matrix.yml` (tags, nightly, on demand; publishes the GitHub Release), the reusable `test-suite.yml` and `ui-suite.yml`. |

<!-- template:end -->
## Installation

The package isn't on Packagist, so add the repository to the app's `composer.json`, then install:

```json
"repositories": [
    { "type": "vcs", "url": "https://github.com/strontiumcorp/laravel-package-template" }
]
```

```bash
composer require strontiumcorp/laravel-package-template
php artisan vendor:publish --tag=package-template-config
```

The published `config/package-template.php` is deep-merged with the package defaults, so keys added in later versions apply without republishing.

`php artisan about` shows the package's state.

## Development

```bash
make install   # dependencies
make ci        # everything CI runs; run before every commit
make           # every target
```

See [CLAUDE.md](CLAUDE.md) for the testing rules and the release process, and [CHANGELOG.md](CHANGELOG.md) for releases.
