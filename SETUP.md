# Allez! — setup

Speaking-first French for the Paris trip. One HTML file, no build step, no logins.

---

## 1. Get it live (~2 minutes — same drill as Bookshelf)

1. New GitHub repo (e.g. `Allez`). Drop in: `index.html`, `manifest.json`, `sw.js`, `icon-192.png`, `icon-512.png`.
2. Settings → Pages → deploy from `main`.
3. Open `https://anthonygeo3.github.io/Allez/` on both phones → browser menu → **Add to Home Screen**.

(`worker.js` and this file don't need to be in the repo — harmless if they are.)

**Works immediately, no accounts, offline after first load:**

- 229 trip phrases with audio and phonetic respellings, across café, métro, hotel, shopping, numbers, emergencies and small talk
- Daily smart-repetition drills — the app schedules each phrase for the moment you're about to forget it, separately for each of you
- Speak-and-score: say the French out loud, the mic checks you
- 11 Paris scenarios — **café, boulangerie and asking directions work fully offline** with a scripted Parisian
- Personal 🔥 and household 🏠 streaks (🏠 only counts when you've *both* done a session that day)

Progress saves per device until you do step 2.

---

## 2. Optional — shared sync between your phones (Firebase, ~5 min)

Exactly the Bookshelf pattern. Reuse that Firebase project or make a new one:

1. Firebase console → **Firestore Database** → create (production mode).
2. Project settings → **Add app → Web** → copy the `firebaseConfig` object.
3. Firestore → **Rules** → publish:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    match /allez/{house} { allow read, write: if true; }
    match /allez/{house}/{doc=**} { allow read, write: if true; }
  }
}
```

4. In the app on **both** phones: ⚙️ → paste the config JSON → same household code (default `maison`).

Open rules gated only by the household code — the same trade-off as Bookshelf, and it's only flashcard schedules and streaks.

---

## 3. Optional — live AI conversation (~10 min, unlocks À deux mode)

This turns the scripted Parisian into a real conversation partner that adapts to each of you — and switches on **À deux**, the pass-the-phone couples mode.

1. **API key:** console.anthropic.com → API Keys → create one, add a small amount of credit.
2. **Worker:** dash.cloudflare.com → Workers & Pages → Create Worker → replace the code with `worker.js` → Deploy. Free tier is plenty.
3. **Secret:** in the Worker → Settings → Variables and Secrets → add secret `ANTHROPIC_API_KEY` = your key.
4. **Connect:** in the app → ⚙️ → paste the Worker URL.

Cost: conversations on Haiku are pennies; Sonnet (switchable in ⚙️) is sharper French for a little more. Current rates: https://docs.claude.com/en/docs/about-claude/pricing

**Security note:** anyone who has the Worker URL can spend your credit, so don't post it anywhere public, and set a monthly spend limit in the Anthropic console.

---

## 4. Suggested routine

Ten minutes a day each: one drill session (8–12 cards), then one scenario. Both done = 🏠 streak ticks. À deux on the sofa a couple of evenings a week — the waiter knows who's who and corrects you each by name.

Allez allez allez. 🔴
