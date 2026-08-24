import requests
from ui import console, print_header, print_error, print_success, print_info, ask_input, ask_back, create_table, RED_PALETTE

def ip_lookup():
    while True:
        print_header("IP Geolocation & ASN Lookup", category="OSINT / IP")
        ip = ask_input("Enter IP address or host")
        if not ip:
            return
        
        print_info(f"Querying IP intelligence for [bold white]{ip}[/bold white]...")
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            data = response.json()
            console.print()

            if data.get("status") == "success":
                table = create_table(
                    title=f"IP Information for {ip}",
                    columns=[
                        ("PROPERTY", {"style": f"bold {RED_PALETTE['primary']}", "width": 20}),
                        ("VALUE", {"style": "bold white"}),
                    ]
                )
                fields = [
                    ("Query IP", data.get("query")),
                    ("Country", f"{data.get('country')} ({data.get('countryCode')})"),
                    ("Region / City", f"{data.get('regionName')}, {data.get('city')}"),
                    ("ZIP Code", data.get("zip")),
                    ("Coordinates", f"Lat: {data.get('lat')}, Lon: {data.get('lon')}"),
                    ("Timezone", data.get("timezone")),
                    ("ISP", data.get("isp")),
                    ("Organization", data.get("org")),
                    ("AS / ASN", data.get("as")),
                ]
                for k, v in fields:
                    if v:
                        table.add_row(k, str(v))
                console.print(table)
            else:
                print_error(f"Lookup failed: {data.get('message', 'Unknown error')}")

        except Exception as e:
            print_error(f"Connection failed: {e}")

        if not ask_back("another IP"):
            return

if __name__ == "__main__":
    ip_lookup()