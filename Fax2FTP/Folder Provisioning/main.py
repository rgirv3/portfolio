import csv
import ibm_db
import json
import yaml

CONFIG_FILE = 'config.yaml'
with open(CONFIG_FILE) as file:
    configs = yaml.full_load(file)

user = configs['db_auth']['user']
password = configs['db_auth']['password']
host = configs['db_auth']['host']
database = configs['db_auth']['database']

try:
    conn = ibm_db.connect(f'DATABASE={database}; HOSTNAME={host}; PORT=50005; PROTOCOL=TCPIP; UID={user};'
                          f'PWD={password}', '', '')
    ibm_db.autocommit(conn, ibm_db.SQL_AUTOCOMMIT_ON)
except:
    print('Couldn\'t connect to the database.')
    raise


class FtpRewrite:
    def __init__(self):
        self.numbers_to_move = []
        self.filename = 'data.csv'

    def append(self):
        with open(self.filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                block = row[0]
                comment = row[1]
                parameter = {}
                parameter["ftpFolder"] = str(row[0])
                parameter = json.dumps(parameter)
                self.numbers_to_move.append([block, parameter, comment])

    # @staticmethod
    # def getParameter(number):
    #     sql = "SELECT SERVICECONF_PARAMETER FROM RING_SERVICECONFIGS WHERE BLOCKNUMBER_SIMPLE = '%s';" % number
    #     stmt = ibm_db.exec_immediate(conn, sql)
    #     data = ibm_db.fetch_assoc(stmt)
    #     parameter = json.loads(data['SERVICECONF_PARAMETER'])
    #     return parameter

    def numberUpdate(self):
        for number in self.numbers_to_move:
            sql = f'''UPDATE RING_SERVICECONFIGS SET SERVICE_PROFILE_REFID = '19800', SERVICECONF_PARAMETER =
             \'{number[1]}\', CONFIG_COMMENT = \'{number[2]}\', DISPLAYNUMBER = \'{number[0]}\'
             WHERE BLOCKNUMBER_SIMPLE = \'{number[0]}\';'''
            ibm_db.exec_immediate(conn, sql)


ECAS_rewrite = FtpRewrite()
ECAS_rewrite.append()
ECAS_rewrite.numberUpdate()

input('press enter to exit')
