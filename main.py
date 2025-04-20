#!/usr/bin/env python3
import argparse
import threading
from dns_server import DNSServer


def interactive_mode(server):
    """Interactive mode for managing DNS records"""
    print("DNS Server Interactive Mode")
    print("Type 'help' for available commands")

    while True:
        try:
            command = input("DNS> ").strip()

            if command.lower() == 'quit' or command.lower() == 'exit':
                break
            elif command.lower() == 'help':
                print("Available commands:")
                print("  add <domain> <type> <ttl> <data>  - Add a DNS record")
                print("  quit/exit                         - Exit interactive mode")
                print("Examples:")
                print("  add example.com A 3600 192.168.1.1")
                print("  add example.com MX 3600 10 mail.example.com")
                print("  add example.com CNAME 3600 www.example.com")
                print("  add example.com NS 3600 ns.example.com")
            elif command.lower().startswith('add '):
                parts = command.split(' ', 4)
                if len(parts) < 5:
                    print("Invalid add command. Use: add <domain> <type> <ttl> <data>")
                else:
                    _, domain, record_type, ttl_str, data = parts
                    try:
                        ttl = int(ttl_str)
                        if server.add_record(domain, record_type, ttl, data):
                            print(f"Record added: {domain} {record_type} {ttl} {data}")
                        else:
                            print("Failed to add record")
                    except ValueError:
                        print("TTL must be a number")
            else:
                print("Unknown command. Type 'help' for available commands")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Exiting interactive mode")


def main():
    parser = argparse.ArgumentParser(description='Simple DNS Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=53, help='Port to bind the server to')
    parser.add_argument('--db', default='dns_records.json', help='Database file path')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')

    args = parser.parse_args()

    server = DNSServer(host=args.host, port=args.port, db_file=args.db)

    if args.interactive:
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()

        try:
            interactive_mode(server)
        finally:
            server.stop()
    else:
        try:
            server.start()
        except KeyboardInterrupt:
            print("Shutting down DNS server...")
            server.stop()


if __name__ == "__main__":
    main()