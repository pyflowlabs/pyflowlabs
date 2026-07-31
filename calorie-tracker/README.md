# 🍎 KalTrack — Kalorien-Tracker

Eine mobile-first **Web-App (PWA)** zum Tracken von Kalorien — mit **Kamera-Barcode-Scanner**
und einer **riesigen Lebensmittel-Datenbank** über [Open Food Facts](https://world.openfoodfacts.org)
(über 3 Millionen Produkte).

Läuft komplett im Browser, ganz ohne Server. Das Tagebuch wird lokal auf dem Gerät gespeichert
(`localStorage`) — deine Daten bleiben also bei dir.

## Funktionen

- 📷 **Barcode scannen** mit der Handy-Kamera → Produkt wird automatisch gefunden (Android **und iOS**)
- 📸 **Foto vom Essen → KI schätzt die Kalorien** automatisch (Claude Vision)
- 🔍 **Suche** in der Datenbank nach Namen (z. B. „Haferflocken")
- ⌨️ **Manuelle Barcode-Eingabe** als Fallback
- 🍽️ **Portionsrechner** — Menge in Gramm eingeben, Kalorien & Makros werden berechnet
- 📖 **Tagebuch** mit Tagesübersicht (Kalorien-Ring + Eiweiß / Kohlenhydrate / Fett)
- 🎯 Einstellbares **Tagesziel**
- 📱 **Installierbar** als App auf dem Homescreen (PWA), offline-fähige Hülle

## Foto-Kalorienschätzung (KI)

Im Tab **Foto** kannst du ein Bild deines Essens aufnehmen. Die App schickt es an
**Claude Vision** (Anthropic), das das Gericht erkennt und Kalorien + Nährwerte der
sichtbaren Portion schätzt – so genau wie möglich, aber immer *ungefähr*.

Dafür brauchst du einen eigenen **Anthropic-API-Schlüssel**
([console.anthropic.com](https://console.anthropic.com)):

1. Tab **Foto** → **🔑 KI-Schlüssel einrichten**
2. Schlüssel (`sk-ant-…`) eintragen und speichern

> Der Schlüssel wird **nur lokal** auf deinem Gerät gespeichert (`localStorage`) und
> direkt an Anthropic gesendet – nicht an einen fremden Server. Die Nutzung der
> Claude-API kostet je nach deinem Anthropic-Konto ein paar Cent pro Anfrage.

## Ausprobieren

Weil die Kamera nur über **HTTPS** (oder `localhost`) funktioniert, brauchst du eine der
folgenden Varianten:

### 1. Auf dem Handy (empfohlen) — GitHub Pages
1. In den Repo-**Settings → Pages** die Quelle auf diesen Branch/Ordner stellen.
2. Die veröffentlichte URL `…/calorie-tracker/` am Handy im Browser öffnen.
3. „Zum Startbildschirm hinzufügen" → läuft wie eine echte App.

### 2. Lokal testen
```bash
cd calorie-tracker
python3 -m http.server 8000
# dann http://localhost:8000 im Browser öffnen
```
> Hinweis: Über `http://` (nicht localhost) blockiert der Browser die Kamera —
> dann einfach die **manuelle Barcode-Eingabe** oder die **Suche** nutzen.

## Kamera-Scan: Kompatibilität

Der Scanner nutzt die native **`BarcodeDetector`**-API und fällt automatisch auf
die mitgelieferte **ZXing**-Bibliothek zurück, wenn der Browser das nicht kann.
- ✅ **Chrome auf Android** — native, schnelle Erkennung
- ✅ **iOS/Safari** — Erkennung über ZXing (Kamerazugriff nur über HTTPS)

## Technik

Reines HTML/CSS/JavaScript, keine Build-Tools, keine Abhängigkeiten.

| Datei | Zweck |
| --- | --- |
| `index.html` | Aufbau der Oberfläche |
| `styles.css` | Mobile-first Design (Dark Mode) |
| `app.js` | Logik: Suche, Scan, Tagebuch, Speicherung |
| `manifest.webmanifest` | PWA-Metadaten |
| `sw.js` | Service Worker (Offline-Hülle) |
| `vendor/zxing.min.js` | Barcode-Erkennung als iOS-Fallback |

## Ideen für später

- Mahlzeiten (Frühstück / Mittag / Abend), Tage durchblättern, Wochenstatistik
- Eigene Lebensmittel & Favoriten anlegen
- Foto der Mahlzeit anhängen
- Datenexport (CSV/JSON)
