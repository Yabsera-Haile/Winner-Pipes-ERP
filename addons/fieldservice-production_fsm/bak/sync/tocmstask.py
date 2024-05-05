from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

def save_to_mssql(df, table_name, engine, key_name):
    temporary_table = "cms_task_tmp"
    a = []
    for col in df.columns:
        if col == key_name:
            continue
        a.append("CMS_Task.{col}=cms_task_tmp.{col}".format(col=col))
    df.to_sql(temporary_table, engine, if_exists='replace', index=False)
    stmt_1 = "UPDATE CMS_Task "
    stmt_2 = "SET "
    stmt_3 = ", ".join(a)
    stmt_4 = " FROM cms_task_tmp,CMS_Task "
    stmt_5 = "WHERE CMS_Task.task_no=cms_task_tmp.task_no"
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)

# task_no, enpi_eng_id, call_actual_startdate, call_actual_enddate
def data_transformations(data):
    # data = data.drop(columns=[])
    data = data.rename(columns={"call_actual_startdate": "actual_start_date",
                                "call_actual_enddate": "actual_end_date",
                                "write_date": "fsmlastupdated"
                                })
    convert_utc_to_ist_asis(data, 'fsmlastupdated')
    convert_utc_to_ist_asis(data, 'actual_start_date')
    convert_utc_to_ist_asis(data, 'actual_end_date')
    print(data)
    return data


def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('tocmstask.py -o mssqlhost -i postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('tocmstask.py -o <mssqlhost> -i <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('postgres host is ', ihost)
    print('mssql host is ', ohost)
    tap = setup_pgtap(ihost)
    target = setup_mssqltarget(ohost)
    df = tap_read_fields_table_condition(tap, 'cms_info_model', "task_no, enpi_eng_id, call_actual_startdate, call_actual_enddate, write_date", "where call_status != 'Open'")
    df = data_transformations(df)
    target_save_csv(df, "cms_task")
    # create_df_to_target(df, 'cms_task', target)
    if(df.size > 0):
        save_to_mssql(df, 'CMS_Task', target, 'task_no')

if __name__ == "__main__":
    main(sys.argv[1:])
