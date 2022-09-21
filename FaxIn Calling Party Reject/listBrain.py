# see https://confluence.inside/pages/viewpage.action?pageId=86222058
# Feature Setup "FaxIn-Calling-Party-Reject-List"
import csv
import paramiko
import json
import requests
from prettytable import PrettyTable
import yaml

# This config file must exist in the current working directory of the executor
CONFIG_FILE = 'config.yaml'
with open(CONFIG_FILE) as file:
    configs = yaml.full_load(file)

user = configs['ssh_auth']['user']
private_key = configs['ssh_auth']['private_key']
host = configs['ssh_auth']['host']


class List:
    def __init__(self):
        self.filename = 'numbersToAdd.csv'
        self.headers = {"Content-Type": "application/json"}
        self.alreadyQueried = False
        self.addOne = True
        self.modifiedBy = ''
        self.tableID = ''
        self.technicalName = ''
        self.entryID = ''
        self.listEntries = []
        self.CUNO = '99999IE'  # Set to this account for testing purposes
        self.numbers_to_add = []
        self.listData = '''{
                        "list": {
                            "applicationDomain": "fax",
                            "customerId": "%s",
                            "description": "%s",
                            "enabled": true,
                            "entity": "default",
                            "lastModifiedBy": "%s",
                            "listType": "faxin-calling-party-reject-list",
                            "service": "faxin",
                            "technicalName": "%s"
                        }
                    }'''
        self.entryData = '''{
                        "entries": [
                            {
                                "entryType": "E.164",
                                "lastModifiedBy": "%s",
                                "value": "%s",
                                "customerComment": "%s"
                            }
                        ]
                    }'''

    def getCUNO(self):
        self.CUNO = input('What customer number would you like to search for? ')
        return self.CUNO

    def getModified(self):
        self.modifiedBy = input('What\'s your email address? ')
        return self.modifiedBy

    def getCustList(self):
        table = PrettyTable()
        table.field_names = ['Table ID', 'Table Name']
        self.getCUNO()
        custURL = '' + self.CUNO
        data = json.loads(requests.get(custURL).text)
        if data['resultSize'] == 0:
            print('There are no tables for the associated customer.')
            input('\nPlease type enter to go back to the main menu...')
        else:
            for result in range(data['resultSize']):
                tableID = data['result'][result]['id']
                technicalName = data['result'][result]['technicalName']
                table.add_row([tableID, technicalName])
            print(table)
            self.tableID = input('\nWhich list would you like to work with? (Enter ID) ')
            for result in range(data['resultSize']):
                if data['result'][result]['id'] == self.tableID:
                    self.technicalName = data['result'][result]['technicalName']
            self.getListEntries()
            self.alreadyQueried = True
            input('\nPlease type enter to continue...')
            return self.tableID, self.technicalName

    def getListEntries(self):
        table = PrettyTable()
        table.field_names = ['Table ID', 'Entry ID', 'Blocked Number', 'Comment']
        listURL = '' + self.tableID + '/entries?limit=500'
        data = json.loads(requests.get(listURL).text)
        for result in range(data['resultSize']):
            self.listEntries.append(data['result'][result]['id'])
            table.add_row(
                [data['result'][result]['listId'], data['result'][result]['id'], data['result'][result]['value'],
                 data['result'][result]['customerComment']])
        print(table)

    def addEntries(self):
        if self.alreadyQueried:
            addBulk = input('Would you like to add numbers in bulk via CSV? (Y or N)').lower()
            if addBulk == 'y' or addBulk == 'yes':
                self.addOne = False
            if self.addOne:
                self.addSingle()
            else:
                self.addBulk()
        else:
            print('Please select a table to modify by first querying for tables associated with a CUNO.')
            input('\nPlease type enter to go back to the main menu...')

    def addSingle(self):
        self.getModified()
        number = input('What\'s the phone number you would like to add to the list? (e.g. +12017937595): ')
        comment = input('Add a comment: ')
        self.postEntry(number, comment)
        self.getListEntries()
        input('\nPlease type enter to continue...')

    def addBulk(self):
        self.getModified()
        with open(self.filename) as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            for row in reader:
                data = row
                self.numbers_to_add.append(data)

        for number_to_add in self.numbers_to_add:
            number = str(number_to_add[0]).lower()
            comment = number_to_add[1]
            self.postEntry(number, comment)
        self.getListEntries()
        input('\nPlease type enter to continue...')

    def createList(self):
        createURL = ''
        CUNO = input('What is the customer number this list is for? ')
        listName = input('What is the name of this list? ')
        description = input('Please enter a description if you\'d like (else, leave blank for default): ')
        if not description:
            description = "calling party numbers to block on certain fax inbound profiles"
        response = requests.post(url=createURL, data=self.listData % (CUNO, description, self.modifiedBy, listName), headers=self.headers)
        formatted = json.loads(response.text)
        self.tableID = formatted['list']['id']
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully inserted {self.tableID}, status code: {response.status_code}")
            input('\nPlease type enter to continue...')
            self.alreadyQueried = True
        else:
            print(f"Error inserting new list, status code: {response.status_code}")
            input('\nPlease type enter to continue...')

    def postEntry(self, number, comment):
        entryURL = 'http://listsvc.fax.mucre1.retloc/rest/v1/lists/' + self.tableID + '/entries'
        response = requests.post(url=entryURL, data=self.entryData % (self.modifiedBy, number, comment),
                                 headers=self.headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f'Successfully inserted {number}, status code: {response.status_code}')
        else:
            print(f'Error inserting {number}, status code: {response.text}')

    def checkDelete(self, item):
        if self.alreadyQueried:
            if item == 'list':
                deleteURL = 'http://listsvc.fax.mucre1.retloc/rest/v1/lists/' + self.tableID
                self.getListEntries()
                delete_check = input('Press enter again to remove this entire list.')
                if not delete_check:
                    self.deleteEntry(deleteURL)
                    input('\nPlease type enter to continue...')
                else:
                    print(f'{self.tableID} was not removed.')
                    self.getListEntries()
                    input('\nPlease type enter to continue...')
            elif item == 'number':
                self.getListEntries()
                all_items = False
                all_check = input('Would you like to remove all numbers from a list? Y or N: ').lower()
                if all_check == 'y' or all_check == 'yes':
                    all_items = True
                if all_items:
                    input('Press enter to delete all items from this list.')
                    for entry in list(set(self.listEntries)):
                        self.entryID = entry
                        deleteURL = '' + self.tableID + '/entries/' + self.entryID
                        self.deleteEntry(deleteURL)
                    self.getListEntries()
                    self.listEntries = []
                    input('\nPlease type enter to continue...')
                else:
                    still_deleting = True
                    while still_deleting:
                        self.entryID = str(input('Which entry ID would you like to remove? '))
                        deleteURL = '' + self.tableID + '/entries/' + self.entryID
                        self.deleteEntry(deleteURL)
                        check = input('Would you like to delete another entry? ').lower()
                        if check == 'y' or check == 'yes':
                            pass
                        else:
                            still_deleting = False
                            self.getListEntries()
                            input('\nPlease type enter to continue...')
        else:
            print('Please view lists on customer level first.')
            input('\nPlease type enter to go back to the main menu...')

    def deleteEntry(self, deleteURL):
        response = requests.delete(deleteURL)
        if response.status_code == 200:
            print(f'Successfully removed {self.entryID}')
        else:
            print(f'Error during removal of {self.entryID}, status code: {response.status_code}')

    def execute(self, connection, command):
        stdin, stdout, stderr = connection.exec_command(command)
        return stdout.readlines()

    def command(self, choice):
        if self.alreadyQueried:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=user, key_filename=private_key)
            if choice == '1':
                # Setting list for whole customer
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} "{self.technicalName}"'
            elif choice == '2':
                # Setting list for single EAS Profile
                profile = input('What profile should the list be assigned to? ')
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} "{self.technicalName}" "{profile}"'
            elif choice == '3':
                # Setting list for single inbound number
                number = input('What inbound number should the list be assigned to? ')
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} "{self.technicalName}" "{number}"'
            elif choice == '4':
                # Removing list for whole customer
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} ""'
            elif choice == '5':
                # Removing list from specific EAS profile
                profile = input('What profile should the list be unassigned from? ')
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} "" "{profile}"'
            elif choice == '6':
                # Setting list for single inbound number
                number = input('What inbound number should the list be unassigned from? ')
                command = f'java -cp SetCallingPartyRejectList {self.CUNO} "" "{number}"'
            for line in self.execute(ssh, command):
                print(line.strip())
            input('\nPlease type enter to continue...')
            ssh.close()
        else:
            print('Please view lists on customer level first.')
            input('\nPlease type enter to go back to the main menu...')
