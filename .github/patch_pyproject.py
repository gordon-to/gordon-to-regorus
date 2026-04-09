"""Patch bindings/python/pyproject.toml for gordon-to-regorus publishing."""
import re
from pathlib import Path

PYPROJECT = Path("bindings/python/pyproject.toml")

text = PYPROJECT.read_text()

# Rename the package
text = text.replace('name = "regorus"', 'name = "gordon-to-regorus"')

# Fix requires-python to match abi3-py310
text = re.sub(r'requires-python\s*=\s*"[^"]*"', 'requires-python = ">=3.10"', text)

# Add module-name so import stays as `import regorus`
text = text.replace("[tool.maturin]", '[tool.maturin]\nmodule-name = "regorus"')

PYPROJECT.write_text(text)

# Verify
patched = PYPROJECT.read_text()
assert 'name = "gordon-to-regorus"' in patched
assert 'requires-python = ">=3.10"' in patched
assert 'module-name = "regorus"' in patched
print(patched)
