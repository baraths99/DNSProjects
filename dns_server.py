import socket
import struct
import threading
import sys
from record_types import RecordType
from dns_header import DNSHeader
from dns_question import DNSQuestion
from dns_database import DNSDatabase


class DNSServer:
    def __init__(self, host='0.0.0.0', port=53, db_file='dns_records.json'):
        self.host = host
        self.port = port
        self.db = DNSDatabase(db_file)
        self.sock = None
        self.running = False

    def start(self):
        """Start the DNS server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"DNS Server started on {self.host}:{self.port}")

            while self.running:
                data, addr = self.sock.recvfrom(512)  # Standard DNS message size
                threading.Thread(target=self.handle_query, args=(data, addr)).start()

        except PermissionError:
            print(f"Error: Permission denied. Port {self.port} requires root privileges.")
            sys.exit(1)
        except OSError as e:
            print(f"Socket error: {e}")
            sys.exit(1)
        finally:
            if self.sock:
                self.sock.close()

    def stop(self):
        """Stop the DNS server"""
        self.running = False
        if self.sock:
            self.sock.close()

    def handle_query(self, data, addr):
        """Process a DNS query and send a response"""
        try:
            header = DNSHeader.unpack(data)
            pos = 12

            qname, pos = self.parse_name(data, pos)
            qtype, qclass = struct.unpack('!HH', data[pos:pos + 4])

            matching_records = self.db.get_records(qname, qtype)

            response_header = DNSHeader(
                id=header.id,
                flags=0x8180,
                qdcount=1,
                ancount=len(matching_records),
                nscount=0,
                arcount=0
            )

            response = response_header.pack()

            question = DNSQuestion(qname, qtype, qclass)
            response += question.pack()

            for record in matching_records:
                packed_record = record.pack()
                if packed_record:
                    response += packed_record

            self.sock.sendto(response, addr)

        except Exception as e:
            print(f"Error handling query: {e}")

    def parse_name(self, data, pos):
        """Parse a domain name from DNS message format"""
        name_parts = []

        while True:
            length = data[pos]
            pos += 1
            if (length & 0xC0) == 0xC0:
                offset = ((length & 0x3F) << 8) | data[pos]
                pos += 1
                referred_name, _ = self.parse_name(data, offset)
                name_parts.append(referred_name)
                break
            if length == 0:
                break
            name_parts.append(data[pos:pos + length].decode('ascii'))
            pos += length

        return '.'.join(name_parts), pos

    def add_record(self, name, record_type_str, ttl, data):
        """Add a DNS record using string type name"""
        record_type_map = {
            'A': RecordType.A.value,
            'NS': RecordType.NS.value,
            'CNAME': RecordType.CNAME.value,
            'MX': RecordType.MX.value
        }

        record_type = record_type_map.get(record_type_str.upper())
        if not record_type:
            print(f"Invalid record type: {record_type_str}")
            return False
        if record_type == RecordType.MX.value:
            parts = data.split()
            if len(parts) < 2:
                print("MX record requires preference and exchange name")
                return False
            try:
                preference = int(parts[0])
                exchange = parts[1]
                data = (preference, exchange)
            except ValueError:
                print("MX preference must be a number")
                return False

        return self.db.add_record(name, record_type, ttl, data)