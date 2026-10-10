# Task runner for strontiumcorp/laravel-package-template. Run `make` to list targets.
#
# Tests run in parallel. Coverage needs a coverage driver: with Xdebug the
# mode is passed explicitly to every parallel worker (PCOV needs nothing).

PHP        ?= php
PEST       := vendor/bin/pest
PROCESSES  ?= $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
PARALLEL   := --parallel --processes=$(PROCESSES)
XDEBUG_COV := -d xdebug.mode=coverage
MIN_COVERAGE ?= 85

.DEFAULT_GOAL := help
.PHONY: help install test test-filter coverage lint format analyse ci test-laravel test-matrix release release-pr release-tag configure clean
# ui:start
.PHONY: test-js typecheck-stubs remove-ui
# ui:end

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install the dependencies
	composer install --no-interaction
# ui:start
	npm ci --no-audit --no-fund
# ui:end

test: ## Run the test suite in parallel (PROCESSES=2 groups it like CI)
	$(PEST) $(PARALLEL)

test-filter: ## Run tests matching FILTER, e.g. make test-filter FILTER="ConfigMerge"
	@test -n "$(FILTER)" || (echo 'Usage: make test-filter FILTER="pattern"' && exit 1)
	$(PEST) --filter="$(FILTER)"

coverage: ## Run tests in parallel with coverage (fails under MIN_COVERAGE, default 85)
	$(PHP) $(XDEBUG_COV) $(PEST) $(PARALLEL) --passthru-php="'-d' 'xdebug.mode=coverage'" --coverage --min=$(MIN_COVERAGE)

lint: ## Check code style (Pint)
	vendor/bin/pint --test --parallel

format: ## Fix code style (Pint)
	vendor/bin/pint --parallel

analyse: ## Static analysis (PHPStan / Larastan, level 6)
	vendor/bin/phpstan analyse --memory-limit=1G --no-progress

CI_TARGETS := lint analyse test
# ui:start
CI_TARGETS += test-js
# ui:end
ci: $(CI_TARGETS) ## Everything CI runs (the CI_TARGETS above); run before every commit

test-laravel: ## Run the suite against another Laravel major in a scratch copy, e.g. make test-laravel VERSION=11 [LOWEST=1]
	@test -n "$(VERSION)" || (echo 'Usage: make test-laravel VERSION=11|12|13 [LOWEST=1]' && exit 1)
	scripts/test-laravel.sh $(VERSION) $(if $(LOWEST),lowest,stable)

test-matrix: ## Run the suite against Laravel 11, 12 and 13, newest and lowest dependencies (like CI)
	for v in 11 12 13; do scripts/test-laravel.sh $$v stable && scripts/test-laravel.sh $$v lowest || exit 1; done

# ui:start
test-js: ## Type-check the React stubs and run their Vitest tests (needs Node; run make install first)
	npm run typecheck
	npm test

typecheck-stubs: ## Type-check the React stubs against host apps, e.g. make typecheck-stubs APPS="../app-one ../app-two"
	@test -n "$(APPS)" || (echo 'Usage: make typecheck-stubs APPS="../app-one ../app-two"' && exit 1)
	scripts/typecheck-stubs.sh $(APPS)

remove-ui: ## Delete the optional frontend tooling (React stubs, Vitest, tsc, ui-suite.yml)
	python3 scripts/remove-ui.py

# ui:end
configure: ## Rename the template's placeholders, e.g. make configure ARGS="--package laravel-support-sso" (see scripts/configure.py --help)
	python3 scripts/configure.py $(ARGS)

release: ## Release from main: changelog commit and tag, pushed together, e.g. make release ARGS="--dry-run" (see scripts/release.sh --help)
	scripts/release.sh $(ARGS)

release-pr: ## For a protected main: open the release pull request instead (then make release-tag)
	scripts/release.sh --pr $(ARGS)

release-tag: ## Tag the merged release pull request and push the tag, e.g. make release-tag ARGS="--dry-run"
	scripts/release.sh --tag $(ARGS)

clean: ## Remove caches and build output
	rm -rf build .phpunit.cache coverage
