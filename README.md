# TypeTreeGeneratorPy
Current version: 0.1.0-alpha

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

## Prerequisites:
- [Python3](https://www.python.org/downloads/)
- [PythonNET](https://github.com/pythonnet/pythonnet)

## CLI Usage:
Execute `python cli.py -h` in a terminal to see usage instructions.

## Direct Usage:
See `cli.py` for example usage of the `TypeTreeGeneratorPy` module.
