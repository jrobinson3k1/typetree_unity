r"""
Unity type tree generator library.

Classes
-------
    TypeTreeGenerator: Generates type trees for Unity assemblies

Methods
-------
    create_generator(assembly_folder, unity_version)
    export_type_tree(tree, output_file)
"""
__version__ = "0.4.0-alpha"

import os
import logging
from . import assembly_loader
from .exporter import export_type_tree

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

assembly_loader.load()
# needs to be imported after Asset Studio assemblies have been loaded
from .generator import TypeTreeGenerator  # noqa: E402
__all__ = ["TypeTreeGenerator", "export_type_tree"]

# clean up variables
del main_dir
del logs_dir


def create_generator(assembly_folder, unity_version):
    """Create a TypeTreeGenerator."""
    return TypeTreeGenerator(assembly_folder, unity_version)
