##
##███╗   ███╗ █████╗ ██╗██╗     ██████╗ ███████╗ █████╗ ██╗  ██╗                              
##████╗ ████║██╔══██╗██║██║     ╚════██╗██╔════╝██╔══██╗╚██╗██╔╝                              
##██╔████╔██║███████║██║██║      █████╔╝█████╗  ███████║ ╚███╔╝                               
##██║╚██╔╝██║██╔══██║██║██║     ██╔═══╝ ██╔══╝  ██╔══██║ ██╔██╗                               
##██║ ╚═╝ ██║██║  ██║██║███████╗███████╗██║     ██║  ██║██╔╝ ██╗                              
##╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝                              
##                                                                                            
##██████╗ ███████╗ █████╗  ██████╗████████╗██╗██╗   ██╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
##██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║██║   ██║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
##██║  ██║█████╗  ███████║██║        ██║   ██║██║   ██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
##██║  ██║██╔══╝  ██╔══██║██║        ██║   ██║╚██╗ ██╔╝██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
##██████╔╝███████╗██║  ██║╚██████╗   ██║   ██║ ╚████╔╝ ██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
##╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
##
##                                                                                           
## This Script was a collaboration between Patrick and Greg 
## to automate the deactivation of all M2F hierarchical     
## levels.
##
## The need was realized after a customer was still
## able to fax out because of 'client' level settings.
##
## Enjoy!

import requests, re
        
print("Mail2Fax Deactivation v1\n")
CUNO = input("What is the customer number you would like to deactivate? (i.e. 99999US): ").upper()
email = input("What is your email address? ")
modified_by = "?modified_by=" + email
cuno_url = "http://config.mtf.de.service.retloc/rest/v1/customers/" + CUNO
users_url = "http://config.mtf.de.service.retloc/rest/v1/users?customer_number=" + CUNO + "&limit=5000"
clients_url = "http://config.mtf.de.service.retloc/rest/v1/customers/" + CUNO + "/clients"
profiles_url = "http://config.mtf.de.service.retloc/rest/v1/customers/" + CUNO + "/profiles"

## This first check is on the customer url level, but it actually modifies the default profile's active value.
def cust_check():
    put_url = cuno_url + modified_by
    resp = requests.get(cuno_url)
    data = resp.text         
    if data.count(" enabled=\"true\"") == 1:
        cust_deactivate = input("Would you like to set Customer to Active = No? ").lower()
        if cust_deactivate == "yes" or cust_deactivate == "y":
            update = data.replace(" enabled=\"true\"", " enabled=\"false\"")
            new_xml = requests.put(put_url, data=update, headers={"content-type":"text/xml"})
            if new_xml.status_code == 200:
                print("Customer settings updated")
            else:
                print(new_xml.status_code)
        else:
            print("No changes have been made.")
    else:
        print("Default value is already set to default \"No\"")

def profile_check():
    resp = requests.get(profiles_url)
    data = resp.text
    if data.count("enabled=\"true\"") != 0:
        profiles_deactivate = input("Would you like to set the profiles to Active = Default? ").lower()
        if profiles_deactivate == "yes" or profiles_deactivate == "y":
            profiles = re.findall('profile-name="(.*?)"', data)  
            for profile in profiles:
                profile_url = "http://config.mtf.de.service.retloc/rest/v1/customers/" + CUNO + "/profiles/" + profile
                resp = requests.get(profile_url)
                data = resp.text
                if data.count("enabled=\"true\"") == 1:
                    update = data.replace("enabled=\"true\"", "")
                    put_url = profile_url + modified_by
                    new_xml = requests.put(put_url, data=update, headers={"content-type":"text/xml"})
                    if new_xml.status_code == 200:
                        print(profile + " was updated successfully.")
                    else:
                        print("Error updating with")
                        print(new_xml.status_code)
                        continue
                else:
                    continue
        else:
            print("Profiles were not changed.")
    else:
        print("No change needed for profiles.")

def client_check():
    resp = requests.get(clients_url)
    data = resp.text
    if data.count("enabled=\"true\"") != 0:
        clients_deactivate = input("Would you like to set the clients to Active = Default? ").lower()
        if clients_deactivate == "yes" or clients_deactivate == "y":
            clients = re.findall('client-name="(.*?)"', data)
            for client in clients:
                client_url = "http://config.mtf.de.service.retloc/rest/v1/customers/" + CUNO + "/clients/" + client
                resp = requests.get(client_url)
                data = resp.text
                update = data.replace("enabled=\"true\"", "")
                put_url = client_url + modified_by
                new_xml = requests.put(put_url, data=update, headers={"content-type":"text/xml"})
                if new_xml.status_code == 200:
                    print(client + " was updated successfully.")
                else:
                    print("Error updating " + client +", Code: ")
                    print(new_xml.status_code)
                    continue
        else:
            print("Clients were not changed.")
    else:
        print("No change needed for clients.")
                    

def user_check():
    resp = requests.get(users_url)
    data = resp.text
    if data.count("enabled=\"true\"") != 0:
        users_deactivate = input("Would you like to set the users to Active = Default? ").lower()
        if users_deactivate == "yes" or users_deactivate == "y":
            domains = re.findall('domain-name="[^ ]*"', data)
            local_parts = re.findall('local-part="[^ ]*"', data)
            users = [i + j for i, j in zip(local_parts, domains)]
            for user in users:
                user = user.replace("local-part=","")
                user = user.replace("domain-name=","@")
                user = user.replace("\"","")
                user_url = "http://config.mtf.de.service.retloc/rest/v1/users/" + user
                resp = requests.get(user_url)
                data = resp.text
                update = data.replace("enabled=\"true\"", "")
                put_url = user_url + modified_by
                new_xml = requests.put(put_url, data=update, headers={"content-type":"text/xml"})
                if new_xml.status_code == 200:
                    print(user + " was updated successfully.")
                else:
                    print("Error updating " + user +", Code: ")
                    print(new_xml.status_code)
                    continue
        else:
            print("Users were not changed.")
    else:
        print("No change needed for users.")
                    


cust_check()
profile_check()
client_check()
user_check()
input("\nPress enter to quit.")
