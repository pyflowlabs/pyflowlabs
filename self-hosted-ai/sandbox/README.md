# Polyglot-Sandbox & Toolchains

Damit die KI Code nicht nur *schreibt*, sondern auch *ausführt/kompiliert*,
braucht sie die jeweiligen Toolchains. Zwei Wege:

## Weg A – lokal installieren (Agent läuft auf dem Host)
Der `run_code`-Werkzeug ruft die lokal installierten Tools auf. Installiere, was
du brauchst:

| Sprache | Braucht | Prüfen |
| --- | --- | --- |
| Python | Python 3 | `python3 --version` |
| JavaScript | Node.js | `node --version` |
| C | gcc | `gcc --version` |
| C++ | g++ | `g++ --version` |
| Java | JDK (`javac`) | `javac -version` |
| C# | .NET SDK (`dotnet`) | `dotnet --version` |
| SQL | sqlite3 | `sqlite3 --version` |
| HTML | – (Markup, wird gerendert) | – |

Mathe/DL in Python (Lineare Algebra, Analysis, Wahrscheinlichkeit, Deep Learning):
```bash
pip install -r agent/requirements-science.txt
```

## Weg B – alles in einem Container (empfohlen, isoliert)
Ein Image mit **allen** Toolchains + Mathe/DL-Bibliotheken:
```bash
docker build -t nero-sandbox ./sandbox
```
Enthält: gcc/g++, JDK, .NET SDK, Node.js, SQLite, sowie
NumPy/SciPy/SymPy/pandas/scikit-learn und **PyTorch (CPU)**.

Damit läuft ausgeführter Code isoliert vom Host – die sichere Variante, sobald
der Agent autonomer wird. (Die Anbindung des `run_code`-Werkzeugs an diesen
Container statt an den Host richte ich dir ein, wenn du so weit bist.)

## Mathe als Basis von Algorithmen
Die Mathe-Grundlagen (Lineare Algebra, Analysis, Wahrscheinlichkeit) kennt das
Modell inhaltlich; **rechnen** kann es damit über Python:
- **Lineare Algebra:** `numpy` (Matrizen, Eigenwerte, Lösungssysteme)
- **Analysis:** `sympy` (symbolisch: Ableitungen, Integrale, Grenzwerte), `scipy` (numerisch)
- **Wahrscheinlichkeit/Statistik:** `scipy.stats`, `numpy.random`
- **Machine/Deep Learning:** `scikit-learn`, `torch`

## Sicherheit
`run_code` läuft mit Zeitlimit (`config.py` → `CODE_TIMEOUT`) und im
`WORKSPACE_DIR`. Für echte Isolation Weg B (Container) verwenden. Toolchain
fehlt? Dann meldet `run_code` das klar, und es steht im `logs/nero-agent.log`.
