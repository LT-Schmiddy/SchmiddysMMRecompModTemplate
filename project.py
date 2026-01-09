import platform, shutil, os, subprocess
from pathlib import Path
from modbuildcore.jobs import *

# ============== Job Variables ==============

# This template is based around the concept of declaring inter-dependent jobs that run based on task the user invokes.

# If you declare a job, add it to one of these dicts to make it directly invokable from the command line.
# Jobs are considered 'resolved' if the job is run, or if it's determined the job doesn't need to run.
# For example, a download is 'resolved' if the download is run, or if the downloaded file is already present.
# When a job is run, it will automatically resolve any other jobs it depends on. However, the root job must still be invoked 
# (meaning you need to add it to one of these dicts, and run ./modbuild.py with the appropriate subcommand). If a job is 
# resolved by determining it doesn't need to run, the dependency jobs will also not be resolved, as it is assumed those jobs
# do not need to run either.

# In this file, you will only need to create the job instances. Actually resolving jobs is handled in tasks.py
# We don't need to declare the jobs here. We'll just create the dicts and populate them as we go.
downloads: dict[str, DownloadJob] = {}
archive_extractions: dict[str, ArchiveExtractJob] = {}
makefiles: dict[str, MakefileJob] = {}
mod_tomls: dict[str, ModTomlJob] = {}
cmake_build_groups: dict[str, dict[str, CMakeBuildJob]] = {}
build_outputs: dict[str, BuildOutputJob] = {}
thunderstore_packages: dict[str, ThunderstorePackageJob] = {}

# Every job has a dict member called `mod_output_files`, which specifies what files (if any) the job generates that are required for the mod
# to run (such as the .nrm file or an extlib), i.e. files that should go in Zelda64Recompiled's 'mods' folder or a Thunderstore package.
# It is acceptable to add additional mod_output_files to any job, either by accessing 'my_job.mod_output_files' directly, or using 
# the `add_mod_output_files` method that all job types have.

# Each key/value pair in `mod_output_files` represents a file to include, and should follow this pattern:
# * The key will be relative path, indicating the location in a build output folder or thunderstore package.
# * The value is the path to the file in this project, for example, a file built by CMake.

# It is important to understand that the term 'mod_output_file[s]' refers this behavior specifically, and just any file created by a job.
# For instance, DownloadJobs do not assume that you want include the downloaded file as part of the mod, and thus the downloaded file is 
# not part of mod_output_files. If you want to include it, you should add it manually. The same is true of ArchiveExtractJobs.
 
# In this template, only ModTomlJobs will specify a mod_output_file automatically (the resultant .nrm), and only CMakeBuildJobs require
# you to specify mod_output_files when declaring the job. Other jobs are allowed to have mod_output_files, but only if you declare them manually.

# You can also declare additional job types by subclassing `modbuildcore.job_base.JobBase`.

# ============== Misc. Variables ==============
# Any variable defined here is accessable and usable in `tasks.py`. But in this template, this is the only other 
# variable that `tasks.py` uses directly.
nrm_path_fix_by_default = False

# This project template relies heavily Python's standard 'pathlib' module to determine filenames and locations.
# This statement gives us Path a object that correponds to the project root, and will let us ensure we have paths 
# relative to the project root and not the current working directory.
root_dir: Path = Path(__file__).parent

# Defining some other misc variables that we'll use later.
archive_downloads_dir: Path = root_dir.joinpath("downloads")
build_dir: Path = root_dir.joinpath("build")
binaries_dir: Path = root_dir.joinpath("binaries")

make_mips_compiler_path: Path = None
make_mips_linker_path: Path = None
mod_tool_path: Path = None
zig_dir_path: Path = None
llvm_path: Path = None

# ============== Artifact Downloads and Extractions ==============

# Convienience function to create DownloadJobs and ArchiveExtractJobs for the compiler artifacts.
def add_archive_download_and_extract(name: str, url: str, extract_dir: Path) -> tuple[DownloadJob, ArchiveExtractJob]:
    global archive_extractions, downloads, archive_downloads_dir
    
    new_download = DownloadJob(url, archive_downloads_dir)
    new_extraction = ArchiveExtractJob(new_download.download_path, extract_dir)
    # This new extraction job depends on the download being completed.
    new_extraction.depends_on([new_download])
    downloads[name] = new_download
    archive_extractions[name] = new_extraction
    
    return new_download, new_extraction

# Here we decide which compiler/tool archives to download for your platform, and setting the relevant variables.
# The `llvmmips` download/extraction is the "RecompEssentials" archive maintained by myself (LT_Schmiddy).
# It contains a MIPS-only version of clang, ld.lld, and a few select LLVM tools useful for working with elf binaries (to keep the size down).
# It also contains builds of the RecompModTool and the other N64Recomp tools.

# The 'zig' download/extraction is the complete binary package for the Zig, since this template offers cross-compilation using Zig's C/C++ compiler/linker. 
# Zig isn't available on every package manager (and is a mercifully small download compared to LLVM), so it's easier to download it here.
# The advantage of declaring these compilers as downloads is that you can be confident that other developers/GitHub Actions will always have the correct/same
# compiler versions as you.
if platform.system() == "Windows":
    add_archive_download_and_extract(
        "llvmmips",
        "https://github.com/LT-Schmiddy/n64recomp-clang/releases/download/shim-prerelease-0.1.0/N64RecompAndClangEssentials-ClangVersion21.1.6-MipsOnly-Windows-AMD64.zip",
        binaries_dir.joinpath("llvmmips_win")
    )
    make_mips_compiler_path = binaries_dir.joinpath("llvmmips_win/nrs_bin/clang.exe")
    make_mips_linker_path = binaries_dir.joinpath("llvmmips_win/nrs_bin/ld.lld.exe")
    mod_tool_path = binaries_dir.joinpath("llvmmips_win/nrs_bin/RecompModTool.exe")
    
    add_archive_download_and_extract(
        "zig",
        "https://ziglang.org/download/0.14.1/zig-x86_64-windows-0.14.1.zip",
        binaries_dir.joinpath("zig_win")
    )
    zig_dir_path = binaries_dir.joinpath("zig_win/zig-x86_64-windows-0.14.1")
    zig_bin_path = zig_dir_path.joinpath("zig.exe")
    
elif platform.system() == "Darwin":
    add_archive_download_and_extract(
        "llvmmips",
        "https://github.com/LT-Schmiddy/n64recomp-clang/releases/download/shim-prerelease-0.1.0/N64RecompAndClangEssentials-ClangVersion21.1.6-MipsOnly-Darwin-arm64.tar.xz",
        binaries_dir.joinpath("llvmmips_macos")
    )
    make_mips_compiler_path = binaries_dir.joinpath("llvmmips_macos/nrs_bin/clang")
    make_mips_linker_path = binaries_dir.joinpath("llvmmips_macos/nrs_bin/ld.lld")
    mod_tool_path = binaries_dir.joinpath("llvmmips_macos/nrs_bin/RecompModTool")
    
    add_archive_download_and_extract(
        "zig",
        "https://ziglang.org/download/0.14.1/zig-aarch64-macos-0.14.1.tar.xz",
        binaries_dir.joinpath("zig_macos")
    )
    zig_dir_path = binaries_dir.joinpath("zig_linux/zig-aarch64-macos-0.14.1")
    zig_bin_path = zig_dir_path.joinpath("zig")
    
else:
    add_archive_download_and_extract(
        "llvmmips",
        "https://github.com/LT-Schmiddy/n64recomp-clang/releases/download/shim-prerelease-0.1.0/N64RecompAndClangEssentials-ClangVersion21.1.6-MipsOnly-Linux-x86_64.tar.xz",
        binaries_dir.joinpath("llvmmips_linux")
    )
    
    make_mips_compiler_path = binaries_dir.joinpath("llvmmips_linux/nrs_bin/clang")
    make_mips_linker_path = binaries_dir.joinpath("llvmmips_linux/nrs_bin/ld.lld")
    mod_tool_path = binaries_dir.joinpath("llvmmips_linux/nrs_bin/RecompModTool")
    
    add_archive_download_and_extract(
        "zig",
        "https://ziglang.org/download/0.14.1/zig-x86_64-linux-0.14.1.tar.xz",
         binaries_dir.joinpath("zig_linux")
    )
    zig_dir_path = binaries_dir.joinpath("zig_linux/zig-x86_64-linux-0.14.1")
    zig_bin_path = binaries_dir.joinpath("zig")

# Registering asset_archive extraction, and associated variables.
assets_archive_path = root_dir.joinpath("assets_archive.zip")
assets_extracted_path = root_dir.joinpath("assets_extracted/assets")
assets_archive_job = ArchiveExtractJob(assets_archive_path, assets_extracted_path)
archive_extractions['assets'] = assets_archive_job

# ============== Mod Toml/.nrm Building ==============

# Declaring the mod toml files to build. Note that we've not set up the makefile that will build the elf. We'll do that next.
# Note that the mod toml job doesn't automatically find the RecompModTool. We'll need to pass that in ourselves.
# ModTomlJob instances automatically register the resultant .nrm file as a mod_output_file. Therefore the .nrm will 
# automatically be added to any build output folders or thunderstore packages that depend on this job.
main_toml = ModTomlJob(mod_tool_path, root_dir.joinpath("mod.toml"))
# The mod toml file is read when the job is first created. We now have access to all the information in the toml.

# Declaring the makefile that will build our mod's elf binary. In this template, we've declared it second so that we can pass information
# from the mod toml to the makefile job.
main_makefile = MakefileJob(
    root_dir.joinpath("mod_elf.mk"),
    # We can pass information to the makefile here, by declaring additional environmental variables for make to use.
    # Environmental variables are automatically added to the variable namespace in a makefile.
    # This template uses a generalized makefile that could be configured to compile multiple mods by passing
    # different environmental variables here. It's also set up to let us pass in the compiler and linker we want to use.
    {
        "_ELF_PATH": str(main_toml.get_elf_path()),
        "_BUILD_DIR": str(main_toml.build_dir),
        "_MIPS_CC": str(make_mips_compiler_path),
        "_MIPS_LD": str(make_mips_linker_path),
        "_SRC_DIR": "src/mod"
    }
)

# We've set the makefile to use the MIPS-only clang and ld.lld that we downloaded and extracted (The 'llvmmips' DownloadJob and ArchiveExtractJob).
# So, we'll mark this MakefileJob as depending on that ArchiveExtractJob. We don't need to mark it as depending on the DownloadJob,
# since the ArchiveExtractJob already depends on the DownloadJob.
main_makefile.depends_on([archive_extractions["llvmmips"], assets_archive_job])

# Our toml file depends on the makefile to produce the mod elf, so we'll declare that dependency here.
# It also depends on the RecompModTool we extracted from 'llvmmips', so we declare that dependency too.
main_toml.depends_on([main_makefile, archive_extractions["llvmmips"]])

# Adding both jobs to their respective dicts for direct invoking.
mod_tomls['mod'] = main_toml
makefiles['mod'] = main_makefile

# ============== CMake/Extlib Compilation ==============

# A little helper function to prepend file paths to your environmental PATH argument.
def prepend_to_env_path(to_append: Path) -> str:
    global llvm_path
    PATH_DELIMITER = ";" if os.name == 'nt' else ":"
    env_path = os.environ['PATH']
    for i in to_append:
        env_path = str(i) + PATH_DELIMITER + env_path
    return env_path

# The CMake project in this template is set up to recieve the name of the extlib it compiles from an environmental variable.
# That way, we can have a single source for truth for the name, and changing it is easy.
# We'll also need that name for some other declarations later, so we'll store it in a variable here.
# This template reads the name of the first extlib declared in the main toml, and uses that as the CMake project name.
extlib_name = main_toml.data["manifest"]["native_libraries"][0]["name"]

# CMakeProjectConfig defines information that will be common between lots of CMakeBuildJob instances.
extlib = CMakeProjectConfig(
    root_dir,
    {
        # Unlike with the makefile, we're gonna prepend the ZIG directory to the PATH that CMake recieves.
        # I could probably things this way for the makefile as well...
        "PATH": prepend_to_env_path([zig_dir_path]),
        "LIB_NAME": extlib_name # The actual environmental variable that CMake looks at for the extlib name
    }
)

# While build jobs could be defined manually (passing in the configuration and build arguments directly to the CMakeBuildJob contructor),
# This template features an extensive CMakePresets.json which contains all the different build variations, which is what we'll use.
# With that in mind, this is a helper function that determines the output directories for the binaries that CMake will produce, following
# the conventions in our preset file.
def get_preset_lib_path(preset_name: str) -> Path:
    global root_dir
    return root_dir.joinpath(f"build/{preset_name}/lib")

# Producing extlib binaries for Windows, Mac, and Linux will involve multiple invokations of CMake.
# As a result, CMakeBuildJobs are organized into groups that can be run together.
cmake_build_groups["Debug"] = {
    #  CMakeBuildJob.from_preset_pair is a sort of alernate constructor where the CMake configure and build arguments will be
    # automatically set to those that invoke CMake configure and build presets with the specified name(s). If only the 
    # configure preset is specified (as is the case here), it will be assumed that the build preset will have the same name.
    "Windows": CMakeBuildJob.from_preset_pair(extlib, {
        # Unlike with ModTomlJobs, CMakeBuildJobs cannot automatically determine what mod_output_files they produce, so they need to be specified 
        # manually in this dict. The format is the same as the `add_mod_output_files` method.
            Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-Debug").joinpath(f"lib{extlib_name}.dll"),
            # Including the Windows debug symbols file...
            Path(f"{extlib_name}.pdb"): get_preset_lib_path("zig-windows-x64-Debug").joinpath(f"lib{extlib_name}.pdb")
        }, "zig-windows-x64-Debug"),
    "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-Debug").joinpath(f"lib{extlib_name}.dylib")
        }, "zig-macos-aarch64-Debug"),
    "Linux": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-Debug").joinpath(f"lib{extlib_name}.so")
        }, "zig-linux-x64-Debug"),
}

# Admittely, this part of this file could probably be DRYer.
cmake_build_groups["Release"] =  {
    "Windows": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-Release").joinpath(f"lib{extlib_name}.dll")
        }, "zig-windows-x64-Release"),
    "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-Release").joinpath(f"lib{extlib_name}.dylib")
        }, "zig-macos-aarch64-Release"),
    "Linux": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-Release").joinpath(f"lib{extlib_name}.so")
        }, "zig-linux-x64-Release"),
}

cmake_build_groups["RelWithDebInfo"] = {
    "Windows": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-RelWithDebInfo").joinpath(f"lib{extlib_name}.dll"),
            Path(f"{extlib_name}.pdb"): get_preset_lib_path("zig-windows-x64-RelWithDebInfo").joinpath(f"lib{extlib_name}.pdb")
        }, "zig-windows-x64-RelWithDebInfo"),
    "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-RelWithDebInfo").joinpath(f"lib{extlib_name}.dylib")
        }, "zig-macos-aarch64-RelWithDebInfo"),
    "Linux": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-RelWithDebInfo").joinpath(f"lib{extlib_name}.so")
        }, "zig-linux-x64-RelWithDebInfo"),
}

cmake_build_groups["MinSizeRel"] = {
    "Windows": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-MinSizeRel").joinpath(f"lib{extlib_name}.dll")
        }, "zig-windows-x64-MinSizeRel"),
    "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-MinSizeRel").joinpath(f"lib{extlib_name}.dylib")
        }, "zig-macos-aarch64-MinSizeRel"),
    "Linux": CMakeBuildJob.from_preset_pair(extlib, {
            Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-MinSizeRel").joinpath(f"lib{extlib_name}.so")
        }, "zig-linux-x64-MinSizeRel"),
}

# All of these presets use Zig, so we'll mark them all depending on the 'zig' extraction.
for group_key, group in cmake_build_groups.items():
    for build_key, build in group.items():
        build.depends_on([archive_extractions["zig"]])

# So far, all the CMakeBuildJob groups have been for cross-compiling the extlib for Windows, Mac, and Linux (regardless of the host system).
# In some cases, compiling without using Zig can be helpful for debugging, and the CMakePresets.json includes presets for compiling natively
# via LLVM. We'll make single-entry build groups for these native presets.

# Note that you must have Clang/LLVM installed on your system to use these presets. An alternate version of this project file exists that
# can automatically download a complete LLVM archive for you (not recommended by default do to size), eliminating this need.

# These are helper functions that will help determine the correct native presets and mod_output_files for your system.
def native_preset_name(build_type: str):
    if platform.system() == "Windows":
        return f"native-windows-x64-{build_type}"
    if platform.system() == "Darwin":
        return f"native-macos-aarch64-{build_type}"
    if platform.system() == "Linux":
        return f"native-linux-x64-{build_type}"

def native_output_files(build_type: str) -> dict[Path, Path]:
    preset_name = native_preset_name(build_type)
    if platform.system() == "Windows":
        win_base = {
            Path(f"{extlib_name}.dll"): get_preset_lib_path(preset_name).joinpath(f"{extlib_name}.dll")
        }
        if build_type == "Debug" or build_type == "RelWithDebInfo":
            win_base[Path(f"{extlib_name}.pdb")] = get_preset_lib_path(preset_name).joinpath(f"{extlib_name}.pdb")
        return win_base
    if platform.system() == "Darwin":
        return {
            Path(f"{extlib_name}.dylib"): get_preset_lib_path(preset_name).joinpath(f"{extlib_name}.dylib")
        }
    if platform.system() == "Linux":
        return {
            Path(f"{extlib_name}.so"): get_preset_lib_path(preset_name).joinpath(f"lib{extlib_name}.so")
        }


cmake_build_groups["native-Debug"] = {
    "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("Debug"), native_preset_name("Debug")),
}
cmake_build_groups["native-Release"] = {
    "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("Release"), native_preset_name("Release")),
}
cmake_build_groups["native-RelWithDebInfo"] = {
    "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("RelWithDebInfo"), native_preset_name("RelWithDebInfo")),
}
cmake_build_groups["native-MinSizeRel"] = {
    "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("MinSizeRel"), native_preset_name("MinSizeRel")),
}

# ============== Build Output and Packaging ==============

# BuildOutputJobs are used to copy the mod_output_files from other jobs into a single, convenient directory. 
# This is primarily used to streamline testing. If you set up a portable instance of Zelda64Recompiled in ./test_env 
# (which is in .gitignore), this BuildOutputJob will automatically copy your mod_output_files into ./test_env/mods, 
# saving you from having to copy files after every build. 

# Alternatively, you can just copy the 'assets' folder into ./test_env and run your normal installation of Zelda64Recompiled 
# with ./test_env as your current working directory. That will produce the same test environment effect.
# I recommend setting this up as a debug config in VSCode's debugger. That has the added benefit of letting you debug extlibs.
debug_test_dir = BuildOutputJob(root_dir.joinpath("test_env/mods"))

# To include mod_output_files from other jobs in the build output, add those jobs as dependencies.
debug_test_dir.depends_on([
    mod_tomls['mod'],
] + [i for i in cmake_build_groups["Debug"].values()])
# You can also declare additional files to include using `debug_test_dir.add_mod_output_files(...)` method.

# Updating build outputs is the default behavior of invoking `./modbuild.py` without arguments.
# If dependencies were set up correctly, a single invokation will run all jobs necessary to produce
# all build output folders defined in `build_outputs`.
build_outputs["debug"] = debug_test_dir

# Helper function to find the URL for your GitHub repo. Used to generate Thunderstore packages.
def package_url_from_git() -> str:
    result = subprocess.run(
        [
            shutil.which("git"),
            "config", 
            "--get", 
            "remote.origin.url"
        ],
        cwd=root_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None

# Here we define the main Thunderstore package we want to produce.
# The ThunderstorePackageJob collects all the mod_output_files and stores them in a zip archive, along with
# the required metadata for a Thunderstore package.
thunderstore_package_name = main_toml.data["manifest"]["id"]
main_package = ThunderstorePackageJob(
    # The GitHub Actions CI Workflows assume the uploaded package will have the following naming scheme:
    #  name_in_package_manifest.thunderstore.zip
    root_dir.joinpath(f"{thunderstore_package_name}.thunderstore.zip"),
    {
        "name": thunderstore_package_name,
        "version_number": main_toml.data["manifest"]["version"], # We'll read the version number from the mod toml.
        "website_url": package_url_from_git(),
        "description": main_toml.data["manifest"]["short_description"],
        "dependencies": []
    },
    root_dir.joinpath("thunderstore_info/README.md").read_text(),
    root_dir.joinpath("thunderstore_info/CHANGELOG.md").read_text(),
    root_dir.joinpath("thumb.png")
)

# To include mod_output_files from other jobs in the build output, add those jobs as dependencies.
main_package.depends_on([
    mod_tomls['mod']
] + [i for i in cmake_build_groups["Release"].values()])
# You can also declare additional files to include using `debug_test_dir.add_mod_output_files(...)` method.

# If dependencies were set up correctly, invoking `./modbuild.py thunderstore` will run all jobs necessary to produce
# all Thunderstore packages defined in `thunderstore_packages`.
thunderstore_packages['package'] = main_package
# Note that the default GitHub Actions CI automatically invokes the and publishes the ThunderstorePackageJob with the key "package".


# ============== Misc ==============
# Here we define the files and directories that should be deleted for a clean and a distclean.
clean_paths: list[Path] = [
    build_dir
]

distclean_paths: list[Path] = [
    binaries_dir,
    archive_downloads_dir,
    assets_extracted_path.parent
]