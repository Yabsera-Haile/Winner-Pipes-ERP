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
        print('fsmload.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('fsmload.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    df = tap_fullread_table(tap, 'engineer_master')
    target_save_csv(df, "cms_employee")
    create_df_to_target(df, "cms_employee", target)

if __name__ == "__main__":
    main(sys.argv[1:])
