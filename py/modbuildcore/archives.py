import pathlib, os, shutil
from pathlib import Path

from invoke import Context
from .job_base import JobBase
from .utils import print_job_header
        
class ArchiveExtractJob(JobBase):
    """This job extracts a specified archive to a location. Does not need to run if the output directory already exists.
    
    The extracted files/directories are not counted as mod_output_files by default.
    """
    archive_path: str
    extract_dir: Path
    force: bool
    
    def __init__(self, archive_path: Path, extract_dir: Path):
        """Initializes the Archive extraction job
        Args:
            archive_path (Path): The file location of the archive to extract.
            extract_dir (Path): The output folder to extract to.
        """
        super().__init__()
        self.archive_path = archive_path
        self.extract_dir = extract_dir
        self.force = False
        
    def needs_to_run(self, c: Context) -> bool:
        retVal = self.force or not self.extract_dir.exists()
        if not retVal:
            print_job_header(f"Archive Extraction Job: {self.extract_dir} already exists.")
        return retVal
    
    def run(self, c: Context):
        print_job_header(f"Archive Extraction Job: {self.archive_path} to {self.extract_dir}")
        if not self.extract_dir.parent.exists():
            os.makedirs(self.extract_dir.parent)
            
        shutil.unpack_archive(self.archive_path, self.extract_dir)