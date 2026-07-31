# 🍎 KalTrack — Kalorien-Tracker

Eine mobile-first **Web-App (PWA)** zum Tracken von Kalorien — mit **Kamera-Barcode-Scanner**
und einer **riesigen Lebensmittel-Datenbank** über [Open Food Facts](https://world.openfoodfacts.org)
(über 3 Millionen Produkte).

Läuft komplett im Browser, ganz ohne Server. Das Tagebuch wird lokal auf dem Gerät gespeichert
(`localStorage`) — deine Daten bleiben also bei dir.

## Funktionen

- 📷 **Barcode scannen** mit der Handy-Kamera → Produkt wird automatisch gefunden (Android **und iOS**)
- 📸 **Foto vom Essen → Kalorien automatisch** (gratis, direkt auf dem Gerät; optional genauere KI)
- 🔍 **Suche** in der Datenbank nach Namen (z. B. „Haferflocken")
- ⌨️ **Manuelle Barcode-Eingabe** als Fallback
- 🍽️ **Portionsrechner** — Menge in Gramm eingeben, Kalorien & Makros werden berechnet
- 📖 **Tagebuch** mit Tagesübersicht (Kalorien-Ring + Eiweiß / Kohlenhydrate / Fett)
- 🎯 Einstellbares **Tagesziel**
- 📱 **Installierbar** als App auf dem Homescreen (PWA), offline-fähige Hülle

## Foto-Kalorienschätzung

Im Tab **Foto** nimmst du ein Bild deines Essens auf. Es gibt zwei Wege:

### 🆓 Gratis – direkt auf dem Gerät (Standard)

Ein **Bilderkennungs-Modell** ([TensorFlow.js MobileNet](https://github.com/tensorflow/tfjs-models/tree/master/mobilenet))
läuft komplett **im Browser auf deinem Handy**:

- **Kostet nichts**, keine Anmeldung, kein Schlüssel.
- Die **Bilder verlassen dein Gerät nicht**.
- Erkennt **gängige Lebensmittel** (Banane, Pizza, Burger, Apfel, Brokkoli, …) und
  schätzt eine **typische Portion** aus einer eingebauten Kalorientabelle.

> ⚠️ Ehrlich: Das ist eine **grobe** Schätzung. Es erkennt vor allem einzelne,
> klare Lebensmittel – kein exaktes Wiegen und keine komplexen Teller. Für genaue
> Werte sind **Barcode** und **Suche** treffsicherer.
>
> Beim ersten Mal wird das Modell (~14 MB) einmalig geladen; danach geht es schnell.

### 🤖 Optional: genauer mit KI (kostet ein paar Cent)

Wer es genauer will, kann **Claude Vision** (Anthropic) nutzen – erkennt auch
komplexere Gerichte und Zutaten. Dafür brauchst du einen eigenen
**Anthropic-API-Schlüssel** ([console.anthropic.com](https://console.anthropic.com)):

1. Tab **Foto** → **🔑 KI-Schlüssel** eintragen und speichern
2. Foto wählen → **🤖 Genauer mit KI**

> Der Schlüssel wird **nur lokal** gespeichert (`localStorage`) und direkt an
> Anthropic gesendet. Jede Anfrage kostet je nach Konto ein paar Cent.

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

## Hinweis zu externen Bibliotheken

Für die Gratis-Fotoerkennung werden TensorFlow.js und das MobileNet-Modell beim
ersten Gebrauch von einem CDN (jsDelivr) geladen. Das passiert nur einmal und nur,
wenn du die Foto-Erkennung wirklich benutzt – der Rest der App bleibt offline-fähig.

## Ideen für später

- Mahlzeiten (Frühstück / Mittag / Abend), Tage durchblättern, Wochenstatistik
- Eigene Lebensmittel & Favoriten anlegen
- Foto der Mahlzeit anhängen
- Datenexport (CSV/JSON)
