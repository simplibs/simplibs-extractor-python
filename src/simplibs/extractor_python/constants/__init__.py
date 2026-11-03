from .PYTHON_CONFIG_NAMES import PYTHON_CONFIG_NAMES
from .PYTHON_OUTPUT_DIR_NAMES import PYTHON_OUTPUT_DIR_NAMES
from .PYTHON_SUFFIXES import PYTHON_SUFFIXES
from .PYTHON_TEST_DIR_NAMES import PYTHON_TEST_DIR_NAMES
from .PYTHON_VENV_DIR_NAMES import PYTHON_VENV_DIR_NAMES


_DESIGN_NOTES = """
# constants — Fixed Values of simplibs-extractor-python

Plain imports, no `__all__` (the package root decides what is public).

## Internal Components Registry

| Component                 | Type     | Description                                      |
| :------------------------ | :------- | :----------------------------------------------- |
| `PYTHON_CONFIG_NAMES`     | Constant | File names of Python project configuration.      |
| `PYTHON_OUTPUT_DIR_NAMES` | Constant | Folders of generated build output.               |
| `PYTHON_SUFFIXES`         | Constant | Suffixes of Python files.                        |
| `PYTHON_TEST_DIR_NAMES`   | Constant | Folders that hold Python tests.                  |
| `PYTHON_VENV_DIR_NAMES`   | Constant | Folders of Python virtual environments.          |

## Layering & Design
- Every value is a tuple of plain strings: the rules are built from them in `file_rules`.
- The names of version-control folders are not here: they come from `IGNORE_VCS` of `simplibs-path`.
"""
