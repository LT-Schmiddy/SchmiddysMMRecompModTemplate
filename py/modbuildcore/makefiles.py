import shutil, os
from pathlib import Path

from invoke import Context
from .job_base import JobBase

from .utils import invoke_subprocess_run, print_job_header
        
class MakefileJob(JobBase):
    """This job executes a makefile with additional environmental variables.
    """
    make_binary_path: Path
    makefile_path: Path
    extended_env: dict[str, str]
    
    def __init__(self, makefile_path: Path, extended_env: dict[str, str], *, make_binary_path: Path = None):
        """Initializes the MakefileJob.

        Args:
            makefile_path (Path): The path to the Makefile to run.
            extended_env (dict[str, str]): Additional/overiding environmental variables to use when invoking Make.
            make_binary_path (Path, optional): The location of the Make binary. If None, defaults the `make` command on your system path. Defaults to None.
        """
        super().__init__()
        if make_binary_path is None:
            self.make_binary_path = shutil.which("make")
        else:
            self.make_binary_path = make_binary_path
        self.makefile_path = makefile_path
        self.extended_env = extended_env
    
    def run(self, c: Context):
        print_job_header(f"Makefile Job: {self.makefile_path}")
        make_env = os.environ.copy()
        make_env.update(self.extended_env)
        
        invoke_subprocess_run(c, True,
            [self.make_binary_path, "-f", self.makefile_path],
            env=make_env
        )