# Python for Zelda64Recompiled

A resource for modders. Enables use of the Python Standard library within mods, and executing Python code inline inside of mod code in a performant manner.

This enabled many behaviors that would otherwise require an external library to be compiled, and in manner that's MUCH easier than compiling your own external library.

Requires Zelda64Recompiled 1.2.1 or above.

The full readme, along with development instructions, can be found on the [GitHub repo](https://github.com/LT-Schmiddy/zelda64recomp-python-extlibs-mod).

```C
// A simple example of reading text from a file, using Python's pathlib module:
void file_access_example() {
    REPY_FN_SETUP;
    REPY_FN_EXEC_CACHE(
        file_access_test_exec1, 
        "from pathlib import Path\n"
        "sound_json_str = Path('sound.json').read_text()\n"
    );

    char* sound_json_str = REPY_FN_GET_STR("sound_json_str");
    recomp_printf("Sound.json Content:\n%s\n", sound_json_str);
    recomp_free(sound_json_str);

    REPY_FN_RETURN;
}
```
