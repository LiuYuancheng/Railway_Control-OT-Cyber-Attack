#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        attckBlackE3.py [python2.7]
#
# Purpose:     This module will be called from the macro in doc "operation manual.docm"
#              to simulation the black energy 3 attack on the OT-platform.
#              > cmd /c C:\Python27\python.exe C:\Users\dcslyc\Documents\BlackE3.py " & sDir
#               
# Author:      JunWen Wong, Yuancheng Liu
#
# Created:     2019/12/05
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

#to run - c:\Python27\python.exe BlackE3.py
import sys
from os import system, name, path
from time import sleep 
try:
    # for Python2
    import urllib as urllib2
except ImportError:
    # for Python3
    import urllib2 

#-----------------------------------------------------------------------------
def clear():
    """ Clear the cmd window. """
    # for windows os.name is 'nt', mac and linux(here, os.name is 'posix'
    _ = system('cls') if name == 'nt' else system('clear')

#-----------------------------------------------------------------------------
def progressBar(count, total, status=''):
    """ Create a process bar."""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # use flash to make the current cmd line refresh.

#-----------------------------------------------------------------------------
def printLog():
    """ Show the simulation scan log messages."""
    # Section 1: scan host computer information.
    clear() 
    print('Searching for Windows credential:') 
    for i in range(101):
        progressBar(i, 100, status='Scan system file.')
        sleep(0.1)
    print('\n Credential found!\n') 
    sleep(1)
    print('Alice:502:aad3c435b514a4eeaad3b935b51304fe:c46b9e588fa0d112de6f59fd6d58eae3:::\n') 
    sleep(2)
    print('Running password cracker...') 
    sleep(3)
    print('Password recovered!\n') 
    sleep(1)
    print('Alice:P@ssW0rd123!\n') 
    sleep(2)
    print('Escalation of privilages for user: Alice') 
    sleep(2)
    print('Success\n') 
    sleep(2)
    print('ipconfig\n') 
    sleep(1)
    print('Windows IP Configuration') 
    print('Ethernet adapter Ethernet0:\n') 
    print('   Connection-specific DNS Suffix  . :') 
    print('   Link-local IPv6 Address . . . . . : fe80::c832:7352:a509:de87%9') 
    print('   IPv4 Address. . . . . . . . . . . : 10.168.10.2') 
    print('   Subnet Mask . . . . . . . . . . . : 255.255.0.0') 
    print('   Default Gateway . . . . . . . . . :\n') 
    sleep(2)
    print('Establishing  connection to C2 server') 
    sleep(2)
    print('Success\n') 
    sleep(3)
    try:
        g = raw_input("")
    except:
        input()
    # Section 2: scan the PLC related information.
    clear() 
    sleep(1) 
    print('smbclient -L 10.168.10.2 -U Alice -p 445\n') 
    sleep(2)
    print('Initiate network scanning....') 
    sleep(0.5)
    print('nmap -T4 -F 10.168.10.0/24\n') 
    sleep(2)
    print('Starting Nmap 7.70 ( https://nmap.org ) at 2019-11-29 16:11 SGT')
    print('Nmap scan report for 10.168.10.62')
    print('Host is up (0.0086s latency).')
    print('All 100 scanned ports on 10.168.10.62 are closed')
    print('MAC Address: 00:80:F4:0E:7D:5F (Telemecanique Electrique)\n')
    print('Nmap scan report for 10.168.10.63')
    print('Host is up (0.0044s latency).')
    print('All 100 scanned ports on 10.168.10.63 are closed')
    print('MAC Address: 28:63:36:80:41:6A (Siemens AG - Industrial Automation - EWA)\n')
    print('Nmap scan report for 10.168.10.234')
    print('Host is up (0.000016s latency).')
    print('All 100 scanned ports on 10.168.10.234 are closed\n')
    print('Nmap done: 256 IP addresses (4 hosts up) scanned in 3.71 seconds\n')
    sleep(2)
    print('nmap --script s7-info.nse -p 10.168.10.63\n') 
    sleep(2)
    print('Starting Nmap 7.70 ( https://nmap.org ) at 2019-11-29 16:20 SGT')
    print('Nmap scan report for 10.168.10.63')
    print('Host is up (0.022s latency).')
    print('Not shown: 1023 closed ports')
    print('PORT    STATE SERVICE')
    print('102/tcp open  iso-tsap')
    print('| s7-info: ')
    print('|   Module: 6ES7 212-1BE40-0XB0 ')
    print('|   Basic Hardware: 6ES7 212-1BE40-0XB0 ')
    print('|_  Version: 4.0.0')
    print('507/tcp open  crs')
    print('MAC Address: 28:63:36:80:41:6A (Siemens AG - Industrial Automation - EWA)')
    print('Service Info: Device: specialized\n') 
    print('Nmap done: 1 IP address (1 host up) scanned in 2.18 seconds\n') 
    sleep(2)
    print('Sending result to C2 server at 5.149.254.114:80\n') 
    sleep(2)
    print('Standby for incoming instruction\n') 
    sleep(2)
    try:
        _ = raw_input("")
    except:
        input()
    clear() 

#-----------------------------------------------------------------------------
def main():
    # Create the simulated executable exe file in the same folder of the doc.
    if len(sys.argv) > 1:
        crtdir = sys.argv[1]
        try:
            print("Current working directory: %s" %crtdir)
            with open(path.join(crtdir, 'sysScanner.exe'), 'wb' ) as fh:
                fh.write(b'010101010110101010101010101010101011010101')
        except:
            print("File creation permisson deny.")
    sleep(1)
    # Show the log.
    printLog()
    # Connect the attack server and send the attack request.
    urllib2.urlopen("http://localhost:8080/") 

if __name__ == '__main__':
    main()
