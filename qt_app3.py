import sys
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
import socket
from time import sleep, time
import pickle
import os
from reportlab.pdfgen import canvas
from os.path import getsize

class Client():
    def __init__(self, id, version, socket=0):
        self.id = id
        self.version = version
        self.socket = socket

class OTAServer(QThread):
    data_updated = pyqtSignal(list)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = []

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"OTA Updater server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            data = client_socket.recv(1024).decode('utf-8').strip()
            id, version = data.split(',')
            client = Client(id, version, client_socket)
            self.clients.append(client)

            self.data_updated.emit(self.clients)  # Emit signal to update UI

class OTATableApp(QWidget):
    def __init__(self):
        super().__init__()

        self.ota_server = OTAServer('127.0.0.1', 8099)
        self.ota_server.data_updated.connect(self.update_data_to_table)
        self.ota_server.start()

        self.setWindowTitle('5G OTA')
        self.setGeometry(100, 100, 600, 400)
        self.num_clients = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Version", "Firmware", "Report"])

        layout.addWidget(self.table)

        update_button = QPushButton('Update Table')
        update_button.clicked.connect(self.update_table)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update_data_to_table(self, clients):
        if self.num_clients < len(clients):
            data = [(client.id, client.version, "Upload", "Download") for client in clients]
            self.num_clients = len(clients)
            self.update_table(data)

    def update_table(self, new_data):
        self.table.setRowCount(len(new_data))

        for row, (id, version, firmware, report) in enumerate(new_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.table.setItem(row, 1, QTableWidgetItem(version))

            firmware_button = QPushButton('Upload')
            firmware_button.clicked.connect(lambda _, row=row: self.on_firmware_button_clicked(row))
            self.table.setCellWidget(row, 2, firmware_button)

            report_button = QPushButton('Download')
            report_button.clicked.connect(lambda _, row=row: self.on_report_button_clicked(row))
            self.table.setCellWidget(row, 3, report_button)

    def on_firmware_button_clicked(self, row):
        print(f"Firmware button clicked for row {row + 1}")

        # Open a file dialog to select a file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select Firmware File')

        if file_path:
            # Send the file content to the client
            client = self.ota_server.clients[row]
            start_time = time()

            with open(file_path, 'rb') as file:
                file_content = file.read()

            # Send the file content
            client.socket.sendall(file_content+ b"EOF")

            end_time = time()
            elapsed_time = end_time - start_time
            file_size = getsize(file_path)  # in bytes
            bandwidth = file_size / elapsed_time  # bytes per second
            # print(f"File sent in {end_time - start_time:.2f} seconds.")
            # print(f"File send in {(end_time - start_time) * 1000:.2f} milliseconds.")
            print(f"File sent in {(elapsed_time) * 1000:.2f} milliseconds.")
            print(f"File size: {file_size} bytes")
            # print(f"Bandwidth used: {bandwidth:.2f} bytes/second")
            print(f"Bandwidth used: {bandwidth / 1024 / 1024:.2f} MB/second")




    # def on_firmware_button_clicked(self, row):
    #     print(f"Firmware button clicked for row {row + 1}")

    #     # Open a file dialog to select a file
    #     file_dialog = QFileDialog()
    #     file_path, _ = file_dialog.getOpenFileName(self, 'Select Firmware File')
        
    #     if file_path:
    #         # Send the file to the client
    #         client = self.ota_server.clients[row]
    #         start_time = time()

    #         with open(file_path, 'rb') as file:
    #             data = file.read(1024)
    #             while data:
    #                 client.socket.send(data)
    #                 data = file.read(1024)

    #         end_time = time()
    #         print(f"File sent in {end_time - start_time:.2f} seconds.")

    def on_report_button_clicked(self, row):
        print(f"Report button clicked for row {row + 1}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ota_app = OTATableApp()
    ota_app.show()
    sys.exit(app.exec_())
