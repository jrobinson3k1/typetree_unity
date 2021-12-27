import os
import logging
from collections import deque
import re
from enum import Enum, unique
import json

PPTR_REGEX = r"^PPtr<(.+)>$"
UNITY_NAMSPACE = ["UnityEngine"]  # Top-level Unity namespaces
UNITY_CLASSES = ["GameObject", "MonoScript", "Sprite"]  # Fully qualified class names


@unique
class OutputMode(Enum):
    JSON = "json"
    TEXT = "txt"

    @property
    def ext(self):
        return self.value

    def fromExt(ext):
        for mode in OutputMode:
            if mode.ext == ext:
                return mode
        return None


class TypeTreeGenerator(object):
    _tree_cache = {}

    def __init__(self, assembly_folder, unity_version):
        from System import Array
        self.generator = self._create_generator(assembly_folder)
        self.unity_version = Array[int]([int(s) for s in unity_version.split('.')])

    def generate_tree(self, assembly_file, class_name="", blacklist=[]):
        if not assembly_file:
            raise ValueError("assembly file not specified")

        dump_all = True if class_name == "" else False
        logging.debug("Generating trees from " + assembly_file + " for " + ("all classes" if dump_all else "class " + class_name))

        blacklist = list(set(blacklist + UNITY_CLASSES))

        # init cache
        if assembly_file not in self._tree_cache:
            self._tree_cache[assembly_file] = {}

        tree = {}
        class_deque = deque([class_name])
        while class_deque:
            next_class = class_deque.popleft()
            if next_class in tree or next_class in blacklist:
                continue

            if next_class in self._tree_cache[assembly_file]:
                tree[next_class] = self._tree_cache[assembly_file][next_class]
                # TODO: Append referenced classes (should already be in cache)
                continue

            type_defs = self.generator.getTypeDefs(assembly_file, next_class, "")

            # will contain one element set to None if could not find class name
            if not (a := type_defs.GetEnumerator()) or not a.MoveNext() or (not a.Current and not a.MoveNext()):
                logging.warn("Could not find class: " + next_class)
                continue

            class_tree, class_refs = self._dump_nodes(type_defs, blacklist)
            tree.update(class_tree)
            if not dump_all:
                for class_ref in class_refs:
                    if (
                        class_ref not in blacklist
                        and class_ref not in tree
                        and class_deque.count(class_ref) == 0
                    ):
                        logging.debug("Appending referenced class " + class_ref + " to queue")
                        class_deque.append(class_ref)

        self._tree_cache[assembly_file].update(tree)

        return tree

    def export_tree(self, tree, dir, filename="typetree", mode: OutputMode = OutputMode.JSON):
        if not os.path.isdir(dir):
            os.mkdir(dir)

        if not os.access(dir, os.W_OK):
            raise RuntimeError("output directory is inaccessible: " + str(dir))

        output_file = os.path.join(dir, filename + "." + mode.ext)
        with open(output_file, "wt", encoding="utf8") as f:
            match mode:
                case OutputMode.JSON:
                    json.dump(tree, f, ensure_ascii=False)
                case OutputMode.TEXT:
                    self._export_tree_as_text(tree, f)
                case _:
                    logging.error("Unhandled export mode: " + mode.name)
                    return

        logging.info("Exported tree to " + output_file)

    def copy_cache(self):
        return self._tree_cache.copy()

    def clear_cache(self):
        self._tree_cache.clear()

    def _dump_nodes(self, type_defs, blacklist):
        tree = {}
        class_refs = []
        for d in type_defs:
            type_name = d.FullName
            if type_name in blacklist:
                continue

            logging.debug("Generating tree for " + type_name)

            try:
                nodes = self.generator.convertToTypeTreeNodes(d, self.unity_version)
            except Exception:
                blacklist.append(type_name)
                logging.exception("Failed getting node: " + type_name)
                continue

            tree[type_name] = []
            for node in nodes:
                tree[type_name].append(
                    {
                        "level": node.m_Level,
                        "type": node.m_Type,
                        "name": node.m_Name,
                        "meta_flag": node.m_MetaFlag,
                    }
                )

                # check for referenced classes
                if (
                    (match := re.match(PPTR_REGEX, node.m_Type))
                    and (pptr_class := match.group(1))
                    and pptr_class.split(".")[0] not in UNITY_NAMSPACE
                    and pptr_class not in class_refs
                ):
                    class_refs.append(pptr_class)
        return (tree, class_refs)

    def _export_tree_as_text(self, tree, f, indent=2):
        for item in tree:
            f.write(item + " ")
            for node in tree[item]:
                f.write((" " * (node["level"] * indent)) + node["type"] + " " + node["name"] + ((" " + str(node["meta_flag"])) if node["meta_flag"] else "") + "\n")

    def _create_generator(self, assembly_folder):
        from Generator import Generator
        g = Generator()
        g.loadFolder(assembly_folder)
        return g
