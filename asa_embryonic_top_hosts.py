from netmiko import ConnectHandler
import argparse
import getpass
import re
import operator

#### Author: Bruno Novais ####
#### brusilva@cisco.com ####
#### This script will show topX-embryonic connection hosts, where X is defined by an argument. ####
#### It uses netmiko to login via ssh to an asa, and parse local-host database as well as conn to do it.####

def toptalkers(con, top):
    '''This function gets a netmiko connection to an ASA and collects some commands to find the top talkers
    it will return a dictionary of the host <> number of connections'''

    dict_h_c = {}

    output_lhost = con.send_command('terminal pager 0')
    output_lhost = con.send_command('show local-host detail')

    list_output = output_lhost.splitlines()

    # Idea is to find a host, then look for the embryonic connection. all of the numbers will be added to a dictionary.
    i = 0
    j = 0
    while i < len(list_output):
        match1 = re.search(r'(local host: <)(.*)(>,.*)', list_output[i])
        if match1:
            #print(match1.group(2))
            j = i + 3
            match2 = re.search(r'(\s+TCP embryonic count to host = )(\d*)', list_output[j])
            if match2:
                #print(match2.group(2))
                i = j + 1

                dict_h_c[match1.group(2)] = match2.group(2)
                # just for test below. enable to check the ordering logic to fill up some numbers
                # dict_h_c[match1.group(2)] = i
        else:
            i += 1

    # Then we get the dictionary with all hosts and connections and sort it in reverse
    sort_dict_h_c = sorted(dict_h_c.items(), key=operator.itemgetter(1), reverse=True)

    # Finally, print the topX hosts and connections by looping through the dict
    print(f'|------------------ TOP {top} ------------------|')
    print('IP\t\tEmbryonic Count')
    i=0
    for item in sort_dict_h_c:
        print(f'{item[0]}\t{item[1]}')
        i+=1
        if i == top: break

    return True

def main():

    #### Argparse block ####
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", '-i', type=str, help="IP of the ASA")
    parser.add_argument("--username", '-u', type=str, help="Your username")
    parser.add_argument("--top", '-t', type=int, default=5, help="Top # of hosts to report")
    arguments = parser.parse_args()
    #### End of Argparse block ####

    # Assigning variables
    password = getpass.getpass()
    ip = arguments.ip
    username = arguments.username
    top = arguments.top
    device_type = 'cisco_asa'

    # Now create dictionary with the ASA credentials
    cisco_asa = {
        'device_type': device_type,
        'ip': ip,
        'username': username,
        'password': password,
    }

    # Open connection
    con = ConnectHandler(**cisco_asa)

    # Call toptalkers function
    toptalkers(con, top)

if __name__ == '__main__':
    main()