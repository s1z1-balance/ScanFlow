import socket

def whois(domain):
    domain = domain.split('/')[0].replace('http://','').replace('https://','').strip()
    
    try:
        s = socket.create_connection(('whois.iana.org', 43), timeout=10)
        s.send((domain + '\r\n').encode())
        iana = s.recv(8192).decode('utf-8', errors='ignore')
        s.close()
        server = 'whois.verisign-grs.com'
        for line in iana.splitlines():
            if line.lower().startswith('whois:'):
                server = line.split(':',1)[1].strip()
                break
    except:
        server = 'whois.verisign-grs.com'

    try:
        s = socket.create_connection((server, 43), timeout=15)
        s.send((domain + '\r\n').encode())
        data = b''
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            data += chunk
        s.close()
        raw = data.decode('utf-8', errors='ignore')
        print(f"\ndomain: {domain}\n")
        print(raw)
    except Exception as e:
        print(f"err: {e}")

def wip():
    while True:
        domain = input("enter domain (or empty to return): ").strip()
        if not domain:
            return
        whois(domain)
        back = input("\nlookup another domain? (y/n): ").lower().strip()
        if back != "y":
            return

if __name__ == "__main__":
    wip()