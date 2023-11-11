import socket
from time import sleep, time

class OTAUpdaterClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_ota_version(self, ota_version):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        # Send client ID and OTA version to the server
        data = "2, 0.1"
        client_socket.sendall(data.encode("utf-8"))

        # Receive the firmware file from the server
        self.receive_firmware(client_socket)

    def receive_firmware(self, client):
        print("receive firmware")
        file_path = f"firmware.bin"  # Unique file name for each client
        with open(file_path, 'wb') as file:

            data = client.recv(1024)
            start_time = time()
            while data:
                data = client.recv(1024)
                if not data or data.endswith(b"EOF"):
                    break  # End of file transfer
                print("writing")
                file.write(data)
            print('out of while loop')
            end_time = time()
            # print(f"File received from client in {end_time - start_time:.2f} seconds.")
            print(f"File received from client in {(end_time - start_time) * 1000:.2f} milliseconds.")


    # def receive_firmware(self, client_socket):
    #     print("receicing firmware")
    #     file_path = "received_firmware2.bin"
    #     with open(file_path, 'wb') as file:
    #         data = client_socket.recv(1024)

    #         while data:
    #             file.write(data)
    #             data = client_socket.recv(1024)

    #     print("Firmware received and saved as:", file_path)

def main():
    client = OTAUpdaterClient(host="127.0.0.1", port=8099)
    ota_version = "0.0.3"
    while True:
        client.send_ota_version(ota_version)
        break

if __name__ == "__main__":
    main()
