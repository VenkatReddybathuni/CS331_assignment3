#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.log import setLogLevel
from mininet.cli import CLI

class CustomTopo(Topo):
    def build(self):
        """
        Build the custom network topology with 4 switches and 8 hosts.
        The topology follows a modified ring pattern with an additional diagonal link.
        """
        # Add switches to form the backbone of the network
        s1 = self.addSwitch('s1')  # Switch 1 in top-left position
        s2 = self.addSwitch('s2')  # Switch 2 in top-right position
        s3 = self.addSwitch('s3')  # Switch 3 in bottom-right position
        s4 = self.addSwitch('s4')  # Switch 4 in bottom-left position

        # Add hosts with specific IP addresses in the 10.0.0.0/24 subnet
        h1 = self.addHost('h1', ip='10.0.0.2/24')  # Host 1 connected to Switch 1
        h2 = self.addHost('h2', ip='10.0.0.3/24')  # Host 2 connected to Switch 1
        h3 = self.addHost('h3', ip='10.0.0.4/24')  # Host 3 connected to Switch 2
        h4 = self.addHost('h4', ip='10.0.0.5/24')  # Host 4 connected to Switch 2
        h5 = self.addHost('h5', ip='10.0.0.6/24')  # Host 5 connected to Switch 3
        h6 = self.addHost('h6', ip='10.0.0.7/24')  # Host 6 connected to Switch 3
        h7 = self.addHost('h7', ip='10.0.0.8/24')  # Host 7 connected to Switch 4
        h8 = self.addHost('h8', ip='10.0.0.9/24')  # Host 8 connected to Switch 4

        # Host-to-switch links with 5ms delay
        # These links connect each host to its corresponding switch
        self.addLink(h1, s1, delay='5ms')  # Connect Host 1 to Switch 1
        self.addLink(h2, s1, delay='5ms')  # Connect Host 2 to Switch 1
        self.addLink(h3, s2, delay='5ms')  # Connect Host 3 to Switch 2
        self.addLink(h4, s2, delay='5ms')  # Connect Host 4 to Switch 2
        self.addLink(h5, s3, delay='5ms')  # Connect Host 5 to Switch 3
        self.addLink(h6, s3, delay='5ms')  # Connect Host 6 to Switch 3
        self.addLink(h7, s4, delay='5ms')  # Connect Host 7 to Switch 4
        self.addLink(h8, s4, delay='5ms')  # Connect Host 8 to Switch 4

        # Switch-to-switch links with 7ms delay
        # These links create the backbone network topology
        self.addLink(s1, s2, delay='7ms')  # Connect Switch 1 to Switch 2 (horizontal top)
        self.addLink(s2, s3, delay='7ms')  # Connect Switch 2 to Switch 3 (vertical right)
        self.addLink(s3, s4, delay='7ms')  # Connect Switch 3 to Switch 4 (horizontal bottom)
        self.addLink(s4, s1, delay='7ms')  # Connect Switch 4 to Switch 1 (vertical left)
        self.addLink(s1, s3, delay='7ms')  # Diagonal link connecting Switch 1 to Switch 3


def run_network():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=OVSController, link=TCLink)
    net.start()
    
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run_network()
