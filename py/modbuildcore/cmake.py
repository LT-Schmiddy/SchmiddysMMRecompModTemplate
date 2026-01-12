import shutil, os
from pathlib import Path

from invoke import Context
from .job_base import JobBase
from .utils import invoke_subprocess_run, print_job_header

# Class declaration before definition:
class CMakeProjectConfig:
    """Common configuration info for CMakeBuildJobs using the same CMake project.
    """
    cmake_binary_path: Path
    project_working_dir: Path
    extended_env: dict[str, str]
    
    def __init__(self, project_working_dir: Path, expanded_env: dict[str, str], *, cmake_binary_path: Path = None):
        """Initializes the CMakeProjectConfig.

        Args:
            project_working_dir (Path): The working directory for this CMake project.
            expanded_env (dict[str, str]): Additional/overiding environmental variables to use when invoking CMake.
            cmake_binary_path (Path, optional): The location of the CMake binary. If None, defaults the `cmake` command on your system path. Defaults to None.
        """
        if cmake_binary_path is None:
            self.cmake_binary_path = shutil.which("cmake")
        else:
            self.cmake_binary_path = cmake_binary_path
        self.project_working_dir = project_working_dir
        self.extended_env = expanded_env


class CMakeBuildJob:
    ...
    
class CMakeBuildJob(JobBase):
    """This job configures and builds a CMake project. The mod_output_files must be manually specified on initialization.
    """
    config_args: list[str]
    build_args: list[str]
    
    def __init__(self, cmake_project: CMakeProjectConfig, mod_output_files: dict[Path, Path], config_args: list[str], build_args: list[str]):
        """Initializes the CMakeBuildJob.

        Args:
            cmake_project (CMakeProjectConfig): Common project information object for this build.
            mod_output_files (dict[Path, Path]): The mod_output_files to this job produces. The key will be the desired file location in the output, the value will be the path in the project.
            config_args (list[str]): Arguments to pass to CMake when configuring.
            build_args (list[str]): Arguments to pass to CMake when building.
        """
        super().__init__()
        self.cmake_project = cmake_project
        self.mod_output_files = mod_output_files
        self.config_args = config_args
        self.build_args = build_args
        
        
    @classmethod
    def from_preset_pair(cls, cmake_project: CMakeProjectConfig, output_files: dict[Path, Path], config_preset_name: str, build_preset_name: str = None) -> CMakeBuildJob:
        """An alternate constructor for a CMakeBuildJob that uses CMakePresets.json for configuring and building.

        Args:
            cmake_project (CMakeProjectConfig): Common project information object for this build.
            output_files (dict[Path, Path]): The mod_output_files to this job produces. The key will be the desired file location in the output, the value will be the path in the project.
            config_preset_name (str): The name of the CMake configure preset.
            build_preset_name (str, optional): The name of the CMake configure preset. If None, uses the same preset name as `config_preset_name`. Defaults to None.

        Returns:
            CMakeBuildJob: The newly initialized CMakeBuildJob.
        """
        if build_preset_name is None:
            build_preset_name = config_preset_name
        
        return cls(
            cmake_project,
            output_files,
            ["--preset", config_preset_name, cmake_project.project_working_dir],
            ["--build", "--preset", build_preset_name]
        )
        
    def run_configure(self, c: Context):
        print_job_header(f"CMake Configure: {self.config_args}:")
        cmake_env = os.environ.copy()
        cmake_env.update(self.cmake_project.extended_env)
        
        invoke_subprocess_run(c, True,
            [self.cmake_project.cmake_binary_path] + self.config_args,
            env=cmake_env,
            cwd=self.cmake_project.project_working_dir
        )
    
    def run_build(self, c: Context):
        print_job_header(f"CMake Build: {self.build_args}:")
        cmake_env = os.environ.copy()
        cmake_env.update(self.cmake_project.extended_env)
        
        invoke_subprocess_run(c, True,
            [self.cmake_project.cmake_binary_path] + self.build_args,
            env=cmake_env,
            cwd=self.cmake_project.project_working_dir
        )

    def run(self, c: Context):
        self.run_configure(c)
        self.run_build(c)
