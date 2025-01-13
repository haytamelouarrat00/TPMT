from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps, loads
from queueclient import QueueClient
from task import Task
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Proxy(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.client = QueueClient()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            task = self.client.task_queue.get()
            task_json = task.to_json()
            self.wfile.write(bytes(task_json, "utf-8"))
            logging.info(f"Sent task {task.identifier} to client.")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            logging.error(f"Error processing GET request: {e}")

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            content_length = int(self.headers.get("content-length", 0))
            content = self.rfile.read(content_length)
            task_json = content.decode()
            task = Task.from_json(task_json)
            self.client.result_queue.put(task)
            response = dumps({"status": "ok"})
            self.wfile.write(bytes(response, "utf-8"))
            logging.info(f"Received task {task.identifier} from client.")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            logging.error(f"Error processing POST request: {e}")

def run(server_class=HTTPServer, handler_class=Proxy, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting server on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Server stopped")

if __name__ == "__main__":
    run()