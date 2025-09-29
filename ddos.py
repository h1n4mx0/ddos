#!/usr/bin/env python3
# ddos.py - Comprehensive DDoSPot Testing Tool

import socket
import struct
import time
import threading
import random
import argparse
import json
from datetime import datetime
import sys

class DDoSPotAttacker:
    def __init__(self, target_ip, verbose=False):
        self.target_ip = target_ip
        self.verbose = verbose
        self.stats = {
            'dns': {'sent': 0, 'errors': 0},
            'ntp': {'sent': 0, 'errors': 0},
            'ssdp': {'sent': 0, 'errors': 0},
            'chargen': {'sent': 0, 'errors': 0},
            'generic': {'sent': 0, 'errors': 0}
        }
        self.running = False
        
    def log(self, message):
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] {message}")
    
    def create_dns_query(self, domain="example.com", query_type=1):
        """Create DNS query packet"""
        # DNS Header
        transaction_id = struct.pack('>H', random.randint(1, 65535))
        flags = struct.pack('>H', 0x0100)  # Standard query, recursion desired
        questions = struct.pack('>H', 1)   # 1 question
        answer_rrs = struct.pack('>H', 0)
        authority_rrs = struct.pack('>H', 0)
        additional_rrs = struct.pack('>H', 0)
        
        header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs
        
        # Query section
        query_name = b''
        for part in domain.split('.'):
            query_name += bytes([len(part)]) + part.encode()
        query_name += b'\x00'  # End of name
        
        query_type_bytes = struct.pack('>H', query_type)  # A record
        query_class = struct.pack('>H', 1)  # IN class
        
        return header + query_name + query_type_bytes + query_class
    
    def create_ntp_packet(self, mode=3):
        """Create NTP packet for different modes"""
        if mode == 3:  # Client mode
            # Standard NTP client request
            packet = b'\x1b' + b'\x00' * 47
        elif mode == 6:  # Control mode
            # NTP control packet
            packet = b'\x16\x02\x00\x01' + b'\x00' * 44
        elif mode == 7:  # Private mode (monlist)
            # NTP monlist request
            packet = b'\x17\x00\x03\x2a' + b'\x00' * 44
        else:
            packet = b'\x1b' + b'\x00' * 47
            
        return packet
    
    def create_ssdp_packet(self):
        """Create SSDP M-SEARCH packet"""
        packet = (
            b'M-SEARCH * HTTP/1.1\r\n'
            b'HOST: 239.255.255.250:1900\r\n'
            b'MAN: "ssdp:discover"\r\n'
            b'ST: upnp:rootdevice\r\n'
            b'MX: 3\r\n'
            b'\r\n'
        )
        return packet
    
    def create_chargen_packet(self):
        """Create CHARGEN request packet"""
        return b'CHARGEN_REQUEST\r\n'
    
    def create_generic_packet(self, size=64):
        """Create generic UDP packet"""
        return b'A' * size
    
    def attack_dns(self, port=53, duration=60, rate=10):
        """DNS amplification attack"""
        self.log(f"Starting DNS attack on port {port}")
        
        domains = [
            "google.com", "facebook.com", "youtube.com", "amazon.com",
            "wikipedia.org", "twitter.com", "instagram.com", "linkedin.com",
            "github.com", "stackoverflow.com", "reddit.com", "netflix.com"
        ]
        
        query_types = [1, 2, 5, 15, 16, 28]  # A, NS, CNAME, MX, TXT, AAAA
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                domain = random.choice(domains)
                query_type = random.choice(query_types)
                packet = self.create_dns_query(domain, query_type)
                
                sock.sendto(packet, (self.target_ip, port))
                self.stats['dns']['sent'] += 1
                
                self.log(f"DNS: Sent query for {domain} (type {query_type})")
                sock.close()
                
                time.sleep(1.0 / rate)
                
            except Exception as e:
                self.stats['dns']['errors'] += 1
                self.log(f"DNS Error: {e}")
    
    def attack_ntp(self, port=123, duration=60, rate=5):
        """NTP amplification attack"""
        self.log(f"Starting NTP attack on port {port}")
        
        modes = [3, 6, 7]  # Client, Control, Private
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                mode = random.choice(modes)
                packet = self.create_ntp_packet(mode)
                
                sock.sendto(packet, (self.target_ip, port))
                self.stats['ntp']['sent'] += 1
                
                self.log(f"NTP: Sent mode {mode} packet")
                sock.close()
                
                time.sleep(1.0 / rate)
                
            except Exception as e:
                self.stats['ntp']['errors'] += 1
                self.log(f"NTP Error: {e}")
    
    def attack_ssdp(self, port=1900, duration=60, rate=3):
        """SSDP amplification attack"""
        self.log(f"Starting SSDP attack on port {port}")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                packet = self.create_ssdp_packet()
                sock.sendto(packet, (self.target_ip, port))
                self.stats['ssdp']['sent'] += 1
                
                self.log("SSDP: Sent M-SEARCH packet")
                sock.close()
                
                time.sleep(1.0 / rate)
                
            except Exception as e:
                self.stats['ssdp']['errors'] += 1
                self.log(f"SSDP Error: {e}")
    
    def attack_chargen(self, port=19, duration=60, rate=2):
        """CHARGEN amplification attack"""
        self.log(f"Starting CHARGEN attack on port {port}")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                packet = self.create_chargen_packet()
                sock.sendto(packet, (self.target_ip, port))
                self.stats['chargen']['sent'] += 1
                
                self.log("CHARGEN: Sent request packet")
                sock.close()
                
                time.sleep(1.0 / rate)
                
            except Exception as e:
                self.stats['chargen']['errors'] += 1
                self.log(f"CHARGEN Error: {e}")
    
    def attack_generic(self, port=1234, duration=60, rate=5):
        """Generic UDP attack"""
        self.log(f"Starting Generic UDP attack on port {port}")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                size = random.randint(32, 512)
                packet = self.create_generic_packet(size)
                sock.sendto(packet, (self.target_ip, port))
                self.stats['generic']['sent'] += 1
                
                self.log(f"Generic: Sent {size} bytes packet")
                sock.close()
                
                time.sleep(1.0 / rate)
                
            except Exception as e:
                self.stats['generic']['errors'] += 1
                self.log(f"Generic Error: {e}")
    
    def run_single_attack(self, protocol, **kwargs):
        """Run single protocol attack"""
        self.running = True
        
        if protocol == 'dns':
            self.attack_dns(**kwargs)
        elif protocol == 'ntp':
            self.attack_ntp(**kwargs)
        elif protocol == 'ssdp':
            self.attack_ssdp(**kwargs)
        elif protocol == 'chargen':
            self.attack_chargen(**kwargs)
        elif protocol == 'generic':
            self.attack_generic(**kwargs)
    
    def run_multi_attack(self, protocols=['dns', 'ntp', 'ssdp'], duration=60):
        """Run multiple protocol attacks simultaneously"""
        self.running = True
        threads = []
        
        print(f"🚀 Starting multi-protocol attack on {self.target_ip}")
        print(f"Protocols: {', '.join(protocols)}")
        print(f"Duration: {duration}s")
        print("-" * 60)
        
        # Attack configurations
        configs = {
            'dns': {'port': 53, 'rate': 10},
            'ntp': {'port': 123, 'rate': 5},
            'ssdp': {'port': 1900, 'rate': 3},
            'chargen': {'port': 19, 'rate': 2},
            'generic': {'port': 1234, 'rate': 5}
        }
        
        # Start attack threads
        for protocol in protocols:
            if protocol in configs:
                config = configs[protocol]
                config['duration'] = duration
                
                thread = threading.Thread(
                    target=self.run_single_attack,
                    args=(protocol,),
                    kwargs=config
                )
                threads.append(thread)
                thread.start()
        
        # Monitor progress
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                remaining = duration - elapsed
                
                # Calculate totals
                total_sent = sum(self.stats[p]['sent'] for p in protocols)
                total_errors = sum(self.stats[p]['errors'] for p in protocols)
                rate = total_sent / elapsed if elapsed > 0 else 0
                
                # Progress display
                progress = f"📊 Sent: {total_sent} | Errors: {total_errors} | "
                progress += f"Rate: {rate:.1f}pps | Remaining: {remaining:.1f}s"
                
                print(f"\r{progress}", end='', flush=True)
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⚠ Attack interrupted by user")
            self.running = False
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Final statistics
        print(f"\n🏁 Attack completed!")
        print("\n📈 Final Statistics:")
        print("-" * 40)
        
        for protocol in protocols:
            sent = self.stats[protocol]['sent']
            errors = self.stats[protocol]['errors']
            success_rate = (sent / (sent + errors) * 100) if (sent + errors) > 0 else 0
            print(f"{protocol.upper():>8}: {sent:>6} sent, {errors:>4} errors ({success_rate:.1f}% success)")
        
        total_sent = sum(self.stats[p]['sent'] for p in protocols)
        total_errors = sum(self.stats[p]['errors'] for p in protocols)
        avg_rate = total_sent / duration
        
        print("-" * 40)
        print(f"{'TOTAL':>8}: {total_sent:>6} sent, {total_errors:>4} errors")
        print(f"Average rate: {avg_rate:.1f} packets/second")

def main():
    parser = argparse.ArgumentParser(description='DDoSPot Attack Testing Tool')
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-p', '--protocol', choices=['dns', 'ntp', 'ssdp', 'chargen', 'generic', 'all'],
                       default='all', help='Protocol to attack (default: all)')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Attack duration in seconds (default: 60)')
    parser.add_argument('-r', '--rate', type=int, default=10,
                       help='Attack rate per second (default: 10)')
    parser.add_argument('--port', type=int, help='Custom port (for single protocol)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    attacker = DDoSPotAttacker(args.target, args.verbose)
    
    if args.protocol == 'all':
        attacker.run_multi_attack(['dns', 'ntp', 'ssdp', 'chargen'], args.duration)
    else:
        kwargs = {'duration': args.duration, 'rate': args.rate}
        if args.port:
            kwargs['port'] = args.port
        attacker.run_single_attack(args.protocol, **kwargs)

if __name__ == "__main__":
    main()
