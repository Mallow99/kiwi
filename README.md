# kiwi

A private addon project for **Mine Mine no Mi** (Forge 1.20.1), for a friends-only server. The goal is to fix the gameplay loop (progression, variety, fruit acquisition, bosses) without patching the base mod.

## Docs
1. [`docs/01-mod-audit.md`](docs/01-mod-audit.md): what the mod is today (0.11.6), measured from the jar
2. [`docs/02-weak-points.md`](docs/02-weak-points.md): where the loop breaks, with evidence
3. [`docs/03-product-map.md`](docs/03-product-map.md): what we're building, in order (draft)

## Reading the base mod
```bash
tools/setup-reference.sh 1.20.1-0.11.6
```
This downloads the release from Modrinth and decompiles it into `.reference/` (git-ignored). The scripts in `tools/analysis/` reproduce the numbers in the audit.

## License note
Mine Mine no Mi is © its authors under a custom license. It allows decompiling and modifying for **private use**, and forbids redistributing the mod by itself, renaming it, or monetising it. This repo contains only our own code and docs; decompiled MMnM source is never committed. Anything shared beyond the friend group needs written permission from the MMnM owner.
