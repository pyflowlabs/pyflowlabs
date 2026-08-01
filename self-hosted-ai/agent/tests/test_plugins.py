"""Tests für das Plugin-System (#2) – ohne externe Abhängigkeiten."""

import os
import sys
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import plugins_loader


def test_plugins_load():
    dispatch, spec = {}, []
    loaded = plugins_loader.load_plugins(dispatch, spec)
    assert "unzip" in loaded
    assert "list_dir" in loaded
    # Jedes registrierte Werkzeug hat eine aufrufbare Funktion und ein Schema
    for name in loaded:
        assert callable(dispatch[name])
    assert len(spec) == len(loaded)


def test_unzip_and_list(tmp_path):
    dispatch, spec = {}, []
    plugins_loader.load_plugins(dispatch, spec)
    z = tmp_path / "a.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("datei.txt", "inhalt")
    out = dispatch["unzip"](path=str(z))
    assert "Entpackt" in out
    listing = dispatch["list_dir"](path=str(tmp_path / "a"))
    assert "datei.txt" in listing
