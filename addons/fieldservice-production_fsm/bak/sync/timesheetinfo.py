from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt


 #id  | call_id |  punch_category   | punch_type  |     start_time
 # |      end_time       |                          start_notes
 # |                     close_notes
 # | punch_in_latitude | punch_in_longitude | punch_out_latitude | punch_out_longitude '
 # | create_uid |        create_date         | write_uid |         write_date         |       call_no
 # select * from call_timesheet_info where punch_category = 'Labourtime';
def data_transformations(data):
    data = data.drop(columns=['create_uid','create_date', 'write_uid', 'call_id', 'punch_in_latitude', 'punch_in_longitude', 'punch_out_latitude', 'punch_out_longitude'])
    data = data[data.columns.drop(list(data.filter(regex='moved')))]
    data = data.rename(columns={"id": "labour_no", "start_notes": "labour_reason", "write_date": "fsmlastupdated"})
    # // loop and convert start_time and end_time
    data = data.reset_index()  # make sure indexes pair with number of rows
    labour_activity = ['Labor Transaction' for i in range(len(data.index))]
    data['labour_activity'] = labour_activity
    convert_utc_to_ist_asis(data, 'fsmlastupdated')
    convert_utc_to_ist_asis(data, 'start_time')
    convert_utc_to_ist_asis(data, 'end_time')
    data['labour_date_time'] = pd.to_datetime(data['start_time']).dt.date
    data['labour_start_time'] = pd.to_datetime(data['start_time']).dt.time
    data['labour_end_time'] = pd.to_datetime(data['end_time']).dt.time
    data['labour_duration'] = (data['end_time'] - data['start_time']) / pd.Timedelta(hours=1)
    data['labour_duration'] = data['labour_duration'].astype('str')
    # data['labour_duration'] =
    data = data.drop(columns=['start_time','end_time'])
    # for index, row in data.iterrows():
    #     print(row['c1'], row['c2'])
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
        print('timesheetinfo.py -o mssqlhost -i postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('timesheetinfo.py -o <mssqlhost> -i <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('postgres host is ', ihost)
    print('mssql host is ', ohost)
    tap = setup_pgtap(ihost)
    target = setup_mssqltarget(ohost)
    df = tap_read_table_condition(tap, 'call_timesheet_info', "where punch_category = 'Labourtime'")
    df = data_transformations(df)
    target_save_csv(df, 'CMS_TASK_LABOUR')
    create_df_to_target(df, 'CMS_TASK_LABOUR', target)

if __name__ == "__main__":
    main(sys.argv[1:])
