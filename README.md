# typetree_unity
[![PyPI](https://img.shields.io/pypi/v/typetree-unity)](https://pypi.org/project/typetree-unity/)
[![MIT](https://img.shields.io/pypi/l/UnityPy.svg)](https://github.com/jrobinson3k1/typetree_unity/blob/master/LICENSE)

A standalone type tree generator for Unity assemblies.

Better README coming in the future. Still in early development. Things will be changing rapidly.

Ultimate goal of this project is to provide lighter weight and more easily accessible options for data mining Unity games, and provide outputs in easily transportable formats.

There are two required parameters to generate a type tree:
- Unity build version
- Game assembly files built with Mono

### Unity build version
The quickest way to determine which version of Unity a game is built against is to open one of the `.assets` files in the game's directory (typically located at `[game_root]/[game]_Data/`) in Notepad (pick a small assets file, any will work). One of the first ASCII text will be the version (ex. 2019.4.23f1). For a scripted approach, see [UnityVersionFinderPy](https://github.com/jrobinson3k1/UnityVersionFinderPy).

### Game assembly files built with Mono
To determine if a game is already built with Mono, look in the game directory for a `Assembly-CSharp.dll` file (typically located at `[game_root]/[game]_Data/Managed`). If it does, then the game's assembly files were built with Mono.

If that's not the case, the game was likely built with il2cpp (will instead have a `GameAssembly.dll` file). To convert from il2cpp to Mono format, see [Il2CppDumper](https://github.com/Perfare/Il2CppDumper).

## Install:
`pip install typtree_unity`

## CLI Usage:
```
usage: python -m typetree_unity [-h] [-c [...]] [-d] [-n] [-o] [-v] assembly_folder unity_version

Generates type trees from Unity assemblies and outputs in JSON format.

positional arguments:
  assembly_folder       folder containing assemblies (game's DLL files)
  unity_version         Unity build version

options:
  -h, --help            show this help message and exit
  -c [ ...], --classes [ ...]
                        classes to dump for the type tree (all if unspecified). Automatically dumps class dependencies.
  -d, --debug           enable debug output
  -n, --namesonly       only output class names (will output as classnames.json if output is not specified)
  -o, --output         type tree output file (default: [script_directory]\output\typetree.json). Supports relative paths.
  -v, --version         version of this package
```

## Library Usage:
See `typetree_unity/__main__.py` for example usage of the `typetree_unity` module.
