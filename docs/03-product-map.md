# 03 — Product Map (draft)

**Goal:** make the Mine Mine no Mi loop worth playing past the first fruit. That means more places to go, progression you *do* rather than grind, fruits you can work toward, and bosses in the world.

**Form:** a separate Forge 1.20.1 addon that depends on Mine Mine no Mi 0.11.x. We don't patch their jar, so their updates don't wipe our work and our friends install the official mod plus ours.

**Rules for every feature:** each one gets its own config toggle; each phase ends with a playtest on the friend server before the next one starts.

Weak point references (W1–W8) point to `02-weak-points.md`.

---

## Phase 0 — Foundation
| # | Item | Notes |
|---|---|---|
| 0.1 | Addon project scaffold | Forge 1.20.1 MDK (47.x), Java 17, MMnM dependency via Modrinth maven, the mixin properties from the official addon setup doc |
| 0.2 | Reference workflow | `tools/setup-reference.sh` downloads and decompiles the current MMnM jar into a git-ignored folder, so we always read the real code |
| 0.3 | Config + test world | one `kiwi-server.toml`; a test world seed with known structure locations |

## Phase 1 — Fix the loop (cheap, high impact)
| # | Item | Fixes | Type | Size |
|---|---|---|---|---|
| 1.1 | **Doriki curve rework.** Replace the 100× cliff with a smooth falloff, and set a target time-to-max | W1 | Code (`DorikiEvent.Pre`) | S |
| 1.2 | **Haki curve rework.** Softer approach to the cap; less penalty for training on weak mobs | W1 | Code (`HakiExpEvent`) | S |
| 1.3 | **Bosses drop boxes.** Standard bosses drop iron, Hard bosses have a golden chance | W5, W6 | Data (loot tables) | XS |
| 1.4 | **Box pity + empty-box fix.** Every N boxes without a tier-up guarantees one; boxes never open to nothing | W5 | Code | S |
| 1.5 | **Faction fairness, part 1.** Marines can't freely loot their own bases' captain chests (needs rank or requisition) | W4 | Code | S |

## Phase 2 — Progression you *do*
| # | Item | Fixes | Type | Size |
|---|---|---|---|---|
| 2.1 | **Breakthrough gates.** At set doriki thresholds you must clear a trial (raid a stronghold / defeat a boss / learn N style skills) before gaining more | W2 | Code (reuse MMnM quest objectives) | M |
| 2.2 | **Late-game open-world enemies.** Elite NPCs in the 6,500–10,000 band (commodores, notorious crews, rev commanders) | W1 | Code + data | M |
| 2.3 | **Death tax preset.** A friend-server default for how much is kept on death | W1 | Config | XS |

## Phase 3 — Strongholds (the variety patch)
| # | Item | Fixes | Type | Size |
|---|---|---|---|---|
| 3.1 | **Revolutionary NPC set.** Grunt, brute, sniper, commander, built on MMnM's existing NPC classes | W3, W4 | Code + textures | M |
| 3.2 | **Pirate Den.** Land stronghold on par with the marine large base, with box chests | W3, W4 | Structure | L |
| 3.3 | **Revolutionary Hideout.** Underground, uses the same approach as the bandit caves, with box chests | W3, W4 | Structure | L |
| 3.4 | Pirate sniper unit | W3 | Code | XS |
| 3.5 | **Faction fairness, part 2.** Each faction has an enemy stronghold worth raiding | W4 | Data | S |

**Structure pipeline:** I generate a first-pass template in code (an NBT writer, using the existing marine base for scale, layout and palette). We also look at schematics online, checking each one's license before using it. Then a real builder polishes it in-game and we re-save it with structure blocks.

## Phase 4 — Bosses in the world
| # | Item | Fixes | Type | Size |
|---|---|---|---|---|
| 4.1 | **Wanted posters → treasure maps.** A poster points to a boss's overworld arena | W6 | Code | M |
| 4.2 | **Overworld boss arenas.** The existing 18 bosses live in themed structures (Baratie, Arlong Park, Syrup Village…) | W6, W3 | Structure + code | L |
| 4.3 | **Respawn timer.** A boss returns about an hour after defeat; loot includes boxes (ties into 1.3) | W6, W5 | Code | S |
| 4.4 | *(optional)* The five bosses MMnM already reserved but never built | W6 | Code + models | L each |

## Phase 5 — Fruits
| # | Item | Fixes | Type | Size |
|---|---|---|---|---|
| 5.1 | **Awakenings.** Test the existing addons (Awaken Awaken no Mi, Awaken Path) against building our own; tie awakening to a Phase 2 gate | W7 | Eval → code | M–L |
| 5.2 | **New fruits, one at a time.** Pick the list with your friends; restoring Mane Mane is a candidate | W7 | Code + art | L each |
| 5.3 | **PvP balance pass** for a friend server | W8 | Config + code | M |

---

## Why this order
1. **Phase 1 first** because it's cheap, fixes the worst part of the loop right away, and forces us to learn the doriki, haki, loot and faction internals that everything later builds on.
2. **Phase 2 next** because gates are only worth adding once the curve under them is sane, and they give Phase 3 and 4 content a reason to be played.
3. **Phase 3 before 4** because the structure pipeline (generate → polish → jigsaw) gets built once for strongholds and then reused for boss arenas.
4. **Fruits last.** They're the most expensive content per unit, and a new fruit doesn't fix a broken loop. They can run as a parallel "fun track" whenever we want a break from systems work.

## Decisions needed from you
1. **Name / mod id** for the addon.
2. **Time-to-max target** for doriki and haki (hours of active play), which tunes 1.1 and 1.2.
3. **Gate thresholds** and whether gates are on by default.
4. **Marine fairness approach** for 1.5 (rank-locked chests, requisition cost, or something else).
5. **Who builds and who playtests**: which friends, and on what server.
