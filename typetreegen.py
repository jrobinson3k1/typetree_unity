# Required dependencies:
# PythonNET (pip install pythonnet)

import os
import sys
from collections import deque
import re
import json
from clr_loader import get_coreclr
from pythonnet import set_runtime

VERSION = "0.1.0"
ROOT = os.path.dirname(__file__)
TYPETREE_GENERATOR_PATH = os.path.join(ROOT, "TypeTreeGenerator")

debug = False

# 2019.4.23f1 - Unity version used by Last Epoch

def main():
    default_output_folder = os.path.join(os.path.dirname(__file__), "output")
    default_assembly_filename = "Assembly-CSharp.dll"
    default_typetree_name = "typetree"
    default_classname_name = "classnames"

    from argparse import Namespace
    from argparse import ArgumentParser
    import validators

    # populate default values
    namespace = Namespace()
    setattr(namespace, "default_output_folder", default_output_folder)

    parser = ArgumentParser(description = "Generates type trees from Unity assemblies and outputs in JSON format")
    parser.add_argument("assembly_folder", type = str, action = validators.ValidateFolderExistsAction, metavar = "input_folder", help = "folder containing assemblies")
    parser.add_argument("unity_version", type = str, action = validators.ValidateUnityVersion, help = "Unity build version")
    parser.add_argument("-a, --assembly", type = str, dest = "assembly_file", default = default_assembly_filename, action = validators.ValidateAssemblyFileExistsAction, metavar = "", help = "assembly file to load (default: " + default_assembly_filename + ")")
    parser.add_argument("-c, --classes", type = str, dest = "class_names", default = "", nargs = "*", metavar = "", help = "classes to dump for the type tree (all if unspecified). Automatically dumps class dependencies.")
    parser.add_argument("-o, --output", type = str, dest = "output_file", action = validators.ValidateOutputFileAction, metavar = "", help = "type tree output file (default: " + default_output_folder + os.path.sep + "[" + default_typetree_name + "|" + default_classname_name + "].json).")
    parser.add_argument("-v, --version", action = "version", version = "%(prog)s " + VERSION, help = "version of this script")
    parser.add_argument("-n, --namesonly", dest = "names_only", action = "store_true", help = "only output class names (will output as " + default_classname_name + ".json if output is not specified)")
    parser.add_argument("-d, --debug", dest = "debug", action = "store_true", help = "enable debug logging")
    args = parser.parse_args(namespace = namespace)

    global debug
    debug = args.debug

    class_names = [args.class_names] if not isinstance(args.class_names, list) else args.class_names
    generator = TypeTreeGenerator(args.assembly_folder, args.unity_version)
    trees = {}
    for class_name in class_names:
        trees.update(generator.generate_tree(args.assembly_file, class_name))

    if trees:
        if args.names_only:
            trees = [
                key for key in trees.keys()
            ]
            trees.sort()

        output_file = args.output_file if args.output_file else os.path.join(default_output_folder, (default_classname_name if args.names_only else default_typetree_name) + ".json")
        generator.export_tree(trees, output_file)
        print("Success")
    else:
        print("Type tree did not generate")

class TypeTreeGenerator():
    PPTR_REGEX = r"^PPtr<(.+)>$"
    UNITY_CLASSES = ["GameObject", "MonoScript", "Sprite"]

    _tree_cache = {}
    _assembly_folder = None

    def __init__(self, assembly_folder, unity_version):
        self.pythonnet_init()
        self.generator = self._create_generator(assembly_folder)

        from System import Array
        self.unity_version = Array[int]([int(s) for s in unity_version.split('.')])

    def pythonnet_init(self):
        print("Loading TypeTreeGenerator runtime...")

        rt = get_coreclr(
            os.path.join(TYPETREE_GENERATOR_PATH, "TypeTreeGenerator.runtimeconfig.json")
        )
        set_runtime(rt)

    def generate_tree(self, assembly_file, class_name = ""):
        if not assembly_file:
            raise ValueError("assembly file not specified")

        dump_all = True if not class_name else False
        if dump_all:
            print("Generating trees for all classes...")
        else:
            print("Generating trees for " + class_name + " and dependencies...")

        # init cache
        if not assembly_file in self._tree_cache:
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

            for d in def_iter:
                if d.FullName in blacklist:
                    if debug:
                        reason = "special Unity class" if d.FullName in self.UNITY_CLASSES else "previously failed to dump"
                        print("Skipping tree generation for " + d.FullName + " (" + reason + ")")
                    continue

                if debug or not dump_all:
                    print("Generating tree for " + d.FullName + "...")

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
                            "level" : node.m_Level,
                            "type" : node.m_Type,
                            "name" : node.m_Name,
                            "meta_flag" : node.m_MetaFlag,
                        }
                    )

                    # check for referenced classes if we're not already dumping every class
                    if (
                        not dump_all and
                        (match := re.match(self.PPTR_REGEX, node.m_Type)) and
                        (pptr_class := match.group(1)) and
                        not pptr_class in blacklist and
                        not pptr_class in tree and
                        class_deque.count(pptr_class) == 0
                    ):
                        if (debug):
                            print("Appending " + pptr_class + " to queue")
                        class_deque.append(pptr_class)

        self._tree_cache[assembly_file].update(tree)

        return tree

    def export_tree(self, tree, output_file):
        dir = os.path.dirname(output_file)
        if dir and not os.path.isdir(dir):
            os.mkdir(dir)

        if not os.access(dir, os.W_OK):
            raise ValueError("output file's directory is inaccessible")

        print("Exporting tree to " + output_file + "...")
        with open(output_file, "wt", encoding = "utf8") as f:
            json.dump(tree, f, ensure_ascii = False)

    def clear_cache(self):
        self._tree_cache.clear()

    def _create_generator(self, assembly_folder):
        # path HAS to be appended before importing clr
        sys.path.append(TYPETREE_GENERATOR_PATH)
        import clr
        clr.AddReference("TypeTreeGenerator")

        from Generator import Generator
        g = Generator()
        g.loadFolder(assembly_folder)
        return g

if __name__ == "__main__":
    main()
