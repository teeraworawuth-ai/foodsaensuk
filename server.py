# -*- coding: utf-8 -*-
"""
Lightweight Local HTTP Server for ครัวแสนสุข Food Cost Dashboard
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("ระบบวิเคราะห์ต้นทุนอาหาร & กระดานสเปกวัตถุดิบครัวแสนสุข")
        print(f"กำลังเปิดระบบที่: {url}")
        print("กด Ctrl+C เพื่อหยุดการทำงานของเซิร์ฟเวอร์")
        print("=" * 60)
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nปิดเซิร์ฟเวอร์เรียบร้อยแล้ว")

if __name__ == "__main__":
    start_server()
