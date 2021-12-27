import os
from argparse import Namespace
from argparse import ArgumentParser
import validators

from TypeTreeGeneratorPy import TypeTreeGenerator
from TypeTreeGeneratorPy import __version__ as version


def main():
    args = get_args()

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

        generator.export_tree(trees, args.output_file)
        print("Success")
    else:
        print("Type tree did not generate")


def get_args():
    default_output_folder = os.path.join(os.path.dirname(__file__), "output")
    default_assembly_filename = "Assembly-CSharp.dll"
    default_typetree_name = "typetree"
    default_classname_name = "classnames"

    # populate default values
    namespace = Namespace()
    setattr(namespace, "default_output_folder", default_output_folder)

    parser = ArgumentParser(description="Generates type trees from Unity assemblies and outputs in JSON format")
    parser.add_argument(
        "assembly_folder",
        type=str,
        action=validators.ValidateFolderExistsAction,
        metavar="input_folder",
        help="folder containing assemblies"
    )
    parser.add_argument(
        "unity_version",
        type=str,
        action=validators.ValidateUnityVersion,
        help="Unity build version"
    )
    parser.add_argument(
        "-a, --assembly",
        type=str,
        dest="assembly_file",
        default=default_assembly_filename,
        action=validators.ValidateAssemblyFileExistsAction,
        metavar="",
        help="assembly file to load (default: " + default_assembly_filename + ")"
    )
    parser.add_argument(
        "-c, --classes",
        type=str,
        dest="class_names",
        default="",
        nargs="*",
        metavar="",
        help="classes to dump for the type tree (all if unspecified). Automatically dumps class dependencies."
    )
    parser.add_argument(
        "-o, --output",
        type=str,
        dest="output_file",
        action=validators.ValidateOutputFileAction,
        metavar="",
        help="type tree output file (default: " + default_output_folder + os.path.sep + "[" + default_typetree_name + "|" + default_classname_name + "].json).")
    parser.add_argument(
        "-v, --version",
        action="version",
        version="%(prog)s " + version, help="version of this package"
    )
    parser.add_argument(
        "-n, --namesonly",
        dest="names_only",
        action="store_true",
        help="only output class names (will output as " + default_classname_name + ".json if output is not specified)")
    parser.add_argument(
        "-d, --debug",
        dest="debug",
        action="store_true",
        help="enable debug logging"
    )

    args = parser.parse_args(namespace=namespace)
    args.output_file = args.output_file if args.output_file else os.path.join(default_output_folder, (default_classname_name if args.names_only else default_typetree_name) + ".json")
    return args


if __name__ == "__main__":
    main()
