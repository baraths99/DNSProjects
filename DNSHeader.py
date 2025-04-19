import struct


class DNSHeader:
    def __init__(self, id=0, flags=0, qdcount=0, ancount=0, nscount=0, arcount=0):
        self.id = id
        self.flags = flags
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount

    def pack(self):
        return struct.pack('!HHHHHH', self.id, self.flags, self.qdcount,
                           self.ancount, self.nscount, self.arcount)

    @classmethod
    def unpack(cls, data):
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', data[:12])
        return cls(id, flags, qdcount, ancount, nscount, arcount)