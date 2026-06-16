# Allez! — upgrade runbook (for the 16th)

Both upgrades, click by click. Order matters slightly: deploy first, Firebase second, AI third. About 20 minutes all in. Use the **allez.zip attached alongside this file** — it contains two small app changes that make this runbook work: a 🤖 *Test AI connection* button in ⚙️, and the Firebase box now accepts the config exactly as the console hands it to you (the console gives you JavaScript, not JSON — the original build would have choked on it).

---

## Step 0 — base deploy (if not already done)

- [ ] New GitHub repo (e.g. `Allez`) → drop in `index.html`, `manifest.json`, `sw.js`, `icon-192.png`, `icon-512.png`
- [ ] Settings → Pages → deploy from `main`
- [ ] Open `https://anthonygeo3.github.io/Allez/` on **both** phones → Add to Home Screen
- [ ] Each of you opens it once and picks your profile

---

## Upgrade 1 — shared sync (Firebase) · ~5 min

**Recommended: reuse the Bookshelf project.** One console, no new project, the `allez` collection sits alongside Bookshelf's data without touching it.

1. [ ] console.firebase.google.com → open the Bookshelf project
2. [ ] **Firestore Database → Rules.** ⚠️ **Add, don't replace** — if you overwrite, Bookshelf breaks. Keep everything that's there and add these two lines *inside* the existing `match /databases/{db}/documents { ... }` block:

```
match /allez/{house} { allow read, write: if true; }
match /allez/{house}/{doc=**} { allow read, write: if true; }
```

3. [ ] **Publish.** (If you do slip, the Rules tab keeps version history — restore the old one and re-add.)
4. [ ] **Get the config:** ⚙️ Project settings → General → Your apps → your web app → SDK setup and configuration → Config. Copy the whole `const firebaseConfig = {...};` block. The same config serves both apps — it identifies the *project*, not the app.
5. [ ] **Your phone:** Allez ⚙️ → paste the config into the Firebase box → household code `maison` (or pick your own) → **Save settings**. Expect the toast *"Firebase connected — progress now syncs"*; reopen ⚙️ and it should read *"Sync: Connected ✓ shared with Amy"*.
6. [ ] **Amy's phone:** same paste, **same household code**, Save.
7. [ ] **Verify:** do one drill card on your phone → open **Progrès** on Amy's → your numbers appear within ~10 seconds.

*New project instead?* SETUP.md §2 steps 1–3, then continue from step 4 here.

---

## Upgrade 2 — live AI conversation (Cloudflare Worker) · ~10 min

### Part A — Anthropic API key (3 min)

1. [ ] console.anthropic.com → sign in
2. [ ] **Billing** → add a small top-up, and **set a monthly spend limit** — a fiver's worth lasts ages at conversation rates (current pricing: https://docs.claude.com/en/docs/about-claude/pricing)
3. [ ] **API Keys → Create Key** → name it `allez` → copy it now (starts `sk-ant-`, shown once)

### Part B — the Worker (5 min)

1. [ ] dash.cloudflare.com → sign up (free tier, plenty for this)
2. [ ] **Workers & Pages → Create → Create Worker** → name it `allez` → **Deploy** (the hello-world it offers)
3. [ ] **Edit code** → select all → delete → paste the contents of `worker.js` → **Deploy**
4. [ ] Back on the worker's page → **Settings → Variables and Secrets → Add** → type **Secret** → name exactly `ANTHROPIC_API_KEY` → value = your key → save/deploy
5. [ ] Copy the worker URL — it looks like `https://allez.<your-subdomain>.workers.dev`

### Part C — smoke test from a terminal (optional, 1 min)

```bash
curl -s https://allez.YOURNAME.workers.dev -X POST \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":40,"messages":[{"role":"user","content":"Say bonjour"}]}'
```

JSON containing "Bonjour" = working. `authentication_error` = secret missing or misnamed.

### Part D — connect the app (1 min)

1. [ ] Allez ⚙️ → paste the Worker URL → tap **🤖 Test AI connection** → expect *"✓ AI connected — Bonjour Anthony et Amy !"*
2. [ ] **Save settings.** Parler is now a live conversation partner and the **À deux** tab is unlocked.
3. [ ] Model: start on **Haiku** (fast, pennies). Flip to **Sonnet** in ⚙️ when you want sharper, more natural French.

---

## Upgrade 3 — premium studio audio (optional, ~5 min on your PC)

Phone text-to-speech quality varies a lot — Android's French is decent, the iPhone's stock voice less so. This bakes one identical neural-voice MP3 per phrase into the app, so both phones hear the same studio-quality French (and it's offline once cached). Worth it mainly for Amy's iPhone; on your Pixel the built-in voice is already fine, especially with an Enhanced voice installed.

It's a one-off run on your always-on PC — no account, free:

1. [ ] `pip install edge-tts`
2. [ ] Put `make_audio.py` next to `index.html` and run `python make_audio.py` (it reads the phrases straight out of `index.html`, writes an `audio/` folder + manifest). Default voice is `fr-FR-DeniseNeural`; `--voice fr-FR-HenriNeural` for male.
3. [ ] Commit the new `audio/` folder to the repo alongside `index.html`.
4. [ ] Done — the app auto-detects it. ⚙️ will show *"🎧 Premium audio pack active"*, and drills + phrasebook switch to it automatically. Delete the folder to revert to phone TTS.

(`make_audio.py` has a header comment with a second engine option and full notes.)

---

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| Toast: *"switching to the built-in scripted scene"* | App can't reach the worker. URL typo (needs `https://`, no trailing space) or worker not deployed. |
| Test button: *✗ HTTP 401* | Secret missing/misnamed. Must be exactly `ANTHROPIC_API_KEY`; re-deploy after adding. |
| Test button: *✗ HTTP 400* | Usually billing — no credit on the Anthropic account. Console → Billing. |
| Test button: *✗ HTTP 429* | Rate limit or credit exhausted. Console → Billing. |
| *✗ Failed to fetch* | Worker URL wrong, or you're testing on plain `file://` — use the Pages URL. |
| ⚙️ shows *"Sync: Error: …"* | Config pasted partially. Paste the **whole** block, braces included (JS or JSON both fine now). |
| Amy's progress not appearing | Both phones must show *Connected ✓* and the **same** household code. Changes push ~1s after you grade a card; give it ten seconds. |
| Bookshelf broke after editing rules | You replaced instead of added. Rules tab → version history → restore, then add the two `allez` lines inside the existing block. |

## Costs, honestly

Firebase free tier covers this forever (it's kilobytes). Cloudflare free tier likewise. The only real cost is the API key — conversations on Haiku are pennies, and the spend limit you set in Part A is the backstop.

If anything throws an error not in the table, bring the exact message back to the chat and we'll fix it from there.

Allez allez allez. 🔴
