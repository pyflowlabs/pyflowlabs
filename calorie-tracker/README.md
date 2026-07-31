# 🍎 KalTrack — Kalorien-Tracker

Eine mobile-first **Web-App (PWA)** zum Tracken von Kalorien — mit **Kamera-Barcode-Scanner**
und einer **riesigen Lebensmittel-Datenbank** über [Open Food Facts](https://world.openfoodfacts.org)
(über 3 Millionen Produkte).

Läuft komplett im Browser, ganz ohne Server. Das Tagebuch wird lokal auf dem Gerät gespeichert
(`localStorage`) — deine Daten bleiben also bei dir.

## Funktionen

- 📊 **Dashboard** wie gewohnt: Gegessen / Übrig / Verbrannt + Makro-Balken
- 🍳🍝🍽️🍎 **Mahlzeiten**: Frühstück, Mittagessen, Abendessen, Snacks – jeweils mit eigenem Ziel
- 🗂️ **Filter im Mahlzeit-Detail**: **Häufig**, **Zuletzt**, **Favoriten** (mit ⭐)
- 📷 **Barcode scannen** mit der Handy-Kamera (Android **und iOS**)
- 📸 **Foto vom Essen → Kalorien automatisch** (gratis auf dem Gerät; optional genauere KI)
- 🔍 **Suche** in der Datenbank (Open Food Facts)
- 🍽️ **Portionsrechner** — Menge in Gramm → Kalorien & Makros
- 🏃 **Aktivitäten**: Schritte & verbrannte Kalorien (fließen in „Übrig" ein)
- 💧 **Wasserzähler** (Gläser à 250 ml, Ziel 2 l)
- ⚖️ **Gewicht** mit Zielgewicht und Trend
- 📅 **Tage durchblättern** (‹ ›) + **7-Tage-Verlauf** als Balken
- 🎯 Einstellbares **Tagesziel** (wird auf die Mahlzeiten aufgeteilt)
- 📱 **Installierbar** als App auf dem Homescreen (PWA), offline-fähige Hülle

## Mahlzeiten & Filter

Auf dem Dashboard tippst du auf eine Mahlzeit (z. B. **Frühstück**) und kommst ins
Detail. Dort gibt es **Suche / Barcode / Foto** zum Hinzufügen und darüber eine
Liste, die du filtern kannst:

- **Häufig** — was du am öftesten isst
- **Zuletzt** — zuletzt gegessene Lebensmittel
- **Favoriten** — mit dem ⭐ markierte Lieblinge

Alles, was du per Suche oder Barcode hinzufügst, landet automatisch in diesem
Verlauf, sodass du es beim nächsten Mal mit einem Tap wieder hinzufügen kannst.

## Aktivitäten & Apple Health

Im Bereich **Aktivitäten** kannst du **Schritte** und **verbrannte Kalorien**
eintragen; die verbrannten Kalorien erhöhen dein „Übrig"-Budget.

### Apple Health per Kurzbefehl (funktioniert ohne native App)

Eine Web-App kann Apple Health nicht direkt lesen. Aber über die iOS-App
**Kurzbefehle** kannst du deine Werte an KalTrack übergeben – die App liest sie
aus der URL. Tippe in der App auf **„🍎 Aus Apple Health importieren"** für die
Anleitung. Kurzfassung:

1. **Kurzbefehle** → neuer Kurzbefehl
2. **„Gesundheitsprobendaten abrufen"** → *Schritte* (heute) → Variable
3. dasselbe für *Aktive Energie* (verbrannte kcal)
4. Aktion **„URLs öffnen"** mit:
   `…/calorie-tracker/?steps=SCHRITTE&burned=KCAL`
   (die Variablen einsetzen)

Beim Öffnen übernimmt KalTrack `steps`, `burned` (und optional `weight`, `water`)
in den heutigen Tag. So kannst du den Kurzbefehl auch automatisieren (z. B. jeden
Abend). Ein **echter Hintergrund-Sync** bräuchte weiterhin eine native App
(Capacitor + HealthKit).

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
