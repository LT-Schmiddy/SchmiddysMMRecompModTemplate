# LTSchmiddy's Majora's Mask: Recompiled Mod Template

This my custom version of the Majora's Mask: Recompiled mod template. It offers a number of features that the base template doesn't have, including:

* Optional building of external libraries (referred to as extlibs) alongside the mod nrm, and keeping the code for both in the same repository.
* Cross-compilation of extlibs using Zig (extlib code is still written in C/C++).
* Dedicated testing environment for mods in the form of the `test_env` directory.
* Automatic creation of Thunderstore packages via a single command.
* Automatic downloading and usage of [the MIPS-only `clang` package I maintain](https://github.com/LT-Schmiddy/n64recomp-clang), along with the RecompModTool and Zig.

## Writing mods

See [this document](https://hackmd.io/fMDiGEJ9TBSjomuZZOgzNg) for an explanation of the modding framework, including how to write function patches and perform interop between different mods.

## Tools

This template has somewhat different requirements from the default mod template. In order to run it, you'll need the following:

* `make`
* `python` (or `python3` on POSIX systems).
* `cmake`
* `ninja`

On Linux and MacOS, you'll need to also ensure that you have the `zip` utility installed.

All of these can (and should) be installed via using [chocolatey](https://chocolatey.org/) on Windows, Homebrew on MacOS, or your distro's package manager on Linux.

**You do NOT need the `RecompModTool` tool or any additional compilers installed. The build scripting will download all of these for you.**

The default configuration (as well as the example configurations) will download the N64RecompEssentials package from [here](https://github.com/LT-Schmiddy/n64recomp-clang)
for your platform, which contains the `RecompModTool` and the MIPS-only LLVM 21 `clang` and `ld.lld` compiler and linker pair for your system.

It will also download Zig 0.14 for project configurations that require it. This is done because Zig's packaging is inconsistent across ecosystems, but the compiler
itself is thankfully small.

## Building

TL;DR: Run `git submodule update --init --recursive` to make sure you've clones all submodules. Then, run `./modbuild.py` to prepare a debug build.
Run `./modbuild.py thunderstore` to create a Thunderstore package.

Due to issues where certain complex tasks become difficult to do in a cross-platform way using Make (and trying invoke Python functions from Make resulted in some
of the worse spaghetti code I've ever written), I've decided to not have Make be the entrypoint for the build process. Instead, I've turned to a lightweight,
Make-inspired Python library called `pyinvoke` to help me create an all-inclusive build script: `modbuild.py`. This script is capable of building the entire project
from scratch, or simply running parts of the build process depending on the subcommands and their arguments.

You can run `./modbuild.py -h` or `./modbuild.py [subcommand] -h` for usage information on the script and various subcommands.

All commands are defined in `tasks.py`, in accordance to the `pyinvoke` library. See that documentation at
[https://docs.pyinvoke.org/en/stable/](https://docs.pyinvoke.org/en/stable/) for info on how to define additional commands.

(Don't worry, there are no Python packages you need to install. All of the required Python code has been incorperated into this template).

## Advanced Usage and the Job System

This template and the default `tasks.py` file work on a system of defining inter-dependent jobs. Jobs are used to define what downloads and extractions to perform, what
makefiles to run, which .nrms to build, which CMake builds to compile, what output folders to prepare, and what Thunderstore packages to create. These jobs and relationships
are specified in `project.py`. When invoking `./modbuild.py`, you declare which job(s) you want to run (each subcommand will run all specified jobs of a type by default), and
the job system runs all dependency jobs as needed.

For most projects, you should be fine with one of the three example `project.py` files provided in `./EXAMPLES` (one is a .nrm only version, and the other two build extlibs),
but if you need to make other changes (for example, you want to declare an additional .nrm to be built as part of the project), that file is fully commented to explain how
everything works. The JobBase class and job subclasses (found in `./py/modbuildcore`) are also documented to explain their use.

The default dependencies are set up to be intuitive: for instance, Makefiles that use the N64RecompEssentials compilers depend on that extraction job, and the
extraction job depend on the download job. CMake builds that depend on Zig depend on those download and extraction jobs as well.

The default `project.py` file at the root of this repo is the same as `nrm_and_zig_extlib` example.

One additional note: Thunderstore package manifests are Python `dict` objects passed to a ThunderstorePackageJob, so you'll need to modify that job's declaration in `project.py` to edit your Thunderstore manifest. In all provided examples, the Thunderstore package manifest information is generated from information in `./mod.toml`.

## Testing

This template includes handling of a dedicated testing environment for you mod in the form of the `./test_env` folder. Copy in recomp's `assets` directory into it (You can also copy any config files, saves, and other mods you want to test against). After a build, your mod's `.nrm` file (and extlib file, if one is being built) will be copied to a folder called `./test_env/mods`. Then, if you use `test_env` and as your CWD, everything's ready to go for immediate testing as soon as your build finishes.

## Updating the Majora's Mask Decompilation Submodule

Mods can also be made with newer versions of the Majora's Mask decompilation instead of the commit targeted by this repo's submodule.
To update the commit of the decompilation that you're targeting, follow these steps:

* Build the [N64Recomp](https://github.com/N64Recomp/N64Recomp) repo and copy the N64Recomp executable to the root of this repository.
  * Make sure you pass `KEEP_MDEBUG=1` to `make` when building the decomp in order to keep debug information. This must be done from a clean build if you have built the decomp already without `KEEP_MDEBUG=1`.
* Build the version of the Majora's Mask decompilation that you want to update to and copy the resulting .elf file to the root of this repository.
* Update the `mm-decomp` submodule in your clone of this repo to point to the commit you built in the previous step.
* Run `N64Recomp generate_symbols.toml --dump-context`
* Rename `dump.toml` and `data_dump.toml` to `mm.us.rev1.syms.toml` and `mm.us.rev1.datasyms.toml` respectively.
  * Place both files in the `Zelda64RecompSyms` folder.
* Try building.
  * If it succeeds, you're done.
  * If it fails due to a missing header, create an empty header file in the `include/dummy_headers` folder, with the same path.
    * For example, if it complains that `assets/objects/object_cow/object_cow.h` is missing, create an empty `include/dummy_headers/objects/object_cow.h` file.
  * If RecompModTool fails due to a function "being marked as a patch but not existing in the original ROM", it's likely that function you're patching was renamed in the Majora's Mask decompilation.
    * Find the relevant function in the map file for the old decomp commit, then go to that address in the new map file, and update the reference to this function in your code with the new name.
