/* KalTrack — Kalorien-Tracker
 * Reine Frontend-App. Lebensmitteldaten live von Open Food Facts,
 * alles andere lokal im Browser (localStorage). */

const OFF = "https://world.openfoodfacts.org";
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const MEALS = [
  { key: "breakfast", label: "Frühstück", emoji: "🍳", pct: 0.25 },
  { key: "lunch",     label: "Mittagessen", emoji: "🍝", pct: 0.35 },
  { key: "dinner",    label: "Abendessen", emoji: "🍽️", pct: 0.30 },
  { key: "snack",     label: "Snacks", emoji: "🍎", pct: 0.10 },
];
const mealLabel = (k) => (MEALS.find((m) => m.key === k) || {}).label || "";

/* ---------- Zustand ---------- */
const state = {
  date: todayKey(),
  goal: Number(localStorage.getItem("kt_goal")) || 2000,
  targetMeal: "breakfast", // Mahlzeit, in die gerade hinzugefügt wird
  filter: "frequent",      // frequent | recent | fav
  pending: null,           // Produkt im Portions-Dialog
};

function todayKey(d = new Date()) { return d.toISOString().slice(0, 10); }
function num(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function round(n) { return Math.round(n); }

/* ---------- Speicher ---------- */
function loadDiary(date) {
  try { return JSON.parse(localStorage.getItem("kt_diary_" + date)) || []; } catch { return []; }
}
function saveDiary(date, e) { localStorage.setItem("kt_diary_" + date, JSON.stringify(e)); }

function loadActivity(date) {
  try { return JSON.parse(localStorage.getItem("kt_act_" + date)) || { steps: 0, burned: 0 }; }
  catch { return { steps: 0, burned: 0 }; }
}
function saveActivity(date, a) { localStorage.setItem("kt_act_" + date, JSON.stringify(a)); }

function loadCatalog() {
  try { return JSON.parse(localStorage.getItem("kt_catalog")) || {}; } catch { return {}; }
}
function saveCatalog(c) { localStorage.setItem("kt_catalog", JSON.stringify(c)); }

/* Merkt sich ein benutztes Produkt (für Häufig/Zuletzt/Favoriten). */
function catalogAdd(product) {
  const c = loadCatalog();
  const key = product.code || (product.name + "|" + (product.brand || ""));
  const prev = c[key] || { count: 0, fav: false };
  c[key] = {
    ...product, count: prev.count + 1, last: nowStamp(), fav: prev.fav,
  };
  saveCatalog(c);
}
let _stamp = 0;
function nowStamp() { return ++_stamp + Date.now() * 1000; } // ohne Date.now-Kollision, monoton

function catalogToggleFav(key) {
  const c = loadCatalog();
  if (c[key]) { c[key].fav = !c[key].fav; saveCatalog(c); }
}

/* ---------- Hilfen ---------- */
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.add("hidden"), 2200);
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function normalizeProduct(p) {
  const n = p.nutriments || {};
  const kcal100 = num(n["energy-kcal_100g"]) || (num(n["energy_100g"]) ? num(n["energy_100g"]) / 4.184 : 0);
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

/* ===================== DASHBOARD ===================== */
function mealGoal(key) {
  const m = MEALS.find((x) => x.key === key);
  return round(state.goal * (m ? m.pct : 0));
}
function mealTotals(entries, key) {
  return entries.filter((e) => e.meal === key).reduce(
    (a, e) => { a.kcal += e.kcal; a.prot += e.prot; a.carb += e.carb; a.fat += e.fat; return a; },
    { kcal: 0, prot: 0, carb: 0, fat: 0 }
  );
}

function renderDashboard() {
  const entries = loadDiary(state.date);
  const act = loadActivity(state.date);
  const sum = entries.reduce(
    (a, e) => { a.kcal += e.kcal; a.prot += e.prot; a.carb += e.carb; a.fat += e.fat; return a; },
    { kcal: 0, prot: 0, carb: 0, fat: 0 }
  );

  // Übersicht
  const left = state.goal - sum.kcal + act.burned;
  $("#kcalEaten").textContent = round(sum.kcal);
  $("#kcalBurned").textContent = round(act.burned);
  $("#kcalLeft").textContent = round(left);
  const C = 2 * Math.PI * 52;
  const pct = Math.min(sum.kcal / Math.max(state.goal, 1), 1);
  const ring = $("#ringFg");
  ring.style.strokeDashoffset = String(C * (1 - pct));
  ring.style.stroke = left >= 0 ? "var(--accent)" : "var(--danger)";

  // Makro-Ziele: 50 % KH, 20 % Eiweiß, 30 % Fett
  const gCarb = round(state.goal * 0.5 / 4);
  const gProt = round(state.goal * 0.2 / 4);
  const gFat = round(state.goal * 0.3 / 9);
  setMacro("Carb", sum.carb, gCarb);
  setMacro("Prot", sum.prot, gProt);
  setMacro("Fat", sum.fat, gFat);

  // Mahlzeit-Karten
  const wrap = $("#mealCards");
  wrap.innerHTML = "";
  const MC = 2 * Math.PI * 22;
  MEALS.forEach((m) => {
    const t = mealTotals(entries, m.key);
    const goal = mealGoal(m.key);
    const p = Math.min(t.kcal / Math.max(goal, 1), 1);
    const list = entries.filter((e) => e.meal === m.key).map((e) => e.name);
    const last = list.length ? list.slice(-2).reverse().join(", ") : "Noch nichts eingetragen";
    const btn = document.createElement("button");
    btn.className = "meal-card";
    btn.type = "button";
    btn.innerHTML = `
      <div class="meal-ring">
        <svg viewBox="0 0 52 52"><circle class="mr-bg" cx="26" cy="26" r="22"/>
          <circle class="mr-fg" cx="26" cy="26" r="22" style="stroke-dashoffset:${MC * (1 - p)}"/></svg>
        <div class="meal-emoji">${m.emoji}</div>
      </div>
      <div class="meal-main">
        <div class="meal-name">${m.label}</div>
        <div class="meal-kcal">${round(t.kcal)} / ${goal} kcal</div>
        <div class="meal-last">${escapeHtml(last)}</div>
      </div>
      <div class="meal-add">＋</div>`;
    btn.addEventListener("click", () => openMeal(m.key));
    wrap.appendChild(btn);
  });

  // Aktivität
  $("#actSteps").textContent = act.steps.toLocaleString("de-DE") + " Schritte";
  $("#actSub").textContent = round(act.burned) + " kcal verbrannt";
}

function setMacro(id, val, goal) {
  $("#m" + id).textContent = round(val) + " / " + goal + " g";
  $("#bar" + id).style.width = Math.min(val / Math.max(goal, 1), 1) * 100 + "%";
}

/* ===================== MAHLZEIT-DETAIL ===================== */
function openMeal(key) {
  state.targetMeal = key;
  $("#mealTitle").textContent = mealLabel(key);
  $("#mealDetail").classList.remove("hidden");
  window.scrollTo(0, 0);
  setMethod("search");
  $("#searchInput").value = "";
  renderMealHeader();
  renderMealEntries();
  renderFoodList();
}
function closeMeal() {
  stopScan();
  $("#mealDetail").classList.add("hidden");
  renderDashboard();
}
function renderMealHeader() {
  const t = mealTotals(loadDiary(state.date), state.targetMeal);
  $("#mealTotal").textContent = round(t.kcal) + " / " + mealGoal(state.targetMeal);
}

function renderMealEntries() {
  const list = $("#mealEntries");
  const entries = loadDiary(state.date);
  list.innerHTML = "";
  entries.forEach((e, i) => {
    if (e.meal !== state.targetMeal) return;
    const portion = e.est ? "📸 Portion (KI)" : (e.amount ? round(e.amount) + " g" : "1 Portion");
    const li = document.createElement("li");
    li.className = "entry";
    li.innerHTML = `
      <img class="entry-thumb" src="${e.img || ""}" alt="" onerror="this.style.visibility='hidden'"/>
      <div class="entry-main">
        <div class="entry-name">${escapeHtml(e.name)}</div>
        <div class="entry-sub">${portion} · ${round(e.kcal)} kcal</div>
      </div>
      <button class="entry-del" data-i="${i}" aria-label="Löschen">×</button>`;
    list.appendChild(li);
  });
  list.querySelectorAll(".entry-del").forEach((b) => {
    b.addEventListener("click", () => {
      const entries = loadDiary(state.date);
      entries.splice(Number(b.dataset.i), 1);
      saveDiary(state.date, entries);
      renderMealEntries();
      renderMealHeader();
    });
  });
}

/* Methoden-Panels umschalten */
function setMethod(method) {
  $$(".panel").forEach((p) => p.classList.add("hidden"));
  $("#panel-" + method).classList.remove("hidden");
  $$(".method").forEach((m) => m.classList.toggle("active", m.dataset.method === method));
  if (method !== "scan") stopScan();
}
$$(".method").forEach((m) => m.addEventListener("click", () => setMethod(m.dataset.method)));
$("#mealBack").addEventListener("click", closeMeal);
$("#mealDone").addEventListener("click", closeMeal);

/* ---------- Suche + Filter (Katalog / Open Food Facts) ---------- */
function renderFoodList() {
  const q = $("#searchInput").value.trim();
  if (q) { doSearch(q); return; }
  // Katalog nach Filter
  const c = loadCatalog();
  let items = Object.entries(c).map(([key, v]) => ({ key, ...v }));
  const hint = $("#searchHint");
  if (state.filter === "fav") items = items.filter((x) => x.fav);
  if (state.filter === "recent") items.sort((a, b) => (b.last || 0) - (a.last || 0));
  else if (state.filter === "fav") items.sort((a, b) => (b.last || 0) - (a.last || 0));
  else items.sort((a, b) => (b.count || 0) - (a.count || 0)); // frequent
  items = items.slice(0, 40);

  if (!items.length) {
    hint.textContent = state.filter === "fav"
      ? "Noch keine Favoriten. Tippe bei einem Lebensmittel auf den Stern."
      : "Noch nichts gespeichert. Suche oben nach einem Lebensmittel.";
    $("#foodList").innerHTML = "";
    return;
  }
  hint.textContent = "";
  renderList(items, true);
}

async function doSearch(term) {
  const hint = $("#searchHint");
  const list = $("#foodList");
  list.innerHTML = "";
  hint.innerHTML = '<div class="spinner"></div>';
  try {
    const url = `${OFF}/cgi/search.pl?search_terms=${encodeURIComponent(term)}` +
      `&search_simple=1&action=process&json=1&page_size=25` +
      `&fields=code,product_name,generic_name,brands,image_front_small_url,image_small_url,nutriments,serving_quantity`;
    const res = await fetch(url);
    const data = await res.json();
    const products = (data.products || []).map(normalizeProduct).filter((p) => p.kcal100 > 0);
    hint.textContent = products.length ? "" : `Keine Treffer für „${term}".`;
    renderList(products, false);
  } catch {
    hint.textContent = "Suche fehlgeschlagen — Internetverbindung?";
  }
}

/* products: Liste normalisierter Produkte. fromCatalog=true zeigt Stern. */
function renderList(products, fromCatalog) {
  const list = $("#foodList");
  list.innerHTML = "";
  products.forEach((p) => {
    const li = document.createElement("li");
    li.className = "result";
    const star = fromCatalog
      ? `<button class="fav-btn ${p.fav ? "on" : ""}" data-key="${escapeHtml(p.key)}">${p.fav ? "★" : "☆"}</button>`
      : "";
    li.innerHTML = `
      <button class="result-tap" type="button">
        <img class="result-thumb" src="${p.img || ""}" alt="" onerror="this.style.visibility='hidden'"/>
        <div class="result-main">
          <div class="result-name">${escapeHtml(p.name)}</div>
          <div class="result-sub">${escapeHtml(p.brand || "—")}</div>
        </div>
        <div class="result-kcal">${p.kcal100} kcal<br><span style="color:var(--muted);font-weight:400">/100g</span></div>
      </button>${star}`;
    li.querySelector(".result-tap").addEventListener("click", () => openPortion(p));
    const fb = li.querySelector(".fav-btn");
    if (fb) fb.addEventListener("click", () => { catalogToggleFav(fb.dataset.key); renderFoodList(); });
    list.appendChild(li);
  });
}

$("#searchBtn").addEventListener("click", () => renderFoodList());
$("#searchInput").addEventListener("keydown", (e) => { if (e.key === "Enter") renderFoodList(); });
$("#searchInput").addEventListener("input", (e) => { if (!e.target.value.trim()) renderFoodList(); });

/* Filter-Menü */
$("#filterBtn").addEventListener("click", () => {
  const menu = $("#filterMenu");
  const r = $("#filterBtn").getBoundingClientRect();
  menu.style.left = r.left + "px";
  menu.style.top = (r.bottom + 6) + "px";
  menu.classList.toggle("hidden");
});
$$("#filterMenu button").forEach((b) => b.addEventListener("click", () => {
  state.filter = b.dataset.filter;
  $("#filterBtn").textContent =
    ({ frequent: "Häufig", recent: "Zuletzt", fav: "Favoriten" }[state.filter]) + " ▾";
  $("#filterMenu").classList.add("hidden");
  renderFoodList();
}));
document.addEventListener("click", (e) => {
  if (!$("#filterMenu").contains(e.target) && e.target !== $("#filterBtn"))
    $("#filterMenu").classList.add("hidden");
});

/* ---------- Barcode ---------- */
async function lookupBarcode(code) {
  toast("Suche Barcode " + code + " …");
  try {
    const res = await fetch(`${OFF}/api/v2/product/${encodeURIComponent(code)}.json` +
      `?fields=code,product_name,generic_name,brands,image_front_small_url,image_small_url,nutriments,serving_quantity`);
    const data = await res.json();
    if (data.status === 1 && data.product) openPortion(normalizeProduct(data.product));
    else toast("Produkt nicht in der Datenbank gefunden.");
  } catch { toast("Abfrage fehlgeschlagen — Internetverbindung?"); }
}
$("#manualBtn").addEventListener("click", () => {
  const c = $("#manualBarcode").value.trim();
  if (c) lookupBarcode(c);
});

/* ---------- Kamera-Scanner (nativ + ZXing-Fallback für iOS) ---------- */
let stream = null, detector = null, scanning = false, zxingReader = null;
function onScanned(code) { stopScan(); if (navigator.vibrate) navigator.vibrate(60); lookupBarcode(code); }

async function startScan() {
  const hint = $("#scanHint");
  $("#startScanBtn").classList.add("hidden");
  $("#stopScanBtn").classList.remove("hidden");
  const video = $("#video");
  try {
    if ("BarcodeDetector" in window) {
      detector = detector || new BarcodeDetector({ formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"] });
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      video.srcObject = stream; await video.play();
      scanning = true; hint.textContent = "Kamera läuft — Barcode ins grüne Feld halten."; scanLoop();
    } else if (window.ZXing && ZXing.BrowserMultiFormatReader) {
      zxingReader = new ZXing.BrowserMultiFormatReader();
      hint.textContent = "Kamera läuft — Barcode ins grüne Feld halten.";
      await zxingReader.decodeFromConstraints({ video: { facingMode: "environment" } }, video,
        (result) => { if (result) onScanned(result.getText()); });
    } else { throw new Error("kein Scanner"); }
  } catch {
    stopScan();
    hint.textContent = "Kamerazugriff nicht möglich. Erlaube die Kamera oder nutze die manuelle Eingabe.";
  }
}
async function scanLoop() {
  if (!scanning) return;
  try { const codes = await detector.detect($("#video")); if (codes.length) { onScanned(codes[0].rawValue); return; } }
  catch {}
  requestAnimationFrame(scanLoop);
}
function stopScan() {
  scanning = false;
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
  if (zxingReader) { try { zxingReader.reset(); } catch {} zxingReader = null; }
  const v = $("#video"); if (v) v.srcObject = null;
  const s = $("#startScanBtn"); if (s) s.classList.remove("hidden");
  const st = $("#stopScanBtn"); if (st) st.classList.add("hidden");
}
$("#startScanBtn").addEventListener("click", startScan);
$("#stopScanBtn").addEventListener("click", () => { stopScan(); $("#scanHint").textContent = "Scan gestoppt."; });

/* ===================== FOTO ===================== */
let photoBase64 = null;
function getApiKey() { return localStorage.getItem("kt_apikey") || ""; }

function fileToScaledBase64(file, maxSize = 1024) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale), h = Math.round(img.height * scale);
      const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
      cv.getContext("2d").drawImage(img, 0, 0, w, h);
      URL.revokeObjectURL(img.src);
      resolve(cv.toDataURL("image/jpeg", 0.8).split(",")[1]);
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
  try { photoBase64 = await fileToScaledBase64(file); }
  catch { toast("Foto konnte nicht gelesen werden."); }
});

/* --- Gratis-Erkennung (TensorFlow.js MobileNet, auf dem Gerät) --- */
const DEFAULT_PHOTO_HINT = $("#photoHint").textContent;
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
  { keys: ["chocolate"], name: "Schokolade (Portion)", kcal: 210, prot: 3, carb: 24, fat: 12 },
  { keys: ["dough"], name: "Teiggebäck (Portion)", kcal: 250, prot: 6, carb: 42, fat: 7 },
  { keys: ["hotpot", "hot pot", "soup", "consomme"], name: "Eintopf/Suppe (Portion)", kcal: 200, prot: 12, carb: 20, fat: 8 },
];
function matchFood(preds) {
  for (const p of preds) {
    const label = (p.className || "").toLowerCase();
    for (const f of FOOD_MAP) if (f.keys.some((k) => label.includes(k))) return { food: f, className: p.className, prob: p.probability };
  }
  return null;
}
let mnModel = null, mnLoading = null;
function loadScript(src) {
  return new Promise((res, rej) => {
    const s = document.createElement("script"); s.src = src; s.onload = res;
    s.onerror = () => rej(new Error("load " + src)); document.head.appendChild(s);
  });
}
async function ensureModel() {
  if (mnModel) return mnModel;
  if (!mnLoading) mnLoading = (async () => {
    if (!window.tf) await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js");
    if (!window.mobilenet) await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js");
    mnModel = await window.mobilenet.load({ version: 2, alpha: 1.0 });
    return mnModel;
  })();
  return mnLoading;
}
async function estimatePhotoLocal() {
  if (!photoBase64) { toast("Bitte zuerst ein Foto wählen."); return; }
  const btn = $("#estimateBtn"), out = $("#estimateResult");
  btn.disabled = true; out.innerHTML = '<div class="spinner"></div>';
  $("#photoHint").textContent = "Modell wird geladen (einmalig)…";
  try {
    const model = await ensureModel();
    const img = new Image(); img.src = "data:image/jpeg;base64," + photoBase64; await img.decode();
    const preds = await model.classify(img, 5);
    const m = matchFood(preds);
    if (!m) { out.innerHTML = ""; renderNoMatch(preds); return; }
    renderEstimate({
      name: m.food.name, kcal: m.food.kcal, prot: m.food.prot, carb: m.food.carb, fat: m.food.fat,
      items: [], note: `Erkannt: ${m.className} (${Math.round(m.prob * 100)} %). Grobe Schätzung für eine typische Portion.`,
    });
  } catch { out.innerHTML = ""; toast("Erkennung fehlgeschlagen – Internet fürs erste Laden nötig."); }
  finally { btn.disabled = false; $("#photoHint").textContent = DEFAULT_PHOTO_HINT; }
}
function renderNoMatch(preds) {
  const g = (preds || []).slice(0, 3).map((p) => `<li>• ${escapeHtml(p.className)} (${Math.round(p.probability * 100)} %)</li>`).join("");
  $("#estimateResult").innerHTML = `
    <div class="est-name">Nicht sicher erkannt 🤔</div>
    <div class="est-note">Nutze für dieses Bild besser die <b>Suche</b> oder den <b>Barcode</b> – oder die genaue KI-Variante.</div>
    ${g ? `<div class="p-per100">Vermutungen:</div><ul class="est-guesses">${g}</ul>` : ""}`;
}
$("#estimateBtn").addEventListener("click", estimatePhotoLocal);

/* --- Genau: Claude Vision (kostenpflichtig, eigener Schlüssel) --- */
const AI_MODEL = "claude-sonnet-5";
const AI_PROMPT =
  "Du bist ein Ernährungsexperte. Schätze für das auf dem Foto gezeigte Essen die Nährwerte der " +
  "SICHTBAREN PORTION, so genau wie möglich. Antworte AUSSCHLIESSLICH mit reinem JSON, ohne Markdown: " +
  '{"name":"Gericht","kcal":Zahl,"prot":Zahl,"carb":Zahl,"fat":Zahl,"items":["Zutat"],"note":"Hinweis"}. ' +
  "kcal/prot/carb/fat sind Gesamtwerte für die Portion. Kein Essen: name \"Kein Essen erkannt\", alles 0.";

async function estimatePhotoAI() {
  const key = getApiKey();
  if (!key) { openSheet("keySheet", "keyBackdrop"); return; }
  if (!photoBase64) { toast("Bitte zuerst ein Foto wählen."); return; }
  const btn = $("#aiEstimateBtn"), out = $("#estimateResult");
  btn.disabled = true; out.innerHTML = '<div class="spinner"></div>';
  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json", "x-api-key": key,
        "anthropic-version": "2023-06-01", "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: AI_MODEL, max_tokens: 1024,
        messages: [{ role: "user", content: [
          { type: "image", source: { type: "base64", media_type: "image/jpeg", data: photoBase64 } },
          { type: "text", text: AI_PROMPT },
        ] }],
      }),
    });
    if (!res.ok) {
      out.innerHTML = "";
      toast(res.status === 401 ? "API-Schlüssel ungültig." : "KI-Anfrage fehlgeschlagen (" + res.status + ").");
      return;
    }
    const data = await res.json();
    const est = parseEstimate((data.content || []).map((b) => b.text || "").join(""));
    if (!est) { out.innerHTML = ""; toast("Antwort nicht verständlich."); return; }
    renderEstimate(est);
  } catch { out.innerHTML = ""; toast("Netzwerkfehler."); }
  finally { btn.disabled = false; }
}
function parseEstimate(text) {
  try { return JSON.parse(text); } catch {}
  const s = text.indexOf("{"), e = text.lastIndexOf("}");
  if (s >= 0 && e > s) { try { return JSON.parse(text.slice(s, e + 1)); } catch {} }
  return null;
}
$("#aiEstimateBtn").addEventListener("click", estimatePhotoAI);

/* Gemeinsame Ergebnis-Anzeige (Foto → ins Tagebuch) */
function renderEstimate(est) {
  const out = $("#estimateResult");
  const kcal = round(num(est.kcal));
  const items = Array.isArray(est.items) ? est.items : [];
  out.innerHTML = `
    <div class="est-name">${escapeHtml(est.name || "Essen")}</div>
    <div class="p-per100">${kcal} kcal · E ${round(num(est.prot))}g · KH ${round(num(est.carb))}g · F ${round(num(est.fat))}g</div>
    ${items.length ? `<ul class="est-items">${items.map((i) => `<li>• ${escapeHtml(i)}</li>`).join("")}</ul>` : ""}
    ${est.note ? `<div class="est-note">ℹ️ ${escapeHtml(est.note)}</div>` : ""}
    <div class="sheet-actions"><button id="estAdd" type="button" class="primary">In ${escapeHtml(mealLabel(state.targetMeal))}</button></div>`;
  $("#estAdd").addEventListener("click", () => {
    if (kcal <= 0) { toast("Kein Essen erkannt."); return; }
    const entries = loadDiary(state.date);
    entries.push({ meal: state.targetMeal, name: est.name || "Essen (Foto)", img: "", est: true,
      kcal, prot: num(est.prot), carb: num(est.carb), fat: num(est.fat) });
    saveDiary(state.date, entries);
    renderMealEntries(); renderMealHeader();
    out.innerHTML = "";
    toast((est.name || "Essen") + " hinzugefügt ✓");
  });
}

/* ===================== PORTIONS-DIALOG ===================== */
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
  const p = state.pending; if (!p) return;
  const f = num($("#pAmount").value) / 100;
  $("#pTotals").innerHTML = `
    <div class="t"><div class="t-val">${round(p.kcal100 * f)}</div><div class="t-lbl">kcal</div></div>
    <div class="t"><div class="t-val">${round(p.prot100 * f)}g</div><div class="t-lbl">Eiweiß</div></div>
    <div class="t"><div class="t-val">${round(p.carb100 * f)}g</div><div class="t-lbl">KH</div></div>
    <div class="t"><div class="t-val">${round(p.fat100 * f)}g</div><div class="t-lbl">Fett</div></div>`;
}
$("#pAmount").addEventListener("input", updatePortionTotals);
$("#pAdd").addEventListener("click", () => {
  const p = state.pending; if (!p) return;
  const g = num($("#pAmount").value);
  if (g <= 0) { toast("Menge größer 0 eingeben."); return; }
  const f = g / 100;
  const entries = loadDiary(state.date);
  entries.push({ meal: state.targetMeal, name: p.name, brand: p.brand, img: p.img, amount: g,
    kcal: p.kcal100 * f, prot: p.prot100 * f, carb: p.carb100 * f, fat: p.fat100 * f });
  saveDiary(state.date, entries);
  catalogAdd(p);
  closeSheet("portionSheet", "sheetBackdrop");
  renderMealEntries(); renderMealHeader(); renderFoodList();
  toast(p.name + " hinzugefügt ✓");
});
$("#pCancel").addEventListener("click", () => closeSheet("portionSheet", "sheetBackdrop"));
$("#sheetBackdrop").addEventListener("click", () => closeSheet("portionSheet", "sheetBackdrop"));

/* ===================== ZIEL / AKTIVITÄT / KEY ===================== */
$("#dateBtn").addEventListener("click", () => { $("#goalInput").value = state.goal; openSheet("goalSheet", "goalBackdrop"); });
$("#goalSave").addEventListener("click", () => {
  const g = num($("#goalInput").value);
  if (g >= 500) { state.goal = g; localStorage.setItem("kt_goal", String(g)); renderDashboard(); closeSheet("goalSheet", "goalBackdrop"); toast("Tagesziel: " + g + " kcal"); }
  else toast("Ziel mind. 500 kcal.");
});
$("#goalCancel").addEventListener("click", () => closeSheet("goalSheet", "goalBackdrop"));
$("#goalBackdrop").addEventListener("click", () => closeSheet("goalSheet", "goalBackdrop"));

$("#activityBtn").addEventListener("click", () => {
  const a = loadActivity(state.date);
  $("#stepsInput").value = a.steps; $("#burnedInput").value = a.burned;
  openSheet("actSheet", "actBackdrop");
});
$("#actSave").addEventListener("click", () => {
  saveActivity(state.date, { steps: Math.max(0, num($("#stepsInput").value)), burned: Math.max(0, num($("#burnedInput").value)) });
  renderDashboard(); closeSheet("actSheet", "actBackdrop"); toast("Aktivität gespeichert ✓");
});
$("#actCancel").addEventListener("click", () => closeSheet("actSheet", "actBackdrop"));
$("#actBackdrop").addEventListener("click", () => closeSheet("actSheet", "actBackdrop"));

$("#apiKeyBtn").addEventListener("click", () => { $("#keyInput").value = getApiKey(); openSheet("keySheet", "keyBackdrop"); });
$("#keySave").addEventListener("click", () => {
  const k = $("#keyInput").value.trim();
  if (k) { localStorage.setItem("kt_apikey", k); toast("Schlüssel gespeichert ✓"); }
  closeSheet("keySheet", "keyBackdrop");
});
$("#keyClear").addEventListener("click", () => { localStorage.removeItem("kt_apikey"); $("#keyInput").value = ""; toast("Schlüssel gelöscht."); closeSheet("keySheet", "keyBackdrop"); });
$("#keyBackdrop").addEventListener("click", () => closeSheet("keySheet", "keyBackdrop"));

/* ---------- Sheet-Helfer ---------- */
function openSheet(id, bd) { $("#" + bd).classList.remove("hidden"); $("#" + id).classList.remove("hidden"); }
function closeSheet(id, bd) { $("#" + bd).classList.add("hidden"); $("#" + id).classList.add("hidden"); }

/* ---------- Start ---------- */
renderDashboard();
if ("serviceWorker" in navigator)
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
