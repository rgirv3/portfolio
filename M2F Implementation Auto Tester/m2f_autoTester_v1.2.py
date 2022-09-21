import requests
import re

print('Mail2Fax Auto Testing Tool v1.2\n')

# Global Variables
CUNO = input('What is the customer number being tested? (i.e. 99999US): ').upper()
modified_by = input('What is your email address?: ').lower()

# Define user
if modified_by:
    user = re.findall('([a-zA-Z0-9._-]+)', modified_by)
    user = user[0] + '.testing'
    domain = 'retarus.com'
    email_address = user + "@" + domain
else:
    modified_by = 'gregory.irving@retarus.com'
    user = 'gregory.irving.testing'
    domain = 'retarus.com'
    email_address = 'gregory.irving.testing@retarus.com'

# Define fax number
fax = input('What 10-digit fax number should be used?: ')
if fax:
    fax_address = '+1' + fax + '@rfax.net'
else:
    fax_address = '+12017937595@rfax.net'

# M2F variables
cuno_url = '' + CUNO
customer_check = requests.get(cuno_url)
url = '' + email_address

# M4A v2 variables
username = ''
password = ''
endpoint = ''
headers = {'Content-type': 'application/json'}


class AddRemoveUser:
    def delete():
        remove_url = requests.delete(url)

    def userCheck():
        if customer_check.status_code == 200:
            user_exists = requests.get(url)
            if user_exists.status_code == 404:
                return True
            else:
                return False

    def userAdd():
        data = '<user-config xmlns="http://retarus.de/mail2fax/dbconfigs" domain-name="' + domain + '" profile-name="default" local-part="' + user + '" version-number="0" enabled="true" customer-no="' + CUNO + '" client-name="' + CUNO.lower() + '"/>'
        put_url = url + '?modified_by=' + modified_by + '@retarus.com'
        new_xml = requests.put(put_url, data=data, headers={'content-type': 'text/xml'})
        if new_xml.status_code != 201:
            print('Error: ' + str(new_xml.status_code))


class Email:
    def sendEmail():
        payload = '''{
       "subject":{
          "content":"Testing Mail2Fax Setup for ''' + CUNO + '''"
       },
       "body":{
          "contentType":"text/plain",
          "content":"This is a test fax from Retarus that proves termination with Retarus. Please disregard this test fax. Thank you."
       },
       "recipients":[
          {
             "mail":{
            "to":[
                   {
                      "email":''' + fax_address + '''
                   }
                ]
             }
          }
       ],
       "mail":{
          "from":{
             "email":''' + email_address + '''
          }
       }
    }'''
        response = requests.post(endpoint, data=payload, headers=headers, auth=(username, password)).json()
        jobId = response['meta']['jobId']
        return jobId


# Program's Execution:
if AddRemoveUser.userCheck() == True:
    AddRemoveUser.userAdd()
else:
    AddRemoveUser.delete()
    AddRemoveUser.userAdd()

while True:
    jobId = Email.sendEmail()
    print('Email sent. Check Reporting.')
    print('M4A Job ID: %s' % jobId)
    response = input('Mail2Fax job successfully sent? ')
    if response.lower() == 'y' or response.lower() == 'yes':
        break
    else:
        pass

input('\nPress enter to exit.')
AddRemoveUser.delete()
quit()
