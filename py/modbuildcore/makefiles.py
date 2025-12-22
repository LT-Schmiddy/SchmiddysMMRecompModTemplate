import tomllib, pathlib, os
from pathlib import Path

from invoke import Context
from .job_base import JobBase

from .utils import invoke_subprocess_run, print_job_header
        
class MakefileJob(JobBase):
    make_binary_path: Path
    makefile_path: Path
    extended_env: dict[str, str]
    
    def __init__(self, make_binary_path: Path, makefile_path: Path, extended_env: dict[str, str]):
        super().__init__()
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