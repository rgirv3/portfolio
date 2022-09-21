import csv
import datetime
import fnmatch
import os
import requests

# Reporting API Details
baseURL = ''
USER = ''
PASS = ''

# Load Country Code Dictionary
countryDict = {}
with open('countryCode.csv', 'r') as countryCode:
    reader = csv.reader(countryCode, delimiter=',')
    for row in reader:
        countryDict.update({row[0]:row[1]})

# Dates
TODAY = datetime.date.today()
DELTA = datetime.timedelta(days=30)
PREVIOUS = TODAY - DELTA
print(str(PREVIOUS))
input()
# New URL Definition
newURL = baseURL + 'inbound' + '?ts=' + str(PREVIOUS) + 'T00:00:00-0000,' + str(TODAY) + 'T23:59:59-0000'

# GET Request and load as JSON
response = requests.get(newURL, auth=(USER, PASS))
data = response.json()
results = data['results']

# To open/create CSV log
file = open('FaxInStatus_' + str(TODAY) + '.csv', "w", newline='')
writer = csv.writer(file, delimiter=',')

# Define writing to the CSV log
def writeToCSVFile(rowToWrite):
    writer.writerow(rowToWrite)

# For Loop which iterates through all returned jobs
jobCount = 0
failCount = 0
writeToCSVFile(['Date', 'Time', 'Job ID', 'Country', 'Final Status'])
for job in results:
    jobID = data['results'][jobCount]['faxId']
    calledNo = data['results'][jobCount]['calledNo'].split('/')
    countryCode = str(calledNo[0])
    # If statement to combine country + area code for 001  numbers
    if countryCode == str('001'):
        countryCode = countryCode + str(calledNo[1])
    else:
        pass
    # For loop to match country code to country name within dictionary of country codes
    if countryCode in countryDict:
        country = countryDict[countryCode]
    else:
        country = 'United States'
    finalStatus = data['results'][jobCount]['faxStatus']
    if finalStatus == 'succeeded':
        finalStatus = 'OK'
    else:
        failCount += 1
    jobDate = data['results'][jobCount]['lastModTs'].split('T')
    jobTime = jobDate[1].split('.')
    writeToCSVFile([jobDate[0], jobTime[0], jobID, country, finalStatus])
    jobCount += 1
file.close()

# Calculate success rate and define new filename
percent = round((100-(failCount * 100) / jobCount), 2)
newFileName = 'FaxInStatus_' + str(TODAY) + '_successful_' + str(percent) + '%.csv'

# Check whether new filename is already existing, and overwrite
for file in os.listdir(''):
    if fnmatch.fnmatch(file, ('FaxInStatus_' + str(TODAY) + '_successful_*.csv')):
        os.remove(file)
    else:
        pass
os.rename(('FaxInStatus_' + str(TODAY) + '.csv'), newFileName)
