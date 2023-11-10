#!/usr/bin/env python3

import socket
import os
import threading
import streamlit as st

class OTAUpdater:
    def __init__(self, host, port, update_folder):
        self.host = host
        self.port = port
        self.update_folder = update_folder
        self.connected_devices = set()
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
                self.connected_devices.add(client_address)

            try:
                # Receive request from the client
                request = client_socket.recv(1024).decode('utf-8').strip()

                # Process the request (assumes request is a file name)
                file_path = os.path.join(self.update_folder, request)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                        # Send the file content to the client
                        client_socket.sendall(file_content)
                        print(f"Sent file {request} to {client_address}")
                else:
                    client_socket.sendall("File not found".encode('utf-8'))
                    print(f"File not found: {request}")

            except Exception as e:
                print(f"Error handling client request: {str(e)}")

            finally:
                client_socket.close()

    def start_web_ui(self):
        st.title("Connected Devices")
        with self.lock:
            st.write(f"Total Connected Devices: {len(self.connected_devices)}")
            for device in self.connected_devices:
                st.write(f"- {device[0]}:{device[1]}")
    


def main():
    updater = OTAUpdater(host="127.0.0.1", port=8080, update_folder="ota_update")
    updater.start_server()

if __name__ == '__main__':
    main()    