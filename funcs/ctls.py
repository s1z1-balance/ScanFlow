import socket
import json
import idna
from datetime import datetime, timezone
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend as db
from ui import console, print_header, print_error, print_success, print_info, print_warning, ask_input, ask_back, create_table, RED_PALETTE

def _m(pat, hn):
    pat = pat.lower()
    hn = hn.lower()
    if pat == hn:
        return True
    if pat.startswith("*."):
        s = pat[1:]
        return hn.endswith(s) and hn.count(".") >= 2
    return False

def hm(cd, hn):
    hn = hn.lower()
    dns = []
    if cd and "subjectAltName" in cd:
        for t, v in cd["subjectAltName"]:
            if t.lower() == "dns":
                dns.append(v.lower())
    if dns:
        for p in dns:
            if _m(p, hn):
                return True, None
        return False, f"{hn} != SAN {dns}"
    if cd:
        for sub in cd.get("subject", []):
            for k, v in sub:
                if k.lower() == "commonname":
                    cn = v.lower()
                    if _m(cn, hn):
                        return True, None
                    return False, f"{hn} != CN {cn}"
    return False, "no SAN/CN"

def fc(h, p=443, t=5):
    r = {"host": h, "port": p, "cert": {}, "err": None}
    try:
        sni = idna.encode(h).decode("ascii")
    except Exception:
        sni = h
    ctx_nv = ssl.create_default_context()
    ctx_nv.check_hostname = False
    ctx_nv.verify_mode = ssl.CERT_NONE
    cb = None
    cd = None
    try:
        with socket.create_connection((h, p), timeout=t) as s:
            with ctx_nv.wrap_socket(s, server_hostname=sni) as ss:
                cb = ss.getpeercert(binary_form=True)
                cd = ss.getpeercert()
    except Exception as e:
        r["err"] = f"conn: {e}"
        return r
    if not cb:
        r["err"] = "no cert"
        return r
    try:
        c = x509.load_der_x509_certificate(cb, db())
    except Exception as e:
        r["err"] = f"parse: {e}"
        return r
    sub = c.subject.rfc4514_string()
    iss = c.issuer.rfc4514_string()
    nb = c.not_valid_before_utc
    na = c.not_valid_after_utc
    ser = hex(c.serial_number)
    try:
        sig = c.signature_hash_algorithm.name
    except Exception:
        sig = None
    sans = []
    try:
        ex = c.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = [str(n) for n in ex.value]
    except Exception:
        pass
    ok, er = hm(cd, h)
    ctx_v = ssl.create_default_context()
    ch_ok = False
    ch_er = None
    try:
        with socket.create_connection((h, p), timeout=t) as s:
            with ctx_v.wrap_socket(s, server_hostname=sni):
                ch_ok = True
    except Exception as e:
        ch_er = str(e)
    r["cert"] = {
        "subject": sub,
        "issuer": iss,
        "serial": ser,
        "sig_algo": sig,
        "not_before": nb.isoformat(),
        "not_after": na.isoformat(),
        "days_left": (na - datetime.now(timezone.utc)).days,
        "sans": sans,
        "host_match": {"ok": ok, "err": er},
        "chain_ok": {"ok": ch_ok, "err": ch_er},
    }
    return r

def ctls():
    while True:
        print_header("SSL/TLS Certificate Inspector", category="SSL / TLS AUDIT")
        i = ask_input("Enter host[:port] (e.g. google.com:443)")
        if not i:
            return
        if ":" in i:
            h, ps = i.rsplit(":", 1)
            try: port = int(ps)
            except: port = 443
        else:
            h = i
            port = 443

        print_info(f"Connecting to [bold white]{h}:{port}[/bold white] and extracting TLS certificate...")
        d = fc(h, port)
        console.print()

        if d.get("err"):
            print_error(f"TLS handshake/certificate error: {d['err']}")
        else:
            cert = d["cert"]
            table = create_table(
                title=f"TLS Certificate for {h}:{port}",
                columns=[
                    ("PROPERTY", {"style": f"bold {RED_PALETTE['primary']}", "width": 20}),
                    ("DETAILS", {"style": "white"}),
                ]
            )
            table.add_row("Subject", cert["subject"])
            table.add_row("Issuer", cert["issuer"])
            table.add_row("Valid From", cert["not_before"])
            table.add_row("Valid Until", cert["not_after"])
            
            days_style = "bold green" if cert["days_left"] > 30 else ("bold yellow" if cert["days_left"] > 7 else "bold red")
            table.add_row("Days Remaining", f"[{days_style}]{cert['days_left']} days[/{days_style}]")
            table.add_row("Signature Algorithm", str(cert["sig_algo"]))
            table.add_row("Serial Number", cert["serial"])

            chain_status = "[bold green]VALID[/bold green]" if cert["chain_ok"]["ok"] else f"[bold red]INVALID ({cert['chain_ok']['err']})[/bold red]"
            host_status = "[bold green]MATCH[/bold green]" if cert["host_match"]["ok"] else f"[bold red]MISMATCH ({cert['host_match']['err']})[/bold red]"
            table.add_row("Chain Validation", chain_status)
            table.add_row("Hostname Match", host_status)
            table.add_row("SANs", "\n".join(cert["sans"]) if cert["sans"] else "-")

            console.print(table)

        if not ask_back("another host"):
            return

if __name__ == "__main__":
    ctls()