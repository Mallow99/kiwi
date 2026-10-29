# kiwi → MallowPiece (MMnM+)

A private addon for **Mine Mine no Mi** (Forge 1.20.1), for a friends-only server. It fixes the gameplay loop (progression, variety, fruit acquisition, fair bosses) and adds an endgame, without patching the base mod.

## Start here
- **AI agents:** read [`AGENTS.md`](AGENTS.md), then [`docs/plan/README.md`](docs/plan/README.md).
- **Humans:** [`docs/03-product-map.md`](docs/03-product-map.md) is the one-screen summary.

## Docs
1. [`docs/01-mod-audit.md`](docs/01-mod-audit.md): what MMnM is today (0.11.6), measured from the jar
2. [`docs/02-weak-points.md`](docs/02-weak-points.md): where the loop breaks, with evidence
3. [`docs/03-product-map.md`](docs/03-product-map.md): the plan at a glance
4. [`docs/plan/`](docs/plan/README.md): the full implementation plan: phases 0–7, task specs, acceptance tests, and [verified MMnM API notes](docs/plan/mmnm-api-notes.md)

## Tools
```bash
tools/setup-reference.sh 1.20.1-0.11.6   # download + decompile MMnM into .reference/ (git-ignored)
python3 tools/sim/progression.py         # doriki/haki curve simulator behind the Phase 1 numbers
```
`tools/analysis/` holds the scripts that produced the audit numbers.

## License note
Mine Mine no Mi is © its authors under a custom license. It allows decompiling and modifying for **private use**, and forbids redistributing the mod by itself, renaming it, or monetising it. This repo contains only our own code, data and docs; MMnM source and assets are never committed (derived assets are generated at build time). Anything shared beyond the friend group needs written permission from the MMnM owner.
