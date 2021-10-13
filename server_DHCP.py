from socket import *
import ipaddress
import datetime
from re import *
import struct

""" ----- SERVER SETTINGS ----- """
server_host = ''
server_port = 67
socket = socket(AF_INET, SOCK_DGRAM)
socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
socket.bind((server_host, server_port))
dest = ('<broadcast>', 68)


""" ----- TESTING ADDRESSES INPUTS ----- """
def testing_network_format(add):
    """Testing the format of the network. It needs this format : X.X.X.X/X
     if it's not, there is a new input to let the user correct himself

     Parameter : add = str, it comes from an input
     Return : add = str, if it has the good format
     """
    b = False
    while (b == False):
        m = match('([\d]*)\.([\d]*)\.([\d]*)\.([\d]*)\/([\d]*)$', add)
        if (m == None):
            add = input('Enter a valid network of this form X.X.X.X/X : ')
        else:
            b = True
    return add
def testing_add_format(add):
    """Testing the format of the address. It needs this format : X.X.X.X
     if it's not, there is a new input to let the user correct himself

     Parameter : add = str, it comes from an input
     Return : add = str, if it has the good format
     """
    b = False
    while (b == False):
        m = match('([\d]*)\.([\d]*)\.([\d]*)\.([\d]*)$', add)
        if (m == None):
            add = input('Enter a valid address of this form X.X.X.X : ')
        else:
            b = True
    return add
def testing_errors(add):
    """Testing the IPv4 format of the network/address.
     if it's not an IPv6 format it raises an exception

     Parameter : add = str, it comes from an input
     Return : -1, if it's not an IPv4 format
     """
    try:
        add = ipaddress.IPv4Network(add)
    except ValueError:
        print('address/netmask is invalid for IPv4:', add)
        exit(-1)

""" ----- ADDRESSES INPUTS ----- """
network = input('Enter a network of this form X.X.X.X/X : ')
network = testing_network_format(network)
testing_errors(network)
network = ipaddress.IPv4Network(network)

gateway = input('Enter a gateway address of this form X.X.X.X : ')
gateway = testing_add_format(gateway)
testing_errors(gateway)
gateway = ipaddress.ip_address(gateway)
"""Testing if the gateway address is in the range of hosts of the network"""
if gateway not in network.hosts():
    print('The gateway is not in the range of the network')
    exit(-1)

dns_prim = input('Enter a primary DNS server address of this form X.X.X.X : ')
dns_prim = testing_add_format(dns_prim)
testing_errors(dns_prim)

dns_second = input('Enter a secondary DNS server address of this form X.X.X.X : ')
dns_second = testing_add_format(dns_second)
testing_errors(dns_second)

bail = input('Enter a lease time in seconds : ')
"""Testing if the input of the lease time is an integer"""
try :
    bail = int(bail)
except ValueError:
    print("Lease time is not an integer")
    exit(-1)

available_add = []
add_currently_used = {}
add_mac_mem = {}

print("Please wait a minute")

"""Implementing the available addresses in the list available_add"""
gateway = str(gateway)
for ip in network.hosts():
    ip = str(ip)
    if(ip != gateway) and (ip != dns_prim) and (ip != dns_second):
        available_add.append(ip)

dhcp_server = available_add[0]
del available_add[0]

""" ----- ADDRESSES AND LEASE TIME MANAGEMENT FUNCTIONS ----- """
def lease_time(bail):
    """Function that creates the lease time date

     Parameter : bail = int
     Return : data+delta = datetime.datetime
     """
    date = datetime.datetime.now()
    delta = datetime.timedelta(seconds=bail)
    return date+delta
def update_time(add_currently_used, available_add, add_mac_mem):
    """Function that updates addresses currently in use and the list of available addresses depending on the lease time.
    The function also verifies if the memory of couples MAC/IP is update

     Parameters : add_currently_used = dict
                  available_add = list
                  add_mac_mem = dict
     Return : nothing
     """
    date = datetime.datetime.now()
    list_pop = []
    for keys in add_currently_used:
        if add_currently_used[keys][1] < date:
            if keys not in add_mac_mem:
                add_mac_mem[keys] = add_currently_used[keys][0]
            available_add.append(add_currently_used[keys][0])
            list_pop.append(keys)
    for k in list_pop:
        del add_currently_used[k]
def offer_ip_selection(mac, add_currently_used, add_mac_mem, available_add, bail) :
    """The function selects an IP address depending on the MAC address

     Parameters : mac = bytes
                  add_currently_used = dict
                  add_mac_mem = dict
                  available_add = list
                  bail = int
     Return : his_ip = str
     """
    update_time(add_currently_used, available_add, add_mac_mem)
    release = lease_time(bail)
    if mac not in add_currently_used and mac not in add_mac_mem:
        his_ip = available_add[0]
        del(available_add[0])
        add_currently_used[mac] = [his_ip, release]
        add_mac_mem[mac] = his_ip
    else:
        if mac in add_currently_used:
            his_ip = add_currently_used[mac][0]
            if his_ip in available_add:
                available_add.remove(his_ip)
            if mac not in add_mac_mem:
                add_mac_mem[mac] = his_ip
            add_currently_used[mac] = [his_ip, release]
        if mac in add_mac_mem and mac not in add_currently_used:
            his_ip = add_mac_mem[mac]
            if add_mac_mem[mac] in available_add:
                available_add.remove(his_ip)
                add_currently_used[mac] = [his_ip, release]
            else:
                his_ip = available_add[0]
                del (available_add[0])
                add_currently_used[mac] = [his_ip, release]
                add_mac_mem[mac] = his_ip
    return his_ip

""" ----- FUNCTIONS FOR MANAGING THE DATA RECEIVED ----- """
def search_message_type(options):
    """Function that searches for the type of the message (Discover or Request)
    Function also find the MAC address, the transaction id, and the IP input by the client

     Parameter : options = bytes
     Returns : mac = bytes
               transaction_id = bytes
               my_ip_client = bytes
               message_type = int
     """
    transaction_id = options[4:8]
    my_ip_client = options[12:16]
    mac = options[28:34]
    for i in range(len(options)):
        if options[i] == 53:
            if options[i+1] == 1:
                message_type = options[i+2]
                break
    return mac, transaction_id, my_ip_client, message_type
def request_requested_ip(options):
    """Function that searches for the requested ip the client needs on the request message

     Parameter : options = bytes
     Returns : requested_IP = bytes
     """
    i = 0
    requested_IP = 0x00
    while i < (len(options)):
        if (options[i] == 61) or (options[i] == 55) or (options[i] == 57) or (options[i] == 60) or (options[i] == 12) or (options[i] == 54):
            jump = options[i + 1]
            i = i + 2 + jump
            continue
        if options[i] == 255:
            break
        if options[i] == 50:
            if options[i+1] == 4:
                requested_IP = options[i+2:i+6]
                i = i + 5
        i += 1
    return requested_IP

""" ----- FUNCTIONS THAT MANAGES THE DATA TO BE SENT ----- """
def add_ip_in_hexa(ip):
    """Function that converts the IP address to bytes

     Parameter : ip = str
     Return : L1+L2+L3+L4 = bytes
     """
    m = match('(\d*)\.(\d*)\.(\d*)\.(\d*)', ip)
    if(m!=None):
        L1 = int(m.group(1)).to_bytes(1, byteorder='big')
        L2 = int(m.group(2)).to_bytes(1, byteorder='big')
        L3 = int(m.group(3)).to_bytes(1, byteorder='big')
        L4 = int(m.group(4)).to_bytes(1, byteorder='big')
        return L1+L2+L3+L4
def server_message(ip, ip_renew, transaction_id, mac_add, network, gateway, dns, dhcp, bail, msg_type):
    """Function that creates the message to send

     Parameters : ip = str
                  ip_renew = bytes
                  transaction_id = bytes
                  mac_add = bytes
                  network = ipaddress.IPv4Network
                  gateway = str
                  dns= str
                  dhcp = str
                  bail = int
                  msg_type = int
     Return : package = bytes
     """
    if(msg_type == 3):
        DHCPOptions53 = bytes([53, 1, 5])  # DHCP ACK
    if(msg_type == 1):
        DHCPOptions53 = bytes([53, 1, 2])  # DHCP Offer
    ip = add_ip_in_hexa(ip)
    ipnet = add_ip_in_hexa(str(network.netmask))
    ipgat = add_ip_in_hexa(gateway)
    ipdns = add_ip_in_hexa(dns)
    ipbroad = add_ip_in_hexa(str(network.broadcast_address))
    ipdhcp = add_ip_in_hexa(dhcp)
    bail = (bail).to_bytes(4, byteorder="big")
    OP = bytes([0x02])
    HTYPE = bytes([0x01])
    HLEN = bytes([0x06])
    HOPS = bytes([0x00])
    XID = transaction_id
    SECS = bytes([0x00, 0x00])
    FLAGS = bytes([0x00, 0x00])
    CIADDR = ip_renew
    YIADDR = ip
    SIADDR = bytes([0x00, 0x00, 0x00, 0x00])
    GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
    CHADDR1 = mac_add
    CHADDR2 = bytes([0x00, 0x00, 0x00, 0x00])
    CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
    CHADDR4 = bytes([0x00, 0x00])
    CHADDR5 = bytes(192)
    Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
    DHCPOptions1 = bytes([1, 4])+ipnet
    DHCPOptions3 = bytes([3, 4])+ipgat
    DHCPOptions6 = bytes([6, 4])+ipdns
    DHCPOptions28 = bytes([28, 4])+ipbroad
    DHCPOptions51 = bytes([51, 4])+bail
    DHCPOptions54 = bytes([54, 4])+ipdhcp
    DHCPOptions255 = bytes([255])

    package = OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 + CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions53 + DHCPOptions1 + DHCPOptions3 + DHCPOptions6 + DHCPOptions28 + DHCPOptions51 + DHCPOptions54 + DHCPOptions255

    return package

""" ----- FUNCTIONS FOR THE SERVER ----- """
def handle_client(data):
    """Function that handle messages from the client and respond to them properly

     Parameters : data = bytes, from the client
     Return : nothing
     """
    mac, transaction_id, ip_renew, msg = search_message_type(data)
    mac_int = ':'.join(map(lambda x: hex(x)[2:].zfill(2), struct.unpack('BBBBBB', mac))).upper() #Transform the MAC address in the good format

    if msg == 1:
        print("Discovery message received")
        File = open('logging.txt', "a")
        File.write(str(datetime.datetime.now()) + "  Discover message received  MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + '\n')
        File.close()

        update_time(add_currently_used, available_add, add_mac_mem)
        ip = offer_ip_selection(mac, add_currently_used, add_mac_mem, available_add, bail)
        offer = server_message(ip, ip_renew, transaction_id, mac, network, gateway, dns_prim, dhcp_server, bail, msg)
        socket.sendto(offer, dest)
        File = open('logging.txt', "a")
        File.write(str(datetime.datetime.now()) + "  Offer message send         MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + " IP: " + ip + '\n')
        File.close()
        print("Message offer send\n")

    if msg == 3:
        requested_IP = request_requested_ip(data)
        print("Requested message received")
        update_time(add_currently_used, available_add, add_mac_mem)
        ip = offer_ip_selection(mac, add_currently_used, add_mac_mem, available_add, bail)

        if (add_ip_in_hexa(ip) == requested_IP or add_ip_in_hexa(ip) == ip_renew):
            File = open('logging.txt', "a")
            File.write(str(datetime.datetime.now()) + "  Request message received   MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + " IP: " + ip + '\n')
            File.close()
            ack = server_message(ip, ip_renew, transaction_id, mac, network, gateway, dns_prim, dhcp_server, bail, msg)
            socket.sendto(ack, dest)
            File = open('logging.txt', "a")
            File.write(str(datetime.datetime.now()) + "  Ack message send           MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + " IP: " + ip + '\n')
            File.close()
            print("ACK send\n")

        else:
            print("DHCP server isn't requested\n")
            File = open('logging.txt', "a")
            File.write(str(datetime.datetime.now()) + "  Request message received   MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + '\n')
            File.write(str(datetime.datetime.now()) + "  Did not accept offer       MAC: " + mac_int + " ID: 0x" + str(transaction_id.hex()) + '\n')
            File.close()
            if mac in add_currently_used:
                available_add.append(add_currently_used[mac][0])
                del add_currently_used[mac]
            if mac in add_mac_mem:
                del add_mac_mem[mac]
def handle_info(data, client):
    """Function that handle the information requested to be seen

     Parameters : data = bytes, from the client
     Return : nothing
     """
    update_time(add_currently_used, available_add, add_mac_mem)
    data = data.decode('utf-8')
    if data == '1':
        data = " ; ".join([str(i) for i in available_add]).encode('utf-8')

    if data == '2':
        new = {}
        for keys in add_currently_used:
            key = ':'.join(map(lambda x: hex(x)[2:].zfill(2), struct.unpack('BBBBBB', keys))).upper() #Transform the MAC address in the good format
            new[key] = add_currently_used[keys].copy()
            new[key][1] = str(new[key][1])
        data = str(new).encode('utf-8')

    if data == '3':
        new = {}
        for keys in add_mac_mem:
            key = ':'.join(map(lambda x: hex(x)[2:].zfill(2), struct.unpack('BBBBBB', keys))).upper() #Transform the MAC address in the good format
            new[key] = add_mac_mem[keys]
        data = str(new).encode('utf-8')
    socket.sendto(data, client)

print('\nServer is ready\n')

File = open('logging.txt', "w")
File.close()

while True:
    data, client_address = socket.recvfrom(2048)
    if(len(data)>50):
        print('Data received')
        handle_client(data)
    else:
        handle_info(data, client_address)

server_socket.close()
