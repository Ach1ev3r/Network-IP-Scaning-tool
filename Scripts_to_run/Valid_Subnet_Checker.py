import csv
import ipaddress

pingfile = input("What is the file called ")

def check_ips(line):
    try:
        ip4 = ipaddress.IPv4Network((0, line[1]))
    except:
        ip4 = ipaddress.IPv4Network((0, 32))
    mask = ip4.prefixlen
    ip_pr = f'{line[0]}/{mask}'
    try:
        ip_pr = ipaddress.ip_network(ip_pr, strict=True)
        print(f"{ip_pr}_True")
    except ValueError:
        raise ValueError(f"Invalid input format or subnet {ip_pr}")
    return


with open(f'./IP_input_data/{pingfile}.csv', "r") as csv_file:
    ping_list = csv.reader(csv_file)
    for line in ping_list:
        check_ips(line)