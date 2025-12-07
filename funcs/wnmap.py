import subprocess

def choose_options():
    while True:
        print("[1] standard scan (-sC -sV)")
        print("[2] quick scan (-T4 -F)")
        print("[3] full port scan (-p-)")
        choice = input("choose scan type: ").strip()
        if choice == "1":
            return ["-sC", "-sV"]
        elif choice == "2":
            return ["-T4", "-F"]
        elif choice == "3":
            return ["-p-"]
        else:
            print("invalid choice, try again.")

def wnmap(target, options):
    try:
        print(f"scanning {target} with {' '.join(options)}...")
        result = subprocess.run(["nmap"] + options + [target],
                              capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr:
            print("nmap errors:")
            print(result.stderr)
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    target = input("enter ip/domain: ").strip()
    if not target:
        print("no target.")
        exit()
    opts = choose_options()
    wnmap(target, opts)