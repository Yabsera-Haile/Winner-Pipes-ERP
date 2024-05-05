from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

def data_transformations(data):
    data = data.drop(columns=['created_by', 'updated_by', 'state_id', 'zone', 'updated_date'])
    data = data.rename(columns={"is_active": "branch_isactive", "created_date": "create_date"})
    data['branch_id'] = data['branch_id'].astype('int')
    data['branch_isactive'] = data['branch_isactive'].astype('bool')
    convert_ist_to_utc(data, 'create_date')
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
        print('branchinfo.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('branchinfo.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    df = tap_fullread_table(tap, 'Branch_Master')
    df = data_transformations(df)
    target_save_csv(df, "branch_info")
    target_save_postgres(target, df, 'branch_info', 'branch_id')

if __name__ == "__main__":
    main(sys.argv[1:])
