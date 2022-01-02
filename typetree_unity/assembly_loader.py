"""Asset Studio importer powered by PythonNET."""
import os
import sys
from clr_loader import get_coreclr
from pythonnet import set_runtime


def load():
    """Load Asset Studio assembly references via CLR."""
    lib_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "libs",
        "AssetStudio"
    )
    set_runtime(
        get_coreclr(
            os.path.join(
                lib_dir,
                "runtimeconfig.json"
            )
        )
    )
    sys.path.insert(0, lib_dir)

    # needs to be imported after runtime is set and path is appended
    import clr  # pylint: disable=import-outside-toplevel
    for filename in os.listdir(lib_dir):
        split_file = os.path.splitext(filename)
        if split_file[1] == ".dll":
            clr.AddReference(os.path.join(lib_dir, split_file[0]))  # pylint: disable=no-member
