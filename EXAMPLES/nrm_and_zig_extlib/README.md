# NRM and Zig Extlib

This `project.py` example will build a single nrm and a simple extlib using CMake and Zig. To use it, simply replace `project.py` in the root of the template with this one.

This example downloads and uses a N64RecompEssentials package from [https://github.com/LT-Schmiddy/n64recomp-clang](https://github.com/LT-Schmiddy/n64recomp-clang),
which contains the RecompModTool binary and MIPS-only versions of `clang` and `ld.lld` from LLVM 21.

This example downloads the Zig 0.14 compiler, to circumvent Zig's inconsistent packaging across ecosystems.

This is actually the default configuration of this template, but is included here for completeness.
