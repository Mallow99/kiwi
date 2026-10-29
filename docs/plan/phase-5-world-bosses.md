# Phase 5 — Bosses in the world

**Milestone (owner playtest):** a wanted poster from a tavern turns into a map to Arlong Park. Arlong is there with his crew, fights with telegraphs, drops a box, and is back an hour later. Out at sea, a Supernova's ship can be found and boarded.

Fixes W6 (bosses stuck in a pocket dimension) and the owner's ask: *"boss ships with a Supernova or a Yonko."*

Facts this phase relies on (see API notes): MMnM's boss entities have a normal `(EntityType, Level)` constructor, so they can be spawned in the overworld. MMnM's challenge arenas are plain hollow boxes built in code (`challenges/arenas/*SimpleArena`), not themed places, so overworld lairs are generated with `tools/structgen` (4.1).

---

## 5.1 Boss framework (L)
**Goal:** one shared system for overworld bosses: our lairs, Supernovas, Yonko (6.3).

**Design**
- **Boss spec (data)** `data/mallowpiece/bosses/<id>.json`:
  ```json
  {
    "entity": "mineminenomi:arlong",
    "lieutenants": ["mineminenomi:kuroobi", "mineminenomi:chew"],
    "minions": {"mallowpiece:fishman_grunt": 6},
    "doriki": 7000,
    "hp_mult": 1.0, "damage_mult": 1.0,
    "phases": [{"below_hp": 0.5, "add_effects": ["minecraft:strength:0"], "summon": {"mineminenomi:pirate_grunt": 3}}],
    "loot": "mallowpiece:bosses/arlong",
    "respawn_minutes": 60,
    "telegraphed": true,
    "bossbar": true
  }
  ```
- **Spawning in a lair:** the lair template has a **boss altar marker**, a structure block in DATA mode with metadata `boss:<id>`. When the structure generates, we record the lair (structure start, altar pos, boss id) in `MallowWorldData`. The boss spawns when a player comes within 48 blocks and the boss is "ready."
- **Leash:** the boss and lieutenants stay within 32 blocks of the altar. Beyond that they walk back and heal 5%/s, so no dragging bosses home.
- **Boss bar** with the boss's name; phase changes announced in the action bar.
- Bosses are added to `#mallowpiece:telegraphed` (3.2) and get damage fairness (3.1).
- Doriki for rewards: set the boss's `IEntityStats` doriki to the spec value after spawn. Our curve (1.1) pays from that.

**Implementation:** `BossManager` (server tick every 20 ticks) looks at lairs near players. `BossSpec` codec. `LairData` in `MallowWorldData`. **Spike first:** summon `mineminenomi:don_krieg` in the overworld with `/summon` and check that its AI and phase goals work outside a challenge (some goals may expect an `InProgressChallenge`). Write down which bosses need a wrapper.

**Acceptance:** place a test lair with `/place structure mallowpiece:lair_test`; walk up; the boss spawns, has a boss bar, won't follow you past 32 blocks, and respawns after `respawn_minutes` (use `/mallowpiece debug boss_timer <id> 1`).

## 5.2 Overworld boss lairs for the existing 18 bosses (L)
Nine **domains**, each a structure from `tools/structgen` (4.1) with themed layout and NPCs:

| Domain | Bosses (boss + lieutenants) | Biome | Boss doriki | Look |
|---|---|---|---|---|
| Alvida's Cove | Alvida | beach | 3,000 | wrecked ship on a sandbar, hideout cave |
| Shells Town | Morgan | plains near coast | 3,500 | walled marine outpost with an execution yard |
| Orange Town Circus | Buggy, Cabaji | plains/savanna | 4,500 | big-top tent ring, cannon (Buggy Ball) platform |
| Syrup Hill | Kuro, Jango, Sham & Buchi | forest hills | 5,500 | mansion on a cliff, slope path |
| Mountain Bandit Camp | Higuma | taiga/mountains | 4,000 | log stockade in a valley |
| Baratie | Don Krieg, Gin, Pearl | ocean (fixed) | 6,500 | floating fish-boat restaurant + Krieg's wrecked galleon alongside |
| Arlong Park | Arlong, Kuroobi, Chew | coast | 7,500 | walled fishman compound, central tower, saltwater pool |
| Little Garden Ruins | Mr. 5 & Miss Valentine, Mr. 3 | jungle | 8,000 | overgrown ruins, giant bones, wax altar |
| Alabasta Ruins | Mr. 1, Mr. 0 | desert | 9,500 | sandstone palace ruins, underground tomb arena |

- Domains are rarer than strongholds: structure set spacing 80 / separation 40, one set for all nine, weighted equally, biome-restricted per domain.
- Each domain has: a lair arena (open, ≥ 24×24 floor, readable fight space), 6–12 themed minions (reuse MMnM grunts with fitting faction; fishmen = MMnM grunts with the fishman race via the style system if possible, otherwise standard), a **T3 treasure chest** behind the boss, and a wanted-poster board near the entrance.
- Boss doriki follows the table so the curve and the gates line up: East Blue domains pay best at 3k–7k, Baroque Works at 7k–10k.
- Loot `mallowpiece:bosses/<domain>`: MMnM's challenge reward table for that boss (reference it) plus the 1.4 box pool (domains count as "Hard": guaranteed iron + 25% golden) plus belly.

**Acceptance:** each domain generates (TESTLOG screenshots); each boss fight works in the overworld; the chest and boss loot drop.

## 5.3 Wanted posters → treasure maps (M)
**Design**
- Item `mallowpiece:wanted_poster` with NBT `boss: <id>` (or `supernova: <id>`). It shows the boss's name, bounty and a portrait slot (reuse MMnM's wanted-poster render if possible; otherwise a simple parchment item with name lore).
- **Sources:** tavern barkeepers sell 2 random posters (rotating each Minecraft day); every domain's notice board has the posters of *other* domains; 10% drop from captains and elites; contracts (6.2) hand them out.
- **Use:** right-click → becomes a vanilla filled map centred on the nearest *ungenerated or generated* domain of that boss (via `ServerLevel.findNearestMapStructure` with the domain's structure tag, like vanilla explorer maps), with a red X decoration. The map is titled `Last seen: <boss>`.
- Supernova posters (5.5) point at their ship's sea region.

**Acceptance:** buy a poster, use it, follow the map, find the boss.

## 5.4 Boss respawn + loot rules (S)
- Respawn timer per lair: `respawn_minutes` (default 60) after death. Uses world time, so a lair only respawns while its chunk is loaded or on the next visit.
- **First-kill bonus** per player per boss: +50% doriki and a guaranteed golden box on the first ever kill (encourages visiting every domain once).
- Repeat kills: normal loot. Our curve already reduces doriki once you out-level the boss.
- The treasure chest refills on boss respawn (re-apply its loot table if it's empty).

## 5.5 Supernova boss ships (L)
**Design**
- Rare ocean structure `mallowpiece:supernova_ship`: a large three-masted ship (structgen; ~60×40×20) with deck, below-deck crew quarters, the captain's cabin and a treasure hold (T4 chest). **Boarding ladders and nets** on both sides (sea safety, 1.8). Spacing 120 / separation 60, deep ocean and warm/lukewarm ocean only.
- Each ship belongs to one **Supernova** (chosen by structure start seed), with themed sails/flag colours and crew:

| Supernova | Doriki | Fruit / style | Signature |
|---|---|---|---|
| Eustass Kid | 12,000 | Jiki Jiki | metal arm, magnetic pulls; lieutenant **Killer** (swordsman, 10,000) |
| Trafalgar Law | 12,000 | Ope Ope | Room + Shambles teleport, sword |
| Basil Hawkins | 11,000 | Wara Wara | straw dolls (damage transfer), sword |
| X Drake | 11,500 | Ryu Ryu (Allosaurus) | dinosaur form, ex-marine officer |
| Scratchmen Apoo | 10,500 | Oto Oto | sound attacks at range |
| Capone Bege | 11,000 | sniper style (Shiro Shiro not in MMnM) | gunmen crew, cannon-heavy deck |
| Urouge | 11,000 | brawler (no fruit) | heavy brawler, high HP |
| Jewelry Bonney | 10,500 | brawler (Toshi Toshi not in MMnM) | fast brawler |

  Fruits use 3.5 loadouts. When 7.x adds a missing fruit (Shiro, Toshi), switch that Supernova to it.
- Crew per ship: 1 Supernova (boss, 5.1 spec), 1–2 elites, 6–10 pirate grunts and brutes, 2 pirate snipers.
- Loot: T4 hold (iron 50% / golden 50%, so always a box), the Supernova's own drop: their **wanted poster** (trophy) + 1 golden box on first kill (5.4) + Renown (6.1).
- Respawn: 120 minutes (config).
- **Canon names** are used by default (private server). Config `useCanonNames=true`; when false, names come from a generated list (`Captain "Iron Arm"`, etc.).
- Textures: v1 derived from MMnM captain skins with recipes (hair colour, coat colour). v2 (optional) original 64×64 skins drawn into `src/main/resources`.

**Acceptance:** `/locate structure mallowpiece:supernova_ship` → go there with Bubbly Coral → board via the ladder → fight the crew and the Supernova (telegraphed) → T4 loot.

## 5.6 Marine and Revolutionary equivalents (M)
Supernovas are pirates, which is fine for marines and revolutionaries (they're natural enemies). For **pirate** players who want marine-side late-game targets:
- **Vice Admiral Fleet:** an ocean structure, a marine battleship (reuse the 5.5 hull generator with marine colours) with a **Vice Admiral** boss (MMnM's marine vice admiral entity, boosted via a boss spec) and 2 commodores. T4 hold.
- **World Government Convoy:** a land event (once per 2 real hours, 25% chance per eligible player ≥ 8,000 doriki): a celestial-dragon procession with CP agents (elites with Rokushiki-style brawler kit) along a road. Defeat the escorts to loot the convoy (T3 + belly). Revolutionaries get double Renown from it. Build on MMnM's caravan/celestial visit event code paths if reusable (`EventsWorldData.addCaravan`, `addCelestialVisit`); otherwise our own event.
