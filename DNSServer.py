

import socket
from dns_message import DNSMessage
from dns_response_builder import DNSResponseBuilder


class DNSServer:

    def __init__(self, record_manager, port=53, address=''):
        self.port = port
        self.address = address
        self.record_manager = record_manager

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))

        try:
            while True:
                data, addr = sock.recvfrom(512)
                try:
                    response = self.process_query(data)
                    sock.sendto(response, addr)
                except Exception as e:
                    print(e)
        finally:
            sock.close()

    def process_query(self, query_data):
        message = DNSMessage()
        message.parse(query_data)
        response_builder = DNSResponseBuilder(message, self.record_manager)
        return response_builder.build_response()