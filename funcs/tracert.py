import socket
import time
from scapy.all import IP, ICMP, sr1
from ui import console, print_header, print_error, print_success, print_info, print_warning, ask_input, ask_back, create_table, RED_PALETTE

def resolve_target(target):
    try:
        ip = socket.gethostbyname(target)
        name = socket.getfqdn(target)
        if ip == name:
            return None, ip
        return name, ip
    except Exception:
        return None, target

def traceroute(target, max_hops=30):
    domain, ip = resolve_target(target)
    print_info(f"Tracing route to [bold white]{target}[/bold white] [[bold {RED_PALETTE['primary']}]{ip}[/]] (max {max_hops} hops)...")
    console.print()

    table = create_table(
        title=f"Traceroute -> {target} ({ip})",
        columns=[
            ("HOP", {"style": f"bold {RED_PALETTE['primary']}", "justify": "center", "width": 6}),
            ("IP ADDRESS", {"style": "bold yellow", "width": 20}),
            ("HOSTNAME", {"style": "white", "width": 35}),
            ("RTT", {"style": "magenta", "width": 12}),
        ]
    )

    timeout_count = 0
    for ttl in range(1, max_hops + 1):
        pkt = IP(dst=ip, ttl=ttl) / ICMP()
        send_time = time.time()
        reply = sr1(pkt, verbose=0, timeout=1)
        recv_time = time.time()
        
        if reply is None:
            table.add_row(str(ttl), "*", "* (Request timed out)", "*")
            timeout_count += 1
            if timeout_count >= 3:
                break
            continue
        
        timeout_count = 0
        hop_ip = reply.src
        try:
            hop_host = socket.gethostbyaddr(hop_ip)[0]
        except Exception:
            hop_host = "-"
        
        rtt_ms = (recv_time - send_time) * 1000
        rtt_str = f"{rtt_ms:.1f} ms"
        table.add_row(str(ttl), hop_ip, hop_host, rtt_str)
        
        if reply.type == 0 or reply.type == 3:
            break

    console.print(table)

def tracert():
    while True:
        print_header("ICMP Traceroute", category="NETWORK ROUTING")
        target = ask_input("Enter domain or IP")
        if not target:
            return
        traceroute(target)

        if not ask_back("another traceroute"):
            return

if __name__ == "__main__":
    tracert()