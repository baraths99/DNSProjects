import json
import os
import threading
import time
from dns_record import DNSRecord


class DNSDatabase:
    def __init__(self, db_file=None):
        self.records = {}
        self.db_file = db_file
        self.lock = threading.Lock()

        if db_file and os.path.exists(db_file):
            self.load_from_file()

    def add_record(self, name, record_type, ttl, data):
        """Add a DNS record to the database"""
        record = DNSRecord(name, record_type, 1, ttl, data)

        with self.lock:
            if name not in self.records:
                self.records[name] = []

            updated = False
            for i, existing in enumerate(self.records[name]):
                if existing.record_type == record_type:
                    self.records[name][i] = record
                    updated = True
                    break

            if not updated:
                self.records[name].append(record)

        if self.db_file:
            self.save_to_file()

        return True

    def get_records(self, name, record_type):
        """Get DNS records matching name and type"""
        with self.lock:
            if name in self.records:
                matching_records = []
                valid_records = []

                for record in self.records[name]:
                    if not record.is_expired():
                        valid_records.append(record)
                        if record.record_type == record_type:
                            matching_records.append(record)

                if valid_records:
                    self.records[name] = valid_records
                else:
                    del self.records[name]

                if self.db_file:
                    self.save_to_file()

                return matching_records
        return []

    def save_to_file(self):
        """Save records to JSON file"""
        if not self.db_file:
            return

        serializable_records = {}

        for name, records in self.records.items():
            serializable_records[name] = []
            for record in records:
                if not record.is_expired():
                    serializable_records[name].append({
                        'type': record.record_type,
                        'class': record.record_class,
                        'ttl': record.original_ttl,
                        'creation_time': record.creation_time,
                        'data': record.data
                    })

        try:
            db_dir = os.path.dirname(self.db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            with open(self.db_file, 'w') as f:
                json.dump(serializable_records, f, indent=2)
        except PermissionError:
            print(f"Warning: Permission denied when writing to {self.db_file}")
            print("Records will not be persisted. Try running with sudo or specify a different file location.")
        except Exception as e:
            print(f"Error saving records: {e}")

    def load_from_file(self):
        """Load records from JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)

            for name, records in data.items():
                self.records[name] = []
                for record_data in records:
                    record = DNSRecord(
                        name,
                        record_data['type'],
                        record_data['class'],
                        record_data['ttl'],
                        record_data['data']
                    )
                    if 'creation_time' in record_data:
                        record.creation_time = record_data['creation_time']
                    if not record.is_expired():
                        self.records[name].append(record)
        except (json.JSONDecodeError, FileNotFoundError):
            self.records = {}
        except Exception as e:
            print(f"Error loading records: {e}")
            self.records = {}