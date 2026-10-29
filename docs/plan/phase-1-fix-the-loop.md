# Phase 1 — Fix the loop

**Milestone (owner playtest):** a fresh character on Hard reaches about 2,000 doriki in about 2 hours of normal play. Ships and bandit forts are worth raiding. Bosses can drop boxes. A box never opens to nothing. A marine who loots a captain's chest without the rank gets hunted.

Fixes weak points W1, W3 (loot side), W4, W5 and the "ships aren't worth it" feedback.

---

## 1.1 Doriki curve (S)
**Goal:** replace the 100× cliff with a smooth falloff, front-load the early game, and land on about 20 h of active play to 10,000 doriki. Farming weak mobs stops being worth it.

**Design**
For a kill of a target with doriki `T` by a player with doriki `P`:
```
r     = P / T
g(r)  = 1                          if r <= 1
      = max(floor, r^(-exponent))  if r > 1          exponent = 3, floor = 0.02
gain  = (T / 100) * g(r) * bandMult(P)
bandMult is chosen by the next 2,000 gate above P:
  preset "phase1": {2000: 2.18, 4000: 1.09, 6000: 0.34, 8000: 0.55, 10000: 0.80}
  preset "full":   {2000: 2.18, 4000: 1.09, 6000: 0.30, 8000: 0.18, 10000: 0.12}
```
- Use the `phase1` preset until tasks 2.4 (elites) and 5.5 (Supernova ships) are done, then switch the default to `full`. The presets differ because the late game needs strong enemies to exist; `phase1` compensates while they don't.
- The sim (`tools/sim/progression.py`) gives about 2/3/4/5/6 h per band, ~20 h total, ~770 kills. For reference: at 10,000 doriki an enderman (~2,100) pays ~0.05 per kill, so farms are dead.
- Unchanged: notorious targets' minimum of 100 (apply our multiplier after it), the base mod's "no doriki for killing your own faction", and anything not from `KILL_NPC`.

**Implementation**
- `LivingDeathEvent` (priority HIGH, server only): if the killer resolves to a `ServerPlayer` (same rules as `StatsGainHandler.giveStats`: direct attacker, ability damage source owner, or last hurt by player), store `KillContext{targetDoriki, targetType, gameTime}` in a per-player map.
- `DorikiEvent.Pre` (MMnM event, normal priority): if `source == KILL_NPC` and there's a `KillContext` from this game tick, compute `gain` as above and `event.setDoriki(gain)`. Clear the context. If there's no context, multiply the incoming amount by `bandMult(P)` as a fallback.
- `/mallowpiece debug doriki_curve <T>` prints the gain at the player's current doriki.

**Config `[progression.doriki]`:** `enabled=true`, `preset="phase1"`, `falloffExponent=3.0`, `falloffFloor=0.02`, `bandMult_2000..bandMult_10000` (override the preset when set), `parityDivisor=100`.

**Acceptance**
1. New world, Hard, `/doriki 0`. Kill 5 marine grunts with `/mallowpiece debug info` before and after each kill: each pays roughly 22–55 doriki (grunt 1,000–2,500 × 2.18 / 100).
2. `/doriki 9000`, kill a grunt: pays < 0.1.
3. `/doriki 5000`, kill a captain (4,500–6,500): pays ~11–22 with `phase1`.
4. `python3 tools/sim/progression.py` still prints ~20 h; the numbers in this file match.

## 1.2 Haki curve (S)
**Goal:** haki to 100 in ~12–17 h of fighting. Remove the asymptotic crawl near the cap and the 5× penalty on weak targets.

**Design**
Per qualifying hit (only where MMnM would already grant exp, keeping its activation rules such as hardening active or Future Sight on):
```
s     = clamp((targetMaxHP + targetAttack) / 120, 0.15, 2.0)
pen   = 0.5 if (targetMaxHP + targetAttack) < currentHaki else 1.0
slow  = 1.25 - 0.5 * currentHaki / hakiLimit
gain  = c * s * pen * slow           c = 0.040 (busoshoku), 0.030 (kenbunshoku on-hit)
```
Passive kenbunshoku gain (+0.025 every 30 s with Future Sight) is left alone.

**Implementation**
- `LivingHurtEvent` (server): when a player hurts a living target, or a living target hurts a player (for kenbunshoku), store `HitContext{strength, tick}` per player.
- `HakiExpEvent.Pre`: for BUSOSHOKU with source `KILL_NPC`/`KILL_PLAYER`, and KENBUNSHOKU with source `NATURAL` *and* a HitContext from this tick, replace the amount with `gain`. Otherwise leave it alone.

**Config `[progression.haki]`:** `enabled=true`, `busoshokuC=0.040`, `kenbunshokuC=0.030`, `strengthDivisor=120`, `weakTargetPenalty=0.5`.

**Acceptance:** `/hakiexp busoshoku 0`, harden, punch a marine captain 20 times, gain ~0.8–1.0 total. At 90 haki, 20 punches on a captain still gain ~0.5 total (today: almost nothing).

## 1.3 Structure loot tiers (M)
**Goal:** every structure that has a "treasure/captain" chest is worth raiding *for its stage of the game*. Ships stop being "rarely worth it."

**Design.** Four tiers. Box odds are per treasure/captain chest (other chests in the structure keep their loot).

| Tier | Structures (chest) | Wooden | Iron | Golden | Key | Extras |
|---|---|---|---|---|---|---|
| T1 early | bandit camp large tent, bandit house, pirate small ship supplies, marine watch tower | 25% | 5% | — | 20% | Bubbly Coral 15% (1.8) |
| T2 mid | bandit fort secret stash, bandit cave gold, pirate medium ship captain, marine small base captain, ghost ship captain, caravan easy | 30% | 20% | 3% | 35% | Ancient manual 5% |
| T3 late | marine large base captain, pirate large ship treasure, marine battleship treasure, caravan hard, (later) Pirate Den captain, Rev Hideout war room | 20% | 40% | 12% | 60% | Ancient manual 15% |
| T4 endgame | (later) Supernova ship, Yonko flagship | — | 50% | 50% | 100% | see Phase 5/6 |

At T3, one specific golden fruit takes ~140 chests on average *before* pity (~452 today). Pity (1.5) cuts that sharply for anyone who keeps opening boxes.

**Implementation**
- `LootTableLoadEvent` for each listed table id (`mineminenomi:chests/...`): remove the MMnM pool named `mineminenomi:fruit_box` if present, then add our pool `mallowpiece:tier_box` with the tier's odds (a `minecraft:random_chance` condition with chance = wooden + iron + golden, and entries weighted by each). Add the key pool and extras as separate pools.
- Tier mapping comes from a datapack-style JSON in our resources: `data/mallowpiece/loot_tiers.json` → `{ "mineminenomi:chests/pirate/large_ship/treasure": "T3", ... }`, plus the tier definitions. This makes rebalancing a data edit.
- **Spike first:** confirm `LootTableLoadEvent` fires for `mineminenomi:` tables in 1.20.1 (it should; Forge fires it in `ForgeHooks.loadLootTable`). If it doesn't, fall back to a Global Loot Modifier `mallowpiece:tier_box_modifier` with a `LootTableIdCondition` per table.

**Config `[loot]`:** `tiersEnabled=true`, `tierFile="mallowpiece:loot_tiers"`.

**Acceptance:** `/loot give @s loot mineminenomi:chests/pirate/large_ship/treasure` 100 times (put it in a command block or function): about 20 wooden, 40 iron and 12 golden boxes (±8). Repeat for one T1 and one T2 table.

## 1.4 Boss rewards include boxes (XS)
**Design:** standard challenge bosses have a 35% chance of an iron box; Hard bosses have a guaranteed iron box plus a 25% golden box. When overworld bosses arrive (5.4), they use the same tables.
**Implementation:** `LootTableLoadEvent` for every `mineminenomi:rewards/*` table: add the pool. Use the id suffix `_hard` to pick the variant.
**Acceptance:** win `alvida_hard` via `/challenge` 4 times: 4 iron boxes, and golden roughly once.

## 1.5 Box pity + empty-box fix (S)
**Goal:** a box never opens to nothing, and bad luck has a floor.

**Design**
- Pity points per player: opening a wooden box +1, iron +3. Golden doesn't add.
- At **30 points**, the next wooden or iron box rolls one tier higher (wooden→iron table, iron→golden table) and resets the points.
- Getting any tier-3 fruit from any source resets the points.
- Empty result → re-roll the same table up to 10 times. If it's still empty (e.g. every fruit is taken in One Fruit per World), give back the box and the key and say `The box is empty… someone else has every fruit it could hold.`

**Implementation**
- Intercept `PlayerInteractEvent.RightClickItem` for `AkumaNoMiBoxItem` (server, our priority HIGH), cancel it, and run our own open logic. It mirrors `AkumaNoMiBoxItem.use` (key check, consume key and box, roll the table, pick the first fruit that passes `OneFruitWorldData.isFruitAvailable`, respect `DevilFruitHelper.hasDFLimitInInventory`, `worldData.inventoryOneFruit(fruit, player, "Obtained from <box name>")`) plus pity and re-roll. Keep a reference comment to the MMnM method we mirror.
- Pity points live in `MallowPlayerData.boxPity`. Show them in the box tooltip: `Lucky streak: 18/30` (client tooltip event, synced value).

**Config `[loot.boxes]`:** `pityEnabled=true`, `pityThreshold=30`, `pityWooden=1`, `pityIron=3`, `rerollAttempts=10`.

**Acceptance:** open 30 wooden boxes with keys: the 31st rolls from the iron table. Set One Fruit per World on and take all wooden fruits (debug): the box comes back with its key.

## 1.6 Marine rank-locked chests + theft (M)
**Goal:** marine bases aren't a free loot piñata for marine players. You can still steal, but you'll be hunted.

**Design**
- Applies to players who are marine-aligned (marine, bounty hunter, world government), i.e. exactly the ones MMnM protects from marine NPCs.
- **Restricted chests** (only at first open, when the chest still has its loot table; already-looted chests are free):

  | Loot table | Required rank (loyalty) |
  |---|---|
  | `mineminenomi:chests/marine/small_base/captain` | Lieutenant (15) |
  | `mineminenomi:chests/marine/large_base/captain` | Captain (25) |
  | `mineminenomi:chests/marine/battleship/treasure` | Commodore (40) |
  | Pirate Den / Rev Hideout chests | n/a (enemy structures) |
- **With the rank:** the chest opens normally. Message: `Requisition approved, Captain.`
- **Without it**, the first time per chest: a warning screen/message, `This is the base captain's requisition chest. Opening it without rank is theft. Open again to steal.` (needs a second open within 10 s). If you steal:
  - `setRogue(true)` for **10 minutes** (remember whether the player was already rogue, and restore that state afterwards).
  - Loyalty −10.
  - Every marine NPC within 48 blocks immediately targets the player.
  - After 60 s, if the player is still within 200 blocks of the structure, an ambush squad spawns 20–30 blocks away: 3 marine grunts, 1 marine brute, 1 marine captain.
  - Message: `You stole from the Marines! You're a deserter for 10:00.` A boss-bar style countdown is shown while rogue.
  - Stealing again while rogue adds 10 minutes and −10 loyalty.
- Non-marine players aren't affected at all; they already have to fight their way in.

**Implementation**
- Access transformer: make `RandomizableContainerBlockEntity.lootTable` readable (or use reflection with the SRG name `f_59605_`; check in the reference).
- `PlayerInteractEvent.RightClickBlock` (server): the block entity is a `RandomizableContainerBlockEntity` with a non-null loot table in the restricted map → check rank → confirm/steal flow. Store the pending confirmation as `{pos, tick}` in `MallowPlayerData`.
- Rogue timer: `MallowPlayerData.rogueUntilTick`, `rogueWasManual`. A server tick handler (every 20 ticks) restores state when the timer expires and calls `ModNetwork.sendTo(new SSyncEntityStatsPacket(player), player)` after each change.
- NPC aggro: for `OPEntity` within 48 blocks whose faction is marine, call `setTarget(player)`.

**Config `[theft]`:** `enabled=true`, `rogueMinutes=10`, `loyaltyPenalty=10`, `aggroRadius=48`, `ambushEnabled=true`, `ambushDelaySeconds=60`, plus the rank map.

**Acceptance**
1. Marine with `/loyalty 0`: open a large base captain chest → warning; open again → loot, rogue on, grunts attack, ambush after 60 s, rogue off after 10 min (use the debug command `/mallowpiece debug theft_timer 30` to shorten it).
2. `/loyalty 30`, new large base: the chest opens normally with the requisition message.
3. A pirate opening the same chest: no change from base behaviour.

## 1.7 Death tax preset + challenge doriki (XS)
- Put the recommended death settings in `docs/recommended-mmnm-config.md`: keep **95%** doriki and haki, 90% bounty, 75% belly, 50% loyalty. Reason: with a ~20 h curve, losing 23% of 8,000 doriki costs about 4 hours, which is a quit moment, not a consequence.
- Scale `StatChangeSource.CHALLENGE` doriki by `challengeDorikiMult=0.5` in our `DorikiEvent.Pre` handler. Otherwise first clears of all 36 challenges would hand out ~5,000+ doriki and skip most of the curve. Gates (2.1) also cap it.
- **Acceptance:** finish a standard challenge: doriki reward is half what MMnM shows in its reward message (we also post our own line: `MMnM+: challenge doriki ×0.5`).

## 1.8 Sea safety for fruit users (XS)
**Goal:** ship content shouldn't be a death trap for fruit users.
- Add Bubbly Coral (3 uses, 3 min water protection each) to T1 ship supplies (15%) and T2 ship captain chests (25%). Guarantee one in every pirate/marine trader's stock.
- Ship structures: no generation change in this phase. Phase 4's structure generator adds boarding ladders to the ships we generate.
- **Acceptance:** `/loot` the pirate small ship supplies 50 times → about 7 Bubbly Corals.
