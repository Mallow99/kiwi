# Phase 6 — Endgame (after 10,000 doriki)

**Milestone (owner playtest):** after clearing the New World breakthrough at 10,000, there's a Renown track with ranks and rewards, daily contracts, a fruit awakening to chase, rare Yonko fleets, and (on the friend server) bounty hunting and crew territory.

Owner feedback: *"Once you get to 10,000 doriki there's nothing to do, no endgame, no reward, just the journey, and that's fine the first time you play the mod and only the first time. That's why PvP was such a big thing."*

**Principle:** endgame rewards are **status, cosmetics, options and small, capped power**. That keeps PvP between a day-1 max player and a day-30 max player fair. The biggest power reward (awakening) comes from a challenge, not a grind.

---

## 6.1 Renown (M)
**Design**
- Unlocked by the 10,000 breakthrough (2.1). After that, **doriki you'd gain at the cap converts 1:1 into Renown**, so every fight still counts.
- Direct Renown sources:

  | Source | Renown |
  |---|---|
  | Supernova (5.5) | 300 (first kill of each: +300) |
  | Yonko commander (6.3) | 500 |
  | Yonko (6.3) | 2,000 |
  | Overworld boss (5.2) | 100 (first per boss per real day) |
  | T3 enemy stronghold cleared | 150 |
  | Notorious target | 75 |
  | Contract (6.2) | 100–400 |
  | Player bounty claim (6.5) | 10% of the claimed bounty / 1,000, min 50 |
  | Territory held (6.6) | 50 per real hour per held post |
- **Ranks** (titles are per faction):

  | Rank | Renown | Pirate | Marine | Revolutionary | Bounty Hunter | Rewards |
  |---|---|---|---|---|---|---|
  | I | 1,000 | Supernova | Hero of Justice | Officer | Hunter | Title, faction coat cosmetic, **Awakening trial access (6.4)** |
  | II | 4,000 | Warlord | Vice Admiral | Commander | Demon Hunter | +5% max HP, **Haki Mastery (6.7)**, Jolly Roger/emblem set |
  | III | 10,000 | Yonko Commander | Admiral | Army Commander | Legend | **Can summon a Yonko fleet with a Yonko poster (6.3)**, second awakening stage |
  | IV | 25,000 | Emperor of the Sea | Fleet Admiral | Chief of Staff | Pirate King's Shadow | +5% max HP (10% total), server-wide announcement, unique aura cosmetic |
- Titles show in the tab list and above the name (if MMnM's name rendering allows; otherwise in chat prefix).
- Renown never decays.

**Implementation:** `MallowPlayerData.renown`, `renownRank`. Hook into our `DorikiEvent.Pre`: at the cap with the 10k gate broken, convert. Max HP via an attribute modifier with a fixed UUID.

**Acceptance:** `/mallowpiece debug gate 10000 complete`, `/mallowpiece debug renown add 1000` → rank I title and the awakening tab unlock.

## 6.2 Bounty board contracts (M)
**Design**
- Block `mallowpiece:bounty_board` (Den Den Mushi + notice board). It generates in taverns (if we can add to MMnM's tavern via a structure processor; otherwise next to them), in our strongholds and domains, and can be crafted.
- **3 contracts per player per real day** (resets at 00:00 server time), pulled from a weighted list for your faction:

  | Type | Goal | Reward |
  |---|---|---|
  | Hunt | Kill a named elite spawned at a marked location (map given) | 150 Renown, belly, 25% iron box |
  | Raid | Clear a T3 enemy stronghold within 15 min of arriving | 250 Renown, golden box 20% |
  | Escort | Protect a caravan (MMnM caravan event if reusable) to its destination | 200 Renown, belly |
  | Siege | Survive 5 waves of enemies at a marked spot | 200 Renown, iron box |
  | Supernova Bounty | Defeat a specific Supernova | 400 Renown, golden box |
- **Modifiers** (one random, +50% Renown): `No Devil Fruit abilities`, `Haki only`, `Under 10 minutes`, `No healing items`.
- Before 10,000 doriki the board offers *practice contracts* with belly and box rewards and no Renown, so it's useful all game.
- The Log Book gets a **Contracts** tab with progress.

## 6.3 Yonko fleets (L)
**Design**
- A rare **world event** at sea: a Yonko flagship plus 2 escort ships appear 300–500 blocks from an eligible player. Eligible means Renown rank II+ (or anyone with a Yonko poster at rank III). Chance: every 2 real hours, 25% per eligible online player, at most one fleet at a time. Lasts 90 real minutes or until defeated.
- **Spike first:** placing and removing big structures at runtime. Place the generated templates with `StructureTemplate.placeInWorld` into ocean chunks that are loaded but player-free. Record every block position changed (sparse). When the event ends and no player is within 128 blocks, restore the old blocks (water/air). If restore is unsafe (player built on it), leave it as a wreck: replace sails with cobwebs and remove the chests' loot. If runtime placement is too fragile, fall back to rare worldgen "Yonko Territories" (islands) with weekly boss respawns.
- **Roster** (fruits limited by what MMnM has; 3.5 provides AI):

  | Yonko | Doriki | Kit | Commanders |
  |---|---|---|---|
  | Whitebeard | 20,000 | Gura Gura, bisento (heavy melee), conqueror's | 2 elite division commanders (one with Moku or Mera) |
  | Blackbeard | 20,000 | Yami Yami **and** Gura Gura (phase 2), conqueror's | 2 elites (one Doku-style) |
  | Shanks | 20,000 | swordsman, strongest haki, conqueror's clash on phase change | 2 elites (sniper and swordsman) |
  | Kaido | 22,000 | huge brute, area club attacks; dragon form once Uo Uo exists (7.x) | 2 elite "All-Stars" (Ryu fruit users) |
- Two phases: phase 2 at 50% HP adds conqueror's-coated attacks, a conqueror's clash (3.6) with the nearest player, and summons.
- Loot: guaranteed golden box + 50% second golden; **Awakening Catalyst** (6.4); Yonko poster trophy; 2,000 Renown.

## 6.4 Awakenings (L)
**Design**
- Requires Renown rank I and MMnM config `Enable Awakenings = true` (0.3).
- **Awakening trial** per fruit type, started from the Log Book. One attempt per real day, and it costs an Awakening Catalyst (from Yonko, Supernova first kills, or rank-up rewards):
  - Logia: survive 3 minutes in a storm arena while elemental adds attack; your logia must stay active.
  - Paramecia: destroy 5 crystals by using your fruit's abilities in creative ways (each crystal needs a different ability).
  - Zoan: defeat a stronger beast version of your own form.
  - The arena is built with structgen in a pocket area at y=-50 beneath the player's position, using MMnM's challenge dimension if it can be reused.
- On success: `DevilFruitBase.setAwakenedFruit(true)` (so MMnM's own awakening logic applies where it exists, e.g. Gomu Gear 5), plus our **generic awakening** for every fruit:
  - All fruits: −20% cooldowns, +15% fruit ability damage (attribute modifiers on fruit abilities, **Spike:** find MMnM's ability damage and cooldown modifier API, `AbilityAttributeModifier`, cooldown components; prefer events if they exist).
  - Logia: **Elemental aura**, an area around you that applies the element's effect to enemies (burning, slow/freeze, shock, blind…) at low damage.
  - Paramecia: abilities that create blocks or areas get +50% size/range.
  - Zoan: in hybrid/full form +1 HP/s regen, +20% damage reduction, knockback resistance.
- Rank III unlocks the **second stage**: aura and buffs +50%.
- Awakening is removed if the player loses their fruit, and kept through death.

## 6.5 Player bounties + hunter contracts (PvP, M)
**Default off** (`[pvp] bountyHunting=false`); turn it on for the friend server.
- Online players with an MMnM bounty ≥ 10,000,000 appear on bounty boards as targets, with the dimension and approximate area (rounded to 200 blocks, updated every 5 minutes).
- Killing a listed player gives the hunter 10% of the target's bounty as belly (from the world, not the target) and Renown (6.1 table). The target loses 10% bounty.
- Protection: 30 minutes of "bounty cooldown" after being claimed (not listed). No listing inside their own crew's territory (6.6).
- Marines and bounty hunters get double rewards.

## 6.6 Crew territory (PvP, L)
**Default off** (`[pvp] territory=false`).
- Craftable **Territory Post** (banner + logs + MMnM flag). A crew places it and claims a 3×3-chunk area. Uses MMnM crews (`FactionsWorldData` crews, `FlagPlacedEvent`).
- A held post gives its crew 50 Renown per real hour (split among online crew members), and a +10% belly drop bonus in the area.
- **Capture:** a rival crew breaks the flag and stays in the centre chunk for 3 minutes with no defender inside. Only possible while ≥1 defender is online, or after 24 h offline (config), so nobody loses territory while asleep.
- Max 3 posts per crew.

## 6.7 Haki Mastery (S)
- Unlocked at Renown rank II. Haki exp gained at the cap (100) becomes **Mastery points** (1:1).
- Spend points in the Log Book on small, capped upgrades (each 3 levels, 30/60/100 points):
  - Hardening: +10% duration per level.
  - Future Sight: +1 dodge per activation per level (**Spike:** find how MMnM's future sight counts dodges).
  - Emission: +10% range per level.
  - Conqueror's (if owned): +0.1 Will per level (3.6).
- Total power gain is deliberately small; it's a long-tail goal.
