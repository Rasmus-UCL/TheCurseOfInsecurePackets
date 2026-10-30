"""Simple local launcher for the Web PoC Split-Screen Cockpit."""

import http.server
import os
import socketserver
import sys
import webbrowser

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_poc")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    os.chdir(DIRECTORY)
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print("=" * 70)
            print("   🚀 THE CURSE OF INSECURE PACKETS — WEB POC COCKPIT LAUNCHER")
            print("=" * 70)
            print(f"Server kører på: {url}")
            print("Åbner automatisk din browser...")
            print("Tryk Ctrl+C i denne terminal for at stoppe serveren.")
            print("=" * 70)
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except OSError as e:
        if "address already in use" in str(e).lower() or getattr(e, "winerror", 0) == 10048:
            alt_port = 8085
            with socketserver.TCPServer(("", alt_port), Handler) as httpd:
                url = f"http://localhost:{alt_port}/index.html"
                print(f"Port 8080 optaget. Kører på alternativ port: {url}")
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                httpd.serve_forever()
        else:
            print(f"Fejl ved start af server: {e}")

if __name__ == "__main__":
    main()
