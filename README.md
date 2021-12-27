# TypeTreeGeneratorPy
Current version: 0.1.0-alpha

Better README coming in the future. Still in early development. Things will be changing rapidly.

Ultimate goal of this project is to provide lighter weight and more easily accessible options for data mining Unity games, and provide outputs in easily exportable json format.

Generating a type tree of game data is one of many steps towards that goal. While solutions already exist, many are out-of-date, unintuitive, or can only be achieved through bulky and buggy UI.

Will likely be automated in the future, but for early release, there are two key components needed before this script will work: The Unity build version used by the game, and dumped game assemblies if the game was compiled with il2cpp.

The quickest way to determine which version of Unity a game is built against is to open one of the `.assets` files in the game's directory (typically in `[game_root]/[game]_Data/`) in Notepad (pick a small assets file, any will work). One of the first ASCII text will be the version (ex. 2019.4.23f1). For a scripted approach, see [UnityVersionFinderPy](https://github.com/jrobinson3k1/UnityVersionFinderPy).

To know if a game is compiled with il2cpp, look for `GameAssembly.dll` in the game's folder. If it is present, it was compiled with il2cpp. Use [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) to extract the game's assemblies, then use that folder with this script for the input folder.

If the game has a `Managed` folder (typically `[game_root]/[game]_Data/Managed`), or a folder containing `Assembly-CSharp.dll` then you're good to go. Use that folder as the input folder.

## Prerequisites:
- [Python3](https://www.python.org/downloads/)
- [PythonNET](https://github.com/pythonnet/pythonnet)

## CLI Usage:

Execute `python3 cli.py -h` in a terminal to see usage available options.
## Direct Usage:

See `cli.py` for usage example.
