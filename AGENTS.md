# AGENTS.md — instructions for AI coding agents

You're implementing **MallowPiece** (display name **MMnM+**), a Forge 1.20.1 addon for the Mine Mine no Mi mod (MMnM). The owner is one player building this for themselves and a few friends. They aren't a programmer, and they test in single-player. Work as autonomously as possible. When a choice isn't specified, make the conservative one, write it down in the task's "Decisions made" section, and keep going.

## Read first
1. `docs/plan/README.md`: the phase order, the task list and the global rules.
2. `docs/plan/mmnm-api-notes.md`: verified facts about MMnM internals (class names, events, data paths). **Don't guess at MMnM APIs.** If something isn't in the notes, read the decompiled reference (below) and add what you learn to the notes.
3. The phase file for the task you're on (`docs/plan/phase-N-*.md`). Every task there has: Goal, Design, Implementation, Config, Acceptance tests.
4. `docs/01-mod-audit.md` and `docs/02-weak-points.md` for the why.

## Reading MMnM's code
```bash
tools/setup-reference.sh 1.20.1-0.11.6
```
This decompiles MMnM into `.reference/1.20.1-0.11.6/src` (code) and `.reference/1.20.1-0.11.6/jar` (data, assets). It's git-ignored.
- **The decompiled code uses SRG names** (`m_21204_`, `f_19796_`). Our project uses official Mojang mappings. Translate them (IDE or `build/createSrgToMcp/output.srg`); never paste SRG names into our code.

## Hard rules
- **Never commit MMnM's code, textures, models, sounds or structure files**, decompiled or otherwise. The MMnM license allows private modification but forbids redistributing its assets. Anything derived from MMnM assets (e.g. recoloured textures) is generated at build time from the local reference jar into a git-ignored folder (see Phase 0, task 0.4).
- **Never modify MMnM's jar.** Change behaviour through: Forge events, MMnM's own events (`DorikiEvent`, `HakiExpEvent`, `HakiKnockoutEvent`, …), `LootTableLoadEvent`, our own registries, our own data, and Mixins only as a last resort (each Mixin needs a comment explaining why no event works).
- **Every feature has a config toggle** in `mallowpiece-server.toml` (or `-client.toml` for visual-only things), and defaults to the value given in the plan.
- **Compatibility target:** MMnM `1.20.1-0.11.6`, Forge 47.3+ (use 47.4.x), Java 17, official mappings.
- **Mod id:** `mallowpiece`. Package: `dev.mallow.mallowpiece`. Display name: `MMnM+`. The MMnM license forbids renaming *their* mod; ours is a separate addon, so this is fine.
- No new dependencies besides Forge and MMnM without writing down why in the task. (Curios, Cloth Config and GeckoLib are fine *if* a task needs them; prefer not to.)
- Keep MMnM-facing code in an `integration/mmnm/` package, so an MMnM update breaks one place.

## How to work a task
1. Pick the lowest-numbered task whose dependencies are done (status table in `docs/plan/README.md`).
2. Read its spec and the API notes. Spike anything marked **Spike first** before building the rest.
3. Implement. Small commits, messages like `P1.1: smooth doriki curve via DorikiEvent.Pre`.
4. Run `./gradlew build`. It must pass.
5. Run the task's **Acceptance tests** in a dev client (`./gradlew runClient`, single-player world with cheats). Write what you ran and saw in `docs/plan/TESTLOG.md` (date, task, steps, result).
6. Update the task's status in `docs/plan/README.md` and fill in its "Decisions made" section if you made any.
7. If a spec is wrong (the API doesn't exist, the numbers feel bad in testing), fix the spec in the same commit and explain the change in the commit message.

## Testing setup
- `./gradlew runClient` with MMnM on the dev classpath (Phase 0 sets this up).
- Test world: creative/cheats single-player, Hard difficulty, seed from `docs/plan/phase-0-foundation.md`.
- Useful commands: see "Commands for testing" in `docs/plan/mmnm-api-notes.md`. Our own debug commands live under `/mallowpiece debug ...` (op only).
- Balance numbers come from `tools/sim/progression.py`. If you change a curve, re-run the sim and update the numbers in the plan.

## Style
- Java 17, 4-space indent, no wildcard imports, `final` where it helps.
- One feature per package under `dev.mallow.mallowpiece.feature.<name>` (e.g. `feature.progression`, `feature.loot`, `feature.theft`).
- Server logic stays server-side; check `level.isClientSide()`.
- Player state we own goes in one capability `MallowPlayerData` (NBT-persisted, copied on death/clone, synced to the client only when the UI needs it).
- World state we own goes in one `SavedData`: `MallowWorldData`.
- Text the player sees goes in `assets/mallowpiece/lang/en_us.json`. No hard-coded strings.
