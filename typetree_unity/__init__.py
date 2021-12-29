r"""
Unity type tree generator library.

Classes
-------
    TypeTreeGenerator: Generates and exports type trees for Unity assemblies
"""
__version__ = "0.2.2-alpha"

import os
import sys
import logging
from clr_loader import get_coreclr
from pythonnet import set_runtime

main_dir = os.path.dirname(os.path.realpath(__file__))
logs_dir = os.path.join(main_dir, "logs")
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
    filename=os.path.join(logs_dir, "logs.txt"),
    filemode="w"
)

typetree_generator_path = os.path.join(
    main_dir,
    "libs",
    "TypeTreeGenerator"
)
runtime_path = os.path.join(
    typetree_generator_path,
    "TypeTreeGenerator.runtimeconfig.json"
)
set_runtime(
    get_coreclr(runtime_path)
)
logging.debug("Loaded runtime configuration from %s", runtime_path)

sys.path.insert(0, typetree_generator_path)
logging.debug("Added %s to path", typetree_generator_path)

# needs to be imported after path is appended
import clr  # pylint: disable=wrong-import-position
clr.AddReference("TypeTreeGenerator")  # pylint: disable=no-member
logging.debug("Imported TypeTreeGenerator.dll")

# needs to be imported after TypeTreeGenerator reference is added
from .generator import TypeTreeGenerator  # pylint: disable=wrong-import-position
__all__ = ["TypeTreeGenerator"]

# clean up variables
del main_dir
del logs_dir
del typetree_generator_path
