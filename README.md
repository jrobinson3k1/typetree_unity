# TypeTreeGeneratorPy
Current version: 0.1.0

Better README coming in the future. Still in early development.

Ultimate goal of this project is to provide lighter weight and more easily accessible options for data mining Unity games, and provide outputs in easily exportable json format.

Generating a type tree of game data is one of many steps towards that goal. While solutions already exist, many are out-of-date, unintuitive, or can only be achieved through bulky and buggy UI.

Will likely be automated in the future, but for early release, there are two key components needed before this script will work: The Unity build version used by the game, and dumped game assemblies if the game was compiled with il2cpp.

The quickest way to determine which version of Unity a game is built against is to open one of the `.assets` files in the game's directory (typically in `[game_root]/[game]_Data/`) in Notepad (pick a small assets file, any will work). One of the first ASCII text will be the version (ex. 2019.4.23f1).

To know if a game is compiled with il2cpp, look for `GameAssembly.dll` in the game's folder. If it is present, it was compiled with il2cpp. Use [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) to extract the game's assemblies, then use that folder with this script for the input folder.

If the game has a `Managed` folder (typically `[game_root]/[game]_Data/Managed`), or a folder containing `Assembly-CSharp.dll` then you're good to go. Use that folder as the input folder.

## Prerequisites:
- [Python3](https://www.python.org/downloads/)
- [PythonNET](https://github.com/pythonnet/pythonnet)

## CLI Usage:

```
usage: typetreegen.py [-h] [-a, --assembly] [-c, --classes [...]] [-o, --output] [-v, --version] [-n, --namesonly]
                      [-d, --debug]
                      input_folder unity_version

Generates type trees from Unity assemblies and outputs in JSON format

positional arguments:
  input_folder          folder containing assemblies
  unity_version         Unity build version

optional arguments:
  -h, --help            show this help message and exit
  -a, --assembly        assembly file to load (default: Assembly-CSharp.dll)
  -c, --classes [ ...]  classes to dump for the type tree (all if unspecified). Automatically dumps class
                        dependencies.
  -o, --output          type tree output file (default:
                        C:\Users\jason\workspace\TypeTreeGeneratorPy\output\[typetree|classnames].json).
  -v, --version         version of this script
  -n, --namesonly       only output class names (will output as classnames.json if output is not specified)
  -d, --debug           enable debug logging
```
## Direct Usage:

`TypeTreeGenerator` can be instantiated and used directly in your script or through the Python interpreter. See `typetreegen.py`, which includes example usage for the CLI implementation.
