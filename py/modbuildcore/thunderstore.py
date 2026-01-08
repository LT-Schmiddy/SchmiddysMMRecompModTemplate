import os, shutil, json, zipfile
from pathlib import Path

from invoke import Context
from .job_base import JobBase
from .utils import print_job_header, print_fl

class ThunderstorePackageJob(JobBase):
    """This job creates a Thunderstore .zip package, ready to be uploaded.
    
    This Job uses dependent mod_output_files to determine what needs to go in the package. 
    The package itself is not a mod_output_file.
    """
    package_file: Path
    manifest: dict[str, str]
    readme_text: Path
    changelog_text: Path
    icon_file: Path
    
    def __init__(self,
            package_file: Path,
            manifest: dict,
            readme_text: Path,
            changelog_text: Path,
            icon_file: Path,
        ):
        """Initializes the ThunderstorePackageJob, and defines the Thunderstore package.

        Args:
            package_file (Path): The output path for the Package file.
            manifest (dict): a dict representing the Thunderstore package's `manifest.json`.
            readme_text (Path): The text to include in the package's `README.md`.
            changelog_text (Path): The text to include in the package's `CHANGELOG.md`.
            icon_file (Path): The source image to use for the package's icon.
        """
        super().__init__()
        self.package_file = package_file
        self.manifest = manifest
        self.readme_text = readme_text
        self.changelog_text = changelog_text
        self.icon_file = icon_file
        
    def run(self, c: Context):
        print_job_header(f"Thunderstore Package Job: {self.manifest['name']}")
        # Thunderstore Metadata:
        output_file = zipfile.ZipFile(self.package_file, 'w', zipfile.ZIP_DEFLATED)
        output_file.writestr("manifest.json", json.dumps(self.manifest, indent=4))
        output_file.writestr("README.md", self.readme_text)
        output_file.writestr("CHANGELOG.md", self.changelog_text)
        output_file.write(self.icon_file, "icon.png")
        
        for dst, src in self.get_recursive_mod_outputs().items():
            print_fl(f"Adding '{src}' as '{dst}'...")
            output_file.write(src, dst)