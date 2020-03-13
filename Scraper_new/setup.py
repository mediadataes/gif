print("#################")
print("STARTING SETUP.PY")
print("#################\n\n\n")

print("Importing nltk...")
import nltk
print("[+] Done (nltk import)\n")

print("Downloading nltk packages...")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('punkt')
print("[+] Done (nltk packages)\n")

from Settings.jQuery import download as jq_download

print("Downloading jQuery...")
jq_download()
print("[+] Done (jQuery download)\n")

print("Importing git...")
try:
    from git import Repo
except ImportError as err:
    print("\n\n\n")
    print(err)
    print("\n\nTo solve this import error you must download git from"
            " https://git-scm.com/downloads\n    and ensure it is in"
            " PATH (environment variable)")
    exit(-1)

from os import getcwd, path
print("[+] Done (git import)\n")


if(not path.exists(f"{getcwd()}//Structures//Sockets")):
    print("Cloning from git...")
    Repo.clone_from("https://github.com/saisua/Sockets",f"{getcwd()}//Structures//Sockets")
    print("[+] Done (git clone)\n")
else:
    print("[?] Sockets has already been downloaded")
    print("Fetching to overwrite with the lastest version...")
    local_repository = Repo(f"{getcwd()}//Structures//Sockets")
    for remote in local_repository.remotes:
        remote.fetch()
    local_repository.git.reset("--hard")
    print("[+] Done (git fetch)\n")

if(not path.isfile(f"{getcwd()}//geckodriver")):
    print("Importing platform...")
    import platform
    print("[+] Done (platform import)\n")
    
    print("Importing wget...")
    import wget
    print("[+] Done (wget import)\n")

    
    system = (f"{'linux' if platform.system() == 'Linux' else 'win'}"
                f"{'64' if '64' in platform.machine() else '32'}"
                f"{'.tar.gz' if platform.system() == 'Linux' else '.zip'}")
    print(f"Downloading geckodriver ({system})...")
    wget.download(f"https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-{system}",
                        out=f"{getcwd()}//geckodriver-{system}")


    if(system.endswith("zip")):
        print("Importing zipfile...")
        import zipfile
        print("[+] Done (zipfile import)\n")

        print(f"Extracting geckodriver-{system}... (not tested)")
        zipfile.ZipFile(f"{getcwd()}//geckodriver-{system}").extractall()
        print(f"[+] Done (extraction)")
    else:
        print("Importing tarfile...")
        import tarfile
        print("[+] Done (tarfile import)\n")

        print(f"Extracting geckodriver-{system}...")
        tarfile.open(f"{getcwd()}//geckodriver-{system}").extractall()
        print(f"[+] Done (extraction)")