# MallowPiece (MMnM+) — Implementation Plan

**What we're making:** a Forge 1.20.1 addon for Mine Mine no Mi 0.11.6 that gives the mod a gameplay loop worth replaying. That means progression you *do*, places worth going, fruits you can work toward, fights that are fair and readable, and an endgame after 10,000 doriki.

**Who it's for:** the owner and a few friends on a private server. It's tested in single-player first.

**How it's built:** an AI agent following `AGENTS.md`, one task at a time, with the owner playtesting at each milestone.

---

## Design pillars (tie-breakers when a task is ambiguous)
1. **Every hour should have a goal.** If the player's only goal is "make a number go up," something is missing.
2. **Fair and readable fights.** You lose because you misplayed, not because an effect filled the screen or a stat check one-shot you.
3. **Variety over volume.** A new kind of place beats more of the same place.
4. **Earned, not rolled.** RNG adds excitement on top of progress; it never replaces it (pity timers, quests for rare powers).
5. **Toggleable.** Every feature can be turned off in config, so a broken feature never blocks a play session.

## The core loop we're building toward
```
Early (0–4k)     Raid camps, small ships, small bases → wooden/iron boxes → first fruit → train a fighting style
Mid (4k–8k)      Strongholds of the enemy factions → captains, elites, bosses in the world → iron/golden boxes, haki
Late (8k–10k)    Grand Line trials, Supernova boss ships, elites → golden boxes, conqueror's trial
Endgame (10k+)   Renown ranks, Yonko fleets, bounty contracts, awakenings, crew territory/PvP
```
Every 2,000 doriki there's a **breakthrough trial**, and one of these activities is the way through it.

## Phases and tasks

Status: ⬜ not started · 🟨 in progress · ✅ done · ⏸ blocked

| Phase | File | Tasks | Milestone the owner tests |
|---|---|---|---|
| 0 | [phase-0-foundation.md](phase-0-foundation.md) | 0.1–0.5 | Game launches with MMnM + MallowPiece; `/mallowpiece debug info` works |
| 1 | [phase-1-fix-the-loop.md](phase-1-fix-the-loop.md) | 1.1–1.8 | New doriki/haki curve feels right; ships and bosses worth raiding; stealing from marines gets you hunted |
| 2 | [phase-2-progression.md](phase-2-progression.md) | 2.1–2.6 | Breakthrough trials at 2k/4k/6k/8k/10k; trainers easy to find and working; conqueror's earned by quest |
| 3 | [phase-3-combat.md](phase-3-combat.md) | 3.1–3.6 | Boss fights readable and fair; no one-shots; conqueror's is a clash, not an instant win |
| 4 | [phase-4-strongholds.md](phase-4-strongholds.md) | 4.1–4.7 | Revolutionary NPCs, Pirate Den, Revolutionary Hideout generate in the world |
| 5 | [phase-5-world-bosses.md](phase-5-world-bosses.md) | 5.1–5.6 | Wanted posters lead to boss arenas; Supernova ships roam the sea |
| 6 | [phase-6-endgame.md](phase-6-endgame.md) | 6.1–6.7 | Post-10k: Renown, Yonko fleets, contracts, awakenings, territory |
| 7 | [phase-7-fruits.md](phase-7-fruits.md) | 7.1–7.4 | New fruits added one at a time |

### Task status
| ID | Task | Depends on | Size | Status |
|---|---|---|---|---|
| 0.1 | Gradle project + MMnM dependency | — | S | ⬜ |
| 0.2 | Config, player capability, world data, debug command | 0.1 | S | ⬜ |
| 0.3 | Recommended MMnM server config + startup check | 0.2 | XS | ⬜ |
| 0.4 | Build-time asset derivation pipeline | 0.1 | S | ⬜ |
| 0.5 | Test world + TESTLOG | 0.1 | XS | ⬜ |
| 1.1 | Doriki curve | 0.2 | S | ⬜ |
| 1.2 | Haki curve | 0.2 | S | ⬜ |
| 1.3 | Structure loot tiers (ships/bandits worth raiding) | 0.2 | M | ⬜ |
| 1.4 | Boss rewards include boxes | 1.3 | XS | ⬜ |
| 1.5 | Box pity + empty-box fix | 0.2 | S | ⬜ |
| 1.6 | Marine rank-locked chests + theft punishment | 0.2 | M | ⬜ |
| 1.7 | Death tax preset + challenge doriki scaling | 1.1 | XS | ⬜ |
| 1.8 | Sea safety for fruit users (Bubbly Coral access) | 1.3 | XS | ⬜ |
| 2.1 | Breakthrough gates (engine) | 1.1 | M | ⬜ |
| 2.2 | Log Book (UI for trials) | 2.1 | M | ⬜ |
| 2.3 | Breakthrough trial content (2k–10k) | 2.1, 2.2 | M | ⬜ |
| 2.4 | Elite NPCs (6.5k–9k band) | 0.2 | M | ⬜ |
| 2.5 | Trainers you can find and use | 0.2 | M | ⬜ |
| 2.6 | Conqueror's Haki: earned by quest | 2.1, 2.2 | M | ⬜ |
| 3.1 | Damage fairness: no one-shots | 0.2 | S | ⬜ |
| 3.2 | Telegraphed boss abilities | 3.1 | L | ⬜ |
| 3.3 | Visual clarity (particle density) | 0.2 | M | ⬜ |
| 3.4 | Challenge boss tuning pass | 3.1, 3.2 | M | ⬜ |
| 3.5 | NPC fruit AI for boss-tier fruits | 0.2 | L | ⬜ |
| 3.6 | Conqueror's Haki clash rework | 2.6 | M | ⬜ |
| 4.1 | Structure generator (tools/structgen) | 0.1 | L | ⬜ |
| 4.2 | Revolutionary NPC set | 0.4 | M | ⬜ |
| 4.3 | Pirate sniper | 0.4 | XS | ⬜ |
| 4.4 | Pirate Den | 4.1 | L | ⬜ |
| 4.5 | Revolutionary Hideout | 4.1, 4.2 | L | ⬜ |
| 4.6 | Faction fairness: enemy strongholds per faction | 4.4, 4.5 | S | ⬜ |
| 4.7 | Structure spawn tuning + /locate tags | 4.4, 4.5 | XS | ⬜ |
| 5.1 | Boss framework (phases, telegraphs, arenas) | 3.2 | L | ⬜ |
| 5.2 | Overworld boss arenas (existing 18 bosses) | 4.1, 5.1 | L | ⬜ |
| 5.3 | Wanted posters → treasure maps | 5.2 | M | ⬜ |
| 5.4 | Boss respawn timers + loot | 5.2 | S | ⬜ |
| 5.5 | Supernova boss ships | 3.5, 4.1, 5.1 | L | ⬜ |
| 5.6 | Marine/rev boss equivalents (Vice Admiral fleet, WG convoy) | 5.5 | M | ⬜ |
| 6.1 | Renown (post-10k progression) | 2.1 | M | ⬜ |
| 6.2 | Bounty board contracts | 6.1 | M | ⬜ |
| 6.3 | Yonko fleets (endgame world event) | 5.5 | L | ⬜ |
| 6.4 | Awakenings | 6.1 | L | ⬜ |
| 6.5 | Player bounties + hunter contracts (PvP) | 6.1 | M | ⬜ |
| 6.6 | Crew territory (PvP) | 6.1 | L | ⬜ |
| 6.7 | Haki mastery (post-cap haki sink) | 6.1 | S | ⬜ |
| 7.1 | Fruit pipeline + first new fruit | 3.5 | L | ⬜ |
| 7.2 | Restore Mane Mane no Mi | 7.1 | L | ⬜ |
| 7.3 | Further fruits (owner picks) | 7.1 | L each | ⬜ |
| 7.4 | PvP balance pass | 6.5 | M | ⬜ |

Sizes: XS ≈ an hour · S ≈ a session · M ≈ a few sessions · L ≈ a week of sessions.

## Decisions already made by the owner
- Name: **MallowPiece** (mod id `mallowpiece`), display **MMnM+**.
- Time to max: owner didn't set one. **Default chosen: ~20 h of active play to 10,000 doriki, ~12–17 h of fighting to 100 haki** (see `tools/sim/progression.py`).
- Breakthrough gates: **on by default, every 2,000 doriki** (2k, 4k, 6k, 8k, and 10k unlocks the endgame).
- Marine fairness: **rank-locked chests; stealing still works but gets you in trouble.**
- Testing: single-player.
- Builders: none. **All structures are generated by code** (`tools/structgen`), and a human may polish them later.

## Open questions for the owner (the agent proceeds with the stated default)
| Question | Default used |
|---|---|
| Conqueror's Haki: unlimited, or a per-world limit? | Unlimited, but the quest is hard (task 2.6) |
| PvP features on by default? | Off by default (6.5, 6.6); turn on for the friend server |
| Canon names (Kid, Law, Kaido…) or original characters for Supernovas/Yonko? | Canon names (private server) behind a config switch for original names |
