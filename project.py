import platform, shutil, enum, os, subprocess
from pathlib import Path
from modbuildcore.jobs import *

root_dir: Path = Path(__file__).parent

archive_downloads_dir: Path = root_dir.joinpath("downloads")
build_dir: Path = root_dir.joinpath("build")
binaries_dir: Path = root_dir.joinpath("binaries")

make_path: Path = shutil.which("make")
cmake_path: Path = shutil.which("cmake")

make_mips_compiler_path: Path = None
make_mips_linker_path: Path = None
mod_tool_path: Path = None
zig_dir_path: Path = None
llvm_path: Path = None

downloads: dict[str, DownloadJob] = {}
archive_extractions: dict[str, ArchiveExtractJob] = {}
makefiles: dict[str, MakefileJob] = {}
mod_tomls: dict[str, ModTomlJob] = {}
cmake_build_groups: dict[str, dict[str, CMakeBuildJob]] = {}
build_outputs: dict[str, BuildOutputJob] = {}
thunderstore_packages: dict[str, ThunderstorePackageJob] = {}

nrm_path_fix_by_default = False

# If you need this enabled, you should probably rethink whatever it is you're doing:
# Convienience function for downloading compiler artifacts.
def add_archive_download_and_extract(name: str, url: str, extract_dir: Path) -> tuple[DownloadJob, ArchiveExtractJob]:
    global archive_extractions, downloads, archive_downloads_dir
    
    new_download = DownloadJob(url, archive_downloads_dir, True)
    new_extraction = ArchiveExtractJob(new_download.download_path, extract_dir)
    new_extraction.depends_on([new_download])
    downloads[name] = new_download
    archive_extractions[name] = new_extraction
    
    return new_download, new_extraction

# Deciding with compiler/tool archive to download for your platform:
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
    

    add_archive_download_and_extract(
        "llvm",
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-19.1.7/clang+llvm-19.1.7-x86_64-pc-windows-msvc.tar.xz",
        binaries_dir.joinpath("llvm_win")
    )
    
    llvm_path = binaries_dir.joinpath("llvm_win/clang+llvm-19.1.7-x86_64-pc-windows-msvc")
        
    
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
    
    
    add_archive_download_and_extract(
        "llvm",
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-19.1.7/LLVM-19.1.7-macOS-ARM64.tar.xz",
        binaries_dir.joinpath("llvm_macos")
    )
    llvm_path = binaries_dir.joinpath("llvm_macos/LLVM-19.1.7-macOS-ARM64")
    
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
    
    add_archive_download_and_extract(
        "llvm",
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-19.1.7/LLVM-19.1.7-Linux-X64.tar.xz",
        binaries_dir.joinpath("llvm_linux")
    )
    llvm_path = binaries_dir.joinpath("llvm_linux/LLVM-19.1.7-Linux-X64")

# Registering asset_archive extraction
assets_archive_path = root_dir.joinpath("assets_archive.zip")
assets_extracted_path = root_dir.joinpath("assets_extracted/assets")
archive_extractions['assets'] = ArchiveExtractJob(assets_archive_path, assets_extracted_path)

# Registering mod toml files to build
# Main NRM

main_toml = ModTomlJob(mod_tool_path, root_dir.joinpath("mod.toml"))
mod_tomls['mod'] = main_toml
makefiles['mod'] = MakefileJob(
    make_path,
    root_dir.joinpath("mod_elf.mk"),
    {
        "_ELF_PATH": str(mod_tomls['mod'].get_elf_path()),
        "_BUILD_DIR": str(mod_tomls['mod'].get_elf_path().parent),
        "_MIPS_CC": str(make_mips_compiler_path),
        "_MIPS_LD": str(make_mips_linker_path),
        "_SRC_DIR": "src/mod",
        "_PY_BUILD_FLAGS": "-DRECOMP_PY_BUILD_MODE"
    }
)
main_toml.depends_on([archive_extractions["llvmmips"], makefiles['mod']])

# CMake Stuff
def prepend_to_env_path(to_append: Path) -> str:
    global llvm_path
    PATH_DELIMITER = ";" if os.name == 'nt' else ":"
    env_path = os.environ['PATH']
    for i in to_append:
        env_path = str(i) + PATH_DELIMITER + env_path
    return env_path

extlib_name = "mm_recomp_mod_template_extlib"
extlib = CMakeProjectConfig(
    cmake_path,
    root_dir,
    {
        # Unlike with clangmips, we're gonna prepend the LLVM and ZIG directories to the PATH that CMake recieves.
        # "PATH": prepend_to_env_path([llvm_path.joinpath("bin"), zig_dir_path]),
        "PATH": prepend_to_env_path([zig_dir_path]),
        "LIB_NAME": extlib_name
    }
)
def get_preset_lib_path(preset_name: str) -> Path:
    global root_dir
    return root_dir.joinpath(f"build/{preset_name}/lib")

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
    
cmake_default_build_group_name: str = "Debug"
cmake_build_groups = {
    "Debug" : {
        "Windows": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-Debug").joinpath(f"lib{extlib_name}.dll"),
                Path(f"{extlib_name}.pdb"): get_preset_lib_path("zig-windows-x64-Debug").joinpath(f"lib{extlib_name}.pdb")
            }, "zig-windows-x64-Debug"),
        "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-Debug").joinpath(f"lib{extlib_name}.dylib")
            }, "zig-macos-aarch64-Debug"),
        "Linux": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-Debug").joinpath(f"lib{extlib_name}.so")
            }, "zig-linux-x64-Debug"),
    },
    "Release" : {
        "Windows": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-Release").joinpath(f"lib{extlib_name}.dll")
            }, "zig-windows-x64-Release"),
        "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-Release").joinpath(f"lib{extlib_name}.dylib")
            }, "zig-macos-aarch64-Release"),
        "Linux": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-Release").joinpath(f"lib{extlib_name}.so")
            }, "zig-linux-x64-Release"),
    }, 
    "RelWithDebInfo": {
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
    },
    "MinSizeRel": {
        "Windows": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dll"): get_preset_lib_path("zig-windows-x64-MinSizeRel").joinpath(f"lib{extlib_name}.dll")
            }, "zig-windows-x64-MinSizeRel"),
        "Darwin": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.dylib"): get_preset_lib_path("zig-macos-aarch64-MinSizeRel").joinpath(f"lib{extlib_name}.dylib")
            }, "zig-macos-aarch64-MinSizeRel"),
        "Linux": CMakeBuildJob.from_preset_pair(extlib, {
                Path(f"{extlib_name}.so"): get_preset_lib_path("zig-linux-x64-MinSizeRel").joinpath(f"lib{extlib_name}.so")
            }, "zig-linux-x64-MinSizeRel"),
    },
    "native-Debug" : {
        "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("Debug"), native_preset_name("Debug")),
    },
    "native-Release" : {
        "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("Release"), native_preset_name("Release")),
    }, 
    "native-RelWithDebInfo": {
        "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("RelWithDebInfo"), native_preset_name("RelWithDebInfo")),
    },
    "native-MinSizeRel": {
        "Native": CMakeBuildJob.from_preset_pair(extlib, native_output_files("MinSizeRel"), native_preset_name("MinSizeRel")),
    }
}

for group_key, group in cmake_build_groups.items():
    for build_key, build in group.items():
        if not group_key.startswith("native-"):
            build.depends_on([archive_extractions["zig"]])
        # build.depends_on([archive_extractions["llvm"]])


debug_test_dir = BuildOutputJob(root_dir.joinpath("test_env/mods"))
debug_test_dir.depends_on([
    mod_tomls['mod'],
] + [i for i in cmake_build_groups["Debug"].values()])

build_outputs["debug"] = debug_test_dir

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

thunderstore_package_name = "RecompExternalPython_for_Zelda64Recompiled"
main_package = ThunderstorePackageJob(
    root_dir.joinpath(f"{thunderstore_package_name}.thunderstore.zip"),
    {
        "name": thunderstore_package_name,
        "version_number": main_toml.data["manifest"]["version"],
        "website_url": package_url_from_git(),
        "description": "An advanced template for recomp mods",
        "dependencies": []
    },
    root_dir.joinpath("thunderstore_info/README.md").read_text(),
    root_dir.joinpath("thunderstore_info/CHANGELOG.md").read_text(),
    root_dir.joinpath("thumb.png")
)
main_package.depends_on([
    mod_tomls['mod']
] + [i for i in cmake_build_groups["Release"].values()])
thunderstore_packages['package'] = main_package

clean_paths: list[Path] = [
    build_dir
]

distclean_paths: list[Path] = [
    binaries_dir,
    archive_downloads_dir,
    assets_extracted_path.parent
]