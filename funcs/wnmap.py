import subprocess

def choose_options():
    while True:
        print("[1] standard scan (-sC -sV) / 60~ secs")
        print("[2] quick scan (-T4 -F) / 5~ secs")
        print("[3] full port scan (-p-) 20~ mins")
        print("[4] custom options")
        print("")
        print("[5] scan CVE's")
        choice = input("choose scan type: ").strip()
        if choice == "1":
            return ["-sC", "-sV"]
        elif choice == "2":
            return ["-T4", "-F"]
        elif choice == "3":
            return ["-p-"]
        elif choice == "4":
            custom_opts = input("enter custom nmap options: ").strip()
            return custom_opts.split()
        elif choice == "5":
            return ["--script", "vuln"]
        else:
            print("invalid choice, try again.")

def wnmap():
    from sncflw import menu
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
        
    back = input("\nback to menu? (y/n): ").lower()
    if back == "y":
        print("\033[H\033[J", end="")
        menu()
    elif back == "n":
            return

if __name__ == "__main__":
    wnmap()
