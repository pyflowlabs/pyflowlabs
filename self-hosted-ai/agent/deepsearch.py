#!/usr/bin/env python3
"""Deep Search – tiefe, mehrstufige Web-Recherche mit Quellen.

Ablauf pro Runde:
  1. Das Modell formuliert mehrere präzise Suchanfragen zur Frage.
  2. Jede Anfrage geht an SearxNG (neutral), Treffer werden gesammelt.
  3. Die vielversprechendsten Seiten werden geladen und ausgelesen (Scraping).
  4. Nach Runde 1 prüft das Modell, welche Lücken bleiben, und recherchiert
     in Runde 2 gezielt nach.
  5. Zum Schluss fasst das Modell alles zu einer Antwort MIT Quellen (URLs) zusammen.

Das ist mehr als eine einzelne Suche: es liest echte Quellen und iteriert.

Start:  python deepsearch.py
Tiefe einstellen in config.py -> DEEP_QUERIES / DEEP_PAGES / DEEP_ROUNDS.
"""

import ollama

import nero_config as config
import logsetup
import tools

log, LOG_FILE = logsetup.setup("nero.deepsearch")


def _make_queries(client, focus: str, n: int) -> list:
    prompt = (
        f"Formuliere genau {n} präzise, voneinander verschiedene Web-Suchanfragen, "
        f"um folgende Frage gründlich zu recherchieren. Gib nur die Suchanfragen "
        f"zurück, eine pro Zeile, ohne Nummerierung:\n\n{focus}"
    )
    resp = client.chat(model=config.MODEL, messages=[{"role": "user", "content": prompt}])
    lines = [l.strip("-•*0123456789. ").strip() for l in resp["message"]["content"].splitlines()]
    return [l for l in lines if l][:n]


def deep_search(question: str) -> str:
    """Führt eine tiefe Recherche durch und gibt eine Antwort mit Quellen zurück."""
    client = ollama.Client(host=config.OLLAMA_HOST)
    seen_urls = set()
    collected = []          # (url, title, text)
    focus = question

    for rnd in range(1, config.DEEP_ROUNDS + 1):
        log.info("Deep-Search Runde %d, Fokus: %s", rnd, focus)
        print(f"   🔎 Runde {rnd}: bilde Suchanfragen …")
        queries = _make_queries(client, focus, config.DEEP_QUERIES)
        if not queries:
            queries = [focus]

        # Kandidaten sammeln
        candidates = []
        for q in queries:
            print(f"      · suche: {q}")
            for r in tools.search_web_raw(q, num_results=6):
                url = r.get("url", "")
                if url and url not in seen_urls:
                    candidates.append(r)

        # Beste Seiten laden (bis DEEP_PAGES neue je Runde)
        loaded = 0
        for r in candidates:
            if loaded >= config.DEEP_PAGES:
                break
            url = r["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)
            print(f"      · lese: {url}")
            page = tools.fetch_page(url)
            if page and not page.startswith("Konnte Seite nicht laden"):
                collected.append((url, r.get("title", ""), page))
                loaded += 1

        if rnd < config.DEEP_ROUNDS and collected:
            # Lücken bestimmen -> Fokus für nächste Runde
            gaps_prompt = (
                f"Frage: {question}\n\nBisher gelesen (Auszüge):\n"
                + "\n\n".join(f"[{u}] {t[:600]}" for u, _, t in collected[-config.DEEP_PAGES:])
                + "\n\nWelche wichtige Teilfrage ist noch offen? Antworte in EINEM kurzen Satz "
                  "als nächste Recherche-Fokusfrage."
            )
            resp = client.chat(model=config.MODEL, messages=[{"role": "user", "content": gaps_prompt}])
            focus = resp["message"]["content"].strip() or question

    if not collected:
        return "Keine verwertbaren Quellen gefunden (Suche/Netz prüfen – siehe Log)."

    # Finale Synthese mit Quellen
    sources_block = "\n\n".join(
        f"QUELLE {i}: {url}\n{text[:1500]}" for i, (url, _, text) in enumerate(collected, 1)
    )
    synth_prompt = (
        f"Beantworte die Frage gründlich und sachlich AUF BASIS der Quellen unten. "
        f"Nenne im Text die verwendeten Quellen als [n] und liste sie am Ende mit URL auf. "
        f"Wenn etwas unklar/widersprüchlich ist, sag es.\n\n"
        f"FRAGE:\n{question}\n\nQUELLEN:\n{sources_block}"
    )
    print("   🧠 fasse Ergebnisse zusammen …")
    final = client.chat(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": synth_prompt},
        ],
    )
    answer = final["message"]["content"].strip()
    src_list = "\n".join(f"[{i}] {url}" for i, (url, _, _) in enumerate(collected, 1))
    return f"{answer}\n\n— Gelesene Quellen —\n{src_list}"


def main() -> None:
    print("Deep Search bereit.")
    print(f"Tiefe: {config.DEEP_QUERIES} Anfragen · {config.DEEP_PAGES} Seiten · "
          f"{config.DEEP_ROUNDS} Runden")
    print(f"Protokoll: {LOG_FILE}\n")
    while True:
        try:
            q = input("🔎 ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"exit", "quit", "ende"}:
            break
        if not q:
            continue
        print()
        print(deep_search(q))
        print()


if __name__ == "__main__":
    main()
