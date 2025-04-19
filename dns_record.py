#!/usr/bin/env python3
import struct
import time
import socket
from dns_question import DNSQuestion
from record_types import RecordType


class DNSRecord:
    def __init__(self, name, record_type, record_class, ttl, data):
        self.name = name
        self.record_type = record_type
        self.record_class = record_class
        self.ttl = ttl
        self.data = data
        self.expiry_time = time.time() + ttl

    def is_expired(self):
        return time.time() > self.expiry_time

    def get_remaining_ttl(self):
        remaining = self.expiry_time - time.time()
        return max(0, int(remaining))

    def pack(self):
        name_bytes = DNSQuestion.pack_name(self.name)

        if self.record_type == RecordType.A.value:
            rdata = socket.inet_aton(self.data)
        elif self.record_type == RecordType.MX.value:
            preference, exchange = self.data
            rdata = struct.pack('!H', preference) + DNSQuestion.pack_name(exchange)
        elif self.record_type in [RecordType.NS.value, RecordType.CNAME.value]:
            rdata = DNSQuestion.pack_name(self.data)
        else:
            rdata = self.data.encode('ascii')

        return (name_bytes +
                struct.pack('!HHI', self.record_type, self.record_class, self.get_remaining_ttl()) +
                struct.pack('!H', len(rdata)) +
                rdata)