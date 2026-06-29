// Allez! — Cloudflare Worker. Two jobs in one Worker:
//   1. POST /      → proxies to the Anthropic API (live conversation + À deux).
//                    Needs the secret  ANTHROPIC_API_KEY.
//   2. POST /stt   → speech-to-text via Workers AI Whisper, so the 🎙️
//                    pronunciation check works on iPhone (where the browser's
//                    own speech recognition is broken). Needs the  AI  binding.
//
// Full setup is in UPGRADES.md §2. You need BOTH of these on the Worker:
//   • Secret   ANTHROPIC_API_KEY   (Settings → Variables and Secrets → add Secret)
//   • Binding  AI = Workers AI     (Settings → Bindings → add → Workers AI, name it AI)

export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": request.headers.get("Origin") || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "POST") return new Response("POST only", { status: 405, headers: cors });

    const url = new URL(request.url);

    // --- 2. Speech-to-text route ---
    if (url.pathname.replace(/\/+$/, "").endsWith("/stt")) {
      if (!env.AI) return json({ error: "Worker is missing the AI (Workers AI) binding — see UPGRADES.md §2" }, 500, cors);
      try {
        const buf = await request.arrayBuffer();
        if (!buf || buf.byteLength < 1200) return json({ text: "" }, 200, cors); // empty / too short to be speech
        const prompt = url.searchParams.get("p") || "";
        const input = {
          audio: toBase64(buf),
          language: "fr",
          task: "transcribe",
          condition_on_previous_text: false, // curbs hallucinated runaway transcriptions
        };
        if (prompt) input.initial_prompt = prompt; // bias toward the phrase the learner is attempting
        const out = await env.AI.run("@cf/openai/whisper-large-v3-turbo", input);
        return json({ text: (out && out.text ? out.text : "").trim() }, 200, cors);
      } catch (e) {
        return json({ error: String((e && e.message) || e) }, 500, cors);
      }
    }

    // --- 1. Anthropic conversation proxy (default route) ---
    if (!env.ANTHROPIC_API_KEY) return json({ error: "Worker is missing the ANTHROPIC_API_KEY secret — see UPGRADES.md §2" }, 500, cors);
    const upstream = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: await request.text(),
    });
    const res = new Response(upstream.body, upstream);
    for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
    return res;
  },
};

// base64-encode without needing the Node Buffer polyfill (clips are small)
function toBase64(buf) {
  const b = new Uint8Array(buf);
  let s = "";
  const chunk = 0x8000;
  for (let i = 0; i < b.length; i += chunk) s += String.fromCharCode.apply(null, b.subarray(i, i + chunk));
  return btoa(s);
}
function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json" } });
}
