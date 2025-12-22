import tomllib, pathlib, zipfile, os
from pathlib import Path

from invoke import Context
from .job_base import JobBase
from .utils import invoke_subprocess_run, print_job_header

class ModTomlJob(JobBase):
    mod_tool_path: Path
    toml_path: Path
    run_nrm_path_fix: bool
    build_dir: Path
    
    def __init__(self, mod_tool_path: Path, toml_path: Path, run_nrm_path_fix: bool = False, build_dir: Path = None):
        super().__init__()
        self.mod_tool_path = mod_tool_path    
        self.toml_path = toml_path
        self.run_nrm_path_fix = run_nrm_path_fix
        self.build_dir = build_dir
        self.data = tomllib.loads(self.toml_path.read_text())
        
        if self.build_dir is None:
            self.build_dir = self.get_elf_path().parent
            
        self.mod_output_files[self.get_output_path()] = Path(self.get_output_path().name)
    
    def get_path_from_toml(self, rel_path: str | Path) -> Path:
        return self.toml_path.parent.joinpath(rel_path).resolve()
    
    def get_elf_path(self) -> Path:
        return self.get_path_from_toml(self.data["inputs"]["elf_path"])
    
    def get_output_path(self) -> Path:
        return self.build_dir.joinpath(self.data["inputs"]["mod_filename"]).with_suffix(".nrm")
    
    def nrm_path_fix(self):
        in_zip = zipfile.ZipFile(self.get_output_path(), 'r')
        out_file_path = self.get_output_path().with_suffix(".nrm_temp")        
        out_zip = zipfile.ZipFile(out_file_path, 'w', in_zip.compression)        
        
        for file in in_zip.filelist:
            new_path = file.filename.replace("\\", "/")
            out_zip.writestr(new_path, in_zip.read(file))
        
        in_zip.close()
        out_zip.close()
        
        os.remove(self.get_output_path())
        os.rename(out_file_path, self.get_output_path())
        
    def run(self, c: Context):
        print_job_header(f"Mod Toml Job: {self.toml_path}")
        invoke_subprocess_run(c, True,
            [self.mod_tool_path, self.toml_path, self.build_dir]
        )