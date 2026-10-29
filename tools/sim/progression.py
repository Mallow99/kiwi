"""Progression simulator for the MallowPiece doriki/haki curves.

Models a player raiding structures and fighting world enemies, then reports how
long each 2,000-doriki band takes. Used to pick the defaults in
docs/plan/phase-1-fix-the-loop.md. Pure python, no deps:  python3 tools/sim/progression.py
"""
import random, statistics

# Enemy roster after MallowPiece (Hard difficulty). (name, min doriki, max doriki, combat strength = HP+ATK)
ROSTER = [
    ("grunt",            1000,  2500,  20),
    ("sniper",           3500,  5000,  35),
    ("brute",            4000,  5500,  75),
    ("captain",          4500,  6500, 110),
    ("elite",            7000,  9000, 160),   # Phase 2: commodores, rev commanders, notorious officers
    ("supernova_crew",   9000, 11000, 220),   # Phase 4: boss-ship crews
]

CFG = dict(
    kills_per_hour=45,       # raiding pace including travel/looting
    hits_per_kill=6,
    parity_divisor=100,      # gain = T / divisor at parity (base mod uses 100)
    falloff_exponent=3.0,    # gain *= (P/T)^-exp when out-levelling the target
    falloff_floor=0.02,
    # Per-band multipliers (band = the 2,000-doriki gate you're working towards).
    # Front-loaded: early game is quick, late game slower. Tuned for ~2/3/4/5/6 h per band (~20 h total).
    band_mult_phase1={2000: 2.18, 4000: 1.09, 6000: 0.34, 8000: 0.55, 10000: 0.80},  # roster ends at captains
    band_mult_full={2000: 2.18, 4000: 1.09, 6000: 0.30, 8000: 0.18, 10000: 0.12},    # once elites/supernova crews exist
    band_mult=None,          # set by preset
    gate_hours=0.75,         # time to clear one breakthrough trial
    gates=(2000, 4000, 6000, 8000),
    haki_c=0.040,            # haki per hit at strength 1.0 (tuned for ~15 h of fighting to 100)
    haki_weaker_penalty=0.5, # x0.5 when target strength < current haki
    haki_limit=100.0,
)

def doriki_gain(P, T, c=CFG):
    r = P / T if T else 99
    g = 1.0 if r <= 1 else max(c["falloff_floor"], r ** -c["falloff_exponent"])
    band = next(b for b in sorted(c["band_mult"]) if P < b) if P < 10000 else 10000
    return T / c["parity_divisor"] * g * c["band_mult"][band]

def haki_gain(H, strength, c=CFG):
    s = min(2.0, max(0.15, strength / 120.0))
    pen = c["haki_weaker_penalty"] if strength < H else 1.0
    slow = 1.25 - 0.5 * (H / c["haki_limit"])   # gentle slowdown, never asymptotic
    return c["haki_c"] * s * pen * slow

def pick_target(P, rng, max_tier):
    pool = ROSTER[:max_tier]
    # 70% of fights: the strongest enemy type you'd reasonably take on (doriki <= 1.3P); 30%: whatever's around
    fair = [e for e in pool if e[1] <= max(1500, 1.3 * P)]
    e = rng.choice(fair[-2:]) if rng.random() < 0.7 else rng.choice(fair)
    return rng.uniform(e[1], e[2]), e[3]

def run(max_tier=len(ROSTER), seed=1, c=CFG):
    rng = random.Random(seed)
    P, H, kills, hours = 0.0, 0.0, 0, 0.0
    band_hours, band_start = {}, 0.0
    for g in c["gates"] + (10000,):
        while P < g:
            T, strength = pick_target(P, rng, max_tier)
            P = min(g, P + doriki_gain(P, T, c))
            for _ in range(c["hits_per_kill"]):
                H = min(c["haki_limit"], H + haki_gain(H, strength, c))
            kills += 1
        hours = kills / c["kills_per_hour"] + c["gate_hours"] * sum(1 for x in c["gates"] if x <= g)
        band_hours[g] = hours - band_start
        band_start = hours
    return dict(hours=hours, kills=kills, haki=H, bands=band_hours)

def haki_hours(c=CFG, seed=1, max_tier=len(ROSTER)):
    rng = random.Random(seed); P = 0; H = 0; kills = 0
    while H < 99.9 and kills < 10**6:
        T, strength = pick_target(P, rng, max_tier)
        P = min(10000, P + doriki_gain(P, T, c))
        for _ in range(c["hits_per_kill"]):
            H = min(c["haki_limit"], H + haki_gain(H, strength, c))
        kills += 1
    return kills / c["kills_per_hour"]

if __name__ == "__main__":
    for label, tier, preset in (("Phase 1 only (no new enemies)", 4, "band_mult_phase1"),
                                ("With Phase 2+4 enemies", len(ROSTER), "band_mult_full")):
        CFG["band_mult"] = CFG[preset]
        res = [run(tier, s) for s in range(20)]
        print(f"== {label}")
        print(f"   0 -> 10,000 doriki: {statistics.mean(r['hours'] for r in res):.1f} h active play, "
              f"{statistics.mean(r['kills'] for r in res):.0f} kills (incl. {len(CFG['gates'])} gate trials)")
        for g in CFG["gates"] + (10000,):
            print(f"   band to {g:>6,}: {statistics.mean(r['bands'][g] for r in res):5.1f} h")
        print(f"   haki 0 -> 100: {statistics.mean(haki_hours(seed=s, max_tier=tier) for s in range(20)):.1f} h of fighting")
    print("\nFor comparison, base MMnM 0.11.6: ~37,500 enderman kills (Hard) to max doriki;"
          " ~6,500 is the strongest repeatable target.")
