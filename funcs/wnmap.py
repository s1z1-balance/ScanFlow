import subprocess
from ui import console, print_header, print_error, print_success, print_info, print_warning, ask_input, ask_back, create_table, RED_PALETTE
from rich.panel import Panel

def choose_options():
    console.print(f"  [{RED_PALETTE['tag']}][1][/{RED_PALETTE['tag']}] Standard Scan   (-sC -sV)           ~ 60s")
    console.print(f"  [{RED_PALETTE['tag']}][2][/{RED_PALETTE['tag']}] Quick Scan      (-T4 -F)            ~ 5s")
    console.print(f"  [{RED_PALETTE['tag']}][3][/{RED_PALETTE['tag']}] Full Port Scan  (-p-)               ~ 10-20m")
    console.print(f"  [{RED_PALETTE['tag']}][4][/{RED_PALETTE['tag']}] Vulnerability   (-sC -sV --script vuln)")
    console.print(f"  [{RED_PALETTE['tag']}][5][/{RED_PALETTE['tag']}] Custom Flags")
    console.print()

    choice = ask_input("Select nmap profile", default="1")
    if choice == "1":
        return ["-sC", "-sV"]
    elif choice == "2":
        return ["-T4", "-F"]
    elif choice == "3":
        return ["-p-"]
    elif choice == "4":
        return ["-sC", "-sV", "--script", "vuln"]
    elif choice == "5":
        custom_opts = ask_input("Enter custom nmap flags (e.g. -Pn -A)")
        return custom_opts.split()
    else:
        return ["-sC", "-sV"]

def wnmap():
    while True:
        print_header("Nmap CLI Wrapper", category="EXTERNAL SCANNER")
        target = ask_input("Enter target domain or IP")
        if not target:
            return
        
        console.print()
        options = choose_options()

        try:
            cmd_str = f"nmap {' '.join(options)} {target}"
            print_info(f"Executing: [bold white]{cmd_str}[/bold white]...")
            console.print()

            result = subprocess.run(
                ["nmap"] + options + [target],
                capture_output=True,
                text=True,
                timeout=1200
            )
            if result.stdout:
                panel = Panel(
                    result.stdout.strip(),
                    title=f"[{RED_PALETTE['primary_bold']}] Nmap Output: {target} [/{RED_PALETTE['primary_bold']}]",
                    border_style="#a8001e",
                    padding=(1, 2)
                )
                console.print(panel)
            if result.stderr:
                print_warning(f"Nmap stderr:\n{result.stderr.strip()}")
        except FileNotFoundError:
            print_error("Nmap is not installed or not found in system PATH. Use [4] Async Port Scanner instead.")
        except Exception as e:
            print_error(f"Nmap execution failed: {e}")
            
        if not ask_back("another scan"):
            return

if __name__ == "__main__":
    wnmap()
