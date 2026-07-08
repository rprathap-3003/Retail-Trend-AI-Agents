import http.server
import socketserver
import webbrowser
import os
import time
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Prevent caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def run_server():
    # Retry logic for port binding
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"✅ Dashboard running at http://localhost:{PORT}/web/")
                print("Press Ctrl+C to stop")
                
                # Open browser automatically
                time.sleep(1)
                webbrowser.open(f"http://localhost:{PORT}/web/")
                
                httpd.serve_forever()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"⚠️ Port {PORT} in use, trying again in 1s...")
                time.sleep(1)
            else:
                raise e
    print(f"❌ Could not bind to port {PORT} after {max_retries} attempts.")

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nStopping server...")
        sys.exit(0)
