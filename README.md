# CS331_assignment3
## Q1: Network Loops

### Instructions for Running the Code
1. Navigate to the question directory
2. Run the topology script with:
   ```bash
   sudo python3 topology.py
   ```
3. Execute the test commands in the Mininet CLI as described below

### Ping Tests and Observations
After launching the topology with:

```bash
sudo python3 topology.py
```

Execute the following commands in the Mininet CLI:

```bash
h3 ping -c 3 h1
h5 ping -c 3 h7
h8 ping -c 3 h2
```


### Resolution Strategy
Enable the Spanning Tree Protocol (STP) on all switches to prevent broadcast loops while maintaining full connectivity.

Commands (from Mininet CLI):

```bash
sh ovs-vsctl set bridge s1 stp_enable=true
sh ovs-vsctl set bridge s2 stp_enable=true
sh ovs-vsctl set bridge s3 stp_enable=true
sh ovs-vsctl set bridge s4 stp_enable=true
```


### Ping Results After STP
Reran the same ping commands:

```bash
h3 ping -c 3 h1
h5 ping -c 3 h7
h8 ping -c 3 h2
```
Wait ~30 seconds for each case while running 3 times

## Q2: Network Address Translation (NAT)

### Instructions for Running the Code
1. Navigate to the question directory:
2. Run the topology script with:
   ```bash
   sudo python topology.py
   ```
   This will create a network with public (10.0.0.0/24) and private (10.1.1.0/24) segments 
   connected through a NAT gateway.

### Manual Testing in Mininet CLI
After launching the topology with `sudo python b_topology.py`, you can run these tests manually:

#### A. Test internal to external communication:
```bash
h1 ping -c 4 10.0.0.6    # Ping from h1 to h5
h2 ping -c 4 10.0.0.4    # Ping from h2 to h3
```

#### B. Test external to internal communication:
```bash
h8 ping -c 4 172.16.10.11  # Ping from h8 to h1 (via NAT)
h6 ping -c 4 172.16.10.12  # Ping from h6 to h2 (via NAT)
```

#### C. Run iperf3 tests:
```bash
# Test C-i: h1 server, h6 client
h1 iperf3 -s &
h6 iperf3 -c 172.16.10.11 -t 120

# Test C-ii: h8 server, h2 client
h8 iperf3 -s &
h2 iperf3 -c 10.0.0.9 -t 120
```

#### View NAT rules and connection tracking:
```bash
# View NAT PREROUTING rules
h9 iptables -t nat -L PREROUTING -v -n

# View NAT POSTROUTING rules
h9 iptables -t nat -L POSTROUTING -v -n
```

## Q3: Network Routing

### Instructions for Running the Code
1. Navigate to the question directory

2. Run the simulation:
   ```bash
   ./distance_vector
   ```

3. When prompted for TRACE value, choose one of the following:
   - Enter 0: Minimal output (final results only)
   - Enter 1: Standard output (shows major events)
   - Enter 2: Detailed output (shows all packet exchanges and table updates)

### Trace Details
Different trace levels provide different amounts of information:

- **TRACE=0**: Shows only the final converged state of the network
- **TRACE=1**: Shows initialization of each node and updates when link costs change
- **TRACE=2**: Shows detailed packet contents for every exchange between nodes

The simulation includes a dynamic link cost change between nodes 0 and 1:
- At time 10000: Cost changes from 1 to 20
- At time 20000: Cost changes back from 20 to 1

You can observe how the network adapts to these changes in real-time.
