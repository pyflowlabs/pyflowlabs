# NERO QUANTUM – Polyglot-Sandbox
# Ein Container mit allen Toolchains, damit die KI Code in mehreren Sprachen
# ausfuehren/kompilieren kann – plus Mathe- & Deep-Learning-Bibliotheken.
#
# Bauen:   docker build -t nero-sandbox ./sandbox
# Nutzen:  Code im Container ausfuehren lassen (isoliert), oder die Toolchains
#          lokal installieren, wenn der Agent direkt auf dem Host laeuft.

FROM python:3.12-slim

# System-Toolchains: C/C++, Java (JDK), SQLite, Node.js, .NET, Git, Netz-Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ \
        default-jdk \
        sqlite3 \
        nodejs npm \
        curl git ca-certificates iputils-ping dnsutils \
    && rm -rf /var/lib/apt/lists/*

# .NET SDK (fuer C#)
RUN curl -sSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh \
    && bash /tmp/dotnet-install.sh --channel LTS --install-dir /usr/share/dotnet \
    && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet \
    && rm /tmp/dotnet-install.sh
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1

# Python: Mathe (Lineare Algebra, Analysis, Wahrscheinlichkeit) + Deep Learning
RUN pip install --no-cache-dir \
        numpy scipy sympy pandas matplotlib scikit-learn \
        torch --index-url https://download.pytorch.org/whl/cpu

WORKDIR /work
CMD ["bash"]
