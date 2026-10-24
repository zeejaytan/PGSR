# 01: Stop mixing two commits in one Spartan tree

**What to build:** A PGSR job runs the pinned stock commit through `run_from_commit.sh`, and takes its tooling (`slurm/`, `scripts/`) from a second pinned commit unpacked beside it, so each run records both commits instead of a tree whose HEAD says one thing and whose files say another.

**Answers:** none (workbench routine).

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

Amendment 4.3. Today the Spartan checkout is detached at the stock commit with `slurm/` and `scripts/` checked out from main on top (`AGENTS.md`, Paths). Also untrack the 8 `.DS_Store` files (amendment 2.4).

- [ ] One job run this way records both commits in its run directory
- [ ] Canonical checkout back to fetch-only and clean
- [ ] `.DS_Store` untracked and ignored
- [ ] `AGENTS.md` Paths row rewritten
