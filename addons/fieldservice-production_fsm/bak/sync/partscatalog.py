from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('partscatalog.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('partscatalog.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    df = tap_fullread_table(tap, 'CMS_Partcode')
    target_save_csv(df, "parts_catalog")
    target_save_postgres(target, df, 'parts_catalog', 'item_num')

if __name__ == "__main__":
    main(sys.argv[1:])
