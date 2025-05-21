import subprocess, os, shutil, json, zipfile, re
from pathlib import Path
import build_n64recomp_tools as bnt
import build_mod as bm

package_dir = bm.project_root.joinpath("thunderstore_package")

deps = bnt.deps = bnt.deps

def slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r'[\s_]+', '_', text)
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    return text


def get_description() -> str:
    description = re.sub(r'[\n]+', ' ', bm.mod_data["manifest"]["description"]).strip()
    if len(description) > 0 and len(description) <= 256:
        return description
    return bm.mod_data["manifest"]["short_description"]


def get_website_url() -> str:
    if "website_url" in bm.mod_data["manifest"]:
        return bm.mod_data["manifest"]["website_url"]

    result = subprocess.run(
        [
            deps["git"],
            "config", 
            "--get", 
            "remote.origin.url"
        ],
        cwd=bm.project_root,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        # print(f"Command output: {result.stdout}")
        return result.stdout.strip()
    else:
        # print(f"Command failed with error: {result.stderr}")
        return None


def get_package_manifest() ->dict[str, str]:
    return {
        "name":  slugify(bm.mod_data["manifest"]["display_name"]),
        "version_number":  bm.mod_data["manifest"]["version"],
        "website_url":  get_website_url(),
        "description":  get_description(),
        "dependencies":  []
    }


def create_package_directory():
    print(f"Creating package directory at '{package_dir}'...")
    os.makedirs(package_dir)


def create_manifest(path: Path):
    print(f"Creating manifest at '{path}'...")
    path.write_text(json.dumps(get_package_manifest(), indent=4))


def update_manifest(path: Path):
    print(f"Updating manifest at '{path}'...")
    manifest = get_package_manifest();
    del manifest["name"]

    current_manifest: dict[str, str] = json.loads(path.read_text());
    current_manifest.update(manifest)

    path.write_text(json.dumps(current_manifest, indent=4))


def create_readme(path: Path):
    print(f"Creating readme at from description at '{path}'...")
    readme_str = f"# {bm.mod_data['manifest']['display_name']}\n\n{bm.mod_data['manifest']['description']}"
    path.write_text(readme_str)


def copy_icon(src_path: Path, dst_path: Path) -> bool:
    if (src_path.is_file()):
        print(f"Copying icon from '{src_path}' to '{dst_path}'...")
        shutil.copy(src_path, dst_path)
        return True
    else:
        print(f"No file '{src_path}' exists. You may need to create an icon manually...")
        return False


def copy_mod(src_path: Path, dst_path: Path) -> bool:
    if (src_path.is_file()):
        print(f"Copying mod from '{src_path}' to '{dst_path}'...")
        shutil.copy(src_path, dst_path)
        return True
    else:
        print(f"No file '{src_path}' exists. You need to build the mod first.")
        return False

def create_archive(package_dir: Path, dst_path: Path):
    new_zip = zipfile.ZipFile(dst_path, 'w')
    
    for i in os.listdir(package_dir):
        if i == "images":
            continue
        src_path = package_dir.joinpath(i)
        new_zip.write(src_path, i)
        
    new_zip.close()

def create_package():
    bm.run_build()
    
    fully_collected = True
    
    if not package_dir.is_dir():
        create_package_directory()
        
    manifest_file = package_dir.joinpath("manifest.json")
    if not manifest_file.is_file():
        create_manifest(manifest_file)
    else: 
        update_manifest(manifest_file)
        
    readme_file = package_dir.joinpath("README.md")
    if not readme_file.is_file():
        create_readme(readme_file)
    
    icon_file = package_dir.joinpath("icon.png")
    if not icon_file.is_file():
        fully_collected = fully_collected and copy_icon(bm.project_root.joinpath("thumb.png"), icon_file)
    
    mod_file = package_dir.joinpath(bm.build_nrm_file.name)
    fully_collected = fully_collected and copy_mod(bm.build_nrm_file, mod_file)
    
    if fully_collected:
        print("Fully collected. Zipping mod package.")
        create_archive(package_dir, bm.project_root.joinpath(f"{bm.mod_data['inputs']['mod_filename']}.thunderstore.zip"))
    else:
        print("Files are missing.")
    
        
        

if __name__ == '__main__':
    create_package()

