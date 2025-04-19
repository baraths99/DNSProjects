import struct


class DNSQuestion:
    def __init__(self, qname, qtype, qclass=1):
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass

    def pack(self):
        packed_qname = self.pack_name(self.qname)
        return packed_qname + struct.pack('!HH', self.qtype, self.qclass)

    @staticmethod
    def pack_name(name):
        result = b''
        for part in name.split('.'):
            if part:
                result += bytes([len(part)]) + part.encode('ascii')
        result += b'\x00'
        return result