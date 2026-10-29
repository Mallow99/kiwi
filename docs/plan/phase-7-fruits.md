# Phase 7 — Fruits

**Milestone:** at least one new devil fruit is in the game: it drops from boxes, has abilities with icons, NPCs can use it, and it's balanced against fruits of its tier.

This is last because each fruit is the most expensive unit of content, and new fruits don't fix a broken loop. It's still the community's most-wanted feature, so it should land once the loop is fixed.

---

## 7.1 Fruit pipeline + first new fruit (L)
**Goal:** a documented, repeatable way to add a fruit, proven with one.

**Implementation**
- **Spike first:** read MMnM's Ability API docs (`pixelatedw.xyz/mine-mine-no-mi/docs/addons/ability-api/ability-core.html`) and how `init/ModFruits` + `init/ModAbilities` register fruits and abilities. Confirm an addon can register: `AbilityCore`s (MMnM's ability registry), an `AkumaNoMiItem` (our item registry), and the fruit's entry in the Devil Fruit encyclopedia.
- Write `docs/plan/fruit-pipeline.md` covering: registry objects, ability classes (by MMnM component: cooldown, charge, continuous, projectile…), icons (`textures/abilities/<id>.png`, 16×16 or MMnM's size), fruit item texture/model, lang keys, box table entry (via our 1.3 `LootTableLoadEvent` handler: append to the tier pool), NPC loadout (3.5), telegraph data (3.2), awakening hooks (6.4).
- **First fruit:** owner's pick. Default if not picked: **Toshi Toshi no Mi** (Jewelry Bonney, tier 2, Paramecia), so Bonney (5.5) gets her fruit. Abilities (5): *Age Down Touch* (melee, target gets Weakness II + Slowness I, 8 s), *Age Up Touch* (melee, Mining Fatigue + Slowness II), *Distorted Future* (self buff: Strength II + Speed II for 10 s, then Weakness I for 10 s), *Child Form* (toggle: smaller hitbox via MMnM's size system, +speed, −damage), *Age Rewind* (cleanse your own negative effects, long cooldown).

**Acceptance:** `/give @s mallowpiece:toshi_toshi_no_mi`, eat it, use all abilities; it appears in iron boxes; an NPC with it uses at least 3 abilities; `/check_fruits` lists it.

## 7.2 Restore Mane Mane no Mi (L)
MMnM removed it between 0.9.5 and 0.11.x. Rebuild it as ours (tier 2, Paramecia): *Memoir* (copy the face of the last player/NPC you hit: your skin and name tag render as theirs for 60 s; NPCs of their faction treat you as friendly unless you attack), *Mane Mane Montage* (melee combo), and Okama Kenpo as a kick set. Bon Clay (Mr. 2) becomes possible as a boss (5.2: add him to Little Garden Ruins).
- **Spike:** skin swapping needs a client render hook (`RenderPlayerEvent.Pre`, swap the texture/profile). Check that MMnM's own morph system (`init/ModMorphs`) can't do it first.

## 7.3 Further fruits (L each)
The owner picks the order. Candidates, chosen because they complete existing content:

| Fruit | Tier | Why |
|---|---|---|
| Shiro Shiro no Mi | 3 | Capone Bege's fortress body (5.5) |
| Soru Soru no Mi | 3 | Big Mom as a 5th Yonko (6.3) |
| Uo Uo no Mi, Model: Seiryu | 3 | Kaido's dragon form (6.3) |
| Hobi Hobi no Mi | 2 | Sugar; turns NPCs into toys (strong PvE identity) |
| Gasha Gasha no Mi | 2 | builder fruit, fits structures |
| Mega Mega no Mi | 1 | restore (removed by MMnM) |

## 7.4 PvP balance pass (M)
- Only with the friend server running PvP. Gather 3 sessions of PvP feedback, then tune: conqueror's clash numbers (3.6), awakening buffs (6.4), Renown HP bonus (6.1), and the fairness caps if they're ever applied to PvP (3.1 is PvE-only by default).
- Record every change and why in `docs/plan/balance-log.md`.
