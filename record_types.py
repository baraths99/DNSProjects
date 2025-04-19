from enum import Enum


class RecordType(Enum):
    A = 1      # IPv4 Address
    NS = 2     # Name Server
    CNAME = 5  # Canonical Name
    MX = 15    # Mail Exchange