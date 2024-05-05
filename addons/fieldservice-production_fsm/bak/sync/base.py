import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys, getopt
from datetime import datetime

import pytz
ist = pytz.timezone('Asia/Calcutta')
# pytz.UTC

def update_df_to_target(df, table_name, engine, key_name):
    temporary_table=table_name+"_tmp"
    a=[]
    for col in df.columns:
        if col == key_name:
            continue
        a.append("{col}=t.{col}".format(col=col))
    df.to_sql(temporary_table, engine, if_exists='replace', index=False)
    stmt_1 = "UPDATE \"{final_table}\" AS f ".format(final_table=table_name)
    stmt_2 = "SET "
    stmt_3 = ", ".join(a)
    stmt_4 = " FROM \"{temporary_table}\" AS t ".format(temporary_table=temporary_table)
    stmt_5 = "WHERE f.{primary_key}=t.{primary_key} ".format(primary_key=key_name)
#    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
#    print(sql)
#    with engine.begin() as conn:     # TRANSACTION
#        conn.execute(sql)
    # step 2. insert unknown/new key entries at target
    # lets make sure write_date is updated
    stmt_1 = "INSERT INTO \"{final_table}\" (".format(final_table=table_name)
    stmt_2 = ", ".join(df.columns) + ", write_date) select "
    stmt_3 = ", ".join(df.columns) + ", CURRENT_TIMESTAMP"
    stmt_4 = " FROM \"{temporary_table}\" ".format(temporary_table=temporary_table)
    stmt_5 = "WHERE {primary_key} not in (select {primary_key} from \"{final_table}\") ".format(primary_key=key_name, final_table=table_name)
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)
    # step 3. delete from target table entries that are not present in tmp
    # delete from lov_master where lov_no NOT IN (select lov_no from lov_master_tmp);

# imports dataframe to sql table
# This function to be called with df (with table data) and engine configured
def create_df_to_target(df, table_name, engine):
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# setup tap (mssql)
# @todo: pickup these from env variables?
def tap_setup(server, db, user, password):
    #tap = pyodbc.connect('Driver={FreeTDS};'
    tap = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                        'Server=' + server + ';'
                        'Database=' + db + ';'
                        'uid='+user+';pwd='+password)
    return tap

def convert_ist_to_utc(data, column):
    data[column] = pd.to_datetime(data[column], errors='coerce')
    data[column] = data[column].fillna(pd.datetime.now())
    # IST to UTC
    data[column] = data[column].dt.tz_localize(ist).dt.tz_convert(pytz.UTC)
    data[column] = data[column].dt.tz_localize(None)

def convert_ist_to_utc_asis(data, column):
    data[column] = pd.to_datetime(data[column], errors='coerce')
    # IST to UTC
    data[column] = data[column].dt.tz_localize(ist).dt.tz_convert(pytz.UTC)
    data[column] = data[column].dt.tz_localize(None)

def convert_utc_to_ist_asis(data, column):
    data[column] = pd.to_datetime(data[column], errors='coerce')
    # UTC to IST
    data[column] = data[column].dt.tz_localize(pytz.UTC).dt.tz_convert(ist)
    data[column] = data[column].dt.tz_localize(None)
    data[column] = pd.to_datetime(data[column]).apply(lambda x: x.to_datetime64())

# setup tap (postgres)
# @todo: pickup these from env variables?
def pg_tap_setup(server, db, user, password):
    return target_setup(server, db, user, password)

def tap_fullread_table(tap, table):
    sql_query = "SELECT * FROM " + table
    print(sql_query)
    data = pd.read_sql_query(sql_query, tap)
    return data

def tap_read_table_condition(tap, table, condition):
    sql_query = "SELECT * FROM " + table + " " + condition
    print(sql_query)
    data = pd.read_sql_query(sql_query, tap)
    return data

def tap_read_fields_table_condition(tap, table, fields, condition):
    sql_query = "SELECT " + fields + " FROM " + table + " " + condition
    print(sql_query)
    data = pd.read_sql_query(sql_query, tap)
    return data

# data = pd.read_sql_query('SELECT * FROM LOV_Master', tap)

def target_save_csv(data, fname):
    # save to target
    filepath = Path('output/'+datetime.today().strftime('%Y/%m/%d/%H-%M-')+fname + '.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(filepath)

def target_setup(server, db, user, password):
    engine = create_engine('postgresql://'+user+':'+password+'@' + server + '/' + db)
    return engine

def mssql_target_setup(server, db, user, password):
    engine = create_engine('mssql+pyodbc://'+user+':'+password+'@' + server + '/' + db + "?driver=ODBC+Driver+17+for+SQL+Server")
    return engine

def target_save_postgres(target, data, table, table_key):
    update_df_to_target(data, table, target, table_key)

def setup_mssqltap(ihost):
    # tap = tap_setup(ihost, 'CMSFieldServiceApp_UAT', 'sa', 'test1234$')
    return tap_setup(ihost, 'CMSFieldServiceApp_UAT', 'FSMApp01', 'Welcome@1234#')

def setup_pgtap(ihost):
    return pg_tap_setup(ihost, 'Fsm', 'vertivadmin', '$Welcome@123456#$')

def setup_mssqltarget(ohost):
    return mssql_target_setup(ohost, 'CMSFieldServiceApp_UAT', 'FSMApp01', 'Welcome@1234#')

def setup_pgtarget(ohost):
    # target = target_setup(ohost, 'testsync', 'ea', '')
    return target_setup(ohost, 'Fsm', 'vertivadmin', '$Welcome@123456#$')

# save to target db
#engine = create_engine('postgresql://postgres:rEoM6ZIbcoUPANPl8dso926R9DSp7PXPQ0JlzKFRIH9o8nc2t70FTuVyQc6aQ8rc@localhost:6432/test0319')
#{'index': 0, 'lov_no': 1, 'lov_name': 'Severity', 'lov_value': 'Critical', 'craate_date': datetime.date(2011, 9, 7), 'write_date': None, 'is_enable': '1'}
# create_df_to_target(data, 'lov_master', engine)
#cursor = tap.cursor()
#cursor.execute('SELECT * FROM LOV_Master')
#for i in cursor:
    #print(i)
