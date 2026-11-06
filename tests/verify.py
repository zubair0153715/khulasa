"""Khulasa verification — engine math, content bank, AI-shape
validation, routes.

Run: ~/workspace/.venv-fc/bin/python tests/verify.py
Exit code 0 = all pass. No network, no key needed (AI tests only
check the no-key error path and the JSON extractor, never a live
call).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from khulasa import engine, gemini, library  # noqa: E402

PASS = 0
FAIL = []


def check(name, cond, extra=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(f"{name} {extra}")


# --- word count / reading time (honest minutes, 200 wpm) ---
check("word count", engine.word_count("one two three") == 3)
check("word count empty", engine.word_count("") == 0)
check("reading 200w = 1 min", engine.reading_minutes(200) == 1)
check("reading 201w = 2 min", engine.reading_minutes(201) == 2)
check("reading 714w = 4 min", engine.reading_minutes(714) == 4)
check("reading 0w = 1 min", engine.reading_minutes(0) == 1)

# --- depth bands ---
check("flash band ok", engine.depth_ok("flash", 81) is True)
check("flash band low", engine.depth_ok("flash", 59) is False)
check("flash band high", engine.depth_ok("flash", 121) is False)
check("standard band ok", engine.depth_ok("standard", 315) is True)
check("deep band ok", engine.depth_ok("deep", 714) is True)
check("deep band high", engine.depth_ok("deep", 901) is False)
check("unknown depth", engine.depth_ok("study", 100) is False)

# --- paste validation ---
ok, _ = engine.validate_paste("x" * 200)
check("paste min ok", ok is True)
ok, _ = engine.validate_paste("x" * 199)
check("paste too short", ok is False)
ok, _ = engine.validate_paste("x" * 8000)
check("paste max ok", ok is True)
ok, _ = engine.validate_paste("x" * 8001)
check("paste too long", ok is False)
ok, _ = engine.validate_paste("   ")
check("paste blank", ok is False)

# --- quiz ---
item = library.BOOKS[0]["quiz"][0]
check("quiz right", engine.check_quiz(item, 0) is True)
check("quiz wrong", engine.check_quiz(item, 1) is False)
check("quiz bad index", engine.check_quiz(item, 9) is False)
c, t = engine.quiz_score([0, 1, 1], library.BOOKS[0]["quiz"])
check("quiz_score 3/3", (c, t) == (3, 3), f"got {(c, t)}")
c, t = engine.quiz_score([0, 0, 0], library.BOOKS[0]["quiz"])
check("quiz_score 1/3", (c, t) == (1, 3), f"got {(c, t)}")
c, t = engine.quiz_score([], [])
check("quiz_score empty", (c, t) == (0, 0))

# --- flashcards from key ideas ---
cards = engine.flashcards(library.BOOKS[0])
check("flashcards 5", len(cards) == 5, str(len(cards)))
check("flashcard shape", all("front" in c and "back" in c for c in cards))

# --- SRS ---
check("srs box0 +1d", engine.srs_next(0, "2026-11-06") == "2026-11-07")
check("srs box2 +7d", engine.srs_next(2, "2026-11-06") == "2026-11-13")
check("srs box clamped", engine.srs_next(9, "2026-11-06") == "2026-12-06")

# --- AI result shape validation ---
good = {
    "summary": "word " * 60,
    "key_ideas": ["a", "b", "c", "d", "e"],
    "action_plan": ["1", "2", "3", "4"],
    "quiz": [
        {"q": "q1", "options": ["a", "b", "c", "d"], "answer": 0, "why": "w"},
        {"q": "q2", "options": ["a", "b", "c", "d"], "answer": 1, "why": "w"},
        {"q": "q3", "options": ["a", "b", "c", "d"], "answer": 2, "why": "w"},
    ],
}
check("ai result good", engine.validate_ai_result(good) == [])
bad = dict(good, summary="too short")
check("ai result short summary", engine.validate_ai_result(bad) != [])
bad = dict(good, quiz=good["quiz"][:2])
check("ai result 2 quiz", engine.validate_ai_result(bad) != [])
bad = dict(good, quiz=[dict(good["quiz"][0], answer=9)] + good["quiz"][1:])
check("ai result bad answer", engine.validate_ai_result(bad) != [])
check("ai result not dict", engine.validate_ai_result("nope") != [])

# --- gemini JSON extractor (no network) ---
raw = 'Here is the result:\n```json\n{"summary": "x", "key_ideas": []}\n```'
check("extract json fenced", gemini._extract_json(raw) == {"summary": "x", "key_ideas": []})
check("extract json none", gemini._extract_json("no json here") is None)
check("summarize no-key error",
      gemini.summarize_text("x" * 300, "standard", "en")[1] is not None
      if not gemini.key_available() else True)
check("summarize bad depth",
      gemini.summarize_text("x" * 300, "nope", "en")[0] is None)
check("summarize bad language",
      gemini.summarize_text("x" * 300, "standard", "xx")[0] is None)
check("summarize short paste",
      gemini.summarize_text("tiny", "standard", "en")[0] is None)

# --- library ---
errs = engine.validate_library(library)
check("library valid", errs == [], str(errs))
check("book count 6", len(library.BOOKS) == 6, str(len(library.BOOKS)))
check("every book 3 depths",
      all(set(b["summaries"]) == {"flash", "standard", "deep"}
          for b in library.BOOKS))
n_ideas = sum(len(b["key_ideas"]) for b in library.BOOKS)
check("key ideas 30", n_ideas == 30, str(n_ideas))
n_quiz = sum(len(b["quiz"]) for b in library.BOOKS)
check("quiz items 18", n_quiz == 18, str(n_quiz))
n_actions = sum(len(b["action_plan"]) for b in library.BOOKS)
check("actions 24", n_actions == 24, str(n_actions))
check("gutenberg links all search pages",
      all(b["gutenberg"].startswith("https://www.gutenberg.org/ebooks/search/?query=")
          for b in library.BOOKS))
check("no headway text copied",
      all("Headway" not in b["summaries"]["deep"] for b in library.BOOKS))

# --- routes via TestClient ---
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from khulasa.routes import router

    app = FastAPI()
    app.include_router(router)
    c = TestClient(app)
    r = c.get("/khulasa")
    check("route page 200", r.status_code == 200 and "Khulasa" in r.text)
    check("page has no trial copy",
          "auto-renew" not in r.text.lower() or "no auto-renewal" in r.text.lower())
    r = c.get("/khulasa/api/library")
    check("route library valid", r.status_code == 200 and r.json()["valid"] is True)
    check("route library 6 books", len(r.json()["books"]) == 6)
    check("route library depths carry minutes",
          all("minutes" in b["depths"]["deep"] for b in r.json()["books"]))
    r = c.get("/khulasa/api/ai-status")
    check("route ai-status", r.status_code == 200
          and r.json()["ai_available"] is False)
    r = c.post("/khulasa/api/quiz-score",
               data={"payload": '{"quiz": [{"answer": 0}, {"answer": 1}], "answers": [0, 0]}'})
    check("route quiz-score", r.status_code == 200 and r.json() == {"ok": True, "correct": 1, "total": 2})
    r = c.post("/khulasa/api/summarize",
               data={"text": "x" * 300, "depth": "standard", "language": "en"})
    check("route summarize no-key error", r.status_code == 200
          and r.json()["ok"] is False)
    r = c.post("/khulasa/api/summarize",
               data={"text": "tiny", "depth": "standard", "language": "en"})
    check("route summarize short paste", r.status_code == 200
          and r.json()["ok"] is False)
except ImportError as e:
    FAIL.append(f"testclient import failed: {e}")

print(f"{PASS} PASS, {len(FAIL)} FAIL")
for f in FAIL:
    print("FAIL:", f)
sys.exit(1 if FAIL else 0)
