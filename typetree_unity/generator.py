"""Container for TypeTreeGenerator class and export methods."""

import os
import logging
from collections import deque
import re
import json

from System import Array  # pylint: disable=import-error
from Generator import Generator  # pylint: disable=import-error

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

class TypeTreeGenerator:
    """
    Generates and exports type trees from Unity assemblies.

    Methods
    -------
    generate_tree(assembly_file, class_names=None) : Dict[str]
    export_tree(tree, output_file)
    """

    _tree_cache = {}
    _assembly_folder = None

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
        self.generator = self._create_generator(assembly_folder)
        self.unity_version = Array[int]([int(s) for s in unity_version.split('.')])

    def generate_tree(self, assembly_file, class_names=None):
        """
        Generate type trees for the specified classes (all if not specified).

        Referenced class types will be automatically dumped. Results are cached.

        Parameters
        ----------
        assembly_file : str
            File name of the assembly to dump (typically Assembly-CSharp.dll)
        class_names : list[str], optional
            The classes to dump (default is all classes)

        Returns
        -------
        dict[str, list]
            Dictionary of class names containing a list of type definitions
        """
        if not assembly_file:
            raise ValueError("assembly file not specified")

        dump_all = False
        if not class_names:
            dump_all = True
            class_names = [""]

        if not isinstance(class_names, list):
            class_names = [class_names]

        logging.debug("Generating trees from %s for %s",
            assembly_file,
            ("all classes" if dump_all else "classes " + str(class_names))
        )

        # init cache
        if assembly_file not in self._tree_cache:
            self._tree_cache[assembly_file] = {}

        tree = {}
        blacklist = _UNITY_CLASSES.copy()
        class_deque = deque(class_names)
        while class_deque:
            next_class = class_deque.popleft()
            if next_class in tree:
                continue

            if next_class in self._tree_cache[assembly_file]:
                tree[next_class] = self._tree_cache[assembly_file][next_class]
                continue

            def_iter = self.generator.getTypeDefs(assembly_file, next_class, "")

            # will contain one element set to None if could not find class name
            if (
                not (enumerator := def_iter.GetEnumerator())
                or not enumerator.MoveNext()
                or (not enumerator.Current and not enumerator.MoveNext())
            ):
                logging.warning("Could not find class: %s", next_class)
                continue

            class_tree, class_refs = self._dump_nodes(def_iter, blacklist)
            tree.update(class_tree)
            if not dump_all:
                for class_ref in class_refs:
                    if (
                        class_ref not in blacklist
                        and class_ref not in tree
                        and class_deque.count(class_ref) == 0
                    ):
                        logging.debug("Appending referenced class %s to queue", class_ref)
                        class_deque.append(class_ref)

        self._tree_cache[assembly_file].update(tree)

        return tree

    def _dump_nodes(self, def_iter, blacklist):
        tree = {}
        class_refs = []
        for type_def in def_iter:
            name = type_def.FullName
            if name in blacklist:
                continue

            logging.debug("Generating tree for %s", name)

            try:
                nodes = self.generator.convertToTypeTreeNodes(type_def, self.unity_version)
            except Exception: # pylint: disable=broad-except
                blacklist.append(name)
                logging.exception("Failed getting class: %s", name)
                continue

            tree[name] = []
            for node in nodes:
                tree[name].append(
                    {
                        "level": node.m_Level,
                        "type": node.m_Type,
                        "name": node.m_Name,
                        "meta_flag": node.m_MetaFlag,
                    }
                )

                # check for referenced classes
                if (
                    (match := re.match(_PPTR_REGEX, node.m_Type))
                    and (pptr_class := match.group(1))
                    and pptr_class not in class_refs
                ):
                    class_refs.append(pptr_class)

        return (tree, class_refs)

    @classmethod
    def export_tree(cls, tree, output_file):
        """
        Export type tree to JSON.

        Parameters
        ----------
        tree : dict[str, list]
            Type trees created from the generate_tree method
        output_file: str
            File path where type tree(s) will be exported
        """
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        if not os.access(output_dir, os.W_OK):
            raise RuntimeError("output file's directory is inaccessible")

        with open(output_file, "wt", encoding="utf8") as stream:
            json.dump(tree, stream, ensure_ascii=False)

        logging.info("Exported tree to %s", output_file)

    def get_cached_trees(self):
        """
        Get a copy of the type trees that have been created from the generate_tree method.

        Returns
        -------
        dict[str, dict[str, list]]
            Dictionary of assembly file names containing dictonary of the type tree for class names
        """
        return self._tree_cache.copy()

    def clear_cache(self):
        """Clear type tree cache populated from the generate_tree method."""
        self._tree_cache.clear()

    @classmethod
    def _create_generator(cls, assembly_folder):
        generator = Generator()
        generator.loadFolder(assembly_folder)
        return generator
