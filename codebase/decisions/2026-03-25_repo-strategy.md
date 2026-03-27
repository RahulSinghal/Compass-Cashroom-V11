# Decision: Repository Strategy for Phase 2

**Date**: 2026-03-25
**Decision**: Fork + feature branch

---

## Context

Phase 2 features need to be built on top of the existing Compass-Cashroom-V11 codebase without modifying the original repository.

## Decision

- Forked `RAKSHAKAR/Compass-Cashroom-V11` → `RahulSinghal/Compass-Cashroom-V11`
- Working branch: `phase2-features`
- Remotes: `origin` (fork) + `upstream` (original)

## Rationale

- Keeps original repo untouched
- Can sync upstream changes via `git fetch upstream`
- Can submit PRs back if needed
- Full commit history preserved

## Alternatives Considered

1. **Clone + feature branch only** — no fork visibility on GitHub
2. **Local copy without git** — no version control, risky
3. **Fork** (chosen) — clean separation with sync capability
