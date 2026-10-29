# Phase 3 — Fair, readable fights

**Milestone (owner playtest):** at matching doriki, a Hard challenge boss can't take you from full HP to dead in under ~4 seconds. You can see its big attacks coming. The screen stays readable. Conqueror's Haki is a clash you can win or lose, not a stat check.

Owner feedback this addresses: *"Challenges are visually difficult, it's just spamming effects. The NPCs are simple brain-wise: they run at you and delete your HP. Either you cheese them or they kill you so fast that even at 10,000 doriki you're fucked."* And: *"Conqueror's means if you have it you instantly win against anyone weaker, and if you don't you instantly lose."*

---

## 3.1 Damage fairness: no one-shots (S)
**Design**
- **Burst cap:** one hit from an NPC can do at most **35%** of the player's max HP (40% for Hard challenge bosses), unless the attack was **telegraphed** (3.2), which can do up to 70%.
- **Combo cap:** damage from one NPC source within any 2-second window is capped at **60%** of max HP. Extra damage in that window is dropped.
- Applies to NPC → player only. PvP is untouched here (7.4).

**Implementation:** `LivingHurtEvent` (lowest priority, server): if the target is a player and the source entity is a non-player `LivingEntity` (or the owner of a projectile or ability), clamp. Keep a per-player ring buffer of `(attackerId, tick, amount)`. Telegraphed hits carry a flag the attacker sets (3.2) in its persistent data for that tick.

**Config `[combat.fairness]`:** `enabled=true`, `burstCap=0.35`, `bossBurstCap=0.40`, `telegraphedCap=0.70`, `comboWindowTicks=40`, `comboCap=0.60`.

**Acceptance:** at 2,000 doriki, fight Don Krieg (Hard) via `/challenge`: no single hit above 35–40% of your max HP (log hits with `/mallowpiece debug combat_log on`).

## 3.2 Telegraphed boss abilities (L)
**Design:** every big ability a boss uses gets three parts:
1. **Wind-up** (10–30 ticks, per ability): the boss stops, plays a cue (sound plus a distinct particle ring or glow on the boss, and a red ground marker for area attacks), and is slowed.
2. **Release:** the ability fires as normal. Damage is capped by `telegraphedCap`.
3. **Recovery** (20–40 ticks): the boss can't start another big ability and takes +15% damage. This is your opening.

Small abilities (jabs, basic projectiles) skip the telegraph but count toward a **global ability cooldown** per boss of 30 ticks, so bosses can't chain everything at once.

**Implementation**
- **Spike first:** find where MMnM NPC ability goals actually call the ability (`AbilityWrapperGoal.startWrapper()` in each subclass, e.g. `ProjectileAbilityWrapperGoal`). Then pick the least invasive hook:
  - (a) preferred: MMnM's `AbilityCanUseEvent` / `AbilityUseEvent` (in `api/events/ability`). If `AbilityCanUseEvent` is cancelable and fires for NPCs, deny use while a boss is in wind-up or recovery, and start the wind-up on the first request.
  - (b) otherwise, a Mixin on `AbilityWrapperGoal#start` (`m_8056_` in SRG) for entities in `#mallowpiece:telegraphed`, which defers `startWrapper()` until the wind-up ends.
- Per-ability timings in data: `data/mallowpiece/telegraphs/<ability id>.json` → `{ "windup": 20, "recovery": 30, "big": true, "cue": "area" }`. Default for abilities with no file: `big=true` if the ability's damage ≥ 15 or it's an area/charge ability, else small.
- Entity tag `#mallowpiece:telegraphed`: every MMnM boss (Alvida … Mr. 0), our elites, Supernovas and Yonko.

**Acceptance:** fight Arlong (Hard): every big move has a visible and audible wind-up you can dodge by moving; after it there's a short window where he doesn't attack.

## 3.3 Visual clarity (M)
**Design:** a client setting **Ability Effects Density**: 100% (default MMnM) / 60% / 30%. Our own abilities and telegraph cues are always shown. Separate toggles: "reduce screen shake," "reduce flashes."
**Implementation**
- **Spike first:** work out how MMnM spawns ability particles (the `particles/` package has ~144 classes; they likely go through vanilla `ParticleEngine` or a custom effect spawner sent by packet). Choose a hook:
  - vanilla path: Mixin `ParticleEngine#createParticle(ParticleOptions, ...)`. If `options.getType()` is in the `mineminenomi` namespace, skip it with probability `1 − density`;
  - custom path: Mixin the client packet handler that spawns MMnM particle effects and thin the count.
- Also check MMnM's own client config (`Fire Visibility` exists). Expose MMnM options we can't change in our docs.

**Config (client) `[visuals]`:** `abilityEffectDensity=1.0`, `reduceShake=false`, `reduceFlashes=false`.

**Acceptance:** fight Mr. 0 at 30% density: the arena stays readable and telegraph cues are still visible.

## 3.4 Challenge boss tuning pass (M)
**Goal:** with 3.1 and 3.2 in place, make each challenge beatable without cheese at the doriki its gate expects.
- For each of the 36 challenges, do one test fight at the target doriki: standard = gate it's offered for (2k/4k), Hard = 8k–10k. Record time-to-kill both ways in `docs/plan/challenge-tuning.md`. Target: player dies in ≥ 20 s if they stand still; boss dies in 60–120 s with competent play.
- Tuning levers (data, `data/mallowpiece/challenge_tuning.json`): boss damage multiplier, boss HP multiplier, telegraph timings, global ability cooldown. Apply via `EntityJoinLevelEvent` for boss entities in the challenge dimension (attribute modifiers).
- Write down anything that's an AI problem rather than a numbers problem, for 5.1.

## 3.5 NPC fruit AI for boss-tier fruits (L)
**Problem:** only 12 fruits have NPC AI in MMnM (Mera, Moku, Bomu, Awa, Suke, Goe, Kilo, Mogu, Sai, Neko Leopard, Ushi Bison, Ushi Giraffe). Supernovas and Yonko need more.

**Design:** NPC loadouts for these fruits, in this order:
1. **Logia:** Goro, Hie, Magu, Pika, Yami, Suna, Gasu, Yuki
2. **Boss Paramecia:** Gura, Ope, Jiki, Ito, Doku, Wara, Nikyu, Bari
3. **Zoan:** Ryu (Allosaurus, Pteranodon, Brachiosaurus), Tori (Phoenix), Zou (Mammoth)

Each loadout picks 3–5 of the fruit's abilities and wraps them in MMnM's generic goals (`ProjectileAbilityWrapperGoal`, `CloseMeleeAbilityWrapperGoal`, `AreaAbilityWrapperGoal` with min/max distance, `DashAbilityWrapperGoal`, `ActiveBuffAbilityWrapperGoal`, `ReactiveGuardAbilityWrapperGoal`, `MorphAbilityWrapperGoal` for zoans). It also includes the logia passives.

**Implementation**
- `NpcFruitLoadouts` registry (our code): `fruit id → List<GoalFactory>`; `GoalFactory = (Mob) -> AbilityWrapperGoal`. Abilities are referenced by their `AbilityCore` registry objects (find the names in `init/ModFruits` and `abilities/<fruit>/`).
- `MallowNpcHelper.giveFruit(OPEntity mob, AkumaNoMiItem fruit)`: sets the devil fruit capability, unlocks/equips the abilities as MMnM's helper does (**Spike:** check whether NPCs need the abilities added to their ability capability or only the goals; mirror `MobsHelper.getDevilFruitAbilities`), and adds goals at priority 2. Uses MMnM's own wrappers when `hasGoalWrapper()`, ours otherwise.
- All loadout big moves are registered with the telegraph data (3.2).

**Acceptance per fruit:** summon an elite with the fruit (`/mallowpiece debug npc_fruit <entity> <fruit>`) and fight it for 60 s. It uses at least 3 different abilities, doesn't stand idle at range, and doesn't break blocks in protected areas.

## 3.6 Conqueror's Haki clash rework (M)
**Today:** if the user's total haki/100 is ≥ 0.5 above the target's, the target is knocked out (`UNCONSCIOUS`) instantly. No resistance, no counterplay.

**Design: Will**
- `Will = totalHaki/100 + doriki/10000 + (has conqueror's ? 0.75 : 0) + clashBonus`.
- When a conqueror's burst would knock out a target (`HakiKnockoutEvent.Pre`, cancelable), we decide instead:
  - **NPC targets:** fodder (grunts, snipers, brutes, ≤ 0.5× the user's doriki) are knocked out as before, which is the iconic moment. Captains, elites and bosses take **Intimidated** (Slowness II, Weakness I, can't use abilities) for 3 s. Bosses are immune to knockout entirely.
  - **Players without conqueror's:** if attacker Will − target Will ≥ 1.0 **and** the target is below 40% HP → knockout (shorter: 3 s). Otherwise → Intimidated for 2 s plus knockback.
  - **Players with conqueror's:** a **clash**. Both players get a 3-second prompt (an action-bar meter plus a key, default `G`: press when the meter is in the zone, 3 rounds). Each round won adds +0.25 Will for this clash. The higher final Will wins: the loser is staggered (1.5 s) and the winner's burst costs no cooldown. A draw knocks both back.
- Conqueror's coating (infusion) is unchanged here; review in 7.4.

**Implementation:** `HakiKnockoutEvent.Pre` → cancel and apply our logic. Effects: our own `MobEffect`s `mallowpiece:intimidated`, `mallowpiece:clash_stagger`. Clash: server-authoritative state machine per pair, with a client overlay plus key packet. Single-player testing uses the Shadow of a King NPC (2.6), which "presses" with a fixed skill (60% per round).

**Config `[conqueror.clash]`:** `enabled=true`, `fodderRatio=0.5`, `knockoutWillGap=1.0`, `knockoutHpThreshold=0.4`, `intimidateSeconds=3`, `clashRounds=3`.

**Acceptance:** with conqueror's (debug-granted), burst near 5 grunts and a captain: grunts drop, the captain is intimidated and keeps fighting. Fight the Shadow of a King and win or lose the clash based on your timing.
