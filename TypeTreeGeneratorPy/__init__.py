__version__ = "0.1.0-alpha"

import os
import sys
from clr_loader import get_coreclr
from pythonnet import set_runtime

typetree_generator_path = os.path.join(os.path.dirname(__file__), "libs", "TypeTreeGenerator")

set_runtime(
    get_coreclr(
        os.path.join(typetree_generator_path, "TypeTreeGenerator.runtimeconfig.json")
    )
)

sys.path.append(typetree_generator_path)
del typetree_generator_path

# needs to be imported after path is appended
import clr  # noqa: E402
clr.AddReference("TypeTreeGenerator")

# needs to be imported after TypeTreeGenerator reference is added
from .generator import TypeTreeGenerator  # noqa: E402
from .generator import OutputMode  # noqa: E402
__all__ = ["TypeTreeGenerator", "OutputMode"]
