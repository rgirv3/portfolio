# Load The Appropriate Python Modules
import mysql.connector
import random
import string
import yaml
from prettytable import PrettyTable

CONFIG_FILE = 'config.yaml'
with open(CONFIG_FILE) as file:
    configs = yaml.full_load(file)

user = configs['db_auth']['user']
password = 'jOure92MQWV5hwK4'
host = configs['db_auth']['host']
database = configs['db_auth']['database']
reuse = configs['cuno_tokenID']

# Connect to Database
conn = mysql.connector.connect(user=user, password=password, host=host, database=database)
cursor = conn.cursor()


class topicGen:
    def __init__(self):
        self.CUNO = ''
        self.COUNT = 0
        self.reuseToken = False
        self.lastRow = ''
        self.TOKEN_ID = 0
        self.TOKEN_VALUE = ''
        self.TOPIC = ''
        self.table = PrettyTable()
        self.table.field_names = ['Token ID', 'CUNO', 'Token', 'Topic']

    # To get customer ID
    def get_CUNO_AND_COUNT(self):
        self.CUNO = input("What is the customer ID?  For Example: 12345US 99999US 12222JP: ").upper()
        if self.CUNO in reuse:
            self.reuseToken = True
            self.TOKEN_ID = reuse[self.CUNO]
            self.TOKEN_VALUE = ''
        self.COUNT = int(input("How many topics do you need?: "))

    # To generate a random token_value - 16 random Letters & Numbers
    def get_token(self):
        if not self.reuseToken:
            lettersAndDigits = string.ascii_letters + string.digits
            self.TOKEN_VALUE = ''.join(random.choice(lettersAndDigits) for i in range(16))
            cursor.execute("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE "
                           "TABLE_SCHEMA = 'FAXINPOLL' AND TABLE_NAME = 'FAXINPOLL_TOKENS'")
            self.TOKEN_ID = cursor.fetchone()[0]

    # To generate a random topic - 8 random capitalized letters & numbers -- Edited to omit O and 0
    def get_topic(self):
        lettersAndDigits = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
        self.TOPIC = ''.join(random.choice(lettersAndDigits) for i in range(8))

    def set_values_to_database(self):
        sql = f"insert into FAXINPOLL.FAXINPOLL_TOKENS (token_id, customer_no, token_value) " \
              f"VALUES ('{self.TOKEN_ID}', '{self.CUNO}', '{self.TOKEN_VALUE}')"

        sql2 = f"insert into FAXINPOLL.FAXINPOLL_TOKEN_SCOPE (token_id, topic) " \
               f"VALUES ('{self.TOKEN_ID}', '{self.TOPIC}')"

        # Execute "sql" statement to insert token_id, cuno and token_value to FAXINPOLL_TOKENS table
        if not self.reuseToken:
            try:
                cursor.execute(sql)
                conn.commit()
            except:
                print("failed to insert: ")
                print(sql)
                print("********************")

        # Execute "sql2" statement to insert token_id and topic to FAXINPOLL_TOKENS_SCOPE table
        try:
            cursor.execute(sql2)
            conn.commit()
        except:
            print("failed to insert: ")
            print(sql2)
            print("********************")

        self.table.add_row([self.TOKEN_ID, self.CUNO, self.TOKEN_VALUE, self.TOPIC])


topicService = topicGen()

topicService.get_CUNO_AND_COUNT()
while topicService.COUNT > 0:
    topicService.get_token()
    topicService.get_topic()
    topicService.set_values_to_database()
    topicService.COUNT -= 1
print(topicService.table)
input()
