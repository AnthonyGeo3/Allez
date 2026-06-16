#!/usr/bin/env python3
"""
make_audio.py — generate the Allez! premium audio pack.

Reads the phrase library straight out of index.html, synthesizes one MP3 per
phrase with a neural French voice, and writes an audio/ folder + manifest.
Drop the audio/ folder into the repo next to index.html; the app detects it
automatically and switches phrase playback from device TTS to these files
(identical studio voice on both phones, offline once played).

Two engines:

  EDGE (default — free, no account, unofficial)
      pip install edge-tts
      python make_audio.py
    Uses Microsoft Edge's neural voices via the edge-tts package. Voices:
    fr-FR-DeniseNeural (default, female) or fr-FR-HenriNeural (male).
    Caveat: it's an unofficial wrapper around a public endpoint — fine for a
    one-off personal generation, but it could stop working someday.

  GOOGLE (official, sturdier — needs billing enabled on your GCP project)
      Enable "Cloud Text-to-Speech API" on your Firebase/GCP project,
      create an API key, then:
      TTS_API_KEY=AIza... python make_audio.py --engine google
    Voice: fr-FR-Neural2-A by default. ~7k characters total — comfortably
    inside the monthly free tier, so effectively £0, but billing must be on.

Re-runnable: existing MP3s are skipped, so you can resume or regenerate
selectively by deleting files.

  python make_audio.py --voice fr-FR-HenriNeural    # male voice (edge)
  python make_audio.py --engine google --voice fr-FR-Neural2-B
"""

import argparse, base64, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audio")

PHRASE_RE = re.compile(r'^P\("((?:[^"\\]|\\.)*)","(?:[^"\\]|\\.)*","(?:[^"\\]|\\.)*","\w+",\d\)', re.M)

def load_phrases():
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        html = f.read()
    frs = [m.group(1) for m in PHRASE_RE.finditer(html)]
    if len(frs) < 200:
        sys.exit(f"Only found {len(frs)} phrases in index.html — aborting (expected ~229).")
    # ids must match the app's PHRASES.forEach((p,i)=>p.id="p"+i) — same file order
    return [(f"p{i}", fr) for i, fr in enumerate(frs)]

def synth_edge(text, voice, path):
    import asyncio, edge_tts
    async def run():
        await edge_tts.Communicate(text, voice).save(path)
    asyncio.run(run())

def synth_google(text, voice, path, key):
    body = json.dumps({
        "input": {"text": text},
        "voice": {"languageCode": "fr-FR", "name": voice},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.95},
    }).encode()
    req = urllib.request.Request(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}",
        data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        audio = json.load(r)["audioContent"]
    with open(path, "wb") as f:
        f.write(base64.b64decode(audio))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["edge", "google"], default="edge")
    ap.add_argument("--voice", default=None)
    args = ap.parse_args()

    voice = args.voice or ("fr-FR-DeniseNeural" if args.engine == "edge" else "fr-FR-Neural2-A")
    key = os.environ.get("TTS_API_KEY", "")
    if args.engine == "google" and not key:
        sys.exit("Set TTS_API_KEY=<your Google API key> for --engine google.")
    if args.engine == "edge":
        try:
            import edge_tts  # noqa
        except ImportError:
            sys.exit("pip install edge-tts   (then re-run)")

    phrases = load_phrases()
    os.makedirs(OUT, exist_ok=True)
    files, made, skipped, failed = {}, 0, 0, []

    for pid, fr in phrases:
        fname = f"{pid}.mp3"
        path = os.path.join(OUT, fname)
        if os.path.exists(path) and os.path.getsize(path) > 200:
            files[pid] = fname; skipped += 1; continue
        try:
            (synth_edge if args.engine == "edge" else
             lambda t, v, p: synth_google(t, v, p, key))(fr, voice, path)
            files[pid] = fname; made += 1
            print(f"  ✓ {pid}  {fr[:48]}")
        except Exception as e:
            failed.append(pid)
            print(f"  ✗ {pid}  {fr[:40]}  ({e})", file=sys.stderr)

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"engine": args.engine, "voice": voice, "files": files}, f, indent=0)

    print(f"\nDone: {made} generated, {skipped} already present, {len(failed)} failed.")
    if failed:
        print("Re-run the same command to retry the failures.")
    print(f"Manifest: audio/manifest.json ({len(files)} entries)")
    print("Now commit the audio/ folder to the repo — the app picks it up automatically.")

if __name__ == "__main__":
    main()
