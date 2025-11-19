import http.server
import socketserver
import webbrowser
import os
import sys

# 설정
PORT = 8000
DEMO_PATH = "/examples/web-demo/index.html"

def run_server():
    # 현재 스크립트 위치를 루트로 설정
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    handler = http.server.SimpleHTTPRequestHandler
    
    # 포트 재사용 허용 (서버 껐다 켰을 때 에러 방지)
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}{DEMO_PATH}"
        print(f"\nStarting DongnaeJS Demo...")
        print(f"Serving at: {url}")
        print(f"Press Ctrl+C to stop the server.\n")
        
        # 브라우저 자동 실행
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    run_server()