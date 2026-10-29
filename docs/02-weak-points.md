# 02 — Weak Points

Each weak point lists what players feel, what the code shows (see `01-mod-audit.md`), and why it matters. They're ranked by how much they hurt the core loop.

The core loop today:

> **Spawn → raid the same few structures for boxes → hope for a good fruit → grind doriki and haki on mobs until bored → (on servers) PvP.**

Almost every step has a problem.

---

## W1. Late progression is a desert (doriki and haki)
**Feels like:** grinding endermen for hours; "grinding XP for 2949392994 years."
**Code says:**
- A 100× drop in doriki the moment you out-doriki a target.
- The strongest repeatable open-world NPC is about 6,500 doriki, against a 10,000 cap. The last ~35% of progression has almost no repeatable source.
- Enderman farm to max: about 37,000–52,000 kills *(sim)*.
- Haki gain slows as you approach the cap, and weak mobs get a further 5× penalty, so the last 10 points take thousands of hits.
- Dying costs 23% of everything by default, which stacks on top of all this.

**Why it matters:** this is the part of the game players spend the most hours in, and there's nothing to do in it except farm. It's also why "make an enderman farm" is the meta, which Wynd acknowledged.

## W2. Progression is just a number going up
**Feels like:** no milestones. You don't *do* anything to get stronger; you just accumulate.
**Code says:** doriki and haki come from kills, challenges and manuals only. Trials exist (20 of them) but only unlock fighting-style abilities. `ReachDorikiObjective` exists and isn't used for gating.
**Why it matters:** gates ("at 5,000 doriki, clear a base / beat a boss to break through") turn a grind into goals, and make players use the content that does exist.

## W3. Not enough places to go, and the same structure every time
**Feels like:** looting the same marine base for the 40th time.
**Code says:**
- The structure lineup is essentially unchanged since 2023.
- Only one real multi-room dungeon exists (the marine large base).
- Pirates exist only as ships on water.
- **The Revolutionary Army has no NPCs and no structures at all.**
- The bandit caves are the only underground faction structure, which is proof the pipeline supports it.

**Why it matters:** variety is what makes a sandbox worth exploring. It's also the cheapest kind of new content, because structures are data plus templates and reuse existing NPCs and loot.

## W4. Faction imbalance: marines get free loot
**Feels like:** "marine is infinitely better because of how fast you can raid bases."
**Code says:** marine-aligned NPCs and players can't hurt each other. Marine bases have the best box odds on land. Pirates only have ships; revolutionaries have nothing.
**Why it matters:** your faction choice decides how fast you get a fruit, and that has nothing to do with skill or roleplay. Every faction needs an equivalent "enemy stronghold" to raid, and the strongholds of your own faction shouldn't be a free loot piñata.

## W5. Fruit acquisition is pure RNG with no floor
**Feels like:** 8 hours with no good box while a friend opens Goro Goro from their first golden box.
**Code says:**
- Fruits are uniform within a tier.
- Getting one specific golden fruit takes about 185 battleship treasure chests, or about 450 large-base captain chests *(sim)*.
- No pity system.
- **Bosses drop no boxes.**
- About 1 in 20 boxes may open to nothing (possible bug).

**Why it matters:** fruits are the main draw. A loop where getting a fruit is a lottery with no progress makes people quit early or stop once they hit the jackpot.

## W6. Bosses live in a pocket dimension
**Feels like:** the mod can't decide what it wants to be; a boss rush where you get teleported away to fight.
**Code says:** all 18 bosses are challenge-only (arena dimension); none spawn in the world. The challenge doriki pool is finite, and repeat clears are cut by `1.5 × completions`. Five more bosses are already planned in the challenge order (Mohji & Richie, Hatchan, Mr. 2, Mr. 4 & Miss Merry Christmas, Miss Doublefinger).
**Why it matters:** bosses are the best content in the mod, and they're cut off from the world. Bringing them into the overworld would make the map worth exploring and give the late game a repeatable activity, which is also the dev's own stated goal ("open-world bosses for late-game players").

## W7. Fruit content is frozen
**Feels like:** "it's all the same fruits"; no awakenings.
**Code says:** 73 fruits in 2023, 72 now (two removed, one added). The awakening framework exists but is off by default, admin-only, and implemented for one fruit (Gomu).
**Why it matters:** this is the thing the community wanted most for years, and it's left to addons. It's also the most expensive item on this list per unit of content, which is why it isn't first.

## W8. The endgame loop is PvP, but the mod moved away from it
**Feels like:** once you have a good fruit and max stats, the only lasting fun is fighting people.
**Code says:** the dev deprioritised PvP (stated reason: it drove away newer players on public servers). Bounty, crews and the death tax all still exist.
**Why it matters for us:** we're building for a private server of friends, not a public one. The "PvP drives off casuals" problem mostly doesn't apply, so we can lean into PvP-adjacent loops (bounty hunting, faction wars, contested bosses) on our own terms.

---

## Smaller things noticed
- Pacifistas (2,000–4,000 doriki) are weaker than captains (4,000–6,000). That's odd for lore and for difficulty.
- Pirates have no sniper unit; marines and bandits do.
- Heavy addon stacking (e.g. several haki addons at once) causes the box and haki problems you saw on your friend's server, and those problems are separate from the base mod. Our addon should replace systems cleanly rather than layering on top of other addons.
