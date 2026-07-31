# Roadmap: Eigene neutrale KI (selbst gehostet)

> Ziel: Ein selbst gehostetes KI-System mit **voller Kontrolle**, ohne fremde Richtlinien,
> das als **Suchmaschine, Coder und Task-Completer** arbeitet — auf eigenem Server/PC.
>
> Diese Roadmap ist der ehrliche, technische Fahrplan dorthin. Kein Marketing.

---

## 0. Ehrliche Einordnung (bitte zuerst lesen)

Es gibt zwei Dinge, die oft verwechselt werden:

1. **Ein Fundament-Modell selbst trainieren** (das „Gehirn" von Grund auf bauen).
   → Für Einzelpersonen/kleine Teams **nicht realistisch**: tausende GPUs, Monate Rechenzeit,
     kuratierte Datenmengen im Petabyte-Bereich, Kosten im zwei- bis dreistelligen Millionenbereich.
   → **Das machen wir NICHT.**

2. **Ein eigenes KI-*System* auf einem offenen Modell bauen** (das „Gehirn" nehmen, aber alles
   drumherum — Regeln, Werkzeuge, Wissen, Verhalten — selbst bestimmen).
   → **Sehr wohl realistisch** und genau das, was „volle Kontrolle, keine Filter, eigene Funktionen"
     bedeutet. **Das machen wir.**

**Was „besser als Claude" realistisch heißt:** Nicht das Modell an sich (rohe Intelligenz bleibt
etwas hinter den größten Cloud-Modellen zurück), sondern das **Gesamtsystem für deine Aufgaben**:

- keine Rate-Limits, keine Kosten pro Anfrage,
- keine fremden Inhaltsfilter — du bestimmst jede Regel,
- vollständiger Zugriff auf deine eigenen Daten und deinen Rechner,
- beliebige Werkzeuge (Code ausführen, Web durchsuchen, Dateien schreiben, APIs steuern),
- 100 % Datenschutz — nichts verlässt deinen Server.

---

## 1. Architektur — die 5 Bausteine

```
                ┌────────────────────────────────────────────────┐
                │                   Oberfläche / UI               │
                │        (Open WebUI · eigenes Web-Frontend)      │
                └───────────────────────┬────────────────────────┘
                                        │
                ┌───────────────────────▼────────────────────────┐
                │              Agent- / Orchestrierung            │
                │   Planung · Werkzeug-Auswahl · Gedächtnis       │
                └──────┬──────────┬───────────┬──────────┬────────┘
                       │          │           │          │
          ┌────────────▼──┐ ┌─────▼─────┐ ┌───▼─────┐ ┌──▼──────────┐
          │  Modell-Kern  │ │  Websuche │ │  RAG /  │ │  Werkzeuge  │
          │ (Inferenz-    │ │ (SearxNG) │ │ Wissen  │ │ Code · Shell│
          │  Engine + LLM)│ │           │ │ (Vektor)│ │ Dateien·API │
          └───────────────┘ └───────────┘ └─────────┘ └─────────────┘
```

1. **Modell-Kern** — das offene LLM + eine Inferenz-Engine, die es ausführt.
2. **Agent-/Orchestrierungsschicht** — entscheidet, *was* getan wird, ruft Werkzeuge auf,
   hält Gedächtnis. **Hier entsteht der „Task-Completer".**
3. **Websuche** — selbst gehostete Suche (SearxNG) → neutral, keine Tracker, keine Filter.
4. **RAG / Wissensspeicher** — deine Dokumente/Daten als durchsuchbare Vektor-Datenbank.
5. **Werkzeuge** — Code ausführen, Shell, Dateien lesen/schreiben, APIs aufrufen. **Der „Coder".**

Der Clou: Punkte 2–5 sind da, wo du ein Cloud-Modell für *deine* Zwecke schlägst — nicht das Modell selbst.

---

## 2. Modell-Auswahl (offene Modelle, Stand 2026)

Alles frei herunterladbar und selbst hostbar. Auswahl nach Aufgabe und Hardware:

| Modell (Familie) | Stärke | VRAM (quantisiert) |
| --- | --- | --- |
| **Qwen 2.5 / 3 (7B–32B)** | Allrounder, sehr stark bei Code & Werkzeugen | 6–24 GB |
| **DeepSeek-V3 / R1 (destilliert)** | Reasoning, Task-Planung | 8–40 GB |
| **Llama 3.x (8B / 70B)** | Solider Allrounder, riesiges Ökosystem | 6–48 GB |
| **Mistral / Mixtral** | Schnell, effizient (MoE) | 6–30 GB |
| **Qwen2.5-Coder / DeepSeek-Coder** | Spezialist fürs Programmieren | 6–24 GB |

**Empfehlung zum Start:** ein **Qwen2.5-Coder 14B/32B** oder **Llama 3.x 8B/70B** als Allrounder.
Später kannst du je Aufgabe zwischen Modellen wechseln (Router).

> „Quantisiert" = das Modell wird komprimiert (z. B. 4-bit), damit es auf weniger VRAM passt —
> bei minimalem Qualitätsverlust. Format meist **GGUF** (llama.cpp/Ollama) oder AWQ/GPTQ (vLLM).

---

## 3. Hardware-Stufen (mit grober Kostenorientierung)

Der wichtigste Faktor ist **VRAM** (Grafikspeicher). Mehr VRAM = größeres, klügeres Modell.

| Stufe | Hardware | Was läuft | Grobkosten* |
| --- | --- | --- | --- |
| **Einstieg** | 1× RTX 4060 Ti 16 GB / gebrauchte 3090 24 GB | 7B–14B flüssig, 32B quantisiert | 400–900 € |
| **Solide** | 1× RTX 4090 24 GB / RTX 5090 32 GB | 32B flüssig, 70B quantisiert | 1.500–2.500 € |
| **Ernsthaft** | 2× 3090/4090 (48 GB) | 70B gut, mehrere Modelle parallel | 2.500–4.500 € |
| **Profi** | RTX 6000 Ada 48 GB / A6000 / mehrere GPUs | 70B+ komfortabel, Feintuning | 6.000 €+ |
| **Mac-Alternative** | Mac Studio M-Serie, 64–192 GB Unified Memory | 70B dank Unified Memory | 2.500–6.000 € |

\* Richtwerte, keine Angebote. Gebraucht (v. a. RTX 3090) ist das Preis-Leistungs-Ideal für den Start.

**Ohne eigene GPU zum Testen:** stundenweise Cloud-GPU (RunPod, Vast.ai) — ein paar Euro, um alles
auszuprobieren, bevor du Hardware kaufst.

---

## 4. Software-Stack (alles Open Source, selbst gehostet)

| Baustein | Werkzeug | Warum |
| --- | --- | --- |
| **Inferenz-Engine** | **Ollama** (einfach) → später **vLLM** (schnell/produktiv) | Führt das Modell aus, stellt eine API bereit |
| **Oberfläche** | **Open WebUI** | Chat-Oberfläche wie ChatGPT, self-hosted |
| **Agent-Framework** | eigenes Python-Gerüst (später ggf. LangGraph) | Volle Kontrolle über Regeln & Werkzeuge |
| **Websuche** | **SearxNG** (self-hosted Meta-Suche) | Neutral, keine Tracker, keine Filter |
| **Wissen/RAG** | **Qdrant** oder **Chroma** (Vektor-DB) + Embedding-Modell | Deine Dokumente durchsuchbar machen |
| **Code-Ausführung** | Sandbox (Docker-Container) | Sicher Code laufen lassen |
| **Betrieb** | **Docker Compose** | Alles mit einem Befehl starten |

Der ganze Stack läuft als Docker-Compose-Verbund auf **einer** Maschine.

---

## 5. Die drei geforderten Rollen — konkret

### 🔎 Suchmaschine
- **SearxNG** liefert neutrale Web-Ergebnisse (aggregiert viele Suchmaschinen, ohne Tracking).
- Der Agent ruft die Suche als Werkzeug auf, liest die Top-Treffer, fasst sie mit Quellenangabe zusammen.
- Ergebnis: „Antwort-Engine" mit echten, aktuellen Quellen — komplett unter deiner Kontrolle.

### 💻 Coder
- Coder-Modell (Qwen-Coder / DeepSeek-Coder) schreibt Code.
- **Werkzeug „Code ausführen"** in einer Docker-Sandbox: der Agent schreibt Code, führt ihn aus,
  liest Fehler, verbessert — echte Schleife statt nur Textausgabe.
- Zugriff auf dein Dateisystem/Projekte (Grenzen bestimmst du).

### ✅ Task-Completer
- Die **Agent-Schicht** zerlegt einen Auftrag in Schritte, wählt Werkzeuge, arbeitet sie ab,
  prüft das Ergebnis. Das ist die eigentliche „Magie" — und hier kannst du für deine Abläufe
  besser werden als ein generisches Cloud-Modell, weil du eigene Werkzeuge einbaust
  (Discord, Scraper, APIs — passend zu deinen bestehenden Projekten).

---

## 6. „Neutral / keine Filter" — was das bedeutet

Weil du selbst hostest, gibt es **keine fremden Inhaltsfilter**: Du schreibst den System-Prompt und
die Regeln. Das ist bei offenen Modellen völlig legitim und technisch einfach.

Zwei ehrliche Hinweise, damit du nicht in Fallen läufst:
- **Verantwortung liegt dann bei dir.** Ohne fremde Leitplanken gilt trotzdem geltendes Recht
  (Urheberrecht, Datenschutz/DSGVO, Persönlichkeitsrechte). „Neutral" ≠ „rechtsfrei".
- **Ein Minimum an eigenen Regeln ist klug** — nicht als Zensur, sondern gegen Fehler
  (z. B. „führe keine löschenden Shell-Befehle ohne Rückfrage aus"). Du definierst sie, nicht ein Konzern.

---

## 7. Phasen-Roadmap

### Phase 1 — Fundament (Wochenende)
- [ ] Ollama installieren, erstes Modell ziehen (`qwen2.5-coder` oder `llama3.x`)
- [ ] Open WebUI per Docker starten → im Browser chatten
- [ ] Eigenen System-Prompt/„Persönlichkeit" & Regeln festlegen
- **Ergebnis:** eigener, lokaler Chat-Assistent ohne fremde Filter.

### Phase 2 — Werkzeuge & Coder (1–2 Wochen)
- [ ] Python-Agent-Gerüst, das die Modell-API anspricht
- [ ] Werkzeug „Code ausführen" in Docker-Sandbox
- [ ] Werkzeug „Datei lesen/schreiben"
- **Ergebnis:** die KI *tut* Dinge, nicht nur reden — echter Coder.

### Phase 3 — Suche & Wissen (1–2 Wochen)
- [ ] SearxNG self-hosted, als Werkzeug angebunden
- [ ] Vektor-DB (Qdrant/Chroma) + Embeddings → eigene Dokumente einlesen (RAG)
- **Ergebnis:** Antworten mit aktuellen Web-Quellen + deinem eigenen Wissen.

### Phase 4 — Task-Completer / Autonomie (fortlaufend)
- [ ] Planungs-Schleife (Auftrag → Schritte → Werkzeuge → Prüfen)
- [ ] Gedächtnis über mehrere Sitzungen
- [ ] Anbindung deiner bestehenden Projekte (Discord-Bot, Scraper, APIs)
- **Ergebnis:** autonomer Assistent, der ganze Aufgaben abschließt.

### Phase 5 — Optimieren (optional, später)
- [ ] Wechsel Ollama → vLLM für Tempo
- [ ] Modell-Router (je Aufgabe anderes Modell)
- [ ] Feintuning auf deinen Stil/deine Daten (LoRA)

---

## 8. Realistische Erwartung

| Was | Erreichbar? |
| --- | --- |
| Eigener, lokaler Assistent ohne fremde Filter | ✅ Ja, in einem Wochenende |
| Coder + Websuche + Task-Automatisierung | ✅ Ja, in einigen Wochen |
| Volle Kontrolle über Regeln, Daten, Werkzeuge | ✅ Ja, das ist der Kern |
| Für *deine* Abläufe nützlicher als ein Cloud-Dienst | ✅ Ja, realistisch |
| Rohes Modell „schlauer als Claude/GPT" trainieren | ❌ Nein, nicht als Einzelperson |

---

## 9. Nächster konkreter Schritt

Sag mir deine **aktuelle Hardware** (welche GPU / wie viel VRAM / oder Mac mit wie viel RAM),
dann bekommst du von mir:
1. die passende Modell-Empfehlung für genau deine Maschine,
2. eine **fertige `docker-compose.yml`** für Phase 1 (Modell + Open WebUI),
3. die konkreten Befehle zum Starten.

Damit chattest du noch heute mit deiner eigenen, lokalen KI.
