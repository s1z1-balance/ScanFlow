import socket
import time
from scapy.all import IP, ICMP, sr1

def resolve_target(target):
    try:
        ip = socket.gethostbyname(target)
        name = socket.getfqdn(target)
        if ip == name:
            return None, ip
        return name, ip
    except:
        return None, target

def traceroute(target, max_hops=30):
    domain, ip = resolve_target(target)
    print("")
    if domain:
        print(f"tracing route to {domain} [{ip}]")
    else:
        print(f"tracing route to {ip}")
    print(f"over a maximum of {max_hops} hops:\n")
    print(f"{'hop':<5} {'ip address':<18} {'hostname':<40} {'time'}")
    
    timeout_count = 0
    for ttl in range(1, max_hops + 1):
        pkt = IP(dst=ip, ttl=ttl) / ICMP()
        send_time = time.time()
        reply = sr1(pkt, verbose=0, timeout=1)
        recv_time = time.time()
        
        if reply is None:
            print(f"{ttl:<5} {'*':<18} {'*':<40} {'*'}")
            timeout_count += 1
            if timeout_count >= 2:
                break
            continue
        
        timeout_count = 0
        
        hop_ip = reply.src
        try:
            hop_host = socket.gethostbyaddr(hop_ip)[0]
        except:
            hop_host = "-"
        
        rtt_ms = (recv_time - send_time) * 1000
        rtt_str = f"{rtt_ms:.1f} ms"
        print(f"{ttl:<5} {hop_ip:<18} {hop_host:<40} {rtt_str}")
        
        if reply.type == 0:
            break
        if reply.type == 3:
            break


def tracert():
    from sncflw import menu
    target = input("enter domain or ip: ").strip().lower()
    traceroute(target)

    back = input("\nback to menu? (y/n): ").lower().strip()
    if back == "y":
        print("\033[H\033[J", end="")
        menu()
    else:
        return

if __name__ == "__main__":
    tracert()