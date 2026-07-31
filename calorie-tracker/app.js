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
    li.innerHTML = `
      <img class="entry-thumb" src="${e.img || ""}" alt="" onerror="this.style.visibility='hidden'"/>
      <div class="entry-main">
        <div class="entry-name">${escapeHtml(e.name)}</div>
        <div class="entry-sub">${round(e.amount)} g · E ${round(e.prot)}g · KH ${round(e.carb)}g · F ${round(e.fat)}g</div>
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

/* ---------- Kamera-Scanner ---------- */
let stream = null;
let detector = null;
let scanning = false;

async function startScan() {
  const hint = $("#scanHint");
  if (!("BarcodeDetector" in window)) {
    hint.textContent =
      "Dein Browser unterstützt den Kamera-Scan (noch) nicht. Gib den Barcode bitte unten manuell ein. Tipp: Chrome auf Android klappt am besten.";
    return;
  }
  try {
    detector = detector || new BarcodeDetector({
      formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"],
    });
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
    });
    const video = $("#video");
    video.srcObject = stream;
    await video.play();

    scanning = true;
    $("#startScanBtn").classList.add("hidden");
    $("#stopScanBtn").classList.remove("hidden");
    hint.textContent = "Kamera läuft — Barcode ins grüne Feld halten.";
    scanLoop();
  } catch (err) {
    hint.textContent =
      "Kamerazugriff nicht möglich. Erlaube den Kamerazugriff oder nutze die manuelle Eingabe.";
  }
}

async function scanLoop() {
  if (!scanning) return;
  const video = $("#video");
  try {
    const codes = await detector.detect(video);
    if (codes.length) {
      const code = codes[0].rawValue;
      stopScan();
      if (navigator.vibrate) navigator.vibrate(60);
      lookupBarcode(code);
      return;
    }
  } catch { /* einzelne Frames dürfen fehlschlagen */ }
  requestAnimationFrame(scanLoop);
}

function stopScan() {
  scanning = false;
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
  const v = $("#video");
  if (v) v.srcObject = null;
  $("#startScanBtn").classList.remove("hidden");
  $("#stopScanBtn").classList.add("hidden");
}

$("#startScanBtn").addEventListener("click", startScan);
$("#stopScanBtn").addEventListener("click", () => { stopScan(); $("#scanHint").textContent = "Scan gestoppt."; });

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
