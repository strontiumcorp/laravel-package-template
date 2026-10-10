#!/usr/bin/env bash
# Type-check stubs/inertia-react against each host app's node_modules (React
# and @inertiajs/react versions vary between apps). Nothing is written into
# the apps.
#
# Files are laid out the way the package publishes them: pages under
# pages/package-template/, components under components/vendor/laravel-package-template/
# (imported as "@/components/vendor/laravel-package-template/<name>").
set -euo pipefail

[ "$#" -gt 0 ] || { echo "Usage: scripts/typecheck-stubs.sh <app-dir>..." >&2; exit 1; }
root="$(cd "$(dirname "$0")/.." && pwd)"
stubs="$root/stubs/inertia-react"
status=0

for app in "$@"; do
  nm="$(cd "$app" && pwd)/node_modules"
  [ -x "$nm/.bin/tsc" ] || { echo "$app: no node_modules/.bin/tsc (run npm/pnpm install there)"; status=1; continue; }

  work="$(mktemp -d)"
  mkdir -p "$work/pages/package-template" "$work/components/vendor/laravel-package-template"
  if [ -d "$stubs/pages" ]; then cp -R "$stubs/pages/." "$work/pages/package-template/"; fi
  if [ -d "$stubs/components" ]; then cp -R "$stubs/components/." "$work/components/vendor/laravel-package-template/"; fi
  cat > "$work/tsconfig.json" <<JSON
{ "compilerOptions": { "target": "ES2022", "module": "ESNext", "moduleResolution": "bundler", "jsx": "react-jsx",
  "strict": true, "noEmit": true, "skipLibCheck": true, "lib": ["DOM", "ES2022"],
  "paths": { "@/*": ["./*"], "*": ["$nm/@types/*", "$nm/*"] }, "typeRoots": ["$nm/@types"] }, "include": ["pages/**/*", "components/**/*"] }
JSON
  if (cd "$work" && "$nm/.bin/tsc" -p .); then echo "$app: OK"; else echo "$app: FAILED"; status=1; fi
  rm -rf "$work"
done

exit $status
