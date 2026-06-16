// Allez! — Cloudflare Worker proxy for the Anthropic API
//
// Why this exists: the app can't ship with an API key in it (anyone could read
// it from the page source). This tiny worker holds the key as a secret and
// forwards requests. Paste this whole file into a new Cloudflare Worker, then
// add a secret named ANTHROPIC_API_KEY (Worker → Settings → Variables).
//
// The app sends a standard /v1/messages request body; we just add the headers.

export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": request.headers.get("Origin") || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("POST only", { status: 405, headers: cors });
    }
    if (!env.ANTHROPIC_API_KEY) {
      return new Response(
        JSON.stringify({ error: "Worker is missing the ANTHROPIC_API_KEY secret" }),
        { status: 500, headers: { ...cors, "Content-Type": "application/json" } }
      );
    }

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
