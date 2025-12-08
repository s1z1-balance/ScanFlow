import subprocess

def choose_options():
    while True:
        print("[1] standard scan (-sC -sV) / 60~ secs")
        print("[2] quick scan (-T4 -F) / 5~ secs")
        print("[3] full port scan (-p-) 20~ mins")
        choice = input("choose scan type: ").strip()
        if choice == "1":
            return ["-sC", "-sV"]
        elif choice == "2":
            return ["-T4", "-F"]
        elif choice == "3":
            return ["-p-"]
        else:
            print("invalid choice, try again.")

def wnmap():
    target = input("enter ip/domain: ").strip()
    if not target:
        print("no target.")
        return
    
    options = choose_options()

    try:
        print(f"scanning {target} with {' '.join(options)}...")
        result = subprocess.run(
            ["nmap"] + options + [target],
            capture_output=True,
            text=True,
            timeout=1200
        )
        print(result.stdout)
        if result.stderr:
            print("nmap errors:")
            print(result.stderr)
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    wnmap()
