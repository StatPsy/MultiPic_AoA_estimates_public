"""Check the recorded Python versions and load the requested modules."""
from importlib import import_module
from importlib.metadata import version
import json
from pathlib import Path
import platform

expected = json.loads(Path('/opt/aoa/expected-python.json').read_text())
if platform.python_version() != expected['python']:
    raise SystemExit('Python runtime does not match the recorded environment.')
distribution_names = {'pyqt': 'PyQt5'}
for name, required in expected['packages'].items():
    actual = version(distribution_names.get(name, name))
    if actual != required:
        raise SystemExit(f'{name}: expected {required}, found {actual}')
modules = ('numpy', 'pandas', 'matplotlib', 'seaborn', 'bottleneck', 'numexpr',
           'odf', 'xlrd', 'PIL', 'IPython', 'ipykernel', 'jupyter_client',
           'jupyter_core', 'PyQt5.QtCore')
for name in modules:
    import_module(name)
print(f"Python {platform.python_version()} and recorded Python packages verified.")
