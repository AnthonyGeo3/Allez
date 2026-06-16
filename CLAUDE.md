# Allez! — project context for Claude Code

Single-file French-learning PWA for **two named users** (Anthony, Amy) prepping for a Paris trip. Speaking/listening-first, dyslexia-friendly, offline-capable. Personal app — not multi-tenant, two hardcoded profiles is intentional.

## Run & deploy
- Pure static site. **No build step, no bundler, no framework.** Open `index.html` to run; deploy by pushing to `main` (GitHub Pages). Live at `https://anthonygeo3.github.io/Allez/`.
- Owner reviews every diff in GitHub Desktop before committing. Make minimal, well-justified changes.

## File map
- `index.html` — the whole app. Two `<script>` blocks: **block 1 = DATA**, **block 2 = logic**, divided by `// ---------- SECTION ----------` banners: UTILS, STATE, TTS, PREMIUM AUDIO PACK, SPEECH RECOGNITION, SRS, STREAKS, FIREBASE, AI, CHAT, DRILL SESSION, RENDER, PHRASEBOOK, NUMBERS/PRICES/TIMES TRAINER, SETTINGS, BOOT.
- `manifest.json`, `sw.js` (offline cache — see release checklist), `icon-192/512.png`.
- `worker.js` — Cloudflare Worker proxy to the Anthropic API (holds `ANTHROPIC_API_KEY` secret). Optional; enables live conversation + À deux.
- `make_audio.py` — optional premium audio generator (edge-tts neural voices → `audio/` folder; app auto-detects).
- `SETUP.md` (first deploy), `UPGRADES.md` (Firebase + AI Worker + audio, click-by-click).

## Data shapes (block 1)
- `P(f,e,p,c,l)` → phrase `{f:French, e:English, p:phonetic, c:category-key, l:level 1|2}`. ~230 phrases. `CATS` = category-key→label.
- `SCENARIOS[]` = `{id,em,t,s,role,starter:{f,e,p}}`. `SCRIPTS{}` = offline keyword-matched fallback dialogues for `cafe`/`boul`/`dir` only.
- Phonetic house style: `"bohn-ZHOOR"` — `(n)` = nasal, CAPS = stressed syllable. Match it for new phrases.

## State & persistence
- Global `S`; `localStorage` key `allez.v1`; `save()` is debounced. `me()` / `other()` helpers. `freshProfile(level)` seeds defaults; loader merges defaults over stored data (so new fields are safe).
- **Only `profiles` + `days` sync via Firebase. `settings` are device-local by design** (workerUrl, firebase config, chosen voice differ per phone — never sync them).
- Firestore path: `allez/{house}/profiles/{name}` + `days` map on the house doc. Anonymous shared-path model (no auth, no login flows — owner preference).

## SRS (spaced repetition)
- SM-2-lite in `srsOf`/`grade`/`buildSession`/`dueCount`. ease 1.3–3, buttons again/good/easy, 12-card sessions, `newPerDay` budget.
- **Invariants (don't regress):** a card is "new" only until its record is first created (counted against the daily new budget exactly once, in `prepCard`); "due" = any introduced card past its due time (a failed/"Encore" card returns as a review, it does NOT re-consume the new budget). `prepCard` also picks direction: mature cards (reps≥2) flip to listen-first ~40% of the time.
- `markDone(names)` advances personal streak + writes `days`; `houseStreak()` counts days where **both** profiles practised.

## Audio & speech — the fragile part, handle with care
- **Playback:** `say(id)` for library phrases (premium audio file if present, else TTS). `speak(text)` for dynamic text (AI replies, generated numbers). The numbers trainer MUST use `speak()`, not `say()`.
- **iOS (Amy's iPhone X) needs both of these — do not remove:** `unlockTTS` primes speech on the first user gesture; a `visibilitychange` handler re-arms it when the PWA returns to foreground (iOS silently re-locks `speechSynthesis` after backgrounding).
- **Speech recognition is Chrome-only.** `const SR = ... || null`. On iOS it's null and mic buttons are hidden by design. Never assume a mic exists; always keep the Reveal/tap path working. `micErr()` maps error codes to advice.

## AI conversation
- `callAI` posts to the Worker URL if set, else the keyless direct endpoint (**that direct path only works inside a claude.ai Artifact, not on GitHub Pages** — real devices need the Worker). `buildSystem` enforces a strict minified-JSON contract `{fr,en,phon,note,done}`, level-calibrated per user.
- Models: Worker default `claude-haiku-4-5-20251001`, option `claude-sonnet-4-6`; `DIRECT_MODEL` is for the artifact path only. Scenes that need AI are locked in the UI until a Worker URL is set.

## How to test (do this every change — there is no test runner)
1. **Syntax** — extract inline JS and `node --check`:
   ```
   python3 -c "import re;h=open('index.html').read();open('/tmp/a.js','w').write(chr(10).join(re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>',h,re.S)))" && node --check /tmp/a.js
   ```
2. **Behaviour** — pure functions are DOM-free; test them in a node VM by slicing the relevant section out of `index.html`. Cover at least:
   - SRS: failed card comes back as due (not new); new counted once; passed card leaves today's queue.
   - Numbers: every `numQ(kind)` returns exactly 1 correct + 4 distinct options; `frNum` matches known forms — 71 `soixante et onze`, 80 `quatre-vingts`, 91 `quatre-vingt-onze`, 12:45 `une heure moins le quart`.
3. **Can't be tested headless** (audio, mic, Firestore live sync) → owner QAs on real Pixel + iPhone. Say so rather than claiming it works.

## Release checklist
- [ ] **Bump the `CACHE` version string in `sw.js`** (e.g. `allez-v1`→`allez-v2`) or the PWA serves stale files.
- [ ] Run both tests above.
- [ ] Keep it single-file, offline-first, minimal-dependency, mobile-first.
- [ ] Leave a one-line summary of what changed for the GitHub Desktop diff review.

## Gotchas
- iPhone X is capped at iOS 16; ITP can evict `localStorage` after ~7 days unused → Firebase sync is the real backup for Amy, not a nice-to-have.
- Firebase config copied from the console is **JavaScript, not JSON** — `parseCfg` accepts both; don't tighten it to `JSON.parse`.
- Firebase is guarded against double-init (`fbCfgUsed`); changing config needs a reload.
- Bottom nav is 4 tabs; iPhone X is 375 px wide. Add big features as a **Learn-screen entry** (like the phrasebook / numbers trainer), not a 5th nav tab.
- Dyslexia: body font Lexend, avoid italics (use `<strong>`), keep tap targets ≥48 px. Honest, non-overclaiming copy.

## Roadmap / backlog (ranked, not yet built)
1. Post-conversation coach notes — AI logs each person's 3 recurring mistakes after a scene.
2. Trip-countdown pacing on Progrès once travel dates are set.
3. Listening-comprehension scene — hear a Parisian line, pick the right reply.
4. Phrase pack 2 — menu-decoder French, métro announcements (~+150).
5. Weak-spot review — resurface each person's most-failed cards.
