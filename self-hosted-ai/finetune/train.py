#!/usr/bin/env python3
"""Erster echter Lernlauf: QLoRA-Feintuning auf der RTX 4080 Super.

Das ist KEIN Pretraining (Modell von Null) – das wäre auf einer GPU nicht
machbar. Das hier nimmt ein fertiges offenes Modell und trainiert es auf
DEINE Beispiele weiter. Läuft auf 16 GB VRAM, dauert je nach Datenmenge
Minuten bis wenige Stunden – und ist wiederholbar (jedes Mal, wenn du neue
Beispiele gesammelt hast).

Voraussetzung (einmalig, am PC mit GPU):
    pip install -r requirements-train.txt

Start:
    python train.py

Ergebnis:
    - LoRA-Adapter in  outputs/lora_model/
    - optional GGUF-Modell für Ollama in  outputs/gguf/   (Flag EXPORT_GGUF)
Die Auslieferung nach Ollama macht danach der 'deployer'-Subagent.
"""

import json
import os

# --- Einstellungen (für 16 GB VRAM ausgelegt) -----------------------------
# Erster Lauf bewusst mit 7B: passt sicher, ist schnell, beweist die Schleife.
# Später auf "unsloth/Qwen2.5-Coder-14B-Instruct-bnb-4bit" hochstufen.
BASE_MODEL = "unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit"
MAX_SEQ_LENGTH = 2048
EPOCHS = 3                 # kleiner Datensatz -> mehr Epochen; groß -> 1-2
LEARNING_RATE = 2e-4
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
EXPORT_GGUF = False        # True: am Ende GGUF für Ollama exportieren

HERE = os.path.dirname(__file__)
DATASET_FILES = [
    os.path.join(HERE, "dataset", "seed.jsonl"),
    os.path.join(HERE, "dataset", "collected.jsonl"),
]

# Prompt-Vorlage: so lernt das Modell das Antwortformat.
PROMPT = """### Anweisung:
{instruction}

### Kontext:
{input}

### Antwort:
{output}"""


def load_examples() -> list:
    rows = []
    for path in DATASET_FILES:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def main() -> None:
    from unsloth import FastLanguageModel
    from datasets import Dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments

    examples = load_examples()
    print(f"Trainingsbeispiele geladen: {len(examples)}")
    if len(examples) < 20:
        print("Hinweis: sehr wenige Beispiele. Für spürbare Wirkung lieber "
              "erst mehr sammeln (Ziel grob 200+). Der Lauf funktioniert trotzdem.")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    eos = tokenizer.eos_token or ""

    def format_row(row):
        text = PROMPT.format(
            instruction=row.get("instruction", ""),
            input=row.get("input", "") or "(keiner)",
            output=row.get("output", ""),
        ) + eos
        return {"text": text}

    dataset = Dataset.from_list(examples).map(format_row)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            fp16=True,
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=os.path.join(OUTPUT_DIR, "checkpoints"),
        ),
    )

    print("Training startet ... (GPU-Auslastung mit `nvidia-smi -l 1` beobachtbar)")
    trainer.train()

    lora_dir = os.path.join(OUTPUT_DIR, "lora_model")
    model.save_pretrained(lora_dir)
    tokenizer.save_pretrained(lora_dir)
    print(f"Fertig. LoRA-Adapter gespeichert: {lora_dir}")

    if EXPORT_GGUF:
        gguf_dir = os.path.join(OUTPUT_DIR, "gguf")
        model.save_pretrained_gguf(gguf_dir, tokenizer, quantization_method="q4_k_m")
        print(f"GGUF exportiert: {gguf_dir}  (für Ollama via 'deployer')")


if __name__ == "__main__":
    main()
