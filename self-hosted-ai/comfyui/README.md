# ComfyUI – Bild & Video (Vorlagen & Modelle)

ComfyUI erledigt **Bild und Video** über Workflows. Damit es läuft, brauchst du
je Aufgabe (a) die Modelldateien und (b) einen Workflow. Am robustesten sind die
**eingebauten Vorlagen** von ComfyUI (versionssicher) – ein handgeschriebenes
JSON bricht oft zwischen Versionen.

Oberfläche nach dem Start: http://localhost:8188

---

## Ordner (werden vom Container genutzt)

```
comfyui/models/      <- hier die Modelldateien ablegen (Checkpoints, VAE, ...)
comfyui/output/      <- erzeugte Bilder und Videos
comfyui/workflows/   <- eigene/gespeicherte Workflows
```

---

## BILD – SDXL (läuft komfortabel auf 16 GB)

1. **Modelle laden** (nach `comfyui/models/checkpoints/`):
   - SDXL Base Checkpoint (z. B. `sd_xl_base_1.0.safetensors`)
   - optional SDXL VAE nach `comfyui/models/vae/`
2. **Workflow:** in ComfyUI oben **Workflow → Browse Templates → „SDXL"** wählen.
3. Checkpoint im Loader auswählen, Prompt eintragen, **Queue** drücken.
4. Ergebnis landet in `comfyui/output/`.

Alternative Modelle: FLUX **nur quantisiert** (fp8/GGUF), sonst zu groß für 16 GB.

---

## VIDEO – Wan 2.2 / HunyuanVideo

1. **Vorher VRAM freimachen** (LLM entladen), damit die volle Karte bereitsteht:
   ```bash
   docker exec ollama ollama stop qwen2.5-coder:32b
   ```
2. **Modelle laden** (in die von der Vorlage erwarteten Unterordner unter
   `comfyui/models/`, z. B. `diffusion_models/`, `vae/`, `text_encoders/`):
   - **Wan 2.2** (kleinere Variante, z. B. 1.3B/5B) – gute Wahl für 16 GB
   - **HunyuanVideo** (13B) – nur quantisiert, kurze Clips, langsam
3. **Workflow:** **Workflow → Browse Templates → „Wan"** bzw. „Hunyuan Video".
   Aktuelle ComfyUI-Versionen bringen diese Video-Vorlagen mit.
4. Prompt + Clip-Länge/Auflösung einstellen (klein starten!), **Queue** drücken.

**Realistische Erwartung (16 GB):** kurze Clips, moderate Auflösung, Geduld –
aber es funktioniert, weil du immer nur diese eine Aufgabe laufen lässt.

---

## Anbindung an NERO QUANTUM (Bilder direkt aus dem Chat)

NERO QUANTUM → **Admin → Einstellungen → Bilder**:
- Engine: **ComfyUI**
- URL: `http://comfyui:8188`

Danach kannst du im Chat Bilder erzeugen lassen. Video steuerst du direkt in der
ComfyUI-Oberfläche (Video-Ausgabe aus dem Chat ist je nach Version begrenzt).

---

## Grenze
Allgemeine, legale Kreativnutzung: deine Sache. **Nicht** eingerichtet und nicht
unterstützt: sexuelle Inhalte von **echten Personen** oder **Minderjährigen**
(Deepfakes/NCII/CSAM) – das ist hart illegal.

> Hinweis: Das ComfyUI-Docker-Image und die Video-Custom-Nodes sind
> community-gepflegt. Falls beim ersten Start etwas fehlt (Node/Modell), sag mir
> die Fehlermeldung – dann stimmen wir Image, Nodes und Workflow zusammen ab.
