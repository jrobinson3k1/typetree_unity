import os
import logging
from logging import LogRecord
from logging import StreamHandler
from argparse import Namespace
from argparse import ArgumentParser
import validators

from TypeTreeGeneratorPy import OutputMode
from TypeTreeGeneratorPy import TypeTreeGenerator
from TypeTreeGeneratorPy import __version__ as version


def main():
    _init_logger()
    args = _get_args()

    if args.enable_debug_output:
        console.setLevel(logging.DEBUG)

    output_dir, output_file_name, output_file_ext = _deconstruct_path(args.output_file)
    output_mode = OutputMode.fromExt(output_file_ext)

    generator = TypeTreeGenerator(args.assembly_folder, args.unity_version)
    trees = {}
    for class_name in args.class_names:
        trees.update(generator.generate_tree(args.assembly_file, class_name))

    if trees:
        if args.names_only:
            trees = [
                key for key in trees.keys()
            ]
            trees.sort()

        generator.export_tree(trees, output_dir, output_file_name, output_mode)
    else:
        logging.info("Type tree did not generate")


def _deconstruct_path(path):
    dir, file = os.path.split(path)
    file_name, file_ext = os.path.splitext(file)
    file_ext = file_ext.split(".")[1] if file_ext else file_ext
    return dir, file_name, file_ext


def _get_args():
    default_output_folder = os.path.join(os.path.dirname(__file__), "output")
    default_assembly_filename = "Assembly-CSharp.dll"
    default_typetree_name = "typetree"
    default_classname_name = "classnames"

    # populate default values
    namespace = Namespace()
    setattr(namespace, "default_output_folder", default_output_folder)

    parser = ArgumentParser(description="Generates type trees from Unity assemblies and outputs in JSON or text format")
    parser.add_argument(
        "assembly_folder",
        action=validators.ValidateFolderExistsAction,
        metavar="input_folder",
        help="folder containing assemblies"
    )
    parser.add_argument(
        "unity_version",
        action=validators.ValidateUnityVersion,
        help="Unity build version"
    )
    parser.add_argument(
        "-a",
        "--assembly",
        dest="assembly_file",
        default=default_assembly_filename,
        action=validators.ValidateAssemblyFileExistsAction,
        metavar="",
        help="assembly file to load (default: " + default_assembly_filename + ")"
    )
    parser.add_argument(
        "-c",
        "--classes",
        dest="class_names",
        default=[""],
        nargs="*",
        metavar="",
        help="classes to dump for the type tree (all if unspecified). Automatically dumps class dependencies."
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        action=validators.ValidateOutputFileAction,
        metavar="",
        help="type tree output file (default: " + default_output_folder + os.path.sep + default_typetree_name + ".json)."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + version, help="version of this package"
    )
    parser.add_argument(
        "-n",
        "--namesonly",
        dest="names_only",
        action="store_true",
        help="only output class names (will output as " + default_classname_name + ".json if output is not specified)"
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="enable_debug_output",
        action="store_true",
        help="enable debug output"
    )

    args = parser.parse_args(namespace=namespace)
    args.output_file = args.output_file if args.output_file else os.path.join(default_output_folder, (default_classname_name if args.names_only else default_typetree_name) + ".json")
    return args


def _init_logger():
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        filename="logs/logs.txt",
        filemode="w"
    )

    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(console)


class NoStackTraceStreamHandler(StreamHandler):
    def emit(self, record):
        try:
            if record.exc_info:
                record = LogRecord(record.name, record.levelname, record.pathname, record.lineno, record.msg, record.args, None, record.funcName, record.stack_info)
            super().emit(record)
        except Exception:
            self.handleError(record)


console = NoStackTraceStreamHandler()


if __name__ == "__main__":
    main()
