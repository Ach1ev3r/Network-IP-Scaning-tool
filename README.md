#This is some code i have wrote for ip scanning a network using asynchronous methods curently this is set to 64 but this can be edited in the code.
#The ICMP ping is called from the subprocess process module, unlike ping module this does not need admin rights on the users machine.  

#The Ips are read from ip input folder as a csv file i have a test.csv to show the format that needs to be entered. 
#The results are wrote to results folder as a csv file, this is shown in the test_result.csv section. 

#The following modules are required for this script
#import csv
#import ipaddress
#import platform
#import subprocess
#import concurrent.futures
#from datetime import datetime
#from time import perf_counter
#from iteration_utilities import unique_everseen
