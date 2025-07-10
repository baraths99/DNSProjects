# DNS Server

A simple DNS server implementation supporting A, MX, CNAME, and NS record types with TTL functionality.

## Features

- Support for multiple DNS record types:
  - A (IPv4 address)
  - MX (Mail Exchange)
  - CNAME (Canonical Name)
  - NS (Name Server)
- TTL (Time To Live) support for all records
- Persistent storage of DNS records in a JSON file
- Interactive mode for adding and managing records

## Project Structure

The project is organized into the following files:

- `record_types.py`: Defines the DNS record types enum
- `dns_header.py`: Implements the DNS message header structure
- `dns_question.py`: Implements the DNS question section
- `dns_record.py`: Handles record creation and TTL functionality
- `dns_database.py`: Manages record storage with JSON persistence
- `dns_server.py`: Implements the core DNS server functionality
- `main.py`: Entry point for the program with command-line interface

## Requirements

- Python 3.x or higher

## How to Compile and Run

Since this is a Python application, no compilation is necessary. Simply run the main script:

```bash
# Run on a port
python3 main.py --port 5300

# Run in interactive mode
python3 main.py --interactive --port 5300
```




## Command-line Examples

### 1. Interactive Mode

Start the server in interactive mode:

```bash
python3 main.py --interactive --port 5300
```

Add records using the interactive interface:

```
DNS> add example.com A 3600 192.168.1.1
DNS> add example.com MX 3600 10 mail.example.com
DNS> add example.com CNAME 3600 www.example.com
DNS> add example.com NS 3600 ns.example.com
```

### 2. Testing with DNS Client Tools

After starting the server, you can test it with standard DNS tools:

```bash
# Using dig
dig @127.0.0.1 -p 5300 example.com A
dig @127.0.0.1 -p 5300 example.com MX
dig @127.0.0.1 -p 5300 example.com CNAME
dig @127.0.0.1 -p 5300 example.com NS
```

### 3. Testing TTL Functionality

```bash
# Add a record with a short TTL (10 seconds)
DNS> add shortlived.com A 10 192.168.1.10

# Query it immediately
dig @127.0.0.1 -p 5300 shortlived.com A

# Wait 11 seconds and query again - should be expired
sleep 11
dig @127.0.0.1 -p 5300 shortlived.com A
```



