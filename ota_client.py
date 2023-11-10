import socket
import pickle

class OTAUpdaterClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_ota_version(self, ota_version):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        # Send OTA version to the server
        client_socket.sendall(ota_version.encode('utf-8'))

        client_socket.close()

# Example usage
if __name__ == "__main__":
    client = OTAUpdaterClient(host="127.0.0.1", port=8083)
    ota_version = "1.0.0"  # Replace with your actual OTA version
    client.send_ota_version(ota_version)
