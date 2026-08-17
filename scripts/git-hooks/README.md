<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Git Hooks

`.git/hooks/` is never tracked by git itself — that's a real, permanent
git limitation, not something this project can work around. The hook
here has to be installed manually, once, per clone.

## Install

```
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## What it does

Runs `llmos scan-secrets` automatically before every commit, blocking
the commit if it finds anything. A real safety net for the case
someone forgets to run the scan manually — real gap, confirmed by
external audit 2026-08-17: nothing previously enforced this
automatically, `secret_scanner` only existed as a manual command.

## Bypass, if genuinely needed

```
git commit --no-verify
```

Not recommended — only for a confirmed false positive.
