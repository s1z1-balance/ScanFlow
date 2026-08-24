import os
import sys
import subprocess

REQUIRED_PACKAGES = [
    ("rich", "rich"),
    ("requests", "requests"),
    ("dns", "dnspython"),
    ("cryptography", "cryptography"),
    ("scapy", "scapy"),
]

def ensure_environment():
    missing = []
    for import_name, pkg_name in REQUIRED_PACKAGES:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)

    if not missing:
        return

    print(f"[*] Missing dependencies: {', '.join(missing)}")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(root_dir, ".venv")

    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(venv_python):
        print("[*] Creating virtual environment (.venv)...")
        import venv
        venv.create(venv_dir, with_pip=True)

    print("[*] Installing dependencies into .venv...")
    req_file = os.path.join(root_dir, "requirements.txt")
    if os.path.exists(req_file):
        cmd = [venv_python, "-m", "pip", "install", "-r", req_file]
    else:
        cmd = [venv_python, "-m", "pip", "install"] + [p[1] for p in REQUIRED_PACKAGES]

    subprocess.run(cmd, check=True)
    print("[+] Setup complete!\n")

    if sys.executable.lower() != venv_python.lower():
        if sys.platform == "win32":
            sys.exit(subprocess.call([venv_python] + sys.argv))
        else:
            os.execv(venv_python, [venv_python] + sys.argv)

def main():
    ensure_environment()
    from ui import start_tui
    start_tui()

if __name__ == "__main__":
    main()