import netmiko
from netmiko import ConnectHandler
import csv
import concurrent.futures as cf
import time
import pwinput
import sys

'''
Function to read device data from CSV file and
return device list data to main.
'''

def read_devices(devicefile):
    with open(devicefile) as dfh:
        csv_reader = csv.DictReader(dfh)
        for device in csv_reader:
            yield device
            
      
'''
Function to connect to device using netmiko
after connection sucessful, it calls function to
collect data
'''


def connect_device(device_data):
    if device_data['dtype'] != device_chosen:
        pass 
    else:
        try:
            rtr = ConnectHandler(device_type=device_data['dtype'],
                             ip=device_data['ip'],
                             username=device_data['username'],
                             password=password)
        except Exception as error:
            print(error)
            goget_data(rtr, device_data)
        
    
'''
Supplying commands to be collected and write
output to file.
'''
#function to get commands from user
def get_cmd():
    print('Enter commands to run on the devices, when finished type DONE')
    while True:
        cmd = sys.stdin.readline().rstrip('\n')
        if (cmd == "DONE"):
            break
        else:
            cmds.append(cmd)

#function to connect to the device and get run the commands including saving the output to file
def goget_data(rtr, device_data):
    for cmd in cmds:
        outputfile = device_data['name'] + '-' + cmd.replace(' ', '-') + timestr + '-' +  '.txt'
        with open(outputfile, 'w') as ofh:
            print(f'### Collecting {cmd} data from {device_data["name"]}')
            output = rtr.send_command(cmd)
            ofh.write(time.ctime() + '\n')
            ofh.write(f'###   Hostname: {device_data["name"]}')
            ofh.write(output)
    rtr.disconnect()
    
'''
Main function
filename formatting
Multithreading code
'''
#starts the time to later compare to the end time to get total run time. remote the comment to get the complete runtime including the time spent entering data
#starttime = (time.time())

#sets up the filter to select what devices we run the script on
device_chosen = input('Enter the type of device to backup: ')

#sets up variable for the username in the password promt
if device_chosen == 'cisco_ios':
    dev_user = "cisco_admin"
if device_chosen == "paloalto_panos":
    dev_user = "palo_admin"

#output file dir, not in use
#outputfildir = '.\OutputFiles'

#sets the format for the time
timestr = time.strftime("%Y%m%d-%H%M")

#runs function to read the CSV
device_data = read_devices('all-devices.csv')

#prompts user for credentials
password = pwinput.pwinput(prompt='Enter password for ' + dev_user + ':', mask="*")

#empty list to append values for commands to run on the devices
cmds = []
#function to prompt user for commands to run on devices
get_cmd()

#starts the time to later compare to the end time to get total run time of the actual job
starttime = (time.time())
'''
Creating threads to connect to devices simultaneously.
'''
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    ex.map(connect_device, device_data)

print('Done collecting data')
#prints total runtime of the script (does count the time spent typing the password,commands, or device type)
print('Total time:', time.time()-starttime)

