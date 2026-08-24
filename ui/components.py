import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from ui.theme import SCANFLOW_THEME, RED_PALETTE

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(theme=SCANFLOW_THEME)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title: str, category: str = "MODULE"):
    clear_screen()
    header_text = Text()
    header_text.append(f" {category.upper()} ", style="bold #ffffff on #8b0000")
    header_text.append(f"  {title.upper()}", style="bold #ff1e42")
    
    panel = Panel(
        Align.center(header_text),
        border_style="#ff1e42",
        padding=(0, 1)
    )
    console.print(panel)
    console.print()

def print_error(msg: str):
    console.print(f"[{RED_PALETTE['error']}][!][/] [bold white]{msg}[/bold white]")

def print_success(msg: str):
    console.print(f"[{RED_PALETTE['success']}][+][/] [bold white]{msg}[/bold white]")

def print_warning(msg: str):
    console.print(f"[{RED_PALETTE['warning']}][*][/] [bold white]{msg}[/bold white]")

def print_info(msg: str):
    console.print(f"[{RED_PALETTE['accent']}][~][/] [{RED_PALETTE['text']}]{msg}[/{RED_PALETTE['text']}]")

def ask_input(prompt_text: str = "target", default: str = None) -> str:
    prompt_str = f"[bold {RED_PALETTE['primary']}]{prompt_text}[/bold {RED_PALETTE['primary']}]"
    if default:
        prompt_str += f" [dim]({default})[/dim]"
    prompt_str += f" [bold {RED_PALETTE['accent']}]>[/bold {RED_PALETTE['accent']}] "
    val = console.input(prompt_str).strip()
    return val if val else (default or "")

def ask_back(action: str = "another lookup") -> bool:
    console.print()
    prompt_str = f"[{RED_PALETTE['text_dim']}]perform {action}? (y/n)[/] [bold {RED_PALETTE['primary']}]>[/bold {RED_PALETTE['primary']}] "
    val = console.input(prompt_str).lower().strip()
    return val == "y"

def press_enter(prompt: str = "Press Enter to return..."):
    console.input(f"\n[dim]{prompt}[/dim]")

def create_table(title: str = None, columns: list = None, expand: bool = True) -> Table:
    table = Table(
        title=f"[{RED_PALETTE['primary_bold']}]{title}[/{RED_PALETTE['primary_bold']}]" if title else None,
        title_style="bold #ff1e42",
        header_style="bold #ffffff on #5a000e",
        border_style="#7a0015",
        row_styles=["none", "dim"],
        expand=expand,
        padding=(0, 1),
    )
    if columns:
        for col in columns:
            if isinstance(col, tuple):
                name = col[0]
                opts = col[1] if len(col) > 1 and isinstance(col[1], dict) else {}
                style = opts.get("style", "white")
                justify = opts.get("justify", "left")
                width = opts.get("width", None)
                table.add_column(name, style=style, justify=justify, width=width)
            else:
                table.add_column(str(col), style="white")
    return table
