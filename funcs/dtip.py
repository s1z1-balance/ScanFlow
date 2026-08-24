import json
from rich.json import JSON
from ui import console, print_header, print_error, print_success, print_info, ask_input, ask_back, create_table, RED_PALETTE

_resolver = None

def get_resolver():
    global _resolver
    if _resolver is None:
        import dns.resolver
        _resolver = dns.resolver.Resolver()
        _resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        _resolver.cache = dns.resolver.Cache()
    return _resolver

ALL_TYPES = [
    'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV',
    'CAA', 'DNSKEY', 'DS', 'TLSA', 'HTTPS', 'SVCB', 'LOC', 'CERT',
    'NAPTR', 'SSHFP', 'RRSIG', 'NSEC', 'NSEC3', 'URI'
]

def get_records(domain):
    import dns.resolver
    resolver = get_resolver()
    result = {"domain": domain, "records": {}}
    
    for t in ALL_TYPES:
        try:
            answers = resolver.resolve(domain, t)
            records = []
            for rdata in answers:
                if t == "SOA":
                    records.append({
                        "mname": str(rdata.mname).rstrip('.'),
                        "rname": str(rdata.rname).rstrip('.'),
                        "serial": rdata.serial,
                        "refresh": rdata.refresh,
                        "retry": rdata.retry,
                        "expire": rdata.expire,
                        "minimum": rdata.minimum
                    })
                elif t in ["MX", "SRV"]:
                    records.append({
                        "preference" if t == "MX" else "priority": rdata.preference if t == "MX" else rdata.priority,
                        "weight" if t == "SRV" else None: rdata.weight if t == "SRV" else None,
                        "port" if t == "SRV" else None: rdata.port if t == "SRV" else None,
                        "target": str(rdata.target).rstrip('.')
                    })
                elif t == "CAA":
                    records.append({
                        "flags": rdata.flags,
                        "tag": rdata.tag,
                        "value": rdata.value.strip('"')
                    })
                else:
                    records.append(str(rdata).rstrip('.').strip('"'))
            result["records"][t] = records if records else None
        except dns.resolver.NoAnswer:
            continue
        except Exception:
            result["records"][t] = None
    return result

def dtip():
    while True:
        print_header("DNS Records Extractor", category="DNS & DOMAIN")
        domain = ask_input("Enter domain (e.g. example.com)")
        if not domain:
            return

        print_info(f"Querying DNS records for [bold white]{domain}[/bold white]...")
        data = get_records(domain)
        console.print()
        
        found_records = {k: v for k, v in data["records"].items() if v is not None}
        if found_records:
            table = create_table(
                title=f"DNS Records for {domain}",
                columns=[
                    ("TYPE", {"style": f"bold {RED_PALETTE['primary']}", "width": 12}),
                    ("ENTRIES", {"style": "white"}),
                ]
            )
            for rtype, rvalues in found_records.items():
                if isinstance(rvalues, list):
                    val_str = "\n".join(json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item) for item in rvalues)
                else:
                    val_str = str(rvalues)
                table.add_row(rtype, val_str)
            console.print(table)
        else:
            print_error(f"No DNS records retrieved for {domain}")

        if not ask_back("another domain"):
            return

if __name__ == "__main__":
    dtip()