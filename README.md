# Khulasa — Free AI Book-Summary Studio

Kitabein, 2 minute mein — muft, hamesha. An original, clean-room
answer to the Headway gap: a book-summary app that charges
~$89.99/year for static one-size-fits-all 15-minute summaries,
runs a 7-day free trial that auto-renews into a paid subscription
(Trustpilot 3.9/5, with recurring billing complaints), only sells
its own fixed library, has no web reader, and offers no Urdu.

**Live:** https://clinic-demo.fastapicloud.dev/khulasa

## What it does

1. **Library — 6 public-domain classics, 3 depths each.** Meditations,
   The Art of War, As a Man Thinketh, The Prince, Pride and Prejudice,
   Frankenstein. Every summary is original wording written for this app
   — no copyrighted text reproduced, no Headway content copied. Depths:
   Flash (~1 min), Standard (~2 min), Deep (~4 min), with honest reading
   times (words ÷ 200 wpm), never a round "15 minutes" for every book.
2. **Apna Khulasa — summarise YOUR OWN text.** Paste notes, a chapter
   or an article (200–8,000 chars) → Gemini returns a summary at your
   chosen depth (Flash / Standard / Deep / Study), 5 key ideas, a dated
   action plan and a 3-question quiz — in English, Roman-Urdu or Urdu
   script. The AI only ever summarises the text you paste; it never
   claims to know a book you did not paste.
3. **Quiz with explain-every-answer.** Every quiz question carries its
   explanation, right or wrong. Flashcards come from each book's own
   key ideas, with a 1/3/7/14/30-day spaced-repetition schedule.
4. **Action plans.** Every book and every AI summary ends with concrete
   steps to do this week — summaries you can act on, not just read.
5. **Free forever.** No trial, no card, no auto-renewal, no account.
   XP, streak and checklists live in your browser (localStorage).
   Read-aloud uses your device's own speech synthesis.

## Honest limits

- The starter library is 6 public-domain classics, not 1,700
  bestsellers. The real library is whatever you paste — the AI
  summariser covers any text.
- AI summaries need a `GEMINI_API_KEY` in the environment; without
  it the library, quizzes, flashcards and action plans still work
  fully, and the page says the AI is off.
- Summaries are study aids, not substitutes for reading the book.
  Every book page links the free full text on Project Gutenberg.
- Read-aloud uses the device's own speech synthesis, so voice
  quality varies by device; no audio files ship with the app.

## Run the tests

```bash
~/workspace/.venv-fc/bin/python tests/verify.py
# 57 checks: engine math, depth bands, paste limits, quiz scoring,
# flashcards, SRS dates, AI-output shape validation, library
# validity, and the FastAPI routes (TestClient, no key needed).
```

## Layout

- `khulasa/engine.py` — pure logic: word counts, reading time,
  depth bands, paste validation, quiz scoring, flashcards, SRS.
- `khulasa/library.py` — the 6-book starter bank (original summaries).
- `khulasa/gemini.py` — optional Gemini summariser (urllib, key read
  at call time, never stored).
- `khulasa/routes.py` — FastAPI routes (`/khulasa`, `/api/library`,
  `/api/ai-status`, `/api/summarize`, `/api/quiz-score`).
- `khulasa/pages.py` — single-file HTML/JS front end.
- `tests/verify.py` — the full check suite.

## Gap report

`~/workspace/market-gaps/daily/2026-11-06-khulasa.md` — Headway
pricing, review and billing evidence from public sources only.
