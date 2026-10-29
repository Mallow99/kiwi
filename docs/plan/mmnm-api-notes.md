# MMnM API Notes (verified against 1.20.1-0.11.6)

Everything here was read from the decompiled 0.11.6 jar (`tools/setup-reference.sh`). Paths are relative to `.reference/1.20.1-0.11.6/src/xyz/pixelatedw/mineminenomi/`.

**Mappings warning.** The decompiled source shows SRG names (`m_21204_`, `f_19796_`, …). In the dev environment, MMnM is pulled with `fg.deobf(...)` and our project uses official (Mojang) mappings, so in our code you write `getAttributes()`, `random`, etc. When you read a SRG name in the reference, look up its Mojang name in your IDE, or in the `build/createSrgToMcp/output.srg` file ForgeGradle generates. Never paste SRG names into our code.

If anything below disagrees with the code you're compiling against, the code wins. Update this file.

---

## Stats (doriki, belly, bounty, loyalty)
- Capability: `data/entity/stats/EntityStatsCapability.get(entity)` → `LazyOptional<IEntityStats>`.
- `IEntityStats`: `getDoriki()`, `alterDoriki(double, StatChangeSource)`, `setDoriki`, `getLoyalty()`, `alterLoyalty(double, StatChangeSource)`, `getFaction()` → `Optional<Faction>`, `isMarine()`, `isPirate()`*, `isRevolutionary()`, `isBountyHunter()`, `isWorldGovernment()`, `isCivilian()`, `isRogue()` / `setRogue(boolean)`, `getBounty()` / `alterBounty`, `getBelly()` / `alterBelly`. (*check the exact name for pirate.)
- Sync to the client after any change: `ModNetwork.sendTo(new SSyncEntityStatsPacket(player), player)`.
- **`alterDoriki` posts `api/events/stats/DorikiEvent.Pre` (cancelable, `setDoriki(amount)`) before applying, and `DorikiEvent.Post` after.** Clamped to `ServerConfig.getDorikiLimit()` (default 10,000).
- `api/enums/StatChangeSource`: `NATURAL, KILL_NPC, KILL_PLAYER, QUEST, CHALLENGE, COMMAND, DEATH, STORE`.
- Haki: `data/entity/haki/HakiDataBase` posts `HakiExpEvent.Pre/Post` (has `HakiType`: KENBUNSHOKU / BUSOSHOKU / …) the same way. Capability: `HakiCapability.get(entity)` → `IHakiData` (`getBusoshokuHakiExp`, `alterBusoshokuHakiExp`, `getKenbunshokuHakiExp`, …).

## How kill rewards work today
`handlers/entity/StatsGainHandler.giveStats(target, source)` runs on death:
- Skipped in the challenge dimension, and for targets whose loot table has a `mineminenomi:stats` pool.
- Non-player target: `plus = targetDoriki / 100`, but if the player's doriki is above the target's, `targetDoriki / 10000`. Notorious targets pay at least 100. Multiplied by `ServerConfig.getDorikiRewardMultiplier()`.
- Marines get nothing for killing marines; revolutionaries nothing for revolutionaries.
- Calls `props.alterDoriki(plus, StatChangeSource.KILL_NPC)`, so **our `DorikiEvent.Pre` handler sees every kill reward with source `KILL_NPC`**.
- Vanilla and modded mobs get spawn doriki in `StatsGainHandler.setSpawnStats` from HP and attack (cap 10,000 × 0.8).

## NPC doriki at spawn (Hard adds +500 to min and max; New World adds +250 to min)
Grunt 500–2,000 · Sniper 3,000–4,500 · Brute 3,500–5,000 · Captain 4,000–6,000 · Pacifista 2,000–4,000 · Challenge bosses 1,000–2,000 (standard) / 10,000 (hard). Method: `OPEntity.getRandomDorikiBonus(min, max)`.

## Factions
- Registry: `init/ModFactions` → `PIRATE, MARINE, BOUNTY_HUNTER, REVOLUTIONARY_ARMY, BANDIT, WORLD_GOVERNMENT, CIVILIAN` (`RegistryObject<Faction>`).
- `api/entities/charactercreator/Faction.canHurt(attacker, target)` ANDs every check added with `addCanHurtCheck`. You can only *add restrictions* this way.
- `MARINE_HURT_CHECK`: marine-aligned (marine, bounty hunter, WG) can't hurt marine-aligned.
- **Rogue override:** `api/helpers/FactionHelper` lets an NPC attack a target that `isRogue()`, regardless of faction. Players toggle it with `/gorogue`. **We use `setRogue(true)` as the punishment state for theft.**
- Marine ranks: `api/factions/MarineRank`, by loyalty: CHORE_BOY 0, SEAMAN 5, PETTY_OFFICER 10, LIEUTENANT 15, COMMANDER 20, CAPTAIN 25, COMMODORE 40, VICE_ADMIRAL 50, ADMIRAL 70, FLEET_ADMIRAL 100. Rank is `props.getLoyalty() >= rank.getRequiredLoyalty()`. Revolutionaries use `RevolutionaryRank` (same pattern).

## NPCs
- Base class: `entities/mobs/OPEntity`. Faction NPCs: `GruntEntity`, `BruteEntity`, `SniperEntity`, `CaptainEntity`, `NotoriousEntity`, `PacifistaEntity`, `TraderEntity`, `TrainerEntity`.
- **The faction is injected, not hard-coded:** `GruntEntity.createMarineGrunt(type, level)` does `new GruntEntity(type, level)` then `setFactionInit(GruntEntity::initMarine)`. `OPEntity.setFactionInit(IMobDetails<OPEntity>)` is public. So a Revolutionary grunt is a new `EntityType` whose factory calls `setFactionInit(e -> { e.getEntityStats().setFaction(ModFactions.REVOLUTIONARY_ARMY.get()); e.setTextures(REV_GRUNT_TEXTURES); })`.
- Attributes: `GruntEntity.createAttributes()` (and the same for each class), registered in `EntityAttributeCreationEvent` (see `init/ModMobs` ~line 441).
- Renderer: `renderers/.../OPHumanoidRenderer.Factory(ctx)` (see `init/ModMobs` ~line 594). Reuse it for our humanoid NPCs.
- Textures: `OPEntity.setTextures(ResourceLocation[])` plus `chooseTexture()`. Texture arrays live in `api/helpers/MobsHelper` (`MARINE_CAPTAINS_TEXTURES`, …). Skins use the 64×64 player-skin layout.
- **Giving an NPC a devil fruit:** `MobsHelper.getDevilFruitAbilities(AkumaNoMiItem fruit, Mob mob)` → pair of (fruit, `List<AbilityWrapperGoal>`). Then `DevilFruitCapability.get(mob).ifPresent(p -> p.setDevilFruit(fruit))` and add each goal to `goalSelector` at priority 2 (see `CaptainEntity.finalizeSpawn`). **Only abilities whose `AbilityCore.hasGoalWrapper()` is true produce goals.** In 0.11.6 that's only Mera, Moku, Ushi (Bison), Ushi (Giraffe), Sai, Neko (Leopard), Mogu, Kilo, Bomu, Awa, Suke, Goe.
- **Generic NPC ability goals** you can construct for *any* `AbilityCore`: `entities/ai/goals/abilities/` → `ProjectileAbilityWrapperGoal`, `CloseMeleeAbilityWrapperGoal`, `AreaAbilityWrapperGoal` (`setMinDistance/setMaxDistance/setMinTargetsRequired`), `DashAbilityWrapperGoal`, `GrabAbilityWrapperGoal`, `ActiveBuffAbilityWrapperGoal`, `ActiveGuardAbilityWrapperGoal`, `ReactiveGuardAbilityWrapperGoal`, `AntiProjectileAbilityWrapperGoal`, `AntiAirAbilityWrapperGoal`, `JumpAbilityWrapperGoal`, `MorphAbilityWrapperGoal`, `RepeaterAbilityWrapperGoal`, `AlwaysActiveAbilityWrapperGoal`, `HakiAbilityWrapperGoal`. Base: `api/entities/ai/AbilityWrapperGoal<E extends Mob, A extends IAbility>` (constructor `(E entity, AbilityCore<A> core)`; abstract `canUseWrapper/startWrapper/tickWrapper/stopWrapper/canContinueToUseWrapper`).
- Boss AI example: `entities/mobs/pirates/kriegpirates/DonKriegEntity` uses phase goals (`DonKriegPhaseSwitcherGoal`, `MH5PhaseGoal`) plus ability wrapper goals.

## Devil fruits & boxes
- Fruits: `init/ModFruits` (`RegistryObject<AkumaNoMiItem>`), `new AkumaNoMiItem(tier, FruitType, abilities...)`. Tiers 1–3 match the wooden/iron/golden boxes. Mochi only registers on April 1.
- Box item: `items/AkumaNoMiBoxItem`. It needs a `mineminenomi:key` in the inventory, consumes key and box, rolls `dfboxes/{wooden,iron,golden}_box` loot tables, and gives the **first available** fruit (one-fruit-per-world aware). **If no fruit rolled, it adds `ItemStack.EMPTY`, so the box and key are lost** (the 95% fruit pool can fail; possible bug).
- Loot condition `mineminenomi:random_chance_with_luck` (`chance`, `luckBonus` per luck point). Function `mineminenomi:fruit_already_exists`.
- Awakening: `data/entity/devilfruit/DevilFruitBase.hasAwakenedFruit()/setAwakenedFruit(boolean)`, which only works when config `Enable Awakenings` is true. Only Gomu's abilities check it.

## Loot tables (data paths under `data/mineminenomi/loot_tables/`)
- Box sources: `chests/marine/large_base/captain`, `chests/marine/small_base/captain`, `chests/marine/battleship/treasure`, `chests/pirate/large_ship/treasure`, `chests/pirate/medium_ship/captain`, `chests/bandit/fort/secret_stash`, `chests/caravan/{easy,hard}`, `chests/ghost_ship/captain`. Vanilla overrides live in `vanilla/chests/...`.
- Other chests: `chests/pirate/small_ship/supplies`, `chests/marine/watch_tower/tower`, `chests/bandit/camp/*`, `chests/bandit/cave/*`, …
- Boss rewards: `rewards/<boss>.json` and `rewards/<boss>_hard.json`. **None contain boxes.**
- Keys drop from `entities/{marine_captain,pirate_captain,bandit_leader}` and a few vanilla chests.
- **How we change them:** Forge `LootTableLoadEvent` (fires for every table, including other mods'). Add or replace pools there. Don't ship same-path JSON overrides; datapack load order between mods isn't reliable.

## Structures
- Worldgen: `data/mineminenomi/worldgen/structure/<group>/<name>.json` (all `minecraft:jigsaw`), structure sets in `worldgen/structure_set/`, pools in `worldgen/template_pool/`, templates in `structures/`.
- IDs: `mineminenomi:marine/{small_base,large_base,watch_tower,battleship}`, `mineminenomi:pirate/{small_ship,medium_ship,large_ship}`, `mineminenomi:bandit/{camp,house,fort,arena}`, `mineminenomi:unaligned/{tavern,ghost_ship,swordsman_dojo,...}`, `mineminenomi:sky_islands/{single,town}`.
- **NPC spawns inside templates:** a 2×1×1 "mob" template holds a `minecraft:jigsaw` (`name`/`target` = `mineminenomi:mob`, `pool` = `minecraft:empty`, joint `rollable`) next to a `mineminenomi:custom_spawner` block entity with NBT `{entityToSpawn: "<entity id>", spawnLimit: N, playerDistance: 100, spawns: []}`. Building templates put a jigsaw pointing at a pool of these mob templates (e.g. `mineminenomi:marine/mobs/captain`). **Our structures can point `entityToSpawn` at our own entity ids.**
- Checking "is this position inside structure X": `serverLevel.structureManager().getStructureWithPieceAt(pos, structureOrTag).isValid()`. Use a structure tag in our data (`data/mallowpiece/tags/worldgen/structure/*.json`).
- Bandit caves (`structures/bandit/small_base/cave_{1,2,3}.nbt`, 36×~21×37) hang underground off the bandit house/arena via jigsaw. They're the template for "underground stronghold."

## Challenges
- `api/challenges/Challenge`, `ChallengeCore`, registry `WyRegistry.CHALLENGES`; definitions in `challenges/<group>/*Challenge.java` (arena, enemy spawns, time limit, `setRewardsFactor`, `setRewards(lootTable)`).
- Rewards: pool per difficulty from config (`Doriki Reward Pool` [1000, 4000, 0], `Belly` [5000, 15000, 0], `Haki` [10, 40, 0]), split by reward factor; repeats divided by `1.5 × completions` (max 10). Doriki is paid via `alterDoriki(..., StatChangeSource.CHALLENGE)`, **which is how we detect a challenge completion** without mixins.
- Unlocks: `items/ChallengePosterItem` (NBT `challengeId`) → `ChallengeCapability.get(player).addChallenge(core)`.
- The order list reserves unbuilt bosses: Mohji & Richie, Hatchan, Mr. 2, Mr. 4 & Miss Merry Christmas, Miss Doublefinger.

## World events
- `data/world/EventsWorldData` (SavedData `mineminenomi-events`): notorious targets, caravans, celestial visits, `addSpecialBusterCall(level, target)`. POIs: `api/poi/POIEventTarget` (position, open time, trigger within 100 blocks), `NTEventTarget`, `TrackedNPC`.
- Wanted posters: block `ModBlocks.WANTED_POSTER`, item `WantedPosterItem`, `WantedPosterPackageItem`/`Entity` (airdropped packages).
- Flags: `items/FlagItem`, `api/events/FlagPlacedEvent`, `FlagDestroyedEvent` (used for crew territory in Phase 6).

## Haki: Conqueror's (Haoshoku)
- Config `Haoshoku Haki Unlock Logic` (`ServerConfig.HaoshokuUnlockLogic`): `NONE, RANDOM, EXPERIENCE, COMBINED (default), TRUE_RANDOM`.
- `abilities/haki/HakiHelper.isHaoshokuBorn(player)`: sums the digits of the UUID's most-significant bits, then `Mth.clamp(sum & 10, 0, 10)`. RANDOM/COMBINED grant it when that's ≤ 1, i.e. 0. Because it's a **bitwise AND** (almost certainly meant to be `% 10`), the result is 0 whenever bits 1 and 3 of the digit sum are 0, which is roughly **1 in 4 players**. It's tied to the UUID, so it's the same on every server. TRUE_RANDOM compares the same value to one derived from the world seed.
- EXPERIENCE path (`HaoshokuHakiAbility.canUnlock`): total haki exp ≥ 80% of max and ≥ 2 other haki abilities unlocked.
- Knockout (`HaoshokuHakiAbility.knockoutNearbyEnemies`): for each enemy in radius, if `targetTotalHaki/100 + 0.5 < userTotalHaki/100` → `ModEffects.UNCONSCIOUS` (with mastery) or Slowness. Posts **`HakiKnockoutEvent.Pre` (cancelable)** before applying, which is our hook for 3.6.
- Other haki thresholds are also UUID-seeded per player: `getBusoshokuHardeningExpNeeded` 28–55, full body 50–70, emission 70–80, internal destruction 80–95, kenbunshoku aura 25–50.

## Trainers
- `entities/mobs/TrainerEntity` (abstract) plus `civilians/{Swordsman,Sniper,Doctor,BrawlerTrainer,BlackLeg,ArtOfWeather}TrainerEntity`.
- Despawn: `removeWhenFarAway` returns false only if spawned by a spawner and within 200 blocks; nametagged ones despawn unless config `Despawn NPCs with Nametags` is false.
- Interaction: `mobInteract` main hand only; server sends `SOpenTrainerDialogueScreenPacket` and **returns `InteractionResult.PASS`** (client returns PASS too), which is a candidate cause of unreliable dialogue buttons. Screens: `ui/screens/TrainerTrialsListScreen`, packets `packets/client/entity/interaction/CTrainerResetTreePacket`.
- Random spawns: `world/spawners/TrainerSpawner`, config `Time Between Trainer Spawns` 2 min, `Chance for Trainer Spawns` 15%.
- Trainer buildings (always have a trainer via `custom_spawner`): `mineminenomi:unaligned/{swordsman_dojo,medic_tent,brawler_ring,black_leg_kitchen,sniper_range}`; Art of Weather trainer in `sky_islands/town`.

## Entity ids (verified in lang file)
Bosses: `mineminenomi:{alvida,morgan,buggy,cabaji,higuma,kuro,jango,sham,buchi,don_krieg,gin,pearl,arlong,kuroobi,chew,mr_5,miss_valentine,mr_3,mr_1,mr_0}`. Others: `marine_vice_admiral`, `pirate_notorious_captain`, `celestial_dragon`, `marine_{grunt,brute,sniper,captain,trader}`, `pirate_{grunt,brute,captain,trader}`, `bandit_{grunt,brute,sniper,leader}`, `pacifista`. Boss classes have a normal `(EntityType, Level)` constructor plus a challenge constructor; check that their AI works outside a challenge (5.1 spike).

## Faction hostility quick table
- Pirate NPCs vs pirate players: **hostile unless same crew** (pirate hurt check compares crews).
- Marine-aligned NPCs vs marine-aligned players: never (unless rogue).
- Revolutionary NPCs vs revolutionary players and civilians: never (unless rogue).
- Anyone vs a rogue target: allowed.

## Useful events (`api/events/...`)
`stats/DorikiEvent`, `stats/HakiExpEvent`, `stats/BountyEvent`, `stats/LoyaltyEvent`, `entity/IssueBountyEvent`, `entity/CrewEvent`, `entity/EntityCarryEvent`, `entity/WyLivingHurtEvent`/`WyLivingDamageEvent`, `ability/AbilityUseEvent`, `ability/AbilityCanUseEvent`, `ability/UnlockAbilityEvent`, `onefruit/EatDevilFruitEvent`, `FlagPlacedEvent`, `FlagDestroyedEvent`.

## Commands for testing (single-player, cheats on)
`/doriki <amount> [targets]` (adds, source COMMAND) · `/hakiexp <type> <amount> [targets]` · `/loyalty <amount> [targets]` · `/bounty ...` · `/change_character faction|race|style <target> <value>` · `/gorogue` · `/removedf` · `/events notorious_target|caravan|celestial_dragon|ambush ...` · `/challenge ...` · `/check_fruits` · `/fg ...` (debug; needs config `Enable Debug Commands`). Plus vanilla `/locate structure mineminenomi:marine/large_base`, `/place structure ...`, `/loot give @s loot <table>`.

## Base-mod config worth knowing (file: `mine-mine-no-mi-server.toml` / common)
`Doriki Limit` 10000 · `Haki Exp Limit` 100 · `Doriki Reward Multiplier` 1.0 · `Haki Exp Multiplier` 1.0 · `Percentage of Doriki kept after death` 77 (same for bounty/belly/haki) · `Enable Awakenings` false · `Open World Fruit Users Chance` 0 · `Ability Bars` 4 · `One Fruit per World` · `Doriki/Belly/Haki Reward Pool` (challenges).
