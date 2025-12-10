import socket
import json
import idna
from datetime import datetime, timezone
from rich import print as p
from rich.json import JSON as rj
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend as db

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
    if "subjectAltName" in cd:
        for t, v in cd["subjectAltName"]:
            if t.lower() == "dns":
                dns.append(v.lower())
    if dns:
        for p in dns:
            if _m(p, hn):
                return True, None
        return False, f"{hn} != SAN {dns}"
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
    except:
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
    except:
        sig = None
    sans = []
    try:
        ex = c.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = [str(n) for n in ex.value]
    except:
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
    try:
        from sncflw import menu
    except:
        menu = lambda: None
    while True:
        i = input("host: ").strip()
        if not i: continue
        if ":" in i:
            h, ps = i.rsplit(":", 1)
            try: port = int(ps)
            except: port = 443
        else:
            h = i
            port = 443
        d = fc(h, port)
        p(rj(json.dumps(d, ensure_ascii=False, indent=2)))
        if input("\nback to menu? (y/n): ").lower().strip() == "y":
            print("\033[H\033[J", end="")
            menu()
        else:
            break

if __name__ == "__main__":
    ctls()