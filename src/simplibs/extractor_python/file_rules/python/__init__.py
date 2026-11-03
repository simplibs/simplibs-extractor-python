from .PYTHON_BASE import PYTHON_BASE
from .PYTHON_CONFIG import PYTHON_CONFIG
from .PYTHON_STRICT_EXCLUDE import PYTHON_STRICT_EXCLUDE
from .PYTHON_TESTS import PYTHON_TESTS
from .build_python_base import build_python_base


_DESIGN_NOTES = """
# python — File Rules for Python Projects

Plain imports, no `__all__` (the package root decides what is public).

## Internal Components Registry

| Component               | Type     | Description                                                          |
| :---------------------- | :------- | :------------------------------------------------------------------- |
| `PYTHON_BASE`           | Rule     | The default choice of Python files worth reading.                    |
| `PYTHON_CONFIG`         | Rule     | Project configuration files.                                         |
| `PYTHON_STRICT_EXCLUDE` | Rule     | Tests, configuration, environments and build output.                 |
| `PYTHON_TESTS`          | Rule     | Test files, by name or by folder.                                    |
| `build_python_base`     | Function | Builds the base rule; switches for `__init__.py`, `__main__.py`.     |
"""
