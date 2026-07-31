/* KalTrack — Kalorien-Tracker
 * Reine Frontend-App. Lebensmitteldaten kommen live von Open Food Facts,
 * das Tagebuch wird lokal im Browser (localStorage) gespeichert. */

const OFF = "https://world.openfoodfacts.org";
const $ = (sel) => document.querySelector(sel);

/* ---------- Zustand ---------- */
const state = {
  date: todayKey(),
  goal: Number(localStorage.getItem("kt_goal")) || 2000,
  pending: null, // aktuell im Portions-Dialog gewähltes Produkt
};

function todayKey(d = new Date()) {
  return d.toISOString().slice(0, 10); // YYYY-MM-DD (lokaler Tag reicht für uns)
}
function diaryKey(date) { return "kt_diary_" + date; }
function loadDiary(date) {
  try { return JSON.parse(localStorage.getItem(diaryKey(date))) || []; }
  catch { return []; }
}
function saveDiary(date, entries) {
  localStorage.setItem(diaryKey(date), JSON.stringify(entries));
}

/* ---------- Hilfen ---------- */
function num(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function round(n) { return Math.round(n); }

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.add("hidden"), 2200);
}

/* Formt ein Open-Food-Facts-Produkt in unser einfaches Modell. */
function normalizeProduct(p) {
  const n = p.nutriments || {};
  const kcal100 =
    num(n["energy-kcal_100g"]) ||
    (num(n["energy_100g"]) ? num(n["energy_100g"]) / 4.184 : 0);
  return {
    code: p.code || "",
    name: p.product_name || p.generic_name || "Unbenanntes Produkt",
    brand: (p.brands || "").split(",")[0].trim(),
    img: p.image_front_small_url || p.image_small_url || "",
    kcal100: round(kcal100),
    prot100: num(n["proteins_100g"]),
    carb100: num(n["carbohydrates_100g"]),
    fat100: num(n["fat_100g"]),
    serving: num(p.serving_quantity) || 0,
  };
}

/* ---------- Tagesübersicht ---------- */
function renderSummary() {
  const entries = loadDiary(state.date);
  const sum = entries.reduce(
    (a, e) => {
      a.kcal += e.kcal; a.prot += e.prot; a.carb += e.carb; a.fat += e.fat;
      return a;
    },
    { kcal: 0, prot: 0, carb: 0, fat: 0 }
  );

  $("#kcalEaten").textContent = round(sum.kcal);
  $("#kcalGoal").textContent = "/ " + state.goal + " kcal";
  const left = state.goal - sum.kcal;
  $("#kcalLeft").textContent =
    left >= 0 ? round(left) + " übrig" : round(-left) + " drüber";
  $("#kcalLeft").style.color = left >= 0 ? "var(--accent)" : "var(--danger)";

  $("#mProt").textContent = round(sum.prot) + " g";
  $("#mCarb").textContent = round(sum.carb) + " g";
  $("#mFat").textContent = round(sum.fat) + " g";

  const C = 2 * Math.PI * 52; // Ringumfang
  const pct = Math.min(sum.kcal / state.goal, 1);
  const ring = $("#ringFg");
  ring.style.strokeDashoffset = String(C * (1 - pct));
  ring.style.stroke = left >= 0 ? "var(--accent)" : "var(--danger)";
}

/* ---------- Tagebuch ---------- */
function renderDiary() {
  const list = $("#entryList");
  const entries = loadDiary(state.date);
  list.innerHTML = "";
  $("#diaryEmpty").classList.toggle("hidden", entries.length > 0);

  entries.forEach((e, i) => {
    const li = document.createElement("li");
    li.className = "entry";
    const portion = e.est ? "📸 Portion (KI)" : round(e.amount) + " g";
    li.innerHTML = `
      <img class="entry-thumb" src="${e.img || ""}" alt="" onerror="this.style.visibility='hidden'"/>
      <div class="entry-main">
        <div class="entry-name">${escapeHtml(e.name)}</div>
        <div class="entry-sub">${portion} · E ${round(e.prot)}g · KH ${round(e.carb)}g · F ${round(e.fat)}g</div>
      </div>
      <div class="entry-kcal">${round(e.kcal)}</div>
      <button class="entry-del" data-i="${i}" aria-label="Löschen">×</button>`;
    list.appendChild(li);
  });

  list.querySelectorAll(".entry-del").forEach((b) => {
    b.addEventListener("click", () => {
      const entries = loadDiary(state.date);
      entries.splice(Number(b.dataset.i), 1);
      saveDiary(state.date, entries);
      renderDiary();
      renderSummary();
    });
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------- Ansichten wechseln ---------- */
function switchView(view) {
  document.querySelectorAll(".view").forEach((v) => v.classList.add("hidden"));
  $("#view-" + view).classList.remove("hidden");
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.view === view));
  if (view !== "scan") stopScan();
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => switchView(tab.dataset.view));
});

/* ---------- Suche (Open Food Facts) ---------- */
async function doSearch(term) {
  const hint = $("#searchHint");
  const list = $("#searchResults");
  list.innerHTML = "";
  hint.innerHTML = '<div class="spinner"></div>';
  try {
    const url =
      `${OFF}/cgi/search.pl?search_terms=${encodeURIComponent(term)}` +
      `&search_simple=1&action=process&json=1&page_size=25` +
      `&fields=code,product_name,generic_name,brands,image_front_small_url,image_small_url,nutriments,serving_quantity`;
    const res = await fetch(url);
    const data = await res.json();
    const products = (data.products || [])
      .map(normalizeProduct)
      .filter((p) => p.kcal100 > 0);

    hint.textContent = products.length
      ? `${products.length} Treffer für „${term}"`
      : `Keine Treffer für „${term}". Versuch es allgemeiner.`;
    renderResults(products);
  } catch (err) {
    hint.textContent = "Suche fehlgeschlagen — Internetverbindung?";
  }
}

function renderResults(products) {
  const list = $("#searchResults");
  list.innerHTML = "";
  products.forEach((p) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "result";
    btn.innerHTML = `
      <img class="result-thumb" src="${p.img || ""}" alt="" onerror="this.style.visibility='hidden'"/>
      <div class="result-main">
        <div class="result-name">${escapeHtml(p.name)}</div>
        <div class="result-sub">${escapeHtml(p.brand || "—")}</div>
      </div>
      <div class="result-kcal">${p.kcal100} kcal<br><span style="color:var(--muted);font-weight:400">/100g</span></div>`;
    btn.addEventListener("click", () => openPortion(p));
    li.appendChild(btn);
    list.appendChild(li);
  });
}

$("#searchBtn").addEventListener("click", () => {
  const t = $("#searchInput").value.trim();
  if (t) doSearch(t);
});
$("#searchInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { const t = e.target.value.trim(); if (t) doSearch(t); }
});

/* ---------- Barcode-Suche ---------- */
async function lookupBarcode(code) {
  toast("Suche Barcode " + code + " …");
  try {
    const res = await fetch(
      `${OFF}/api/v2/product/${encodeURIComponent(code)}.json` +
      `?fields=code,product_name,generic_name,brands,image_front_small_url,image_small_url,nutriments,serving_quantity`);
    const data = await res.json();
    if (data.status === 1 && data.product) {
      openPortion(normalizeProduct(data.product));
    } else {
      toast("Produkt nicht in der Datenbank gefunden.");
    }
  } catch {
    toast("Abfrage fehlgeschlagen — Internetverbindung?");
  }
}

$("#manualBtn").addEventListener("click", () => {
  const c = $("#manualBarcode").value.trim();
  if (c) lookupBarcode(c);
});

/* ---------- Kamera-Scanner ----------
 * Nutzt den nativen BarcodeDetector (Android/Chrome), sonst ZXing als Fallback
 * (iOS/Safari kann BarcodeDetector noch nicht). Beide rufen lookupBarcode(). */
let stream = null;         // MediaStream (nativer Pfad)
let detector = null;       // BarcodeDetector-Instanz
let scanning = false;      // Loop-Flag (nativer Pfad)
let zxingReader = null;    // ZXing-Reader (Fallback)

function onScanned(code) {
  stopScan();
  if (navigator.vibrate) navigator.vibrate(60);
  lookupBarcode(code);
}

async function startScan() {
  const hint = $("#scanHint");
  $("#startScanBtn").classList.add("hidden");
  $("#stopScanBtn").classList.remove("hidden");
  const video = $("#video");

  try {
    if ("BarcodeDetector" in window) {
      // Nativer Pfad (Android/Chrome)
      detector = detector || new BarcodeDetector({
        formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"],
      });
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      video.srcObject = stream;
      await video.play();
      scanning = true;
      hint.textContent = "Kamera läuft — Barcode ins grüne Feld halten.";
      scanLoop();
    } else if (window.ZXing && ZXing.BrowserMultiFormatReader) {
      // Fallback (iOS/Safari) — ZXing verwaltet die Kamera selbst
      zxingReader = new ZXing.BrowserMultiFormatReader();
      hint.textContent = "Kamera läuft — Barcode ins grüne Feld halten.";
      await zxingReader.decodeFromConstraints(
        { video: { facingMode: "environment" } },
        video,
        (result) => { if (result) onScanned(result.getText()); }
      );
    } else {
      throw new Error("kein Scanner verfügbar");
    }
  } catch (err) {
    stopScan();
    hint.textContent =
      "Kamerazugriff nicht möglich. Erlaube die Kamera in den Einstellungen oder nutze die manuelle Eingabe.";
  }
}

async function scanLoop() {
  if (!scanning) return;
  const video = $("#video");
  try {
    const codes = await detector.detect(video);
    if (codes.length) { onScanned(codes[0].rawValue); return; }
  } catch { /* einzelne Frames dürfen fehlschlagen */ }
  requestAnimationFrame(scanLoop);
}

function stopScan() {
  scanning = false;
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
  if (zxingReader) { try { zxingReader.reset(); } catch {} zxingReader = null; }
  const v = $("#video");
  if (v) v.srcObject = null;
  $("#startScanBtn").classList.remove("hidden");
  $("#stopScanBtn").classList.add("hidden");
}

$("#startScanBtn").addEventListener("click", startScan);
$("#stopScanBtn").addEventListener("click", () => { stopScan(); $("#scanHint").textContent = "Scan gestoppt."; });

/* ---------- Foto → KI-Kalorienschätzung ----------
 * Nutzt Claude Vision (Anthropic). Der API-Schlüssel des Nutzers liegt lokal
 * im Browser und wird direkt an api.anthropic.com gesendet. */
const AI_MODEL = "claude-sonnet-5";
let photoBase64 = null; // aktuelles Foto als JPEG-Base64 (ohne data:-Prefix)

function getApiKey() { return localStorage.getItem("kt_apikey") || ""; }

/* Skaliert das Foto herunter (spart Tokens) und liefert JPEG-Base64. */
function fileToScaledBase64(file, maxSize = 1024) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale);
      const h = Math.round(img.height * scale);
      const canvas = document.createElement("canvas");
      canvas.width = w; canvas.height = h;
      canvas.getContext("2d").drawImage(img, 0, 0, w, h);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
      URL.revokeObjectURL(img.src);
      resolve(dataUrl.split(",")[1]);
    };
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
}

$("#photoInput").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const preview = $("#photoPreview");
  preview.src = URL.createObjectURL(file);
  preview.classList.remove("hidden");
  $("#photoPlaceholder").classList.add("hidden");
  $("#estimateResult").innerHTML = "";
  $("#estimateBtn").classList.remove("hidden");
  $("#aiEstimateBtn").classList.remove("hidden");
  try {
    photoBase64 = await fileToScaledBase64(file);
  } catch {
    toast("Foto konnte nicht gelesen werden.");
  }
});

/* ===== Gratis-Erkennung auf dem Gerät (TensorFlow.js MobileNet) =====
 * Läuft komplett im Browser, keine Kosten, keine Daten verlassen das Gerät.
 * Erkennt gängige Lebensmittel und schätzt eine typische Portion. */
const DEFAULT_PHOTO_HINT = $("#photoHint").textContent;

// Erkanntes ImageNet-Label -> typische Portion (Gesamtwerte). Schlüsselwörter
// werden im Klassennamen gesucht (z. B. "banana", "pizza, pizza pie").
const FOOD_MAP = [
  { keys: ["banana"], name: "Banane", kcal: 105, prot: 1, carb: 27, fat: 0 },
  { keys: ["orange"], name: "Orange", kcal: 62, prot: 1, carb: 15, fat: 0 },
  { keys: ["lemon"], name: "Zitrone", kcal: 17, prot: 1, carb: 5, fat: 0 },
  { keys: ["pineapple", "ananas"], name: "Ananas (Portion)", kcal: 82, prot: 1, carb: 22, fat: 0 },
  { keys: ["granny smith", "apple"], name: "Apfel", kcal: 95, prot: 0, carb: 25, fat: 0 },
  { keys: ["strawberry"], name: "Erdbeeren (Portion)", kcal: 49, prot: 1, carb: 12, fat: 0 },
  { keys: ["pomegranate"], name: "Granatapfel", kcal: 130, prot: 3, carb: 33, fat: 2 },
  { keys: ["fig"], name: "Feige", kcal: 37, prot: 0, carb: 10, fat: 0 },
  { keys: ["pizza"], name: "Pizza (Stück)", kcal: 285, prot: 12, carb: 36, fat: 10 },
  { keys: ["cheeseburger"], name: "Cheeseburger", kcal: 300, prot: 15, carb: 30, fat: 14 },
  { keys: ["hotdog", "hot dog"], name: "Hotdog", kcal: 290, prot: 11, carb: 24, fat: 17 },
  { keys: ["bagel"], name: "Bagel", kcal: 250, prot: 10, carb: 48, fat: 2 },
  { keys: ["pretzel"], name: "Brezel", kcal: 230, prot: 6, carb: 47, fat: 2 },
  { keys: ["french loaf", "baguette"], name: "Baguette (Portion)", kcal: 185, prot: 6, carb: 35, fat: 2 },
  { keys: ["guacamole"], name: "Guacamole", kcal: 150, prot: 2, carb: 8, fat: 13 },
  { keys: ["burrito"], name: "Burrito", kcal: 450, prot: 20, carb: 50, fat: 18 },
  { keys: ["ice cream", "icecream"], name: "Eis (Portion)", kcal: 207, prot: 4, carb: 24, fat: 11 },
  { keys: ["ice lolly", "popsicle"], name: "Eis am Stiel", kcal: 80, prot: 0, carb: 20, fat: 0 },
  { keys: ["espresso", "coffee"], name: "Espresso", kcal: 3, prot: 0, carb: 0, fat: 0 },
  { keys: ["red wine"], name: "Rotwein (Glas)", kcal: 125, prot: 0, carb: 4, fat: 0 },
  { keys: ["broccoli"], name: "Brokkoli (Portion)", kcal: 55, prot: 4, carb: 11, fat: 1 },
  { keys: ["cauliflower"], name: "Blumenkohl (Portion)", kcal: 50, prot: 4, carb: 10, fat: 0 },
  { keys: ["cucumber"], name: "Gurke", kcal: 16, prot: 1, carb: 4, fat: 0 },
  { keys: ["mushroom"], name: "Champignons (Portion)", kcal: 22, prot: 3, carb: 3, fat: 0 },
  { keys: ["bell pepper"], name: "Paprika", kcal: 30, prot: 1, carb: 7, fat: 0 },
  { keys: ["corn", "ear"], name: "Maiskolben", kcal: 125, prot: 4, carb: 27, fat: 2 },
  { keys: ["mashed potato"], name: "Kartoffelpüree (Portion)", kcal: 215, prot: 4, carb: 35, fat: 7 },
  { keys: ["meat loaf", "meatloaf"], name: "Hackbraten (Portion)", kcal: 290, prot: 22, carb: 8, fat: 19 },
  { keys: ["carbonara", "spaghetti"], name: "Spaghetti (Portion)", kcal: 450, prot: 16, carb: 60, fat: 15 },
  { keys: ["zucchini", "courgette"], name: "Zucchini (Portion)", kcal: 33, prot: 2, carb: 6, fat: 1 },
  { keys: ["squash"], name: "Kürbis (Portion)", kcal: 45, prot: 1, carb: 11, fat: 0 },
  { keys: ["artichoke"], name: "Artischocke", kcal: 60, prot: 4, carb: 13, fat: 0 },
  { keys: ["cabbage"], name: "Kohl (Portion)", kcal: 25, prot: 1, carb: 6, fat: 0 },
  { keys: ["trifle"], name: "Dessert (Portion)", kcal: 250, prot: 4, carb: 35, fat: 11 },
  { keys: ["chocolate sauce", "chocolate"], name: "Schokolade (Portion)", kcal: 210, prot: 3, carb: 24, fat: 12 },
  { keys: ["dough", "pretzel"], name: "Teiggebäck (Portion)", kcal: 250, prot: 6, carb: 42, fat: 7 },
  { keys: ["hotpot", "hot pot", "soup", "consomme"], name: "Eintopf/Suppe (Portion)", kcal: 200, prot: 12, carb: 20, fat: 8 },
];

function matchFood(preds) {
  for (const p of preds) {
    const label = (p.className || "").toLowerCase();
    for (const f of FOOD_MAP) {
      if (f.keys.some((k) => label.includes(k))) {
        return { food: f, className: p.className, prob: p.probability };
      }
    }
  }
  return null;
}

let mnModel = null;
let mnLoading = null;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src;
    s.onload = resolve;
    s.onerror = () => reject(new Error("Skript nicht geladen: " + src));
    document.head.appendChild(s);
  });
}

async function ensureModel() {
  if (mnModel) return mnModel;
  if (!mnLoading) {
    mnLoading = (async () => {
      if (!window.tf)
        await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js");
      if (!window.mobilenet)
        await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js");
      mnModel = await window.mobilenet.load({ version: 2, alpha: 1.0 });
      return mnModel;
    })();
  }
  return mnLoading;
}

async function estimatePhotoLocal() {
  if (!photoBase64) { toast("Bitte zuerst ein Foto wählen."); return; }
  const btn = $("#estimateBtn");
  const out = $("#estimateResult");
  btn.disabled = true;
  out.innerHTML = '<div class="spinner"></div>';
  $("#photoHint").textContent = "Erkennungs-Modell wird geladen (einmalig, dann offline nutzbar)…";
  try {
    const model = await ensureModel();
    const img = new Image();
    img.src = "data:image/jpeg;base64," + photoBase64;
    await img.decode();
    const preds = await model.classify(img, 5);
    const m = matchFood(preds);
    if (!m) { out.innerHTML = ""; renderNoMatch(preds); return; }
    renderEstimate({
      name: m.food.name,
      kcal: m.food.kcal, prot: m.food.prot, carb: m.food.carb, fat: m.food.fat,
      items: [],
      note: `Erkannt: ${m.className} (${Math.round(m.prob * 100)} %). Grobe Schätzung für eine typische Portion – Menge kann abweichen.`,
    });
  } catch {
    out.innerHTML = "";
    toast("Erkennung fehlgeschlagen – Internetverbindung fürs erste Laden nötig.");
  } finally {
    btn.disabled = false;
    $("#photoHint").textContent = DEFAULT_PHOTO_HINT;
  }
}

function renderNoMatch(preds) {
  const guesses = (preds || []).slice(0, 3)
    .map((p) => `<li>• ${escapeHtml(p.className)} (${Math.round(p.probability * 100)} %)</li>`).join("");
  $("#estimateResult").innerHTML = `
    <div class="est-name">Nicht sicher erkannt 🤔</div>
    <div class="est-note">Das Gratis-Modell erkennt vor allem gängige Einzel-Lebensmittel.
      Für dieses Bild nutze besser die <b>Suche</b> oder den <b>Barcode</b> – oder probiere die genaue KI-Variante.</div>
    ${guesses ? `<div class="p-per100">Vermutungen:</div><ul class="est-guesses">${guesses}</ul>` : ""}`;
}

$("#estimateBtn").addEventListener("click", estimatePhotoLocal);

const AI_PROMPT =
  "Du bist ein Ernährungsexperte. Schätze für das auf dem Foto gezeigte Essen " +
  "die Nährwerte der SICHTBAREN PORTION, so genau wie möglich (Schätzung ist ok). " +
  "Antworte AUSSCHLIESSLICH mit reinem JSON, ohne Markdown, in diesem Format: " +
  '{"name":"Name des Gerichts","kcal":Zahl,"prot":Zahl,"carb":Zahl,"fat":Zahl,' +
  '"items":["Zutat 1","Zutat 2"],"note":"kurzer Hinweis zu Annahmen (Portionsgröße etc.)"}. ' +
  "kcal/prot/carb/fat sind Gesamtwerte für die Portion (Gramm bei Makros). " +
  'Ist kein Essen zu erkennen: {"name":"Kein Essen erkannt","kcal":0,"prot":0,"carb":0,"fat":0,"items":[],"note":"..."}.';

async function estimatePhotoAI() {
  const key = getApiKey();
  if (!key) { openSheet("keySheet", "keyBackdrop"); return; }
  if (!photoBase64) { toast("Bitte zuerst ein Foto wählen."); return; }

  const btn = $("#aiEstimateBtn");
  const out = $("#estimateResult");
  btn.disabled = true;
  out.innerHTML = '<div class="spinner"></div>';

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: AI_MODEL,
        max_tokens: 1024,
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "base64", media_type: "image/jpeg", data: photoBase64 } },
            { type: "text", text: AI_PROMPT },
          ],
        }],
      }),
    });

    if (!res.ok) {
      const status = res.status;
      out.innerHTML = "";
      if (status === 401) toast("API-Schlüssel ungültig. Bitte prüfen.");
      else if (status === 429) toast("Zu viele Anfragen – kurz warten.");
      else toast("KI-Anfrage fehlgeschlagen (" + status + ").");
      return;
    }

    const data = await res.json();
    const text = (data.content || []).map((b) => b.text || "").join("");
    const est = parseEstimate(text);
    if (!est) { out.innerHTML = ""; toast("Antwort nicht verständlich – nochmal versuchen."); return; }
    renderEstimate(est);
  } catch {
    out.innerHTML = "";
    toast("Netzwerkfehler – Internetverbindung?");
  } finally {
    btn.disabled = false;
  }
}

/* Robust: extrahiert das erste JSON-Objekt aus der Antwort. */
function parseEstimate(text) {
  try { return JSON.parse(text); } catch {}
  const s = text.indexOf("{"), e = text.lastIndexOf("}");
  if (s >= 0 && e > s) { try { return JSON.parse(text.slice(s, e + 1)); } catch {} }
  return null;
}

function renderEstimate(est) {
  const out = $("#estimateResult");
  const kcal = round(num(est.kcal));
  const items = Array.isArray(est.items) ? est.items : [];
  out.innerHTML = `
    <div class="est-name">${escapeHtml(est.name || "Essen")}</div>
    <div class="p-per100">${kcal} kcal · E ${round(num(est.prot))}g · KH ${round(num(est.carb))}g · F ${round(num(est.fat))}g</div>
    ${items.length ? `<ul class="est-items">${items.map((i) => `<li>• ${escapeHtml(i)}</li>`).join("")}</ul>` : ""}
    ${est.note ? `<div class="est-note">ℹ️ ${escapeHtml(est.note)}</div>` : ""}
    <div class="sheet-actions">
      <button id="estAdd" type="button" class="primary">Ins Tagebuch</button>
    </div>`;
  $("#estAdd").addEventListener("click", () => {
    if (kcal <= 0) { toast("Kein Essen erkannt."); return; }
    const entries = loadDiary(state.date);
    entries.push({
      name: est.name || "Essen (Foto)", img: "", est: true,
      kcal, prot: num(est.prot), carb: num(est.carb), fat: num(est.fat),
    });
    saveDiary(state.date, entries);
    renderDiary();
    renderSummary();
    switchView("diary");
    toast((est.name || "Essen") + " hinzugefügt ✓");
  });
}

$("#aiEstimateBtn").addEventListener("click", estimatePhotoAI);
$("#apiKeyBtn").addEventListener("click", () => {
  $("#keyInput").value = getApiKey();
  openSheet("keySheet", "keyBackdrop");
});
$("#keySave").addEventListener("click", () => {
  const k = $("#keyInput").value.trim();
  if (k) { localStorage.setItem("kt_apikey", k); toast("Schlüssel gespeichert ✓"); }
  closeSheet("keySheet", "keyBackdrop");
});
$("#keyClear").addEventListener("click", () => {
  localStorage.removeItem("kt_apikey");
  $("#keyInput").value = "";
  toast("Schlüssel gelöscht.");
  closeSheet("keySheet", "keyBackdrop");
});
$("#keyBackdrop").addEventListener("click", () => closeSheet("keySheet", "keyBackdrop"));

/* ---------- Portions-Dialog ---------- */
function openPortion(product) {
  state.pending = product;
  $("#pName").textContent = product.name;
  $("#pBrand").textContent = product.brand || "";
  $("#pImg").src = product.img || "";
  $("#pImg").style.visibility = product.img ? "visible" : "hidden";
  $("#pPer100").textContent =
    `Pro 100 g: ${product.kcal100} kcal · E ${round(product.prot100)}g · KH ${round(product.carb100)}g · F ${round(product.fat100)}g`;
  $("#pAmount").value = product.serving > 0 ? product.serving : 100;
  updatePortionTotals();
  openSheet("portionSheet", "sheetBackdrop");
}

function updatePortionTotals() {
  const p = state.pending;
  if (!p) return;
  const g = num($("#pAmount").value);
  const f = g / 100;
  $("#pTotals").innerHTML = `
    <div class="t"><div class="t-val">${round(p.kcal100 * f)}</div><div class="t-lbl">kcal</div></div>
    <div class="t"><div class="t-val">${round(p.prot100 * f)}g</div><div class="t-lbl">Eiweiß</div></div>
    <div class="t"><div class="t-val">${round(p.carb100 * f)}g</div><div class="t-lbl">KH</div></div>
    <div class="t"><div class="t-val">${round(p.fat100 * f)}g</div><div class="t-lbl">Fett</div></div>`;
}
$("#pAmount").addEventListener("input", updatePortionTotals);

$("#pAdd").addEventListener("click", () => {
  const p = state.pending;
  if (!p) return;
  const g = num($("#pAmount").value);
  if (g <= 0) { toast("Bitte eine Menge größer 0 eingeben."); return; }
  const f = g / 100;
  const entries = loadDiary(state.date);
  entries.push({
    name: p.name, brand: p.brand, img: p.img, amount: g,
    kcal: p.kcal100 * f, prot: p.prot100 * f, carb: p.carb100 * f, fat: p.fat100 * f,
  });
  saveDiary(state.date, entries);
  closeSheet("portionSheet", "sheetBackdrop");
  renderDiary();
  renderSummary();
  switchView("diary");
  toast(p.name + " hinzugefügt ✓");
});
$("#pCancel").addEventListener("click", () => closeSheet("portionSheet", "sheetBackdrop"));

/* ---------- Ziel-Dialog ---------- */
$("#dateBtn").addEventListener("click", () => {
  $("#goalInput").value = state.goal;
  openSheet("goalSheet", "goalBackdrop");
});
$("#goalSave").addEventListener("click", () => {
  const g = num($("#goalInput").value);
  if (g >= 500) {
    state.goal = g;
    localStorage.setItem("kt_goal", String(g));
    renderSummary();
    closeSheet("goalSheet", "goalBackdrop");
    toast("Tagesziel gespeichert: " + g + " kcal");
  } else {
    toast("Ziel sollte mindestens 500 kcal sein.");
  }
});
$("#goalCancel").addEventListener("click", () => closeSheet("goalSheet", "goalBackdrop"));

/* ---------- Sheet-Helfer ---------- */
function openSheet(sheetId, backdropId) {
  $("#" + backdropId).classList.remove("hidden");
  $("#" + sheetId).classList.remove("hidden");
}
function closeSheet(sheetId, backdropId) {
  $("#" + backdropId).classList.add("hidden");
  $("#" + sheetId).classList.add("hidden");
}
$("#sheetBackdrop").addEventListener("click", () => closeSheet("portionSheet", "sheetBackdrop"));
$("#goalBackdrop").addEventListener("click", () => closeSheet("goalSheet", "goalBackdrop"));

/* ---------- Start ---------- */
renderSummary();
renderDiary();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () =>
    navigator.serviceWorker.register("sw.js").catch(() => {}));
}
