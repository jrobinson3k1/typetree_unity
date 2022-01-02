"""
Container for TypeTreeGenerator class and export methods.

assembly_loader.load() needs to be called first if not importing through the typetree_unity module.
"""

import os
import logging
from dataclasses import dataclass
from collections import deque
from collections.abc import Iterable
import re
from enum import Enum, unique

from System import Array
from System.Collections.Generic import List
from Mono.Cecil import AssemblyDefinition
from AssetStudio import AssemblyLoader
from AssetStudio import SerializedTypeHelper
from AssetStudio import TypeTreeNode
from AssetStudio import TypeDefinitionConverter

_SEM_VER_REGEX = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
_PPTR_REGEX = r"^PPtr<(.+)>$"
_UNITY_CLASSES = ["GameObject", "MonoScript", "Sprite"]


def _normalize_unity_version(version):
    """
    Normalize a version string to a true Semantic Versioning string.

    Unity follows Semantic Versioning (Major.Minor.Patch). However, build versions
    tend to have a qualifier after the Patch value. Strip that out.
    """
    match = re.search(_SEM_VER_REGEX, version)
    if not match:
        raise ValueError(f"Invalid Unity build version: {version}")

    normalized_version = match.group(0)
    if normalized_version != version:
        logging.info("Resolved Unity version from %s to %s", version, normalized_version)
    return normalized_version


@unique
class _AssemblyFile(Enum):
    ASSEMBLY_CSHARP = "Assembly-CSharp"
    ASSEMBLY_CSHARP_FIRSTPASS = "Assembly-CSharp-firstpass"

    def __init__(self, base_name):
        self.base_name = base_name
        self.file_name = base_name + ".dll"


@dataclass(frozen=True)
class _ClassRef:
    assembly: _AssemblyFile
    class_name: str


class TypeTreeGenerator:
    """
    Generates and exports type trees from Unity assemblies.

    Methods
    -------
    generate_tree(assembly_file, class_names=None) : Dict[str]
    get_cached_trees() : Dict[str]
    clear_cache()
    """

    _loader: AssemblyLoader
    _tree_cache = {}

    def __init__(self, assembly_folder, unity_version):
        """
        Generate and export type trees from Unity assemblies.

        Parameters
        ----------
        assembly_folder : str
            Path to Unity assemblies
        unity_version : str
            Unity build version (Format: "Major.Minor.Patch")
        """
        unity_version = _normalize_unity_version(unity_version)
        self._unity_version = Array[int]([int(s) for s in unity_version.split('.')])
        self._available_classes = self._find_all_classes(assembly_folder)
        self._loader = self._create_loader(assembly_folder)
        logging.debug(f"Init TypeTreeGenerator: {len(self._available_classes)} classes found")

    def generate_type_trees(self, class_names=None):
        """
        Generate type trees for the specified classes (all if not specified).

        Referenced class types will be automatically dumped. Results are cached.

        Parameters
        ----------
        assembly_file : str
            File name of the assembly to dump (typically Assembly-CSharp.dll)
        class_names : Union[str, Iterable<str>], optional
            The classes to dump (all if None)

        Returns
        -------
        dict[str, list]
            Dictionary of class names containing a list of type definitions
        """
        if class_names:
            if isinstance(class_names, str):
                class_names = [class_names]
            if not isinstance(class_names, Iterable):
                raise TypeError(f"expected str or Iterable<str>, got {type(class_names)}")
            class_refs = [x for x in self._available_classes if x.class_name in class_names]
        else:
            class_refs = list(self._available_classes)

        if not class_refs:
            logging.debug("No available classes")
            return None

        logging.debug("Generating trees for %s classes", len(class_refs))

        trees = self._generate_type_trees(class_refs)

        # cache results
        count = 0
        for key, value in trees.items():
            count += len(value)
            if key not in self._tree_cache:
                self._tree_cache[key] = value.copy()
            else:
                self._tree_cache[key].update(value.copy())

        logging.debug("Generated trees for %s classes", count)

        return trees

    def _generate_type_trees(self, class_refs):
        trees = {}
        class_deque = deque(class_refs)
        while class_deque:
            class_ref = class_deque.popleft()
            # TODO: Check cache, add parameter to allow checking from cache
            type_tree, referenced_classes = self._dump_class(
                class_ref.assembly.file_name,
                class_ref.class_name
            )
            if type_tree:
                if class_ref.assembly.base_name not in trees:
                    trees[class_ref.assembly.base_name] = type_tree
                else:
                    trees[class_ref.assembly.base_name].update(type_tree)

            for class_name in referenced_classes:
                if (
                    class_name not in _UNITY_CLASSES and
                    class_deque.count(class_name) == 0
                ):
                    class_ref = None
                    for ref in self._available_classes:
                        if ref.class_name == class_name:
                            class_ref = ref
                            break

                    if (
                        class_ref and (
                            class_ref.assembly.base_name not in trees or
                            class_ref.class_name not in trees[class_ref.assembly.base_name])
                    ):
                        logging.debug(
                            "Appending referenced class %s to queue",
                            class_ref.class_name
                        )
                        class_deque.append(class_ref)

        return trees

    def _dump_class(self, assembly_name, class_name):
        type_def = self._loader.GetTypeDefinition(assembly_name, class_name)
        if not type_def:
            logging.warning("Could not find class %s in %s", class_name, assembly_name)
            return None, []

        nodes, referenced_classes = self._convert_to_type_tree_nodes(type_def)
        return {type_def.FullName: nodes}, referenced_classes

    def _convert_to_type_tree_nodes(self, type_def):
        logging.debug("Generating type tree nodes for %s", type_def.FullName)

        nodes = List[TypeTreeNode]()
        type_helper = SerializedTypeHelper(self._unity_version)
        type_helper.AddMonoBehaviour(nodes, 0)
        try:
            type_def_converter = TypeDefinitionConverter(type_def, type_helper, 1)
            nodes.AddRange(type_def_converter.ConvertToTypeTreeNodes())
        except Exception:
            logging.exception("Failed getting class: %s", type_def.FullName)
            return None, []

        type_tree_nodes = []
        referenced_classes = []
        for node in nodes:
            type_tree_nodes.append({
                "level": node.m_Level,
                "type": node.m_Type,
                "name": node.m_Name,
                "meta_flag": node.m_MetaFlag,
            })

            # check for referenced classes
            if (
                (match := re.match(_PPTR_REGEX, node.m_Type))
                and (pptr_class := match.group(1))
                and pptr_class not in referenced_classes
            ):
                referenced_classes.append(pptr_class)

        return type_tree_nodes, referenced_classes

    def _find_class_location(self, class_name):
        for assembly_base, class_list in self._available_classes:
            if class_name in class_list:
                return assembly_base

        return None

    @classmethod
    def _find_all_classes(cls, assembly_folder):
        """Find fully qualified class names from a game's assemblies."""
        class_refs = set()
        for assembly in _AssemblyFile:
            file_path = os.path.join(assembly_folder, assembly.file_name)
            if not os.path.isfile(file_path):
                raise ValueError(f"{assembly.file_name} not found in {assembly_folder}")

            assembly_def = AssemblyDefinition.ReadAssembly(file_path)
            for type_def in assembly_def.MainModule.GetTypes():
                class_refs.add(_ClassRef(assembly, type_def.FullName))

        return class_refs

    def get_cached_trees(self):
        """
        Get a copy of the type trees that have been created from the generate_tree method.

        Returns
        -------
        dict[str, dict[str, list]]
            Dictionary of assembly file names containing dictionary of the type tree for class names
        """
        return self._tree_cache.copy()

    def clear_cache(self):
        """Clear type tree cache populated from the generate_tree method."""
        self._tree_cache.clear()

    @classmethod
    def _create_loader(cls, assembly_folder):
        loader = AssemblyLoader()
        loader.Load(assembly_folder)
        return loader
