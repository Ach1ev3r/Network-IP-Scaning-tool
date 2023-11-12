import csv
import ipaddress
import platform
import subprocess
import concurrent.futures
from datetime import datetime
from time import perf_counter
from iteration_utilities import unique_everseen

report = []
pingfile = input("What is the file called ")
now = datetime.now()
print(now)


def get_valid_ip(ip_list, ips_used):
    ip_list_subnet = []
    for i_ping in ip_list:
        if i_ping not in ips_used:
            ip_list_subnet.append(i_ping)
    return ip_list_subnet


def get_usable_ips(ip_subnet):
    try:
        net = ipaddress.ip_network(ip_subnet, strict=True)
    except ValueError:
        raise ValueError(f"Invalid input format or subnet {ip_subnet}")
    ips = []
    for ip in net.hosts:
        ip.append(str(ip))
    return ips


def get_smartlist(ip_pr, i):
    ip_list = []
    smart_ip_list = list(ipaddress.ip_network(ip_pr).subnets(prefixlen_diff=i))
    return ip_list, smart_ip_list


def get_first_last(smart_ip_list, ip_list):
    for ip_subnet in smart_ip_list:
        usable_ips = []
        usable_ips.extend(get_usable_ips(ip_subnet))
        fr_la = ([usable_ips[i] for i in (0, -1)])
        ip_list.append(fr_la[0])
        ip_list.append(fr_la[1])
    ip_list = list(unique_everseen(ip_list))
    return ip_list


def getsmartlist_small(ip_pr):
    ip_list = []
    try:
        ip_list = list(ipaddress.ip_network(ip_pr, strict=True ))
    except ValueError:
        raise ValueError(f"Invalid input format or subnet {ip_pr}")
    return ip_list


def used_ips(ips_used, ip_list):
    for ip in ip_list:
        ips_used.append(ip)
    ips_used = list(unique_everseen(ips_used))
    return ips_used


def ping(i_ping, packets=2, timeout=100):
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', str(packets), '-w', str(timeout), str(i_ping)]
        ping_result = subprocess.run(command, stdin = subprocess.DEVNULL, stdout=subprocess.PIPE, stderr = subprocess.DEVNULL, creationflags = 0x08000000)
        return ping_result.returncode == 0 and b'TTL=' in ping_result.stdout
    else:
        command = ['ping', '-c', str(packets), '-w', str(timeout), str(i_ping)]
        ping_result = subprocess.run(command, stdin = subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr = subprocess.DEVNULL,)
        return ping_result.returncode == 0
    return


def get_reponces(futures):
    ping_responce = False
    for responce in futures:
        if responce.result():
            ping_responce = True
    return ping_responce


def ping_subnet(ip_pr, mask):
    ping_responce = False
    ips_used = []
    start = perf_counter()
    prefix_list = 32 - mask
    if mask >= 30:
        prefix_list = 3
    for i in range(2,prefix_list):
        if not ping_responce:
            if mask < 30:
                ip_list, smart_ip_list = get_smartlist(ip_pr, i)
                ip_list = get_first_last(smart_ip_list, ip_list)
            else:
                ip_list = getsmartlist_small(ip_pr)
            ip_list_subnet = get_valid_ip(ip_list, ips_used)
            ips_used = used_ips(ips_used, ip_list)
            with concurrent.futures.ThreadPoolExecutor(64) as tasks:
                futures = [tasks.submit(ping, str(i_ping)) for i_ping in ip_list_subnet]
                ping_responce = get_reponces(futures)
    stop = perf_counter()
    print(f'Time taken: {stop - start} number of addresses scaned {len(ips_used)}, {ping_responce}')
    return ping_responce


def process_ping(line):
    ip_ne = f"{line[0]}.{line[1]}"
    ip4 = ipaddress.IPv4Network((0, line[1]))
    ip_netmask = f"{line[0]}.{ip4.netmask}"
    mask = ip4.prefixlen
    netmask = f"{ip4.netmask}"
    ping_result = {
        "Network&Mask": ip_netmask,
        "Network": line[0],
        "NetMask": netmask,
        "Prefix": mask,
        "ICMP_Responce": ""
    }
    ip_pr = f'{line[0]}/{mask}'
    print(ip_pr)
    if int(mask) and mask >= 16:
        ping_responce = ping_subnet(ip_pr, mask)    
        if ping_responce:
            ping_result['ICMP_Responce'] = "Y"
    else:
        ping_result['ICMP_Responce'] = "ICMP Not scanned as is limited to /16 to /32"
    return ping_result


with open(f'./IP_input_data/{pingfile}.csv', "r") as csv_file:
    ping_list = csv.reader(csv_file)
    for line in ping_list:
        report.append(process_ping(line))

    keys = report[0].keys()
    now = datetime.now()
    now_time = str(now).split()[1].replace(":","_")
    with open(f'./Results/{now_time}.csv', 'w', newline='') as final:
        csv_writer = csv.DictWriter(final, keys, delimiter=",")
        csv_writer.writeheader
        csv_writer.writerows(report)
