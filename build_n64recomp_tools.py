import pathlib, subprocess, os, shutil

N64Recomp_module_root = pathlib.Path(__file__).parent.joinpath("N64Recomp")
build_dir = N64Recomp_module_root.joinpath("build")

def _get_tool_path(tool_name: str) -> str:
    if os.name == 'nt':
        tool_name = tool_name + ".exe"
    
    possible_paths: list[pathlib.Path] = [
        build_dir.joinpath(tool_name),
        build_dir.joinpath("Debug").joinpath(tool_name),
        build_dir.joinpath("Release").joinpath(tool_name)
    ]
    
    for i in possible_paths:
        if i.exists():
            return i
    
    raise RuntimeError(f"Couldn't find executable file '{tool_name}' in any of the following locations:\n" 
                       + "".join(["\t" + str(i) + "\n" for i in possible_paths]))
    
def get_dependencies(print_locations: bool = False) -> dict[str, str]:
    retVal = {
        'clang': shutil.which("clang"),
        'git': shutil.which("git") ,
        'make': shutil.which("make"),
        'cmake': shutil.which("cmake"),
    }
    
    for key, value in retVal.items():
        if value is None:
            raise RuntimeError(f"Couldn't find executable for '{key}', which is needed to build this project")
        elif print_locations:
            print(f"Found {key} at '{value}'")
        
    retVal['ninja'] = shutil.which("ninja")
    
    if retVal['ninja'] is None:
        # raise RuntimeWarning(f"Couldn't find executable for ninja. Attempting to build N64Recomp tools may not work correctly.")
        print(f"WARNING: Couldn't find executable for ninja. Attempting to build N64Recomp tools may not work correctly.")
    elif print_locations:
        print(f"Found ninja at '{retVal['ninja']}'")
    return retVal
deps = get_dependencies(True)
        
def get_N64Recomp_path():
    return _get_tool_path("N64Recomp")

def get_OfflineModRecomp_path():
    return _get_tool_path("OfflineModRecomp")

def get_RecompModTool_path():
    return _get_tool_path("RecompModTool")

def get_RSPRecomp_path():
    return _get_tool_path("RSPRecomp")


def rebuild_tools(config_flags: list[str] = [], build_flags: list[str] = [] ):
    global deps
    
    print(f"Ensuring submodules are up to date...")
    subprocess.call(
        [
            deps["git"],
            "submodule",
            "update",
            "--init",
            "--recursive"
        ],
        cwd=pathlib.Path(__file__).parent
        
    )
     
    if build_dir.exists():
        print(f"Deleting old build at {build_dir}...")
        shutil.rmtree(build_dir)
        
    os.makedirs(build_dir, exist_ok=True)

    if len(config_flags) == 0 and deps['ninja'] is not None:
        config_flags = [
            "-G",
            "Ninja"
        ]
    
    cmake_config_args = [deps["cmake"]] + config_flags + [str(N64Recomp_module_root)]    
    print(f"Running CMake configuration with:\n\t{' '.join(cmake_config_args)}")
    subprocess.call(
        cmake_config_args,
        cwd=build_dir
    )

    cmake_build_args = [deps["cmake"], "--build"] + build_flags + ["."]   
    print(f"Running CMake build with:\n\t{' '.join(cmake_build_args)}")
    subprocess.call(
        [deps["cmake"], "--build"] + build_flags + ["."],
        cwd=build_dir
    )

if __name__ == '__main__':
    rebuild_tools()