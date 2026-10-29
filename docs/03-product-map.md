# 03 — Product Map

The full, implementable plan now lives in **[`docs/plan/`](plan/README.md)**. That's the source of truth. This page is the one-screen summary.

**Product:** MallowPiece (mod id `mallowpiece`, display **MMnM+**), a Forge 1.20.1 addon for Mine Mine no Mi 0.11.6.

| Phase | Theme | Headline features | Fixes |
|---|---|---|---|
| 0 | Foundation | Gradle project, config, player data, debug commands, asset derivation | — |
| 1 | Fix the loop | Doriki and haki curves (~20 h to max), structure loot tiers, bosses drop boxes, box pity, marine rank-locked chests and theft | W1, W4, W5, W13 |
| 2 | Progression you do | Breakthrough trials every 2,000 doriki, Log Book, elite NPCs, findable and working trainers, Conqueror's Haki by quest | W2, W11, W12 |
| 3 | Fair, readable fights | No one-shots, telegraphed boss attacks, effect density setting, challenge tuning, NPC AI for boss fruits, conqueror's clash | W10, W11 |
| 4 | Strongholds | Structure generator, Revolutionary NPCs, Pirate Den, Revolutionary Hideout, pirate sniper | W3, W4 |
| 5 | Bosses in the world | 9 boss domains for the existing 18 bosses, wanted-poster maps, respawns, Supernova boss ships, Vice Admiral fleets | W6, W13 |
| 6 | Endgame | Renown ranks, daily contracts, Yonko fleets, awakenings, player bounties and crew territory (PvP, off by default), haki mastery | W9 |
| 7 | Fruits | Fruit pipeline, Toshi Toshi, restored Mane Mane, more fruits | W7 |

**Why this order:** the loop has to be fixed first (1–2), fights have to be fair before we add more of them (3), and the structure generator built in 4 is reused for boss lairs and ships in 5–6. Fruits come last because each one is the most expensive unit of content.
