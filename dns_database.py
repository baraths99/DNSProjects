#!/usr/bin/env python3
import json
import os
import threading
from dns_record import DNSRecord


class DNSDatabase:
    def __init__(self, db_file=None):
        self.records = {}
        self.db_file = db_file
        self.lock = threading.Lock()

        if db_file:
            db_dir = os.path.dirname(db_file)
            if db_dir and not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except PermissionError:
                    print(f"Warning: Cannot create directory for {db_file}. Will not persist records.")
                    self.db_file = None

        if db_file and os.path.exists(db_file):
            self.load_from_file()

    def add_record(self, name, record_type, ttl, data):
        """Add a DNS record to the database"""
        record = DNSRecord(name, record_type, 1, ttl, data)  # Class 1 = IN (Internet)

        with self.lock:
            if name not in self.records:
                self.records[name] = []

            # Check if we're updating an existing record
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
                # Return only non-expired records of matching type
                matching_records = [r for r in self.records[name]
                                    if r.record_type == record_type and not r.is_expired()]

                # Clean up expired records
                self.records[name] = [r for r in self.records[name] if not r.is_expired()]
                if not self.records[name]:
                    del self.records[name]

                return matching_records
        return []

    def save_to_file(self):
        """Save records to JSON file"""
        serializable_records = {}

        for name, records in self.records.items():
            serializable_records[name] = []
            for record in records:
                # Don't save expired records
                if not record.is_expired():
                    serializable_records[name].append({
                        'type': record.record_type,
                        'class': record.record_class,
                        'ttl': record.get_remaining_ttl(),
                        'data': record.data
                    })

        with open(self.db_file, 'w') as f:
            json.dump(serializable_records, f, indent=2)

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
                    # Only add non-expired records
                    if not record.is_expired():
                        self.records[name].append(record)
        except (json.JSONDecodeError, FileNotFoundError):
            # Create empty database if file doesn't exist or is invalid
            self.records = {}