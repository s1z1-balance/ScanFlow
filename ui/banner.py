import sys
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from ui.theme import RED_PALETTE

RAW_BANNER = r"""
  ____                   _____ _                 
 / ___|  ___ __ _ _ __  |  ___| | _____      __  
 \___ \ / __/ _` | '_ \ | |_  | |/ _ \ \ /\ / /  
  ___) | (_| (_| | | | ||  _| | | (_) \ V  V /   
 |____/ \___\__,_|_| |_||_|   |_|\___/ \_/\_/    
"""

def get_banner_renderable():
    banner_lines = RAW_BANNER.strip("\n").splitlines()
    gradient_colors = ["#ff0033", "#ff1e42", "#ff3355", "#ff4d6a", "#ff6680"]
    
    text = Text()
    for idx, line in enumerate(banner_lines):
        color = gradient_colors[idx % len(gradient_colors)]
        text.append(line + "\n", style=f"bold {color}")
    
    return Align.center(text)

def get_header_panel():
    banner = get_banner_renderable()
    subtitle = Text.from_markup(
        f"[{RED_PALETTE['accent']}]v2.0[/]  [dim]|[/]  "
        f"[{RED_PALETTE['text']}]OFFENSIVE & DEFENSIVE RECONNAISSANCE TOOLKIT[/]  [dim]|[/]  "
        f"[{RED_PALETTE['primary']}]PURE ASYNC CORE[/]"
    )
    return banner, Align.center(subtitle)
