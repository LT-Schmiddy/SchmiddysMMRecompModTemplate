# NRM and Zig + LLVM Example

This `project.py` example will build a single nrm and an extlib using CMake, Zig, and LLVM. To use it, simply replace `project.py` in the root of the
template with this one.

This example downloads and uses a N64RecompEssentials package from [https://github.com/LT-Schmiddy/n64recomp-clang](https://github.com/LT-Schmiddy/n64recomp-clang),
which contains the RecompModTool binary and MIPS-only versions of `clang` and `ld.lld` from LLVM 21.

This example downloads the Zig 0.14 compiler, to circumvent Zig's inconsistent packaging across ecosystems.

For some more advanced extlibs, Zig may not be enough and you'll need cross-compilation tools that don't come as part of a regular LLVM install (the Python API mod
ran into this issue. I needed special tools to handle linking against a prebuilt Python interpreter). In these cases, you can use this example configuration to download
and use a complete archive of LLVM tools for such cases. It currently uses LLVM 19.1.7, which is the same LLVM version the included Zig C/C++ compilers are based on.
That being said, this is several gigabytes once downloaded and extracted, so you shouldn't use this example unless you ABSOLUTELY need to.
