import streamlit as st
import socket
import threading
import pickle

class OTAUpdaterServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected_clients = {}
        self.lock = threading.Lock()

    def start_server(self):
        # Start the OTA server in a separate thread
        server_thread = threading.Thread(target=self._start_server_thread)
        server_thread.start()

        # Start the Streamlit web UI
        self.start_web_ui()

    def _start_server_thread(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"OTA Updater server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            with self.lock:
                self.connected_clients[client_address] = self.receive_ota_version(client_socket)

            client_socket.close()

    def receive_ota_version(self, client_socket):
        # Receive OTA version from the client
        ota_version = client_socket.recv(1024).decode('utf-8').strip()
        return ota_version

    def start_web_ui(self):
        st.title("OTA Update Strategies via 5G")
        while True:
            with self.lock:
                for client_address, ota_version in self.connected_clients.items():
                    st.write(f"Client: {client_address} | OTA Version: {ota_version}")

# Example usage
if __name__ == "__main__":
    server = OTAUpdaterServer(host="127.0.0.1", port=8083)
    server.start_server()
