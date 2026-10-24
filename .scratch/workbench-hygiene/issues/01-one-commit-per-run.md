# 01: Stop mixing two commits in one Spartan tree

**What to build:** A PGSR job runs the pinned stock commit through `run_from_commit.sh`, and takes its tooling (`slurm/`, `scripts/`) from a second pinned commit unpacked beside it, so each run records both commits instead of a tree whose HEAD says one thing and whose files say another.

**Answers:** none (workbench routine).

**Blocked by:** None (can start immediately).

**Status:** in-progress
**Working in:** project thread "PGSR one commit per run" (2026-10-24)

Amendment 4.3. Today the Spartan checkout is detached at the stock commit with `slurm/` and `scripts/` checked out from main on top (`AGENTS.md`, Paths). Also untrack the 8 `.DS_Store` files (amendment 2.4).

- [ ] One job run this way records both commits in its run directory
- [ ] Canonical checkout back to fetch-only and clean
- [ ] `.DS_Store` untracked and ignored
- [ ] `AGENTS.md` Paths row rewritten

## Progress 2026-10-24

- Built: `slurm/stock_pin.txt` (the stock pin, `de24f1a`), `slurm/lib/stock_beside.sh` (sourced after
  `run_from_commit.sh`: unpacks the pin beside the tooling, appends `stock_commit=` to `source.txt`,
  deletes both trees on exit), and `slurm/pgsr_two_commit_smoke.slurm` (one stock import, one tooling
  script, outputs only in the run directory).
- Choice: the **tooling** commit is the one `new_run.sh` and `run_from_commit.sh` take, so it names the
  run and its index row; it names the stock commit through its own `stock_pin.txt`. The other way
  round, every PGSR run would be called `..._de24f1a_...` and the index would never show which tooling ran.
- Tested on a mock canonical: both commits recorded, both trees deleted at exit, and a canonical
  that lacks the stock commit is refused before anything runs. On Spartan `origin/main` already
  contains `de24f1a` (our main descends from it), so no second remote is needed.
- `.DS_Store`: 8 untracked, ignored. `AGENTS.md` Paths row rewritten.
- Still to do on Spartan (`runs/` + `attic/` already exist): put the checkout back to clean, run the smoke job, read its `source.txt`.
