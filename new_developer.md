CI /
===========================

Purpose
-------
This file documents how new developers should set up and do this project locally. It includes installation steps, how to add the Husky hook, commands to test commit messages without creating commits, and a small CI snippet you can reuse.

Prerequisites
-------------
- Node.js (v14+ recommended) and `npm`/`npx` installed.
- Git available in PATH.

Quick local install (dev dependencies)
------------------------------------
From the repository root run:

```bash
npm install 
```

------------------------------------------
Run the following from repo root:

```bash

git commit -m "chore(husky): add commitlint hook" || true
```

Make sure the hook is executable and tracked by Git (Windows / PowerShell safe):

```powershell
# From repo root (PowerShell)
git update-index --add --chmod=+x .husky/commit-msg
```

Testing commitlint locally (no commit required)
---------------------------------------------

1) Test a single commit message file (Bash):

```bash
printf '%s\n\n%s\n' "feat: add foo" "more details" > /tmp/commitmsg.txt
npx --no -- commitlint --edit /tmp/commitmsg.txt
```

2) PowerShell equivalent:

```powershell
$path = Join-Path $env:TEMP 'commitmsg.txt'
"feat: add foo`n`nMore details" | Out-File -Encoding utf8 $path
npx --no -- commitlint --edit $path
```

3) Run against a commit range (CI style):

```bash
# Check commit messages from <from>.. <to>
npx --no -- commitlint --from origin/main --to HEAD
```

CI example (GitHub Actions)
---------------------------
This example runs commitlint for the pushed commits (useful for PRs):

```yaml
name: commitlint
on: [push, pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npx --no -- commitlint --from ${{ github.event.before }} --to ${{ github.sha }}

```

Troubleshooting
---------------
- SyntaxError / invalid token when Node loads `commitlint.config.js`:
  - Ensure the config file is CommonJS (`module.exports = ...`) or use `.cjs` extension.
  - Ensure the file is saved as UTF-8 without BOM.
- Hook shows "cannot execute binary file" or exit code 126:
  - Ensure the hook begins with a shebang and the `_` helper is sourced: first lines in `.husky/commit-msg` should be:

    #!/usr/bin/env sh
    . "$(dirname -- "$0")/_/husky.sh"

  - Make the hook executable: `chmod +x .husky/commit-msg` (or `git update-index --add --chmod=+x .husky/commit-msg` on Windows)
  - Ensure the file has LF line endings.
- File locked when attempting to overwrite `commitlint.config.js` (Windows):
  - Close editors that may hold the file.
  - As a workaround create `commitlint.config.cjs` (preferred) so you don't need to replace the locked file.

How to use this doc
--------------------
- New developer: follow the "Quick local install" + "Add the Husky commit-msg hook" steps.
- To test messages without committing, use the `--edit` examples above.
- CI maintainers: copy the GitHub Actions snippet into your `.github/workflows/` and adapt the `--from/--to` range to your workflow.

Contact / Notes
---------------
- If commitlint behavior differs on Windows, ensure `npx` is running a Node version compatible with installed packages and that `commitlint.config.cjs` is readable by Node.
- If you want, this file can be converted to a README (`ci/README.md`) or a runnable script. Request an update and I will create it.

Commit message types (conventional commits)
-----------------------------------------
We follow Conventional Commits (used by `commitlint`) to keep history predictable and machine-readable. Common types:

- **feat:** a new feature
- **fix:** a bug fix
- **docs:** documentation only changes
- **style:** formatting, missing semi-colons, no production code change
- **refactor:** code change that neither fixes a bug nor adds a feature
- **perf:** code change that improves performance
- **test:** adding or changing tests
- **build:** changes that affect the build system or external dependencies
- **ci:** CI configuration and scripts
- **chore:** other changes that don't modify src or tests (see below)

Examples:

- `feat(auth): add JWT token support`
- `fix(api): return 404 for missing user`
- `chore: refresh lockfile`

