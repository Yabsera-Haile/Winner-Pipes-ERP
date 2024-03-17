from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

 #id | call_id | activity_type |  activity_notes
 #|    activity_date    | create_uid |        create_date         | write_uid |
 #          write_date         |      call_no       | task_no |        activity_type_value
def data_transformations(data):
    data = data.drop(columns=['id', 'create_uid','create_date', 'write_uid', 'call_id', 'task_no', 'activity_type'])
    data = data[data.columns.drop(list(data.filter(regex='moved')))]
    data = data.rename(
        columns={"call_no": "Call_no", "activity_type_value": "Call_activity", "activity_notes": "Description", "activity_date": "Activity_Date","write_date": "fsmlastupdated"})
    convert_utc_to_ist_asis(data, 'fsmlastupdated')
    convert_utc_to_ist_asis(data, 'Activity_Date')
    print(data)
    return data


def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('workbenchinfo.py -o mssqlhost -i postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('workbenchinfo.py -o <mssqlhost> -i <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('postgres host is ', ihost)
    print('mssql host is ', ohost)
    tap = setup_pgtap(ihost)
    target = setup_mssqltarget(ohost)
    df = tap_fullread_table(tap, 'workbench_info')
    df = data_transformations(df)
    target_save_csv(df, 'CMS_Call_Activity')
    create_df_to_target(df, 'CMS_Call_Activity', target)

if __name__ == "__main__":
    main(sys.argv[1:])
