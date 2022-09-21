import csv
import requests
import progressbar

filename = 'usersToModify.csv'


class Stats:
    def __init__(self):
        self.willModify = 0
        self.willnotModify = 0


users_to_check = []
stats = Stats()
users_to_modify = []

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        email_address = row[0]
        users_to_check.append(email_address.lower())

print("Mail2Fax Cover Page Template Reset Script v0.5\n")

bar = progressbar.ProgressBar(maxval=len(users_to_check)).start()

for idx, user_to_check in enumerate(users_to_check):
    url = "" + user_to_check
    resp = requests.get(url)
    data = resp.text
    bar.update(idx)
    if data.count("template-name=\"\"") == 1:
        stats.willModify += 1
        users_to_modify.append(user_to_check)
    else:
        stats.willnotModify += 1
bar.finish()

print("\n%s users will be modified.\n%s users will not be modified." % (stats.willModify, stats.willnotModify))
if stats.willModify == 0:
    input("\nPress enter to quit.")
    quit()
else:
    # Input your email address. This will update the modified by section of the URL
    modifiedby = input("\nYour email address?").lower()
    print(modifiedby)

proceed = input("\nWould you like to continue?").lower()

if proceed == "yes" or proceed == "y":
    bar = progressbar.ProgressBar(maxval=len(users_to_modify)).start()
    for idx, user_to_modify in enumerate(users_to_modify):
        url = "" + user_to_modify
        resp = requests.get(url)
        data = resp.text
        update = data.replace("template-name=\"\" ", "")
        put_url = url + "?modified_by=" + modifiedby
        new_xml = requests.put(put_url, data=update, headers={"content-type":"text/xml"})
        bar.update(idx)
        if new_xml.status_code != 200:
            print("\nError updating " + user_to_modify)
        else:
            continue
    bar.finish()
    input("\nPress enter to quit.")
    quit()
else:
    input("\nPress enter to quit.")
