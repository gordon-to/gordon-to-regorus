# /// script
# requires-python = ">=3.10"
# dependencies = ["tomlkit"]
# ///
"""Patch bindings/python/pyproject.toml for gordon-to-regorus publishing."""
from pathlib import Path

import tomlkit

PYPROJECT = Path("bindings/python/pyproject.toml")

doc = tomlkit.parse(PYPROJECT.read_text())

doc["project"]["name"] = "gordon-to-regorus"
doc["project"]["requires-python"] = ">=3.10"
doc["tool"]["maturin"]["module-name"] = "regorus"

PYPROJECT.write_text(tomlkit.dumps(doc))
print(PYPROJECT.read_text())
