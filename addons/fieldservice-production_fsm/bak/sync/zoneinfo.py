from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

def data_transformations(data):
    data = data.drop(columns=['created_by', 'updated_by', 'updated_date'])
    data = data.rename(columns={"created_date": "create_date"})
    data['zone_id'] = data['zone_id'].astype('int')
    data['is_active'] = data['is_active'].astype('bool')
    convert_ist_to_utc(data, 'create_date')
    print(data)
    return data

def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('zoneinfo.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('zoneinfo.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    df = tap_fullread_table(tap, 'zone_master')
    df = data_transformations(df)
    target_save_csv(df, "zone_info")
    target_save_postgres(target, df, 'zone_info', 'zone_id')

if __name__ == "__main__":
    main(sys.argv[1:])
