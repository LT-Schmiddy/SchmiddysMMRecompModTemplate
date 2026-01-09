import os, shutil
from pathlib import Path

from invoke import Context
from .job_base import JobBase
from .utils import invoke_subprocess_run, print_job_header, print_fl

class BuildOutputJob(JobBase):
    """This job outputs the mod_output_files from all dependency jobs (by default) to a specified folder.
    
    Can also included mod_output_files from any previously executed job.
    """
    output_path: Path
    include_unresolved_jobs: bool
    include_all_resolved_jobs: bool
    
    def __init__(self, output_path: Path):
        """Initializes the BuildOutputJob.

        Args:
            output_path (Path): The directory to copy the mod_output_files to.
        """
        super().__init__()
        self.output_path = output_path
        self.include_unresolved_jobs = False
        self.include_all_resolved_jobs = False
        
    def run(self, c: Context):
        print_job_header(f"Build Output Job: {self.output_path}")
        
        os.makedirs(self.output_path, exist_ok=True)
        
        for dst, src in self.get_recursive_mod_outputs(self.include_unresolved_jobs).items():
            if not dst.is_absolute():
                dst = self.output_path.joinpath(dst)
            
            print_fl(f"Copying '{str(src)}' to '{str(dst)}'...")
            shutil.copy(src, dst)
            
        if self.include_all_resolved_jobs:
            for dst, src in self.get_all_resolved_mod_outputs().items():
                if not dst.is_absolute():
                    dst = self.output_path.joinpath(dst)
                
                print_fl(f"Copying '{str(src)}' to '{str(dst)}'...")
                shutil.copy(src, dst)
        
        