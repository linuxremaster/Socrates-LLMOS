<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Housekeeping & Documentation Audit Checklist

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

Real, executable checks -- not an aspirational list. Every item here
was written because it caught an actual, confirmed problem in this
project at least once. Run these periodically, or whenever picking up
the project after time away.

**Scope rule, before running any of this:** a check that finds a
factual documentation gap (a missing command, a stale count, a wrong
version string) can be fixed directly, verified, and logged -- same as
every fix in this checklist's own history. A check that touches kernel
or policy *content* needs C1's full diff discipline, not a quick edit.
Findings you're not confident are safe to fix directly go through
`propose-observation`, not straight into the real files.

## 1. Command/documentation parity

Every real command should be documented; every documented command
should be real.

```
llmos --list-commands 2>&1 | grep -oE "^\s*[a-z-]+" | sed 's/^\s*//' | sort > /tmp/real_commands.txt
grep -oE "\`[a-z-]+\`" llmos_toolkit/README.md | tr -d '\`' | sort -u > /tmp/documented_commands.txt
comm -23 /tmp/real_commands.txt /tmp/documented_commands.txt
```
Non-empty output = a real command with no documentation. **Caught 9
undocumented commands this way, 2026-08-20**, including an entire
plugin (`behavior_log`) that had gone completely undocumented.

## 2. Plugin count/list currency

```
ls llmos_toolkit/plugins/ | grep -v __pycache__ | sort
```
Compare against any doc claiming a specific plugin count or listing
plugins by name (`docs/README.md`, `docs/PROJECT_HANDOFF_SUMMARY.md`,
`llmos_toolkit/README.md`'s architecture tree). **Found stale twice
already** -- once dated 2026-08-14 with a hardcoded "13 plugins" claim
that had drifted to 18.

## 3. Version string consistency

```
grep "^version" pyproject.toml
head -1 docs/CHANGELOG.md's most recent entry
grep -rn "v0\.[0-9]\+\.[0-9]\+-alpha" README.md docs/*.md
```
Any hardcoded version number in prose (not in `docs/CHANGELOG.md`
itself) is a real risk -- **`README.md` said "v0.6.0-alpha" through
three subsequent releases before being caught.** The actual fix that
held: remove the hardcoded number from prose entirely, point to git
tags / `docs/CHANGELOG.md` instead. If a hardcoded version string
shows up anywhere else, apply the same fix, not just an update.

## 4. Embedded/duplicated content staleness

Any file that embeds a full copy of another (e.g.
`docs/ADOPTION_CHECK_PROMPT.md` embedding the kernel) needs to be
regenerated whenever the source changes -- check with a direct string
containment test, not a fragile line-offset diff:
```
python3 -c "
content = open('docs/ADOPTION_CHECK_PROMPT.md', encoding='utf-8').read()
kernel = open('kernel/UNIFIED_BEHAVIORAL_OUTPUT_PROTOCOL_v2.md', encoding='utf-8').read()
print('Embedded kernel matches current source exactly:', kernel in content)
"
```
**Went stale twice already** (still v2.3 after the kernel moved to
v2.4, missing A14 entirely).

## 5. Ledger event-naming consistency

```
python3 -c "
import json
from collections import Counter
entries = [json.loads(l) for l in open('state/growth_ledger.jsonl') if l.strip()]
print(Counter(e.get('event','MISSING') for e in entries).most_common())
"
```
Look for near-duplicate event names describing the same action (e.g.
`file_added` vs `file_created`, found and documented 2026-08-20).
Don't rename historical entries -- document the convention going
forward in `docs/PROJECT_HANDOFF_SUMMARY.md` section 3.5.

## 6. Test suite and secret scan health

```
llmos self-test
llmos scan-secrets
llmos audit-all
```
All three should pass clean before considering any housekeeping pass
complete. A "housekeeping" change that breaks the real suite isn't
housekeeping.

## 7. Stale explicit dates

```
grep -rn "as of 202[0-9]-[0-9][0-9]-[0-9][0-9]" docs/ llmos_toolkit/README.md
```
Any date more than a few real sessions old is worth checking against
what actually changed since. A date isn't automatically a bug -- a
policy/decision timestamp ("on hold as of X") can still be accurate;
an unqualified count or list ("13 plugins as of X") is the kind that
actually goes stale. **Caught one real instance of the latter this
way, 2026-08-20** (a "13 plugins" claim that had drifted to 18).

## How to propose findings

For anything beyond a direct, verified factual fix: stage it, don't
silently apply it.
```
llmos propose-observation "<your-instance-id>" "<subject>" "housekeeping" low "<what you found>"
```
A human reviews with `llmos review-pending` and decides
`approve-pending`/`reject-pending` -- same quarantine boundary as
everything else this project logs from an instance's own findings.
