from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

#UPDATE "ldap" AS f SET ID=t.ID, ADDisplayName=t.ADDisplayName,
#ADUserid=t.ADUserid, ADIsActive=t.ADIsActive, ADMobileNumber=t.ADMobileNumber,
#ADOrganizationName=t.ADOrganizationName, ADMgrDisplayName=t.ADMgrDisplayName,
#ADMgrEmailid=t.ADMgrEmailid, ADLocation=t.ADLocation, ADTitle=t.ADTitle,
#ADDepartment=t.ADDepartment, ADFirstName=t.ADFirstName,
#ADLastName=t.ADLastName FROM "ldap_tmp" AS t WHERE f.ADEmailid=t.ADEmailid ;

# ID | ADDisplayName |  ADUserid   |
# ADEmailid        | ADIsActive | ADMobileNumber |
# ADOrganizationName    | ADMgrDisplayName |
# ADMgrEmailid       | ADLocation |
# ADTitle                    |
# ADDepartment | ADFirstName | ADLastName
def data_transformations(data):
   # data = data.drop(columns=[])
    # data = data.rename(columns={})
    #data["call_actual_startdate"] = data["call_actual_startdate"].fillna(pd.datetime.now())
    # print(data.columns)
    print(data)
    return data


def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('allsync.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('allsync.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = tap_setup(ihost, 'CMSFieldServiceApp_UAT',
                    'FSMApp01', 'Welcome@1234#')
    target = target_setup(ohost, 'Fsm', 'vertivadmin', '$Welcome@123456#$')
    # tap = tap_setup(ihost, 'CMSFieldServiceApp_UAT', 'sa', 'test1234$')
    # target = target_setup(ohost, 'testsync', 'ea', '')
    df = tap_fullread_table(tap, 'ldap')
    df = data_transformations(df)
    target_save_csv(df, "ldap")
    # save a full copy
    create_df_to_target(df, "ldap", target)
    #target_save_postgres(target, df, 'ldap', 'ADEmailid')


if __name__ == "__main__":
    main(sys.argv[1:])
