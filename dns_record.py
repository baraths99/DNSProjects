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
        self.original_ttl = ttl
        self.creation_time = time.time()
        self.data = data

    def is_expired(self):
        """Checks if the record has expired based on its TTL"""
        return (time.time() - self.creation_time) >= self.original_ttl

    def get_remaining_ttl(self):
        """Calculates the remaining TTL for the record"""
        elapsed = time.time() - self.creation_time
        remaining = self.original_ttl - elapsed
        return max(0, int(remaining))

    def pack(self):
        """Serializes the record into binary format"""
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

        remaining_ttl = self.get_remaining_ttl()
        if remaining_ttl <= 0:
            return b''

        return (name_bytes +
                struct.pack('!HHI', self.record_type, self.record_class, remaining_ttl) +
                struct.pack('!H', len(rdata)) +
                rdata)