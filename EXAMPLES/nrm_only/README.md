# NRM Only Example

This `project.py` example will build a single nrm that doesn't need a extlib. To use it, simply replace `project.py` in the root of the template with this one.

This example downloads and uses a N64RecompEssentials package from [https://github.com/LT-Schmiddy/n64recomp-clang](https://github.com/LT-Schmiddy/n64recomp-clang),
which contains the RecompModTool binary and MIPS-only versions of `clang` and `ld.lld` from LLVM 21.

If this example is in use, the following files/directories can be safely deleted:

* ./CMakeLists.txt
* ./CMakePresets.json
* ./zig_toolchain.cmake
* ./include/extlib
* ./src/extlib
