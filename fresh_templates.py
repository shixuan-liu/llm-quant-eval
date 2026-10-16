"""Contamination probe: GSM-Symbolic-style variants of GSM8K test items #0-#19.

Each template keeps the original problem's wording and reasoning steps and only
changes names and numbers. Numbers are drawn so every answer is a positive integer:
where a step divides, the quotient is drawn first and the dividend is built from it.

Writes data/fresh_problems.jsonl in the GSM8K format ({"question", "answer": "#### N"})
plus source_id (the original GSM8K index) and variant, so results can be paired.
"""
import json
import random

PEOPLE = [("Priya", "she", "her"), ("Marcus", "he", "his"), ("Aiko", "she", "her"),
          ("Diego", "he", "his"), ("Fatima", "she", "her"), ("Liam", "he", "his"),
          ("Mei", "she", "her"), ("Omar", "he", "his"), ("Sofia", "she", "her"),
          ("Kwame", "he", "his")]
CITIES = ["Lyon", "Porto", "Dayton", "Fresno", "Tulsa", "Leeds", "Quebec", "Boise", "Malmo", "Perth"]


def person():
    return random.choice(PEOPLE)


def times(k):
    return "twice" if k == 2 else f"{k} times"


def money(x):
    return f"${x:,}"


# 0 — Janet's ducks: (laid - eats - bakes) * price
def t00():
    name, _, _ = person()
    eats, bakes, sold = random.randint(2, 5), random.randint(2, 6), random.randint(5, 15)
    laid, price = eats + bakes + sold, random.randint(2, 5)
    q = (f"{name}'s ducks lay {laid} eggs per day. {name} eats {eats} for breakfast every morning "
         f"and bakes muffins for friends every day with {bakes}. {name} sells the remainder at the "
         f"farmers' market daily for ${price} per fresh duck egg. How much in dollars does {name} "
         f"make every day at the farmers' market?")
    return q, sold * price


# 1 — robe: blue + half as much white
def t01():
    blue = 2 * random.randint(2, 10)
    q = (f"A robe takes {blue} bolts of blue fiber and half that much white fiber. "
         f"How many bolts in total does it take?")
    return q, blue + blue // 2


# 2 — house flip: value rises by pct% of purchase price; profit = gain - repairs
def t02():
    name, he, _ = person()
    price = 10_000 * random.randint(5, 15)
    pct = random.choice([120, 125, 150, 175, 200])
    gain = price * pct // 100
    repairs = 5_000 * random.randint(2, gain // 5_000 - 2)
    q = (f"{name} decides to try flipping a house. {he.capitalize()} buys a house for {money(price)} "
         f"and then puts in {money(repairs)} in repairs. This increased the value of the house by "
         f"{pct}%. How much profit did {he} make?")
    return q, gain - repairs


# 3 — sprints: sprints * times * meters
def t03():
    name, he, _ = person()
    sprints, per_week, meters = random.randint(2, 6), random.randint(2, 5), 10 * random.randint(3, 12)
    q = (f"{name} decides to run {sprints} sprints {per_week} times a week. {he.capitalize()} runs "
         f"{meters} meters each sprint. How many total meters does {he} run a week?")
    return q, sprints * per_week * meters


# 4 — chicken feed: cups*flock - morning - afternoon
def t04():
    name, she, her = person()
    cups, flock = random.randint(2, 4), random.randint(12, 30)
    total = cups * flock
    final = random.randint(5, total // 3)
    morning = random.randint(5, total - final - 5)
    afternoon = total - final - morning
    q = (f"Every day, {name} feeds each of {her} chickens {cups} cups of mixed chicken feed, containing "
         f"seeds, mealworms and vegetables to help keep them healthy. {she.capitalize()} gives the "
         f"chickens their feed in three separate meals. In the morning, {she} gives {her} flock of "
         f"chickens {morning} cups of feed. In the afternoon, {she} gives {her} chickens another "
         f"{afternoon} cups of feed. How many cups of feed does {she} need to give {her} chickens in "
         f"the final meal of the day if the size of {name}'s flock is {flock} chickens?")
    return q, final


# 5 — glasses: every second glass at pct% of price
def t05():
    name, he, his = person()
    price, pct = random.choice([(5, 60), (4, 75), (6, 50), (10, 70), (8, 75), (5, 80), (10, 40)])
    n = 2 * random.randint(4, 12)
    q = (f"{name} went to the store to buy glasses for {his} new apartment. One glass costs ${price}, "
         f"but every second glass costs only {pct}% of the price. {name} wants to buy {n} glasses. "
         f"How much does {he} need to pay for them?")
    return q, n // 2 * price + n // 2 * price * pct // 100


# 6 — sheep: s + k2*s + k1*k2*s
def t06():
    a, b, c = random.sample(CITIES, 3)
    k1, k2, s = random.randint(2, 4), random.randint(2, 5), 5 * random.randint(2, 8)
    q = (f"{a} has {times(k1)} as many sheep as {b}. {b} has {times(k2)} as many sheep as {c}. "
         f"How many sheep do {a}, {b}, and {c} have together if {c} has {s} sheep?")
    return q, s + k2 * s + k1 * k2 * s


# 7 — download restart: pct% of file, wait, full file again
def t07():
    name, she, _ = person()
    rate = random.choice([1, 2, 4, 5])
    size = rate * 20 * random.randint(2, 8)
    pct = random.choice([20, 25, 30, 40, 50, 60, 75])
    wait = 5 * random.randint(2, 8)
    q = (f"{name} is downloading a {size} GB file. Normally {she} can download {rate} GB/minute, but "
         f"{pct}% of the way through the download, Windows forces a restart to install updates, which "
         f"takes {wait} minutes. Then {name} has to restart the download from the beginning. How long "
         f"does it take to download the file?")
    return q, size * pct // 100 // rate + size // rate + wait


# 8 — drive away, come back: out - (0.5*v2 + rest*v3)
def t08():
    while True:
        name, he, _ = person()
        h1, v1 = random.randint(2, 5), 10 * random.randint(4, 7)
        total, stuck = random.randint(3, 5), random.randint(1, 2)
        v2, v3 = 10 * random.randint(2, 4), 10 * random.randint(5, 8)
        back2 = v2 + (2 * (total - stuck) - 1) * v3          # twice the distance driven back
        if back2 % 2 == 0 and 2 * h1 * v1 > back2:
            break
    q = (f"{name} drives for {h1} hours at a speed of {v1} mph and then turns around because {he} "
         f"realizes {he} forgot something very important at home. {he.capitalize()} tries to get home "
         f"in {total} hours but spends the first {stuck} hour{"s" if stuck > 1 else ""} in standstill traffic. {he.capitalize()} "
         f"spends the next half-hour driving at a speed of {v2}mph, before being able to drive the "
         f"remaining time of the {total} hours going at {v3} mph. How far is {he} from home at the "
         f"end of those {total} hours?")
    return q, h1 * v1 - back2 // 2


# 9 — overtime: base*hours + base*mult*extra
def t09():
    name, she, her = person()
    base, mult = random.choice([(10, "1.2"), (15, "1.2"), (12, "1.5"), (20, "1.5"), (14, "1.5"), (18, "2")])
    regular, extra = random.choice([35, 40]), random.randint(2, 10)
    ot_rate = round(base * float(mult))
    q = (f"{name}'s rate per hour for the first {regular} hours {she} works each week is ${base}. "
         f"{she.capitalize()} also receives an overtime pay of {mult} times {her} regular hourly rate. "
         f"If {name} worked for {regular + extra} hours this week, how much are {her} earnings for "
         f"this week?")
    return q, base * regular + ot_rate * extra


# 10 — downloads: a + k*a + k*a*(1 - p%)
def t10():
    first, k = 20 * random.randint(2, 8), random.randint(2, 4)
    p = random.choice([10, 20, 25, 30, 40, 50])
    second = k * first
    third = second - second * p // 100
    word = {2: "twice", 3: "three times", 4: "four times"}[k]
    q = (f"A new program had {first} downloads in the first month. The number of downloads in the "
         f"second month was {word} as many as the downloads in the first month, but then reduced by "
         f"{p}% in the third month. How many downloads did the program have total over the three months?")
    return q, first + second + third


# 11 — bakery: sum of dozens * price per dozen
def t11():
    name, she, _ = person()
    d = [random.randint(1, 6) for _ in range(3)]
    p = [random.randint(30, 90) for _ in range(3)]
    q = (f"{name} went to the bakery and bought various types of pastries. {she.capitalize()} bought "
         f"{d[0]} dozen donuts which cost ${p[0]} per dozen, {d[1]} dozen mini cupcakes which cost "
         f"${p[1]} per dozen, and {d[2]} dozen mini cheesecakes for ${p[2]} per dozen. How much was "
         f"the total cost?")
    return q, sum(x * y for x, y in zip(d, p))


# 12 — lemon tree: years to pay off = cost / (lemons*price - upkeep); answer is the year after
def t12():
    while True:
        name, he, _ = person()
        lemons, price = random.randint(5, 12), random.choice([1, 1.5, 2, 2.5])
        upkeep = random.randint(2, 5)
        net = lemons * price - upkeep
        years = random.randint(6, 15)
        cost = net * years
        if net > 0 and cost == int(cost):
            break
    q = (f"{name} is planting a lemon tree. The tree will cost ${int(cost)} to plant. Each year it will "
         f"grow {lemons} lemons, which {he} can sell for ${price:g} each. It costs ${upkeep} a year to "
         f"water and feed the tree. How many years will it take before {he} starts earning money on "
         f"the lemon tree?")
    return q, years + 1


# 13 — vacuums, worked backwards: x - x/3 - k = 2*left
def t13():
    name, she, her = person()
    k, left = 2 * random.randint(1, 4), random.randint(3, 12)
    start = (2 * left + k) * 3 // 2
    q = (f"{name} is a door-to-door salesperson. {she.capitalize()} sold a third of {her} vacuum "
         f"cleaners at the green house, {k} more to the red house, and half of what was left at the "
         f"orange house. If {name} has {left} vacuum cleaners left, how many did {she} start with?")
    return q, start


# 14 — dance class: percent left after a% then b% of the remainder
def t14():
    while True:
        n = 20 * random.randint(1, 5)
        a, b = random.choice([10, 20, 25, 40, 50]), random.choice([20, 25, 50, 75])
        c1 = n * a / 100
        c2 = (n - c1) * b / 100
        rest_pct = (n - c1 - c2) / n * 100
        if c1 == int(c1) and c2 == int(c2) and rest_pct == int(rest_pct):
            break
    q = (f"In a dance class of {n} students, {a}% enrolled in contemporary dance, {b}% of the remaining "
         f"enrolled in jazz dance, and the rest enrolled in hip-hop dance. What percentage of the "
         f"entire students enrolled in hip-hop dance?")
    return q, int(rest_pct)


# 15 — merchant: max of two percentage gains
def t15():
    while True:
        a, b = 1000 * random.randint(3, 12), 1000 * random.randint(3, 12)
        pa, pb = random.randint(10, 40) / 10, random.randint(10, 40) / 10
        ga, gb = round(a * pa / 100), round(b * pb / 100)
        if a != b and ga != gb:
            break
    q = (f"A merchant wants to make a choice of purchase between 2 purchase plans: jewelry worth "
         f"{money(a)} or electronic gadgets worth {money(b)}. His financial advisor speculates that the "
         f"jewelry market will go up {pa:g}% while the electronic gadgets market will rise {pb:g}% within "
         f"the same month. If the merchant is looking to maximize profit at the end of this month by "
         f"making a choice, how much profit would this be?")
    return q, max(ga, gb)


# 16 — trains: distance per train = day1 + day2
def t16():
    city = random.choice(CITIES)
    d1, d2 = 10 * random.randint(5, 15), 10 * random.randint(8, 20)
    q = (f"Two trains leave {city} at the same time. They begin traveling westward, both traveling for "
         f"{d1} miles. The next day, they travel northwards, covering {d2} miles. What's the distance "
         f"covered by each train in the two days?")
    return q, d1 + d2


# 17 — two jobs: weeks * (rate1*h1 + rate2*h2)
def t17():
    name, she, _ = person()
    r1, r2 = random.randint(15, 30), random.randint(20, 40)
    h1, h2 = random.randint(20, 35), random.randint(5, 15)
    weeks = random.choice([45, 48, 50, 52])
    q = (f"{name} gets paid ${r1} per hour to teach and ${r2} to be a cheerleading coach. If {she} "
         f"works {weeks} weeks a year, {h1} hours a week as a teacher and {h2} hours a week as a coach, "
         f"what's {name}'s annual salary?")
    return q, weeks * (r1 * h1 + r2 * h2)


# 18 — omelets: eggs_per_day * 7 * weeks must divide by 12
def t18():
    name, she, _ = person()
    eggs = random.choice([2, 3, 4, 6])
    step = 12 // {2: 2, 3: 3, 4: 4, 6: 6}[eggs]           # weeks must be a multiple of 12 / gcd(eggs, 12)
    weeks = step * random.randint(1, 4)
    q = (f"{name} makes a {eggs} egg omelet every morning for breakfast. How many dozens of eggs will "
         f"{she} eat in {weeks} weeks?")
    return q, eggs * 7 * weeks // 12


# 19 — hiking: speed for the remaining distance to hit a target average
def t19():
    while True:
        name, she, _ = person()
        target = random.randint(3, 5)
        total_time = random.randint(3, 5)
        trail = target * total_time
        speed = random.randint(target + 1, target + 5)
        remaining = speed * (total_time - 2)
        done = trail - remaining
        if done >= 3:
            first = random.randint(2, done - 1)
            break
    q = (f"{name} is hiking a {trail}-mile trail. {she.capitalize()} took 1 hour to walk the first "
         f"{first} miles, then another hour to walk the next {done - first} miles. If {she} wants "
         f"{'her' if she == 'she' else 'his'} average speed to be {target} miles per hour, what speed "
         f"(in miles per hour) does {she} need to walk the remaining distance?")
    return q, speed


TEMPLATES = {i: globals()[f"t{i:02d}"] for i in range(20)}
VARIANTS = 5

if __name__ == "__main__":
    random.seed(42)
    rows = []
    for source_id, fn in TEMPLATES.items():
        for v in range(VARIANTS):
            q, a = fn()
            assert isinstance(a, int) and a > 0, (source_id, q, a)
            rows.append({"question": q, "answer": f"#### {a}", "source_id": source_id, "variant": v})
    with open("data/fresh_problems.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} problems from {len(TEMPLATES)} templates")
