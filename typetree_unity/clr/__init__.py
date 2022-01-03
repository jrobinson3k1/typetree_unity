"""
Package containing TypeTreeGenerator which utilizes CLR.

Classes
-------
    TypeTreeGenerator: Generates type trees for Unity assemblies

Methods
-------
    create_generator(assembly_folder, unity_version)
"""
from .assembly_loader import load
load()

# needs to be imported after Asset Studio assemblies have been loaded
from .generator import TypeTreeGenerator  # noqa: E402
__all__ = ["TypeTreeGenerator"]


def create_generator(assembly_folder, unity_version):
    """Create a TypeTreeGenerator."""
    return TypeTreeGenerator(assembly_folder, unity_version)
