# NERO QUANTUM – Roadmap zu Version 1.0

Ehrlicher Status gegen die 17 Wunsch-Features + Reihenfolge fürs Weiterbauen.
Legende: ✅ fertig · 🟡 teilweise · ❌ offen

---

## Status

| # | Feature | Status | Wo / Was fehlt |
| --- | --- | --- | --- |
| 1 | Langzeitgedächtnis (RAG + Vektor-DB) | ✅ | `agent/memory.py` (ChromaDB + Ollama-Embeddings) |
| 2 | Plugin-System (Auto-Erkennung) | ✅ | `agent/plugins_loader.py` + `agent/plugins/` |
| 15 | Wissensbasis (PDFs/MD/Notizen) | ✅ | Teil von #1: `kb_ingest` / `kb_search` |
| 5 | Lokales RAG über Ordner | ✅ | Teil von #1: `kb_ingest("D:\\...")` |
| 6 | Agenten-System | 🟡 | MoA + writer/reviewer/… da · Rollen-Agenten offen |
| 3 | Sprachsteuerung (STT/TTS) | 🟡 | in der UI eingebaut · Wake-Word „Hey Nero" offen |
| 7 | GPU-Optimierung | 🟡 | Flash-Attn + Quantisierung an · vLLM/TensorRT offen |
| 11 | Sandbox-Härtung | 🟡 | Zeit-/Pfad-Limit · RAM/CPU/Netz/Container offen |
| 16 | Web-Automatisierung | 🟡 | Scraping da · echter Browser-Controller offen |
| 17 | Rollen-/Persönlichkeit | 🟡 | ein System-Prompt · Multi-Rolle offen |
| 4 | Vision (OCR/Diagramme/Tabellen) | ❌ | Vision-Modell + OCR fehlen |
| 8 | Selbstbewertung | ❌ | Selbst-Kritik-Schleife fehlt |
| 10 | Scheduler | ❌ | geplante Aufgaben fehlen |
| 12 | Automatische Tests | ❌ | pytest/Regression fehlen |
| 13 | Benchmark-System | ❌ | Modellvergleich fehlt |
| 14 | Monitoring | ❌ | Live-Statistiken fehlen |

**Fundament (schon da):** Stack + UI (NERO QUANTUM), Multi-Modell + Umschalten,
Agent mit Werkzeugen, Polyglot-Code, Deep Search, Feintuning, Multimodal-Gen,
Logging, **Gedächtnis/RAG**, **Plugin-System**.

---

## Empfohlene Reihenfolge (baut auf deiner Priorisierung auf)

1. ✅ **Langzeitgedächtnis / RAG** – erledigt
2. ✅ **Plugin-System** – erledigt
3. **Rollen-/Agenten-System** – spezialisierte Rollen (Coding/Recherche/Mathe/
   Sicherheit…) mit eigenem Prompt + Werkzeugsatz; MoA als Basis vorhanden.
4. **Selbstbewertung** – Antwort → Selbst-Kritik → ggf. Verbesserung (Schleife).
5. **Vision** – Vision-Modell (z. B. `llama3.2-vision` / `qwen2-vl` in Ollama) +
   OCR (Tesseract) für Screenshots/Tabellen/Handschrift.
6. **Scheduler** – wiederkehrende Aufgaben (Backup, News, Datei-Sortierung).
7. **Automatische Tests** – pytest + Regressionstests für Agent/Tools/Plugins.
8. **Sandbox-Härtung** – `run_code` in den `nero-sandbox`-Container mit
   RAM-/CPU-/Netz-Limits statt auf dem Host.
9. **Monitoring** – Live CPU/GPU/VRAM/Temp/Token-s.
10. **Benchmark** – nach Modellwechsel Speed/VRAM/Genauigkeit automatisch messen.
11. **Wake-Word** „Hey Nero", **Browser-Automatisierung** (Playwright),
    **GPU-Optimierung** (vLLM/TensorRT) – jeweils eigener Ausbaustein.

---

## Aktivieren von #1 (Gedächtnis/RAG)
```bash
docker exec -it ollama ollama pull nomic-embed-text        # Embedding-Modell
pip install -r agent/requirements-memory.txt                # chromadb + pypdf
```
Dann kann der Agent: `remember`, `recall`, `kb_ingest("D:\\Dokumente")`, `kb_search`.

## Plugins (#2) erweitern
Neue Datei in `agent/plugins/` mit `PLUGIN_TOOLS` ablegen → wird beim Start
automatisch erkannt. Vorlage: `agent/plugins/archive_tools.py`.
