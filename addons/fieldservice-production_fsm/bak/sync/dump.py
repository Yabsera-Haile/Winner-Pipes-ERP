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
    table = 'CMS_Task_Material'
    try:
        opts, args = getopt.getopt(argv, "hi:t:", ["ihost=", "table="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('dump.py -i mssqlhost -t tablename')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('dump.py -i <mssqlhost> -t <tablename>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-t", "--table"):
            table = arg
    print('mssql host is ', ihost)
    print('table is ', table)
    tap = setup_mssqltap(ihost)
    df = tap_fullread_table(tap, table)
    # save a full copy
    target_save_csv(df, 'dump_'+table)

if __name__ == "__main__":
    main(sys.argv[1:])
