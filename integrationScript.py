from http.server import BaseHTTPRequestHandler, HTTPServer
import pyautogui
import secret

ip = secret.ip
port = secret.port

width, height = pyautogui.size()

class RequestHandler(BaseHTTPRequestHandler):
    storage = []

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><head><meta http-equiv='refresh' content='5'></head><body>")

        if self.storage is not None:
            for data in self.storage:
                self.wfile.write(data)
                self.wfile.write(b"<br>")
        else:
            self.wfile.write(b"No storage")

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"POST Request received")
        self.storage.append(post_data)
        post_data_string = post_data.decode('utf-8')
        self.send_prompt(post_data_string)

    def send_prompt(self, prompt):
        pyautogui.moveTo(width/2, 800)
        pyautogui.click()
        pyautogui.write(prompt)
        pyautogui.press('enter')

def start_server():
    serverAddress = (ip, port)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()

start_server()
