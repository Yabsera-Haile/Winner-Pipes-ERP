from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

def save_to_mssql(df, table_name, engine, key_name):
    temporary_table = "CMS_Master_tmp"
    a = []
    for col in df.columns:
        if col == key_name:
            continue
        a.append("CMS_Master.{col}=CMS_Master_tmp.{col}".format(col=col))
    df.to_sql(temporary_table, engine, if_exists='replace', index=False)
    stmt_1 = "UPDATE CMS_Master "
    stmt_2 = "SET "
    stmt_3 = ", ".join(a)
    stmt_4 = " FROM CMS_Master_tmp,CMS_Master "
    stmt_5 = "WHERE CMS_Master.call_no=CMS_Master_tmp.call_no"
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)

# call_no, call_type, call_status, call_attended_date, call_closed_date,problem_code_description,
# resolution_code_description,resolution_summary,reason_of_pending, write_date
def data_transformations(data):
    # data = data.drop(columns=[])
    data = data.rename(columns={"problem_code_description": "prob_code_description",
                                "resolution_code_description": "resolution_code_description",
                                "resolution_summary": "resolution_summery",
                                "reason_of_pending": "reason_of_pending",
                                "write_date": "fsmlastupdated"
                                })
    convert_utc_to_ist_asis(data, 'fsmlastupdated')
    convert_utc_to_ist_asis(data, 'call_attended_date')
    convert_utc_to_ist_asis(data, 'call_closed_date')
    print(data)
    return data

def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('cmstask.py -o mssqlhost -i postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('cmstask.py -o <mssqlhost> -i <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('postgres host is ', ihost)
    print('mssql host is ', ohost)
    tap = setup_pgtap(ihost)
    target = setup_mssqltarget(ohost)
    # select call_no, call_type, call_status, call_attended_date, call_closed_date,problem_code_description,resolution_code_description,resolution_summary,reason_of_pending from cms_info_model
    df = tap_read_fields_table_condition(tap, 'cms_info_model', "call_no, call_type, call_status, call_attended_date, call_closed_date,problem_code_description,resolution_code_description,resolution_summary,reason_of_pending, write_date", "where call_status != 'Open'")
    df = data_transformations(df)
    target_save_csv(df, "cms_master")
    # create_df_to_target(df, 'cms_task', target)
    if(df.size > 0):
        save_to_mssql(df, 'CMS_Master', target, 'call_no')

if __name__ == "__main__":
    main(sys.argv[1:])
