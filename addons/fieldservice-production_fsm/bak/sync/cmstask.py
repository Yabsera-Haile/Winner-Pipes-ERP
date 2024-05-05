from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt


def save_to_postgres(df, table_name, engine, key_name):
    temporary_table = table_name+"_tmp"
    a = []
    for col in df.columns:
        if col == key_name:
            continue
        a.append("{col}=t.{col}".format(col=col))
    df.to_sql(temporary_table, engine, if_exists='replace', index=False)
    stmt_1 = "UPDATE \"{final_table}\" AS f ".format(final_table=table_name)
    stmt_2 = "SET "
    stmt_3 = ", ".join(a)
    stmt_4 = " FROM \"{temporary_table}\" AS t ".format(
        temporary_table=temporary_table)
    stmt_5 = "WHERE f.{primary_key}=t.{primary_key} ".format(
        primary_key=key_name)
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)

    # step 2. insert unknown/new key entries at target
    # lets make sure write_date is updated
    stmt_1 = "INSERT INTO \"{final_table}\" (".format(final_table=table_name)
    stmt_2 = ", ".join(df.columns) + ", write_date) select "
    stmt_3 = ", ".join(df.columns) + ", CURRENT_TIMESTAMP"
    stmt_4 = " FROM \"{temporary_table}\" ".format(
        temporary_table=temporary_table)
    stmt_5 = "WHERE {primary_key} not in (select {primary_key} from \"{final_table}\") ".format(
        primary_key=key_name, final_table=table_name)
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + stmt_5 + ";"
    print(sql)
#    with engine.begin() as conn:     # TRANSACTION
#       conn.execute(sql)
    # step 3. delete from target table entries that are not present in tmp
    # delete from lov_master where lov_no NOT IN (select lov_no from lov_master_tmp);
    # step 2. insert unknown/new key entries at target
    #  update cms_info_model_tmp as f SET sp_eng_name = "Email" FROM cms_employee as t  WHERE f.enpi_eng_id = t.employee_code;
    # update cms_info_model_tmp as f SET call_engineer_mobilenumber = t.id FROM hr_employee as t  WHERE f.sp_eng_name = t.work_email;
    stmt_1 = "update cms_info_model as f SET sp_eng_name = \"Email\" FROM cms_employee as t  WHERE f.enpi_eng_id ilike t.employee_code AND f.sp_eng_name IS NULL;"
    sql = stmt_1
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)
    stmt_1 = "update cms_info_model as f SET \"engineerId\" = t.id FROM hr_employee as t WHERE f.sp_eng_name ilike t.work_email AND \"engineerId\" IS NULL;"
    sql = stmt_1
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)


# UPDATE "cms_info_model" AS f SET task_no=t.task_no, task_subject=t.task_subject, task_owner_type=t.task_owner_type,
# task_assignee_type=t.task_assignee_type, enpi_eng_id=t.enpi_eng_id, call_engineer_mobilenumber=t.call_engineer_mobilenumber,
# sp_eng_name=t.sp_eng_name, reschedule_reason=t.reschedule_reason, call_schedule_startdate=t.call_schedule_startdate,
# call_schedule_enddate=t.call_schedule_enddate, call_actual_startdate=t.call_actual_startdate,
# call_actual_enddate=t.call_actual_enddate, call_assignment_date=t.call_assignment_date,
# Pincode=t.Pincode FROM "cms_info_model_tmp" AS t WHERE f.call_no=t.call_no ;

#,task_no,call_no,task_subject,task_owner_type,task_assignee_type,enpi_eng_id,call_engineer_mobilenumber,
# sp_eng_name,reschedule_reason,call_schedule_startdate,call_schedule_enddate,call_assignment_date,
# fsmlastupdated

def data_transformations(data):
    data = data.drop(columns=['task_type', 'task_status', 'debrief_no',
                              'debrief_status', 'task_assignee_type',
                              'task_assignee', 'planned_start_date', 'planned_end_date',
                              'expense_activity', 'expense_date_time', 'expense_item',
                              'expense_amount', 'labour_activity', 'labour_date_time',
                              'labour_start_time', 'labour_end_time', 'labour_item',
                              'part_activity', 'part_replaced_date', 'eng_subinventory',
                              'eng_locator', 'part_code', 'part_description', 'part_qty',
                              'escalation_id',  'schedule_start_date_initial', 'fsmlastupdated',
                              'Pincode', 'actual_start_date', "actual_end_date"
                              ])
    data = data.rename(columns={"task_owner_name": "task_assignee_type",
                                "EnggMobNo": "call_engineer_mobilenumber",
                                "schedule_start_date": "call_schedule_startdate",
                                "schedule_end_date": "call_schedule_enddate"
                                })
    data['task_no'] = data['task_no'].astype(int)
    convert_ist_to_utc_asis(data, 'call_schedule_startdate')
    convert_ist_to_utc_asis(data, 'call_schedule_enddate')
    convert_ist_to_utc_asis(data, 'call_assignment_date')
    print(data)
    return data


def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('cmstask.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('cmstask.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    # df = tap_read_table_condition(tap, 'cms_task', "where task_status = 'Assigned'")
    df = tap_fullread_table(tap, 'cms_task')
    df = data_transformations(df)
    target_save_csv(df, "cms_info_model")
    save_to_postgres(df, 'cms_info_model', target, 'call_no')

if __name__ == "__main__":
    main(sys.argv[1:])
