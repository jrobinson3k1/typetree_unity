"""Export type trees generated from TypeTreeGenerator."""
import os
import logging
import json


def export_type_tree(tree, output_file):
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
