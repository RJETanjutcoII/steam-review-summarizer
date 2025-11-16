from transformers import pipeline
import re

HYPE_PHRASES = [
    r"best game ever",
    r"best game",
    r"game of the year",
    r"goated",
    r"peak",
    r"10/10",
    r"1000/10",
    r"favorite game",
    r"greatest of all time",
]

FIRST_PERSON_PHRASES = [
    r"\bin my opinion\b",
    r"\bfor me personally\b",
]

SLANG_PHRASES = [
    r"\bgoated\b",
    r"\bpeak\b",
]

ASPECT_KEYWORDS = [
    # 🎮 Gameplay & Mechanics
    "gameplay", "mechanics", "controls", "movement", "responsiveness", "aiming",
    "shooting", "cover", "reload", "accuracy", "hit detection", "recoil", "stealth",
    "parkour", "dodging", "blocking", "melee", "combat", "fighting", "attack", "defense",
    "timing", "combo", "parry", "weapon", "gunplay", "driving", "racing", "flight",
    "crafting", "gathering", "building", "survival", "exploration", "platforming",
    "climbing", "jumping", "swimming", "interaction", "navigation", "camera", "perspective",
    "targeting", "balance", "pacing", "speed", "flow", "rhythm", "customization",
    "progression", "grind", "upgrade", "loot", "inventory", "quest", "side quest",
    "mission", "challenge", "reward", "difficulty", "checkpoint", "respawn",
    "save system", "tutorial", "learning curve",

    # ⚔️ Combat & Enemies
    "battle", "enemy", "enemies", "boss", "bosses", "mini boss", "encounter", "AI",
    "aggression", "patterns", "health", "damage", "weapons", "arsenal", "ammo", "armor",
    "stealth kills", "executions", "finishing moves", "blood", "gore", "animations",
    "targeting", "hitbox", "stamina", "cooldown", "special attack", "skills", "magic",
    "spells", "abilities", "class system", "power-up", "combos", "tactics", "teamfight",
    "squad", "co-op", "multiplayer balance",

    # 🧩 Puzzle & Level Design
    "puzzle", "puzzles", "logic", "riddle", "mystery", "brainteaser", "level design",
    "stage", "platform", "obstacle", "trap", "switch", "physics", "portal", "maze",
    "environment", "secrets", "exploration", "world design", "map", "navigation", "route",
    "checkpoint", "progression", "sandbox", "open world", "linearity", "backtracking",
    "area", "dungeon", "hub", "region",

    # 🕹️ RPG & Story Elements
    "story", "narrative", "plot", "dialogue", "choices", "branching", "endings",
    "moral system", "karma", "alignment", "lore", "worldbuilding", "backstory", "immersion",
    "characters", "NPCs", "protagonist", "companion", "romance", "relationships",
    "voice acting", "roleplay", "leveling", "skill tree", "attributes", "stats",
    "experience", "xp", "economy", "crafting", "alchemy", "forging", "equipment", "armor",
    "upgrade", "enchantment", "class", "build", "talent", "specialization", "faction",
    "guild", "reputation", "morality", "writing",

    # 🧠 AI & Technical Performance
    "pathfinding", "enemy behavior", "friendly AI", "team AI", "responsiveness",
    "awareness", "glitches", "bugs", "crashes", "lag", "performance", "optimization",
    "framerate", "fps", "stability", "memory usage", "load times", "save corruption",
    "network", "servers", "ping", "matchmaking", "netcode", "latency", "connectivity",
    "updates", "patches", "maintenance",

    # 👁️ Graphics, Visuals & Presentation
    "graphics", "visuals", "art", "art style", "direction", "design", "animation",
    "frame rate", "lighting", "color palette", "texture", "shader", "particles",
    "environment", "atmosphere", "visual effects", "realism", "aesthetics", "camera",
    "cinematics", "cutscene", "ui", "hud", "menus", "interface", "readability", "polish",
    "models", "details", "character design", "costume", "environment design",

    # 🎧 Sound, Music & Voice Acting
    "sound", "audio", "soundtrack", "music", "theme", "score", "ambient sound", "effects",
    "voice", "dialogue", "voice lines", "dubbing", "sound design", "footsteps",
    "weapon sounds", "mixing", "audio clarity", "volume balance",

    # 👻 Horror & Emotional Tone
    "horror", "fear", "dread", "tension", "suspense", "jump scare", "darkness",
    "monsters", "ghosts", "entities", "psychological", "disturbing", "unsettling",
    "survival horror", "resource management", "paranoia", "chase sequence", "hiding",
    "safe room", "lighting", "atmosphere",

    # ❤️ Characters & Writing
    "character", "hero", "villain", "antagonist", "sidekick", "personality", "motivation",
    "chemistry", "development", "arc", "depth", "humor", "tone", "consistency",
    "monologue", "emotional impact", "script",

    # 🎨 World, Environment & Immersion
    "world", "universe", "setting", "environment", "atmosphere", "realism", "interactivity",
    "physics", "weather", "day-night cycle", "lighting", "shadows", "scale", "travel",
    "fast travel", "sandbox", "discovery", "secrets", "immersion",

    # 🧑‍🤝‍🧑 Multiplayer, Online & Community
    "multiplayer", "co-op", "cooperative", "versus", "pvp", "pve", "party", "chat",
    "communication", "teamwork", "griefing", "balance", "ranked", "competitive",
    "toxicity", "crossplay", "leaderboards", "clans", "guilds", "social features",
    "community", "mod support", "user content", "server", "matchmaking",

    # 📖 Visual Novels & Narrative Games
    "storytelling", "routes", "choices", "emotion", "pacing", "writing", "script",
    "voice acting", "localization", "translation", "art style", "background art",
    "sprite", "cg", "romance", "themes", "branching paths", "replayability",

    # 💰 Economy, Progression & Rewards
    "economy", "progression", "grind", "balance", "loot", "rarity", "drop rate",
    "currency", "gold", "coins", "credits", "trading", "shop", "microtransactions",
    "pay to win", "monetization", "cosmetics", "skins", "battle pass", "unlocks",
    "achievements", "trophies", "rewards",

    # 🧍 Simulation, Strategy & Management
    "simulation", "management", "tycoon", "construction", "design", "planning",
    "strategy", "tactics", "resource management", "logistics", "efficiency", "automation",
    "worker management", "production", "supply chain", "agriculture", "traffic",
    "city building", "defense", "base building", "research", "policy", "politics",

    # ⚽ Sports, Racing & Physics
    "sports", "race", "driving", "cars", "vehicles", "handling", "drift", "acceleration",
    "physics", "realism", "tracks", "collision", "ball physics", "competition", "team",
    "commentary", "weather", "customization", "tuning",

    # 💻 Technical & UX
    "optimization", "graphics settings", "keybindings", "accessibility", "options",
    "resolution", "ultrawide", "controller support", "ui", "ux", "menus",
    "inventory management", "interface", "save system", "quicksave", "autosave",
    "input lag", "responsiveness", "stability", "bugs", "glitches",

    # 🧱 Content & Longevity
    "content", "replayability", "variety", "dlc", "expansion", "updates", "patches",
    "mods", "customization", "longevity", "endgame", "new game plus", "missions",
    "levels", "events", "story mode", "challenge mode", "time trials",

    # 🧍‍♂️ Immersion & Emotional Engagement
    "immersion", "atmosphere", "emotional impact", "tension", "excitement",
    "adrenaline", "pacing", "satisfaction", "frustration", "addiction", "boredom",
    "flow", "engagement",

    # 🧠 Meta / Player Experience
    "tutorial", "onboarding", "learning curve", "difficulty spike", "accessibility",
    "frustration", "satisfaction", "challenge balance", "feedback", "reward loop",
    "user interface", "clarity", "freedom", "choice", "direction", "objectives",

    # 🧩 General Quality Descriptors
    "polish", "quality", "consistency", "innovation", "originality", "creativity",
    "depth", "complexity", "simplicity", "smoothness", "responsiveness", "pacing",
    "balance", "execution"
]



EMPTY_PHRASES = [
    r"\bhighly regarded\b",
    r"\bfor good reason\b",
    r"\bgreat game\b",
    r"\bamazing game\b",
    r"\bgood game\b",
    r"\b10/10\b",
    r"\bmasterpiece\b",
]



summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Keep this small so prompt + reviews never exceed BART's max length
MAX_CHARS = 1200   # 👈 was 4000 before


def _build_prompt(reviews_text: str, polarity: str, max_points: int) -> str:
    """
    Build an instruction-style prompt for BART to encourage bullet-style,
    objective output.
    """
    if polarity == "positive":
        instruction = (
            "Summarize these positive Steam reviews into "
            f"{max_points} short, objective bullet points.\n"
            "Each bullet must mention a specific aspect of the game, such as gameplay, controls,\n"
            "combat, bosses, exploration, level design, map design, art, graphics, music, sound,\n"
            "story, difficulty, performance, or content.\n"
            "Avoid vague praise like 'great game' or 'highly regarded'; instead, state *why* players\n"
            "like the game (for example: 'players praise the tight controls and responsive combat').\n"
            "Write in a neutral, professional tone. Do not use first-person ('I', 'my', 'me', 'we', 'you').\n"
            f"Provide at most {max_points} bullets, one bullet per line starting with '- '.\n\n"
            "Reviews:\n"
        )
    else:
        instruction = (
            "Summarize these negative Steam reviews into "
            f"{max_points} short, objective bullet points.\n"
            "Each bullet must mention a specific issue that affects players' experience, such as\n"
            "gameplay, controls, combat, bosses, exploration, map design, art, graphics, music,\n"
            "difficulty, performance, bugs, or lack of updates.\n"
            "Avoid vague criticism like 'bad game'; instead, state *what* is wrong.\n"
            "Write in a neutral, professional tone. Do not use first-person ('I', 'my', 'me', 'we', 'you').\n"
            f"Provide at most {max_points} bullets, one bullet per line starting with '- '.\n\n"
            "Reviews:\n"
        )

    return instruction + reviews_text

def _neutralize_sentence(s: str, polarity: str) -> str:
    """
    Try to turn a raw sentence into a more neutral, aspect-style statement.
    Very heuristic, but good enough for an MVP.
    """
    original = s

    # Remove common hype phrases / slang
    s = re.sub(
        r"\b(best( game)?( ever)?|greatest|favorite|goated|peak|10/10|1000/10|game of the year)\b",
        "",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r"\b(in my opinion|for me personally)\b", "", s, flags=re.IGNORECASE)

    # Some specific rewrites for patterns you've already seen
    s = re.sub(r"^Play the game now.*", "Players strongly recommend the game.", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdeserves many titles\b.*", "is considered high quality by many players", s, flags=re.IGNORECASE)

    # Turn "A beautiful game..." into something more aspect-like
    s = re.sub(
        r"^A beautiful game",
        "The game's visuals and presentation are beautiful",
        s,
        flags=re.IGNORECASE,
    )

    # Negative-side common pattern
    s = re.sub(
        r"^This game is fun and all, but",
        "Players find the game fun but",
        s,
        flags=re.IGNORECASE,
    )

    # Clean double spaces introduced by deletions
    s = re.sub(r"\s{2,}", " ", s).strip()

    # Ensure it starts with a capital letter
    if s and not s[0].isupper():
        s = s[0].upper() + s[1:]

    # If the clean version got too short, fall back to the original
    if len(s) < 20:
        return original.strip()

    return s


def _parse_bullets(text: str, max_points: int, polarity: str):
    """
    Turn model output into a clean list of bullet strings.
    Works at sentence + clause level so one long sentence
    can yield several bullets.
    """
    bullets = []
    seen = set()

    # First get raw lines (if model used '- ' or newlines at all)
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not raw_lines:
        raw_lines = [text.strip()]

    sentence_candidates = []
    for line in raw_lines:
        line = re.sub(r"^[-*]\s*", "", line).strip()
        if not line:
            continue

        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', line)
        for sent in sentences:
            s = sent.strip()
            if not s:
                continue

            # If a sentence is long and contains multiple commas,
            # treat comma-separated clauses as separate candidates.
            if len(s) > 80 and "," in s:
                clauses = [c.strip() for c in s.split(",") if c.strip()]
                for c in clauses:
                    sentence_candidates.append(c)
            else:
                sentence_candidates.append(s)

    for s in sentence_candidates:
        if len(s) < 20:
            continue

        # Filter strongly first-person sentences
        if re.search(r"\b(I|my|me|we|us)\b", s, re.IGNORECASE):
            continue

        # Neutralize style a bit
        s = _neutralize_sentence(s, polarity=polarity)

        # Drop empty / hype-y phrases
        if any(re.search(pat, s, re.IGNORECASE) for pat in EMPTY_PHRASES):
            continue

        # Require at least one aspect keyword
        has_aspect = any(
            re.search(rf"\b{kw}\b", s, re.IGNORECASE) for kw in ASPECT_KEYWORDS
        )
        if not has_aspect:
            continue

        if len(s) < 20:
            continue

        # Reject obviously incomplete fragments
        if s.endswith(",") or s.endswith("("):
            continue

        # If there's an open "(" but no ")", strip from "(" onward
        if "(" in s and ")" not in s:
            s = s.split("(", 1)[0].strip()
            if len(s) < 20:
                continue

        key = s.lower()
        if key in seen:
            continue
        seen.add(key)

        bullets.append(s)
        if len(bullets) >= max_points:
            break

    # ✅ Fallback now happens AFTER the loop
    if not bullets:
        if polarity == "negative":
            return [
                "There are very few substantial negative reviews; most players report a positive experience."
            ]
        else:
            return [
                "There are very few substantial positive reviews; most players report a negative experience."
            ]

    return bullets

def _polish_bullet(text: str, polarity: str) -> str:
    """
    Make a bullet more neutral, readable, and consistent.
    This is generic: no game-specific phrases, only common review patterns.
    """
    s = text.strip()

    # 1) Normalize spaces
    s = re.sub(r"\s+", " ", s)

    # 2) Remove hype / extreme phrases
    for phrase in HYPE_PHRASES:
        s = re.sub(phrase, "", s, flags=re.IGNORECASE)

    # 3) Remove first-person qualifiers like "in my opinion"
    for phrase in FIRST_PERSON_PHRASES:
        s = re.sub(phrase, "", s, flags=re.IGNORECASE)

    # 4) Remove generic slang words
    for phrase in SLANG_PHRASES:
        s = re.sub(phrase, "", s, flags=re.IGNORECASE)

    # 5) Strip leftover punctuation/extra spaces from deletions
    s = re.sub(r"\s{2,}", " ", s)
    s = s.strip(" .,!?:;").strip()

    # 6) If the sentence starts generically ("A good", "This game is"),
    #    we can make it more aspect-based.
    if re.match(r"^(A|a) good\b", s):
        # e.g. "A good sequel to the original" -> "Players consider it a good sequel to the original."
        s = "Players consider it " + s[len("A "):].lstrip().lower()

    if re.match(r"^(This game is|The game is)\b", s, flags=re.IGNORECASE):
        # "This game is fun but difficult." -> "Players find the game fun but difficult."
        s = re.sub(r"^(This game is|The game is)", "Players find the game", s, flags=re.IGNORECASE)

    # 7) Make sure it starts with a capital letter
    if s and not s[0].isupper():
        s = s[0].upper() + s[1:]

    # 8) Ensure a period at the end
    if s and not s.endswith((".", "!", "?")):
        s = s + "."

    return s

def summarize_reviews_to_points(
    reviews,
    polarity: str = "positive",
    max_points: int = 6,
    max_reviews: int = 30,   # 👈 was 60 before
):
    """
    From a list of raw reviews (all positive OR all negative)
    to a list of 5–6 objective bullet points.
    """
    if not reviews:
        return ["No reviews found."]

    # Clean + limit how many reviews we use
    clean_reviews = [
        r.strip()
        for r in reviews[:max_reviews]   # 👈 fewer reviews
        if r and len(r.strip()) > 20
    ]
    if not clean_reviews:
        return ["No substantial reviews found."]

    reviews_text = " ".join(clean_reviews)

    # Hard cap on characters so prompt + reviews stay short
    if len(reviews_text) > MAX_CHARS:
        reviews_text = reviews_text[:MAX_CHARS]

    # Optional: debug so you can see what's going on
    # print(f"[{polarity}] reviews_text chars:", len(reviews_text))

    prompt = _build_prompt(reviews_text, polarity=polarity, max_points=max_points)

    # print("Prompt total chars:", len(prompt))

    result = summarizer(
        prompt,
        max_length=256,
        min_length=80,
        do_sample=False,
        truncation=True,
    )[0]["summary_text"]

    bullets = _parse_bullets(result, max_points=max_points, polarity=polarity)
    bullets = [_polish_bullet(b, polarity) for b in bullets]
    return bullets
