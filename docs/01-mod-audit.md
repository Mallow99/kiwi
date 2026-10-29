# 01 — Mod Audit: Mine Mine no Mi 1.20.1-0.11.6

What the mod actually is today, measured from the released jar rather than from memory.

- **Version audited:** `mine-mine-no-mi-1.20.1-0.11.6.jar` (Modrinth, released 2026-10-09), Forge 1.20.1.
- **Baseline for "what changed":** `0.9.5` (1.16.5, released 2023-08-04), roughly three years earlier.
- **Method:** jar decompiled locally with Vineflower; data files (loot tables, worldgen, structures, lang) read directly. Scripts in `tools/analysis/`. Decompiled source is **not** committed (license: private use only).
- Numbers marked *(sim)* are computed from the formulas in the code, not observed in-game.

---

## 1. Size of the thing

| | Count |
|---|---|
| Java classes | 3,271 (≈250k decompiled lines) |
| Abilities (lang entries) | 577 |
| Items | 394 |
| Config options | 131 |
| Structure templates (`.nbt`) | 100 |

This is a big, actively maintained codebase. It isn't abandoned. The work over the last three years went into systems, not content.

## 2. Devil fruits

**71 playable fruits**, plus Mochi Mochi, which only registers on April 1st (`ModFruits.registerMochi` → `WyHelper.isAprilFirst()`).

| Tier (box) | Type | Fruits |
|---|---|---|
| 1 — Wooden | Paramecia (20) | Awa, Baku, Bane, Bari, Chiyu, Deka, Goe, Hiso, Horu, Kachi, Kilo, Kobu, Kuku, Mini, Nagi, Noro, Ori, Sabi, Sube, Suke |
| 1 — Wooden | Zoan (4) | Hito, Kame, Mogu, Ushi (Giraffe) |
| 2 — Iron | Paramecia (19) | Bara, Beta, Bomu, Doa, Doru, Gomu, Hana, Horo, Kage, Karu, Kira, Mero, Netsu, Ope, Oto, Pero, Sui, Supa, Yomi |
| 2 — Iron | Zoan (5) | Neko (Leopard), Sai, Sara (Axolotl), Ushi (Bison), Zou |
| 2 — Iron | Ancient Zoan (4) | Ryu (Allosaurus / Brachiosaurus / Pteranodon), Zou (Mammoth) |
| 3 — Golden | Logia (10) | Gasu, Goro, Hie, Magu, Mera, Moku, Pika, Suna, Yami, Yuki |
| 3 — Golden | Mythical Zoan (2) | Hito (Daibutsu), Tori (Phoenix) |
| 3 — Golden | Paramecia (7) | Doku, Gura, Ito, Jiki, Nikyu, Wara, Zushi |

**Change since Aug 2023:** 73 → 72 registered fruits. Deka Deka was added. **Mane Mane and Mega Mega were removed.** About 120 abilities were added overall, but those are reworks of existing fruits and styles, not new fruits.

**Awakenings:** the framework exists (`DevilFruitBase.hasAwakenedFruit`, config `Enable Awakenings`), but it is **off by default**, only reachable through an admin command (`/ability awaken`), and **only Gomu Gomu has awakened abilities** (Gear 5, Gigant, Dawn Whip).

## 3. Getting a fruit (boxes)

Boxes need a **key**, which drops from marine/pirate captains and bandit leaders or turns up in a few vanilla chests.

**How a box rolls:** the fruit is uniform within its tier. A box has a 5% chance to roll the next tier up (raised by Luck). Every fruit in a tier is equally likely: 1/24 wooden, 1/28 iron, 1/19 golden.

| Source | Wooden | Iron | Golden | Chests needed for **one specific** golden fruit *(sim)* |
|---|---|---|---|---|
| Marine battleship – treasure | 25% | 15% | 10% | ~185 |
| Marine large base – captain | 8% | 8% | 4% | ~452 |
| Woodland mansion (vanilla) | 19.2% | 9.6% | 3.8% | ~462 |
| Pirate large ship – treasure | 15% | 6.3% | 3.8% | ~488 |
| Caravan (hard) | 50% | 35% | 15% | — |
| Marine small base – captain | 8.3% | 4.2% | — | — |
| Bandit fort – secret stash | 10.5% | 5.8% | — | — |
| Pirate medium ship – captain | 6% | 2.5% | 1.5% | — |
| **Any boss (challenge rewards)** | — | — | — | **Bosses never drop boxes** |

⚠️ **Possible bug (needs in-game check):** each box's fruit pool only fires 95% of the time, and the golden box has no fallback pool. If nothing rolls, `AkumaNoMiBoxItem` hands back an empty stack after the box and key are already consumed. That would make roughly **1 in 20 boxes open to nothing**, and Luck makes it *worse* for golden boxes (`luckBonus: -0.05`).

## 4. Progression math

### Doriki
- Cap: **10,000** (config `Doriki Limit`).
- Per kill (`StatsGainHandler.giveStats`): you get `target doriki / 100`, **until you out-doriki the target. Then it drops to `target / 10000`, a 100× cliff.**
- Vanilla mobs get a "threat" doriki from HP and attack. Endermen land around 1,450 (Normal) to 2,100 (Hard).
- Mod NPC doriki: Grunt 500–2,000, Sniper 3,000–4,500, Brute 3,500–5,000, Captain 4,000–6,000, Pacifista 2,000–4,000. Hard adds +500, New World adds +250 to the minimum.
- **So the strongest repeatable open-world target is about 6,500 doriki.** Everything from 6,500 to 10,000 comes from:
  - Challenges. These are a fixed reward pool: 1,000 doriki split across *all* standard challenges and 4,000 across *all* hard ones, plus up to +100% bonus on hard. Repeats are divided by `1.5 × completions`.
  - Notorious targets, which pay at least 100 doriki per kill.
  - Ancient manuals and trials.
- *(sim)* Max doriki from an enderman farm: **37,500 kills** on Hard, 52,000 on Normal. From captains: about 5,300 kills past 6,500.
- Death keeps **77%** of doriki, bounty, belly and haki by default.

### Haki
- Cap: **100** (config `Haki Exp Limit`).
- Busoshoku gain per hit scales with `(target HP + attack) × (100 − current haki)`, and is **divided by 5 more** when the target's HP + attack is below your current haki. It gets slower the closer you get to 100, so the last stretch is the worst.
- *(sim)* Hits needed to go from 90 to 99 haki: zombie ~7,000; enderman ~4,400; marine captain ~440; warden ~86.
- Kenbunshoku passive: +0.025 every 30 seconds with Future Sight active, once you're past 60.

## 5. Structures (world generation)

| Group | Structures | Notes |
|---|---|---|
| Marine | Small base, **Large base** (multi-floor jigsaw + prison), Watch tower, Battleship | The large base is the only real multi-room "dungeon" |
| Pirate | Small / Medium / Large ship | **Water only. No pirate structure on land.** |
| Bandit | Camp, House, Fort, Arena (+ underground **cave** variants under House/Arena) | The caves are the only underground faction structure |
| Unaligned | 5 trainer buildings, Tavern, Ghost ship | |
| Sky | Sky island (single / town) | |
| **Revolutionary** | **None** | |

**Change since Aug 2023:** the lineup is essentially the same. It was rebuilt as modular jigsaw pieces, and Tavern, bandit Fort/Arena and caravans were added. The 2023 jar already had marine/bandit bases, the three pirate ships, the battleship, sky islands, the trainer buildings and the ghost ship.

## 6. NPCs, factions, bosses

- **Player factions:** Pirate, Marine, Bounty Hunter, Revolutionary Army, plus Civilian, Bandit and World Government as NPC alignments.
- **Faction NPCs:** Marine (grunt, brute, sniper, captain, vice admiral, trader), Pirate (grunt, brute, captain, notorious captain, trader, *no sniper*), Bandit (grunt, brute, sniper, leader).
- **Revolutionary Army has zero NPCs and zero structures.** It's a menu option and nothing else.
- **Marine-aligned NPCs and marine-aligned players cannot hurt each other** (`ModFactions.MARINE_HURT_CHECK`). A marine player can walk through every marine base, which has the best box odds on land, without a fight.
- **Bosses (18):** Alvida, Morgan, Buggy, Cabaji, Higuma, Kuro, Jango, Sham & Buchi, Gin, Pearl, Don Krieg, Arlong, Kuroobi, Chew, Mr. 5 & Miss Valentine, Mr. 3, Mr. 1, Mr. 0. That covers East Blue through Alabasta, and each has Standard and Hard versions (36 challenges).
  - **All of them exist only as challenges in a separate arena dimension.** No boss spawns in the overworld.
  - Already reserved in the challenge order but not built: Mohji & Richie, Hatchan, Mr. 2, Mr. 4 & Miss Merry Christmas, Miss Doublefinger.
- **World events:** Notorious targets, Caravans, Celestial Dragon visits, Ambushes, roaming Traders and Trainers, and New World mode (stronger mobs after the Ender Dragon dies).
- **Trials (quests):** 20 total, 4 categories × 5, all tied to fighting-style progression. A `ReachDorikiObjective` already exists in the quest system.

## 7. The developer's own roadmap (docs, last updated 2024-12-22)

Open-world late-game bosses; more things to explore; marine/revolutionary faction progression; quests that aren't fighting-style trials; new fruits, races and styles; more API exposure for addons. Most of this matches the weak points below, and most of it is still open.

## 8. What an addon can hook (for us)

- `DorikiEvent.Pre` / `HakiExpEvent` are cancellable, and both expose `setDoriki` / amount. **We can reshape the whole gain curve without touching their jar.**
- Loot tables (boxes, chests, boss rewards) are plain datapack JSON and can be overridden.
- Structures are vanilla jigsaw structures, so new ones go in as data plus `.nbt` templates.
- There is an official addon setup doc (Modrinth maven `maven.modrinth:mine-mine-no-mi:1.20.1-0.11.x`) and an Ability API doc.
