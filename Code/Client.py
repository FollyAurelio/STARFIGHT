import socket
import pickle

MyIP = socket.gethostbyname(socket.gethostname())


class Network:
    def __init__(self, ip=""):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = self.connect(ip)

    def connect(self, ip):
        if ip:
            host = ip
        else:
            host = MyIP
        port = 12345
        try:
            self.client.connect((host, port))
            return pickle.loads(self.client.recv(4096))
        except:
            return

    def send(self, info):
        try:
            self.client.send(pickle.dumps(info))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(e)

    def send_sol(self, info):
        try:
            self.client.send(pickle.dumps(info))
        except socket.error as e:
            print(e)

    def recv_sol(self):
        return pickle.loads(self.client.recv(2048))
