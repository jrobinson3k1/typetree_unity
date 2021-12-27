import os
from collections import deque
import re
import json

debug = True


class TypeTreeGenerator(object):
    PPTR_REGEX = r"^PPtr<(.+)>$"
    UNITY_CLASSES = ["GameObject", "MonoScript", "Sprite"]

    _tree_cache = {}
    _assembly_folder = None

    def __init__(self, assembly_folder, unity_version):
        from System import Array
        self.generator = self._create_generator(assembly_folder)
        self.unity_version = Array[int]([int(s) for s in unity_version.split('.')])
        print(str(self.unity_version))

    def generate_tree(self, assembly_file, class_name=""):
        if not assembly_file:
            raise ValueError("assembly file not specified")

        dump_all = True if not class_name else False
        if dump_all:
            print("Generating trees for all classes...")
        else:
            print("Generating trees for " + class_name + " and dependencies...")

        # init cache
        if assembly_file not in self._tree_cache:
            self._tree_cache[assembly_file] = {}

        tree = {}
        blacklist = self.UNITY_CLASSES.copy()
        class_deque = deque([class_name])
        while class_deque:
            next_class = class_deque.popleft()

            if next_class in tree:
                if (debug):
                    print("Skipping. Already in tree: " + next_class)
                continue

            if next_class in self._tree_cache[assembly_file]:
                if (debug):
                    print("Found in cache: " + next_class)
                tree[next_class] = self._tree_cache[assembly_file][next_class]
                continue

            def_iter = self.generator.getTypeDefs(assembly_file, next_class, "")

            # will contain one element set to None if could not find class name
            if not (a := def_iter.GetEnumerator()) or not a.MoveNext() or (not a.Current and not a.MoveNext()):
                print("Could not find class: " + next_class)
                continue

            class_tree, class_refs = self._dump_nodes(def_iter, blacklist)
            tree.update(class_tree)
            for class_ref in class_refs:
                if (
                    not dump_all
                    and class_ref not in blacklist
                    and class_ref not in tree
                    and class_deque.count(class_ref) == 0
                ):
                    if (debug):
                        print("Appending " + class_ref + " to queue")
                    class_deque.append(class_ref)

        self._tree_cache[assembly_file].update(tree)

        return tree

    def _dump_nodes(self, def_iter, blacklist):
        tree = {}
        class_refs = []
        for d in def_iter:
            if d.FullName in blacklist:
                if debug:
                    reason = "special Unity class" if d.FullName in self.UNITY_CLASSES else "previously failed to dump"
                    print("Skipping tree generation for " + d.FullName + " (" + reason + ")")
                continue

            if debug:
                print("Generating tree for " + d.FullName)

            try:
                nodes = self.generator.convertToTypeTreeNodes(d, self.unity_version)
            except Exception as e:
                blacklist.append(d.FullName)
                if (debug):
                    print("Failed getting node: " + d.FullName)
                    print(e)
                continue

            tree[d.FullName] = []
            for node in nodes:
                tree[d.FullName].append(
                    {
                        "level": node.m_Level,
                        "type": node.m_Type,
                        "name": node.m_Name,
                        "meta_flag": node.m_MetaFlag,
                    }
                )

                # check for referenced classes
                if (
                    (match := re.match(self.PPTR_REGEX, node.m_Type))
                    and (pptr_class := match.group(1))
                    and pptr_class not in class_refs
                ):
                    class_refs.append(pptr_class)

        return (tree, class_refs)

    def export_tree(self, tree, output_file):
        dir = os.path.dirname(output_file)
        if dir and not os.path.isdir(dir):
            os.mkdir(dir)

        if not os.access(dir, os.W_OK):
            raise ValueError("output file's directory is inaccessible")

        print("Exporting tree to " + output_file + "...")
        with open(output_file, "wt", encoding="utf8") as f:
            json.dump(tree, f, ensure_ascii=False)

    def clear_cache(self):
        self._tree_cache.clear()

    def _create_generator(self, assembly_folder):
        from Generator import Generator
        g = Generator()
        g.loadFolder(assembly_folder)
        return g