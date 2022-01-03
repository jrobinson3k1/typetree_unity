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
__version__ = "0.5.0"

import os
import logging
from .exporter import export_type_tree

__all__ = ["export_type_tree"]

main_dir = os.path.dirname(os.fspath(__file__))
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
    filename=os.path.join(main_dir, "logs.txt"),
    filemode="w"
)
del main_dir
