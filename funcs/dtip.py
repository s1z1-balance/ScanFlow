import dns.resolver
import json

from rich import print as rprint
from rich.json import JSON

resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8', '1.1.1.1']

ALL_TYPES = [
    'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV',
    'CAA', 'DNSKEY', 'DS', 'TLSA', 'HTTPS', 'SVCB', 'LOC', 'CERT',
    'NAPTR', 'SSHFP', 'RRSIG', 'NSEC', 'NSEC3', 'URI'
]

def get_records(domain):
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
    domain = input("domain: ").strip()
    data = get_records(domain)
    rprint(JSON(json.dumps(data, ensure_ascii=False)))

if __name__ == "__main__":
    dtip()
