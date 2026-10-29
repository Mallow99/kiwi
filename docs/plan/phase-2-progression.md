# Phase 2 — Progression you do

**Milestone (owner playtest):** at 2,000 doriki your gain stops and the Log Book shows a breakthrough trial with two ways through it. Trainers can be found on purpose and their buttons work. Conqueror's Haki comes from a quest, not your UUID.

Fixes W2 (number-goes-up), part of W1 (late enemies), and the owner's trainer and conqueror's feedback.

---

## 2.1 Breakthrough gates — engine (M)
**Goal:** every 2,000 doriki, progression asks you to *do* something.

**Design**
- Gates at **2,000 / 4,000 / 6,000 / 8,000 / 10,000** (on by default).
- At an unbroken gate `G`, doriki can't go above `G`. Gains past `G` are banked as **Momentum** (max 500). When you clear the trial, Momentum is added at once, so playing while gated is never wasted.
- `StatChangeSource.COMMAND` and `STORE` bypass gates, so testing still works.
- The 10,000 gate is the **Endgame** breakthrough. Clearing it unlocks Renown (6.1). Until Phase 6 exists it grants the title `New World Pirate/Marine/Revolutionary` and a message.
- Each gate has a **trial** with one or more **paths** (OR). Each path is a list of **objectives** (AND). It also has optional **requirements** that apply to every path (e.g. a minimum haki). The first path to complete clears the gate.
- Trials are data: `data/mallowpiece/breakthroughs/<gate>.json`, so the agent or owner can rebalance without code.

**Objective types** (engine supports these; content in 2.3):

| type | params | counts when |
|---|---|---|
| `kill_npc` | `entity` (id or `#tag`), `min_doriki`, `faction`, `count`, `in_structure` (structure tag, optional) | player kills a matching entity |
| `clear_structure` | `structure` (tag), `count` | player kills the structure's leader NPC (captain/leader/elite/boss) **inside** that structure **and** opens a tiered treasure chest (1.3) in it within 10 min. Each structure start only counts once per player |
| `win_challenge` | `difficulty` (standard/hard/any), `count` | detected via `DorikiEvent.Pre` with source `CHALLENGE` (one per completion) |
| `defeat_boss` | `boss` (id or `#mallowpiece:overworld_bosses`), `count` | 5.x bosses |
| `defeat_notorious` | `count` | kill of an `INotoriousTarget` |
| `haki` | `type` (busoshoku/kenbunshoku/any), `min` | checked live |
| `style_trials` | `count` | completed MMnM fighting-style trials (**Spike:** find the completed-quest list in MMnM's quest capability, `data/entity/quests/*`) |
| `outmatched_win` | `ratio` (e.g. 1.5), `count` | you kill an NPC whose doriki ≥ ratio × yours |

**Implementation**
- `MallowPlayerData`: `brokenGates` (sorted int set), `momentum`, `objectiveProgress` (map objectiveId → int), `clearedStructures` (set of structure start `BlockPos` longs per structure id).
- In our `DorikiEvent.Pre` handler (runs **after** the curve from 1.1; give it lower priority): find the next unbroken gate `G`; if `P + amount > G`, set the amount to `G - P` and add the rest (or `amount` if already at `G`) to Momentum up to its max.
- Objective listeners: `LivingDeathEvent`, the same kill context as 1.1, structure checks via `structureManager().getStructureWithPieceAt(pos, tag)`, chest opens (`PlayerContainerEvent.Open` + block entity loot-table check), `DorikiEvent.Pre` (CHALLENGE).
- On progress, send a toast (`SystemToast` or our own) like `Set Sail: Defeat enemies 7/10`. On completion: title text `BREAKTHROUGH`, a sound (`ui.toast.challenge_complete`), Momentum applied, chat line.
- Debug: `/mallowpiece debug gate <gate> complete|reset`, `/mallowpiece debug objective <id> <n>`.

**Config `[progression.gates]`:** `enabled=true`, `gates=[2000,4000,6000,8000,10000]`, `momentumMax=500`.

**Acceptance**
1. `/doriki 1990`, kill grunts: doriki stops at 2,000 and Momentum rises; `/mallowpiece debug info` shows both.
2. `/mallowpiece debug gate 2000 complete`: Momentum is added and doriki rises past 2,000.
3. Clear a real T1 structure: the `clear_structure` objective ticks once; clearing the same structure again doesn't count.

## 2.2 Log Book (M)
**Goal:** one place where the player sees what to do next.

**Design**
- Item `mallowpiece:log_book`. Given once on first join and craftable (book + compass). Command `/mallowpiece logbook` opens it too.
- Screen with tabs (vanilla-style book look, our own texture):
  1. **Breakthrough:** current gate, each path with its objectives and progress bars, requirements, banked Momentum.
  2. **Trainers** (2.5): trainers you've met, with style, coordinates, distance and dimension, and "Mark on map" (writes a vanilla map decoration via a held map, or sends coordinates to chat).
  3. **The King's Path** (2.6): hidden until stage 1 unlocks.
  4. Later: **Renown** (6.1), **Contracts** (6.2).
- Data from `MallowPlayerData`, synced when the book opens and when progress changes.

**Acceptance:** open the book at 0 doriki: the 2k trial's paths show with 0/N bars. Kill an objective target: the bar updates without reopening.

## 2.3 Breakthrough trial content (M)
Faction-aware where it matters: "enemy structure" means a structure of a faction your NPCs are hostile to. Paths are OR; requirements are AND.

| Gate | Name | Path A | Path B | Requirements |
|---|---|---|---|---|
| 2,000 | **Set Sail** | Clear 1 T1 structure + defeat 10 enemies ≥1,000 doriki | Win 1 standard challenge (Alvida, Morgan or Higuma) | — |
| 4,000 | **First Bounty** | Clear 1 T2 structure + defeat 1 captain | Win 2 standard challenges | — |
| 6,000 | **Grand Line Entry** | Clear 1 T3 enemy structure | Defeat 1 notorious target + 1 outmatched win (≥1.5×) | Any haki ≥ 30 |
| 8,000 | **Paradise Survivor** | Defeat 3 elites (2.4) + 1 overworld boss (5.2) | Win 3 hard challenges | Any haki ≥ 45; 5 style trials done |
| 10,000 | **New World** | Defeat a Supernova (5.5) | Win 5 hard challenges + defeat 3 notorious targets | Busoshoku ≥ 60 or Kenbunshoku ≥ 60 |

Until a referenced task ships (elites, overworld bosses, Supernovas), the engine treats objectives whose content doesn't exist as hidden, and only the other path is shown. Mark them `"requires_feature": "elites"` in JSON.

Doriki rewards on clear: Momentum only (no extra), to keep the sim numbers valid.

**Acceptance:** walk each gate once with debug doriki and real objectives (TESTLOG entry per gate).

## 2.4 Elite NPCs (M)
**Goal:** something worth fighting between 6,500 and 10,000 doriki (the curve's `full` preset depends on this).

**Design**

| Elite | Faction | Doriki (Hard) | HP | ATK | Armor | Notes |
|---|---|---|---|---|---|---|
| Marine Commodore | Marine | 7,000–9,000 | 200 | 8 | 14 | Swordsman or Brawler; Busoshoku haki |
| Notorious Officer | Pirate | 7,000–9,000 | 200 | 8 | 12 | Random style; 30% NPC-capable fruit |
| Revolutionary Commander | Revolutionary | 7,000–9,000 | 190 | 8 | 12 | Added with 4.2 |

- Use MMnM's fighting-style setup the way `CaptainEntity`'s `STYLES` does (read it in the reference).
- Fruit users: pick from fruits that have NPC goals (see API notes). Phase 3.5 widens the list.
- **Spawning:** (a) when a captain spawns from a `custom_spawner` inside a T3 structure (`EntityJoinLevelEvent` + structure check), there's a 35% chance an elite spawns next to it; (b) world patrols: every 20 min, 20% chance per player with ≥6,000 doriki, 2 elites + 3 grunts of a hostile faction spawn 40–60 blocks away (reuse MMnM's ambush-style placement); (c) our own structures (Phase 4) place them directly.
- Loot: key 50%, iron box 10%, golden box 2%, ancient manual 10%.

**Implementation:** own `EntityType`s with factories that build MMnM's `CaptainEntity` (or a subclass) and call `setFactionInit(...)`. Re-set doriki and attributes after `super.finalizeSpawn`. Attributes in `EntityAttributeCreationEvent`. Renderer `OPHumanoidRenderer.Factory`. Textures: derived from MMnM captain skins with a gold trim recipe (0.4).

**Acceptance:** `/summon mallowpiece:marine_commodore`, check its doriki (MMnM's `/fg` debug, or our debug command shows the targeted entity's stats); at 7,000 player doriki a kill pays ~38–50 with the `phase1` curve preset, ~13–16 with `full`.

## 2.5 Trainers you can find and use (M)
**Problem (owner):** you wait for a trainer to spawn, and half the time the buttons don't work.

**What the code shows:** random trainers spawn near players at 15% every 2 minutes. Trainer *buildings* (swordsman dojo, medic tent, brawler ring, black leg kitchen, sniper range; Art of Weather trainers on sky islands) always have a trainer, and they don't despawn while you're within 200 blocks. Nobody is told this. `TrainerEntity.mobInteract` returns `PASS` server-side after sending the dialogue packet; vanilla convention is `SUCCESS`/`CONSUME`, so this is a candidate cause for flaky buttons.

**Design**
1. **Find them:**
   - Tavern barkeepers sell a **Trainer's Chart** (500 belly) for your fighting style: a vanilla explorer map to the nearest matching trainer building. Structure tags: `mallowpiece:trainer/swordsman` → `mineminenomi:unaligned/swordsman_dojo`, etc.
   - The Log Book's Trainers tab lists every trainer you've talked to, with coordinates.
2. **Reach them:** after talking to a trainer once, they give you a **Trainer's Den Den Mushi** (one per style). Using it summons a temporary copy of that trainer next to you for 2 minutes (10 min cooldown, not in combat). The copy is a normal MMnM trainer entity of the same type, marked `mallowpiece:summoned` and removed after 2 minutes.
3. **Make them work:**
   - **Spike first:** reproduce the button failures. In single-player and on a local dedicated server (`./gradlew runServer`), open each trainer type's dialogue 20 times and press every button. Record which fail and when in TESTLOG.
   - Candidate fixes, in order: (a) mixin `TrainerEntity#mobInteract` to return `InteractionResult.sidedSuccess(level.isClientSide)` and ignore the off-hand; (b) if the screen sends packets keyed to an entity that despawned or changed id, keep the trainer alive (`setPersistenceRequired`) while a player has its screen open; (c) if MMnM's screen itself is broken, replace the dialogue with our own screen that calls the same server-side actions. Write down which one fixed it.
   - Random roadside trainers become persistent once any player interacts with them.

**Config `[trainers]`:** `chartEnabled=true`, `chartPrice=500`, `denDenEnabled=true`, `summonSeconds=120`, `summonCooldownSeconds=600`.

**Acceptance:** buy a chart and follow it to a dojo; talk to the trainer; get the Den Den Mushi; walk 2,000 blocks away and summon; every dialogue button works 20/20 times.

## 2.6 Conqueror's Haki: earned by quest (M)
**Problem (owner):** today it's decided by your UUID, so it's the same answer on every server. The "random" check also looks broken: `HakiHelper.isHaoshokuBorn` sums the UUID's digits and does `sum & 10` (bitwise AND) where `% 10` was surely meant, so about a quarter of all players are "born kings." And once you have it, it's an instant win against anyone with less haki (fixed in 3.6).

**Design: The King's Path**, a 4-stage questline in the Log Book. It's available to everyone and hard to finish. Requires MMnM config `Haoshoku Haki Unlock Logic = NONE` (0.3 warns otherwise).

| Stage | Name | Objective | Unlocks when |
|---|---|---|---|
| 1 | **Spark** | Win 3 *outmatched* fights (kill an NPC with ≥1.5× your doriki) | 6,000 breakthrough cleared |
| 2 | **Will** | Survive 30 s below 20% HP in one fight and win it, twice | Stage 1 |
| 3 | **Recognition** | Busoshoku ≥ 50 **and** Kenbunshoku ≥ 50, **and** defeat a Hard challenge boss or an overworld boss | Stage 2 |
| 4 | **The Clash** | Use the Log Book at night, away from structures, to call the **Shadow of a King**: an elite NPC with conqueror's. Win the clash (3.6) and defeat it. Until 3.6 ships, just defeat it | Stage 3 |

- On success: unlock MMnM's `HaoshokuHakiAbility` for the player (**Spike:** find the unlock call in `AbilityCapability` / `IAbilityData`, e.g. how `/ability give` does it, in `commands/AbilityCommand`). Broadcast `<name> has awakened Conqueror's Haki!` with a sound and a brief screen shake for nearby players.
- Optional scarcity: `maxConquerorsPerWorld` (default 0 = unlimited). If set and full, stage 4 is locked with `The seas already have their kings.`

**Config `[conqueror]`:** `enabled=true`, `maxConquerorsPerWorld=0`, `stage1Wins=3`, `stage2Survives=2`, `stage3Haki=50`.

**Acceptance:** with debug commands, walk each stage; at stage 4 the Shadow appears and its defeat grants the ability; with MMnM's unlock logic left at COMBINED, ops see the 0.3 warning.
