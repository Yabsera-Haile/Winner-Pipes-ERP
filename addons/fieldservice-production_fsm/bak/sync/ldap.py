from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

#UPDATE "ldap" AS f SET ID=t.ID, ADDisplayName=t.ADDisplayName,
#ADUserid=t.ADUserid, ADIsActive=t.ADIsActive, ADMobileNumber=t.ADMobileNumber,
#ADOrganizationName=t.ADOrganizationName, ADMgrDisplayName=t.ADMgrDisplayName,
#ADMgrEmailid=t.ADMgrEmailid, ADLocation=t.ADLocation, ADTitle=t.ADTitle,
#ADDepartment=t.ADDepartment, ADFirstName=t.ADFirstName,
#ADLastName=t.ADLastName FROM "ldap_tmp" AS t WHERE f.ADEmailid=t.ADEmailid ;

# ID | ADDisplayName |  ADUserid   |
# ADEmailid        | ADIsActive | ADMobileNumber |
# ADOrganizationName    | ADMgrDisplayName |
# ADMgrEmailid       | ADLocation |
# ADTitle                    |
# ADDepartment | ADFirstName | ADLastName


# insert into user_approval (name, email, write_date) select "ADDisplayName", "ADEmailid",
# CURRENT_TIMESTAMP from ldap where "ADEmailid"  NOT in (select email from user_approval);
def target_transformations(engine):
    stmt_1 = "insert into user_approval (name, mobile, manager, email, x_designation,write_date) "
    stmt_2 = "select \"ADDisplayName\", \"ADMobileNumber\", \"ADMgrEmailid\", \"ADEmailid\", \"ADTitle\", CURRENT_TIMESTAMP from ldap "
    stmt_3 = "where \"ADEmailid\"  NOT in "
    stmt_4 = "(select email from user_approval)"
    sql = stmt_1 + stmt_2 + stmt_3 + stmt_4 + ";"
    print(sql)
    with engine.begin() as conn:     # TRANSACTION
        conn.execute(sql)

def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('ldap.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('ldap.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    df = tap_fullread_table(tap, 'ldap')
    target_save_csv(df, "ldap")
    create_df_to_target(df, "ldap", target)
    target_transformations(target)

if __name__ == "__main__":
    main(sys.argv[1:])
