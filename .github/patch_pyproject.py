# /// script
# requires-python = ">=3.10"
# dependencies = ["tomlkit"]
# ///
"""Patch bindings/python/pyproject.toml for gordon-to-regorus publishing."""
from pathlib import Path

import tomlkit

PYPROJECT = Path("bindings/python/pyproject.toml")

doc = tomlkit.parse(PYPROJECT.read_text())

project = doc["project"]
project["name"] = "gordon-to-regorus"
project["requires-python"] = ">=3.10"
project["description"] = (
    "Rego policy engine implemented in Rust (gordon-to fork of microsoft/regorus)."
)
project["readme"] = "README.md"
project["keywords"] = ["rego", "opa", "policy", "policy-engine", "rust"]
project["authors"] = [{"name": "gordon-to", "email": "me@adamgordon.ca"}]

project["classifiers"] = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "License :: OSI Approved :: BSD License",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Rust",
    "Topic :: Security",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

project["urls"] = {
    "Homepage": "https://github.com/gordon-to/gordon-to-regorus",
    "Repository": "https://github.com/gordon-to/gordon-to-regorus",
    "Issues": "https://github.com/gordon-to/gordon-to-regorus/issues",
    "Upstream": "https://github.com/microsoft/regorus",
}

doc["tool"]["maturin"]["module-name"] = "regorus"

PYPROJECT.write_text(tomlkit.dumps(doc))
print(PYPROJECT.read_text())
