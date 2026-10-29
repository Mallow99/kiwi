# Phase 0 — Foundation

**Milestone:** the game launches with MMnM and MallowPiece, and `/mallowpiece debug info` prints our state.

---

## 0.1 Gradle project + MMnM dependency (S)
**Goal:** a buildable Forge 1.20.1 mod at the repo root that runs with MMnM in dev.

**Implementation**
- Start from the Forge 1.20.1 MDK (47.4.x). Java 17 toolchain, official mappings.
- `gradle.properties`: `mod_id=mallowpiece`, `mod_name=MMnM+`, `mod_group_id=dev.mallow.mallowpiece`, `mod_version=0.1.0`.
- MMnM dependency, following MMnM's own addon guide (`pixelatedw.xyz/mine-mine-no-mi/docs/addons/setup.html`):
  ```gradle
  repositories {
      maven { url = "https://api.modrinth.com/maven"; content { includeGroup "maven.modrinth" } }
  }
  dependencies {
      implementation fg.deobf("maven.modrinth:mine-mine-no-mi:1.20.1-0.11.6")
  }
  ```
  In `minecraft { runs { configureEach { ... } } }` add:
  ```gradle
  property 'mixin.env.remapRefMap', 'true'
  property 'mixin.env.refMapRemappingFile', "${projectDir}/build/createSrgToMcp/output.srg"
  ```
  Without these, MMnM's mixins crash on launch.
- `mods.toml`: depend on `mineminenomi`, `mandatory=true`, `versionRange="[0.11.6,0.12)"`, `ordering="AFTER"`, `side="BOTH"`.
- `.gitignore`: add `build/`, `run/`, `.gradle/`, `src/generated/derived/`.

**Acceptance**
- `./gradlew build` succeeds.
- `./gradlew runClient` launches; the mods list shows Mine Mine no Mi 0.11.6 and MMnM+ 0.1.0; you can create a world and open MMnM's character creator.

## 0.2 Config, player capability, world data, debug command (S)
**Goal:** the shared plumbing every later task uses.

**Implementation**
- `MallowConfig`: `ForgeConfigSpec` server config `mallowpiece-server.toml`, client config `mallowpiece-client.toml`. One section per feature, e.g. `[progression]`, `[loot]`, `[theft]`. Each later task lists its keys.
- `MallowPlayerData` capability on players: NBT-serialised; copied in `PlayerEvent.Clone` (including on death); synced to the client with a `SyncMallowPlayerDataPacket` when a UI needs it. Fields get added per task (gate progress, pity counters, theft timer, renown, …).
- `MallowWorldData extends SavedData` (`mallowpiece` in the overworld data storage): boss respawn timers, world events, conqueror's count, etc.
- Network channel `mallowpiece:main` (`SimpleChannel`, protocol "1").
- Command `/mallowpiece` (op level 2) with `debug info [player]`, which prints doriki, haki, gate state, pity counters and theft timer. Each task adds its own debug subcommands.

**Acceptance:** `/mallowpiece debug info` prints a block of values; the values survive relog and death.

## 0.3 Recommended MMnM config + startup check (XS)
**Goal:** our features assume certain MMnM settings. Ship them, and warn if they're wrong.

**Implementation**
- `docs/recommended-mmnm-config.md` lists the MMnM settings to use with MallowPiece:
  - `Haoshoku Haki Unlock Logic = NONE` (we grant it by quest, task 2.6)
  - `Enable Awakenings = true` (we gate it, task 6.4)
  - `Open World Fruit Users Chance = 10` (some captains/notorious use fruits)
  - Leave `Doriki Limit = 10000` and `Haki Exp Limit = 100` (our curves assume them).
- On `ServerStartedEvent`, read MMnM's values (`ServerConfig.getHaoshokuUnlockLogic()`, `ServerConfig.hasAwakeningsEnabled()`, …). For each mismatch, log a warning and send ops a chat message when they join: `[MMnM+] Conqueror's Haki is still unlocked randomly by MMnM. Set "Haoshoku Haki Unlock Logic" to NONE in mine-mine-no-mi config.`
- Don't change their config from code.

**Acceptance:** with default MMnM config, joining as an op shows the warning; after fixing the config it's gone.

## 0.4 Build-time asset derivation (S)
**Goal:** some of our textures are recolours of MMnM's (e.g. Revolutionary NPC skins from marine grunt skins). We may not commit MMnM-derived files, so we generate them on build from the local reference jar.

**Implementation**
- `tools/derive/derive_assets.py` (Python 3, Pillow allowed) reads `.reference/<version>/jar/assets/mineminenomi/...` and writes into `src/generated/derived/resources/assets/mallowpiece/...` (git-ignored). Recipes live in `tools/derive/recipes.json`, e.g. `{ "out": "textures/entity/rev/grunt_1.png", "from": "textures/entity/npc/marine_grunt_1.png", "ops": [["hue_shift", 140], ["replace_color", "#1f3a8a", "#2e2e2e"]] }`. Look up the real source paths in the reference jar.
- Gradle: add `src/generated/derived/resources` to `sourceSets.main.resources`. Add a `deriveAssets` Exec task that `processResources` depends on, and skip it with a warning if `.reference` is missing.
- Original textures we draw ourselves (not derived) go in `src/main/resources` and **are** committed.

**Acceptance:** fresh clone → `tools/setup-reference.sh` → `./gradlew build` → the jar contains the derived textures; `git status` shows no derived files.

## 0.5 Test world + TESTLOG (XS)
- Create `docs/plan/TESTLOG.md` with a header and table: Date | Task | Steps | Result | Notes.
- Pick a test seed where `/locate structure mineminenomi:marine/large_base`, `.../pirate/large_ship` and `.../bandit/fort` are all within 2,000 blocks of spawn. Record the seed and coordinates in TESTLOG.
- Settings: Hard, cheats on, `Enable Debug Commands = true` in MMnM config.
