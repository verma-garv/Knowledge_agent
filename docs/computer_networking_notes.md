# Computer Networking: Study Notes

These notes cover the basics of how computers talk to each other, from cables and addresses up to web requests. They are written for beginners who want a working mental model.

## 1. What is a computer network
- A computer network is a group of devices connected so they can share data and resources.
- Each device on a network is called a node. Examples are computers, phones, printers, servers and routers.
- Data travels in small pieces called packets. Each packet carries a header with addressing information and a payload with the actual data.
- Rules for how devices communicate are called protocols. Two devices can talk only if they follow the same protocols.

## 2. Network types and topologies
- A PAN (personal area network) covers a few metres, such as a phone connected to earbuds.
- A LAN (local area network) covers a building or home, such as an office network.
- A MAN (metropolitan area network) covers a city.
- A WAN (wide area network) covers large distances. The internet is the largest WAN.
- A topology is the layout of a network. Common ones are star, bus, ring, and mesh.
- In a star topology every device connects to a central switch. Most modern LANs use it, because one broken cable affects only one device.
- In a mesh topology devices connect to many others, which gives several paths between nodes and makes the network resilient but costly.

## 3. The OSI model and the TCP/IP model
- The OSI model describes networking in seven layers. Each layer has one job and talks only to the layers next to it.

| Layer | Name | Job |
|---|---|---|
| 7 | Application | Services used by programs, such as HTTP and DNS |
| 6 | Presentation | Formatting, encryption and compression |
| 5 | Session | Opening, managing and closing conversations |
| 4 | Transport | Reliable or fast delivery between programs, using TCP or UDP |
| 3 | Network | Addressing and routing between networks, using IP |
| 2 | Data link | Delivery between devices on the same network, using MAC addresses |
| 1 | Physical | Cables, radio signals and electrical pulses |

- The TCP/IP model used on the real internet has four layers: application, transport, internet, and link.
- A handy memory aid for the OSI layers from the top is "All People Seem To Need Data Processing".
- Sending data moves down the layers, with each layer adding its own header. Receiving data moves back up, with each layer removing its header.

## 4. IP addressing
- An IP address identifies a device on a network. IPv4 addresses are 32 bits long, written as four numbers, for example 192.168.1.10.
- IPv4 allows about 4.3 billion addresses, which ran short. IPv6 uses 128 bits and has a practically unlimited supply.
- Private IPv4 ranges are used inside homes and offices and are not routable on the internet: 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16.
- A subnet mask, or CIDR prefix, splits an address into a network part and a host part. A /24 network has 256 addresses, of which 254 can be given to hosts.
- DHCP assigns IP addresses to devices automatically when they join a network.
- NAT lets many devices with private addresses share one public IP address when they reach the internet.
- A MAC address is a 48-bit hardware address burned into a network card. It is used for delivery within one local network.
- ARP finds the MAC address that belongs to an IP address on the local network.

## 5. TCP and UDP
- TCP is connection-oriented. It guarantees that data arrives complete and in order, by numbering packets and resending lost ones.
- UDP is connectionless. It sends packets with no guarantee of delivery or order, and it has lower overhead and delay.
- Use TCP when correctness matters, such as web pages, email and file transfers. Use UDP when speed matters more than perfect delivery, such as video calls, games, and DNS queries.
- TCP opens a connection with a three-way handshake: the client sends SYN, the server replies SYN-ACK, and the client answers ACK.
- A port number identifies a program on a device. Ports run from 0 to 65535.

| Service | Port |
|---|---|
| HTTP | 80 |
| HTTPS | 443 |
| SSH | 22 |
| DNS | 53 |
| SMTP | 25 |
| FTP | 21 |

## 6. DNS
- DNS, the Domain Name System, translates names like example.com into IP addresses.
- A lookup starts at a recursive resolver, usually run by your internet provider. The resolver asks a root server, then a top-level domain server such as the one for .com, then the authoritative server for the domain.
- Answers are cached for a time set by the record's TTL, which saves repeated lookups.
- Common record types: A maps a name to an IPv4 address, AAAA maps it to an IPv6 address, CNAME makes one name an alias of another, and MX points to mail servers.
- If DNS fails, you can still reach a site by its IP address, which is a quick way to tell a DNS problem from a connection problem.

## 7. HTTP and HTTPS
- HTTP is the protocol of the web. A client sends a request, and a server sends back a response.
- Common methods are GET to read, POST to create, PUT to replace or update, and DELETE to remove.
- HTTP is stateless. Each request stands alone, and the server does not remember earlier ones unless cookies or tokens are used.
- HTTPS is HTTP carried inside TLS, which encrypts the traffic and proves the server's identity with a certificate.
- Status codes tell the client what happened. The first digit gives the class: 2xx success, 3xx redirect, 4xx client error, and 5xx server error.

| Code | Meaning |
|---|---|
| 200 | OK, the request succeeded |
| 301 | Moved permanently |
| 404 | Not found |
| 429 | Too many requests, the client has hit a rate limit |
| 500 | Internal server error |
| 503 | Service unavailable, often because a dependency is down |

- A health check endpoint is a URL that load balancers call to decide whether a server is working. It returns 200 when healthy and 503 when not.

## 8. Switching and routing
- A switch connects devices inside one LAN. It works at layer 2 and forwards frames using MAC addresses.
- A router connects different networks. It works at layer 3 and forwards packets using IP addresses.
- A router keeps a routing table. For each destination network it records the next hop, which is the next router to hand the packet to.
- The default gateway is the router a device uses for any destination outside its own network.
- Static routes are set by hand. Dynamic routing protocols let routers learn routes from each other.
- OSPF is a dynamic protocol used inside one organisation's network. BGP is the protocol that exchanges routes between the large networks, called autonomous systems, that make up the internet.
- A hub is an older device that repeats every signal to all ports, so it is slower and less secure than a switch.

## 9. Other network devices
- A firewall filters traffic using rules about addresses, ports and protocols.
- A load balancer spreads incoming requests across several servers, so no single server is overwhelmed.
- A wireless access point connects Wi-Fi devices to a wired network. Wi-Fi follows the IEEE 802.11 standards, and wired Ethernet follows IEEE 802.3.
- A modem converts signals between your provider's line and your local network.

## 10. Measuring performance
- Bandwidth is the maximum amount of data a link can carry per second.
- Throughput is the amount of data that actually gets through, which is usually lower than the bandwidth.
- Latency is the time a packet takes to travel from sender to receiver. Round-trip time is the time to go there and back.
- Jitter is the variation in latency. High jitter hurts video calls and games.
- Packet loss is the share of packets that never arrive. TCP hides it by resending, at the cost of delay.
- The ping command measures round-trip time, and traceroute lists each hop along the path.

## 11. Reliability: timeouts and retries
- Networks fail in small ways all the time, so programs set a timeout, a limit on how long to wait for a reply.
- When a request fails, a program can retry it. Retrying immediately and repeatedly can overload a struggling server.
- Exponential backoff waits longer after each failure, for example 1, 2, 4 and then 8 seconds, often with random jitter added.
- A retry is safe only if repeating the request does no harm. GET and PUT are designed to be safe to repeat. POST is not, unless the server detects duplicates.
- A server that returns 429 is asking the client to slow down. Respect it and wait before retrying.

## 12. Security basics
- Encryption with TLS protects data from being read while it travels.
- A VPN creates an encrypted tunnel across an untrusted network, so traffic looks like it comes from the VPN's endpoint.
- A firewall blocks traffic that no rule allows. A good default is to deny everything and allow only what is needed.
- A man-in-the-middle attack secretly sits between two parties to read or change their traffic. Valid certificates make it much harder.
- A DDoS attack floods a service with traffic from many sources until real users cannot get through.
- Never trust data just because it arrived over the network. Check and validate what a remote system sends you.

## 13. Troubleshooting checklist
1. Check the physical connection: the cable, the Wi-Fi signal, and whether the device shows as connected.
2. Check your IP configuration with ipconfig on Windows or ip addr on Linux. An address starting 169.254 means DHCP failed.
3. Ping your default gateway. If this fails, the problem is inside your local network.
4. Ping a public IP address such as 8.8.8.8. If this works but websites do not load, suspect DNS.
5. Ping a domain name. If the IP ping works and the name ping fails, DNS is the problem.
6. Run traceroute (tracert on Windows) to see where along the path packets stop.
7. Check firewall rules and the status of the service you are trying to reach.

## 14. Glossary

| Term | Meaning |
|---|---|
| Packet | A small unit of data sent across a network |
| Protocol | An agreed set of rules for communication |
| Router | A device that forwards packets between networks |
| Switch | A device that forwards frames inside one network |
| Port | A number that identifies a program on a device |
| DNS | The system that turns names into IP addresses |
| TTL | How long a DNS answer may be cached |
| Latency | The delay between sending and receiving |
| Subnet | A smaller network carved out of a larger address range |
| Gateway | The router that leads out of a local network |
