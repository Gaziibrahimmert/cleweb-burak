// Contact form endpoint (Vercel Node function).
// Validates the request and forwards it as an e-mail via SMTP.
//
// Environment variables (set in the Vercel project settings):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS  – mail account used for sending
//   MAIL_TO    – recipient (default: arkanburak@gmail.com)
//   MAIL_FROM  – sender address (default: SMTP_USER)
//   MAIL_TRANSPORT=json  – local testing only: build the mail without sending it

const nodemailer = require("nodemailer");

const LIMITS = { name: 100, email: 200, phone: 40, message: 5000 };
const EMAIL_RE = /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/;
const BACK_RE = /^\/(de|tr|en)\/[a-z-]+\.html$/;

// best-effort throttle per warm instance: 5 requests / 10 minutes / IP
const hits = new Map();
function throttled(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < 10 * 60 * 1000);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > 5;
}

function clean(value, max) {
  return String(value == null ? "" : value).replace(/\r\n?/g, "\n").trim().slice(0, max);
}

function oneLine(value) {
  return value.replace(/[\r\n\t]+/g, " ");
}

function validate(body) {
  const data = {
    name: oneLine(clean(body.name, LIMITS.name)),
    email: oneLine(clean(body.email, LIMITS.email)),
    phone: oneLine(clean(body.phone, LIMITS.phone)),
    message: clean(body.message, LIMITS.message),
    consent: body.consent === true || body.consent === "on" || body.consent === "true",
    lang: ["de", "tr", "en"].includes(body.lang) ? body.lang : "de",
  };
  const errors = [];
  if (data.name.length < 2) errors.push("name");
  if (!EMAIL_RE.test(data.email)) errors.push("email");
  if (data.message.length < 2) errors.push("message");
  if (!data.consent) errors.push("consent");
  return { data, errors };
}

function transport() {
  if (process.env.MAIL_TRANSPORT === "json") return nodemailer.createTransport({ jsonTransport: true });
  const port = Number(process.env.SMTP_PORT || 465);
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });
}

function buildMail(d) {
  const to = process.env.MAIL_TO || "arkanburak@gmail.com";
  const from = process.env.MAIL_FROM || process.env.SMTP_USER || to;
  const lines = [
    "Neue Anfrage über das Kontaktformular auf praxis-arkan.de",
    "",
    `Name:     ${d.name}`,
    `E-Mail:   ${d.email}`,
    `Telefon:  ${d.phone || "–"}`,
    `Sprache:  ${d.lang.toUpperCase()}`,
    "",
    "Nachricht:",
    d.message,
    "",
    "—",
    "Die Person hat der Verarbeitung ihrer Angaben laut Datenschutzhinweis zugestimmt.",
    "Antworten Sie direkt auf diese E-Mail, um zu reagieren.",
  ];
  return {
    from: { name: "Website praxis-arkan.de", address: from },
    to,
    replyTo: { name: d.name, address: d.email },
    subject: `Kontaktanfrage: ${d.name}`,
    text: lines.join("\n"),
  };
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const wantsJson = String(req.headers["content-type"] || "").includes("application/json");
  const back = BACK_RE.test(body.back || "") ? body.back : "/de/kontakt.html";
  const reply = (status, payload) => {
    if (wantsJson) return res.status(status).json(payload);
    // plain form post (no JavaScript): send the visitor back to the form
    const flag = payload.ok ? "gesendet=1" : `fehler=${payload.error}`;
    res.setHeader("Location", `${back}?${flag}#formular`);
    return res.status(303).end();
  };

  // honeypot: real visitors never see or fill this field
  if (clean(body.website, 200)) return reply(200, { ok: true });

  const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "unknown";
  if (throttled(ip)) return reply(429, { ok: false, error: "rate" });

  const { data, errors } = validate(body);
  if (errors.length) return reply(422, { ok: false, error: "invalid", fields: errors });

  if (process.env.MAIL_TRANSPORT !== "json") {
    const missing = ["SMTP_HOST", "SMTP_USER", "SMTP_PASS"].filter((k) => !process.env[k]);
    if (missing.length) {
      console.error("contact mail not configured, missing env:", missing.join(", "));
      return reply(503, { ok: false, error: "send" });
    }
  }

  try {
    const info = await transport().sendMail(buildMail(data));
    if (process.env.MAIL_TRANSPORT === "json") console.log(info.message);
    return reply(200, { ok: true });
  } catch (err) {
    // e.g. EAUTH 535 = wrong user/app password, ESOCKET/ETIMEDOUT = wrong host/port
    console.error("contact mail failed:", err && err.code, err && err.responseCode, err && err.message);
    return reply(502, { ok: false, error: "send" });
  }
};
