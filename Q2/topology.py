#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

class CustomTopo(Topo):
    def build(self):
        """
        Network topology with public (10.0.0.0/24) and private (10.1.1.0/24) segments.
        Features a ring topology with redundant diagonal link between switches.
        Uses NAT gateway (h9) to connect private hosts to public network.
        """
        # Create switches with STP enabled for loop prevention
        s1 = self.addSwitch('s1', stp=True)  # Core switch connected to NAT
        s2 = self.addSwitch('s2', stp=True)  # Edge switch for public hosts
        s3 = self.addSwitch('s3', stp=True)  # Edge switch for public hosts
        s4 = self.addSwitch('s4', stp=True)  # Edge switch for public hosts
        s5 = self.addSwitch('s5')            # Private network switch

        # Public network hosts
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        
        # NAT gateway and private hosts (IPs configured later)
        natGW = self.addHost('h9', ip=None)
        h1 = self.addHost('h1', ip=None)
        h2 = self.addHost('h2', ip=None)

        # Connect public hosts to edge switches
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

        # Connect NAT gateway to both networks
        self.addLink(natGW, s1, cls=TCLink, delay='5ms', intfName1='h9-eth0')  # Public interface
        self.addLink(natGW, s5, cls=TCLink, delay='1ms', intfName1='h9-eth1')  # Private interface

        # Connect private hosts to private switch
        self.addLink(h1, s5, cls=TCLink, delay='1ms') 
        self.addLink(h2, s5, cls=TCLink, delay='1ms') 

        # Create backbone network with redundancy
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')  # Diagonal redundant link


def configure_nat(net):
    """
    Configure NAT gateway and private hosts.
    Sets up IP addressing, routing and firewall rules.
    """
    h1 = net.get('h1')
    h2 = net.get('h2')
    h9 = net.get('h9') 

    # Configure private hosts
    print("* Setting up private hosts...")
    h1.cmd("ifconfig h1-eth0 10.1.1.2/24 up")
    h1.cmd("ip route add default via 10.1.1.1")
    
    h2.cmd("ifconfig h2-eth0 10.1.1.3/24 up")
    h2.cmd("ip route add default via 10.1.1.1")

    # Configure NAT gateway interfaces
    print("* Setting up NAT gateway...")
    # Public interface with multiple IPs
    h9.cmd("ifconfig h9-eth0 10.0.0.1/24 up")
    h9.cmd("ip addr add 172.16.10.10/24 dev h9-eth0")  # Main NAT public IP
    h9.cmd("ip addr add 172.16.10.11/24 dev h9-eth0")  # For h1 port forwarding
    h9.cmd("ip addr add 172.16.10.12/24 dev h9-eth0")  # For h2 port forwarding
    
    # Private interface
    h9.cmd("ifconfig h9-eth1 10.1.1.1/24 up")

    # Enable packet forwarding
    h9.cmd("sysctl -w net.ipv4.ip_forward=1")

    # Setup NAT and firewall rules
    print("* Configuring firewall rules...")
    h9.cmd("iptables -F")
    h9.cmd("iptables -t nat -F")
    h9.cmd("iptables -X")
    h9.cmd("iptables -t nat -X")

    # Outbound NAT (masquerading)
    h9.cmd("iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth0 -j MASQUERADE")

    # Port forwarding for incoming connections
    # ICMP forwarding
    h9.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.11 -p icmp -j DNAT --to-destination 10.1.1.2")
    h9.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.12 -p icmp -j DNAT --to-destination 10.1.1.3")
    
    # TCP port forwarding for services
    h9.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.11 -p tcp --dport 5201 -j DNAT --to-destination 10.1.1.2:5201")
    h9.cmd("iptables -t nat -A PREROUTING -i h9-eth0 -d 172.16.10.12 -p tcp --dport 5201 -j DNAT --to-destination 10.1.1.3:5201")

    # Firewall rules to allow traffic flow
    # Allow outbound connections
    h9.cmd("iptables -A FORWARD -i h9-eth1 -o h9-eth0 -s 10.1.1.0/24 -j ACCEPT")
    
    # Allow established connections
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT")
    
    # Allow specific inbound services
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p icmp -d 10.1.1.2 -j ACCEPT")
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p icmp -d 10.1.1.3 -j ACCEPT")
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p tcp -d 10.1.1.2 --dport 5201 -j ACCEPT")
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o h9-eth1 -p tcp -d 10.1.1.3 --dport 5201 -j ACCEPT")

    # Configure public hosts routing
    print("* Setting up public hosts routing...")
    for h_name in ['h3', 'h4', 'h5', 'h6', 'h7', 'h8']:
        h = net.get(h_name)
        h.cmd("ip route add default via 10.0.0.1")
        h.cmd("ip route add 172.16.10.0/24 via 10.0.0.1")


def run():
    """
    Create and run the network topology.
    """
    # Create topology and network
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSBridge, controller=None)

    # Start network and configure NAT
    print("* Starting network...")
    net.start()
    configure_nat(net)

    # Wait for STP convergence
    print("* Waiting for network convergence...")
    time.sleep(15)
    print("* Network ready")

    # Start CLI
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()