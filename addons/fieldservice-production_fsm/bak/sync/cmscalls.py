from base import *
import pyodbc
import pandas as pd
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine
import sys
import getopt

# UPDATE "cms_info_model" AS f SET sr_no=t.sr_no, call_type=t.call_type, call_severity=t.call_severity,
# call_status=t.call_status, call_booked_by=t.call_booked_by, call_logged_through=t.call_logged_through,
# call_incident_date=t.call_incident_date, call_log_date=t.call_log_date, call_planned_start_date=t.call_planned_start_date,
# call_planned_end_date=t.call_planned_end_date, call_attended_date=t.call_attended_date, call_closed_date=t.call_closed_date,
# call_aging=t.call_aging, cusotmer_account_no=t.cusotmer_account_no, customer_name=t.customer_name,
# site_no=t.site_no, customer_site_address=t.customer_site_address, customer_contact_person=t.customer_contact_person,
# customer_contact_mobile=t.customer_contact_mobile, customer_distance_category=t.customer_distance_category,
# customer_city=t.customer_city, customer_state=t.customer_state, customer_pincode=t.customer_pincode,
# sent_for_sr_creation=t.sent_for_sr_creation, zone=t.zone, sr_group=t.sr_group, sr_owner=t.sr_owner,
# last_updated_by=t.last_updated_by, fault_reported=t.fault_reported, last_update_date=t.last_update_date,
# interaction=t.interaction, call_back_date_time=t.call_back_date_time, eng_responded_intime=t.eng_responded_intime,
# eng_behaviour=t.eng_behaviour, inconvenience_caused=t.inconvenience_caused, service_rating=t.service_rating,
# explanation=t.explanation, addi_site_info=t.addi_site_info, call_logged_by=t.call_logged_by, customer_site_contactno=t.customer_site_contactno,
# warrenty_status=t.warrenty_status, warranty_aspercustomer=t.warranty_aspercustomer, contract_no=t.contract_no,
# contract_status=t.contract_status, contract_start_date=t.contract_start_date, contract_end_date=t.contract_end_date,
# contract_coverage_description=t.contract_coverage_description, instance_no=t.instance_no, product_group=t.product_group,
# product_code=t.product_code, product_serial_no=t.product_serial_no, product_model=t.product_model, product_rating=t.product_rating,
# service_channel=t.service_channel, call_activity=t.call_activity, call_description=t.call_description,
# field_service_report_no=t.field_service_report_no, problem_code_description=t.problem_code_description,
# resolution_code_description=t.resolution_code_description, resolution_summery=t.resolution_summery,
# reason_of_pending=t.reason_of_pending, cancallation_reason=t.cancallation_reason, pm_visit_no=t.pm_visit_no,
# pm_visit_total=t.pm_visit_total, window_period=t.window_period, calllogdatetime=t.calllogdatetime, callattendeddatetime=t.callattendeddatetime,
# callcloseddatetime=t.callcloseddatetime, cms_type=t.cms_type, customer_address1=t.customer_address1,
# customer_address2=t.customer_address2, customer_address3=t.customer_address3, product_installation_date=t.product_installation_date,
# file_content=t.file_content, file_name=t.file_name, con_per_category=t.con_per_category, customer_contact_landline=t.customer_contact_landline,
# customer_email=t.customer_email, prefered_engineer=t.prefered_engineer, non_Emerson_product=t.non_Emerson_product,
# sr_error=t.sr_error, AlarmCodeId=t.AlarmCodeId, Noofvisit=t.Noofvisit,
# TelecomCustomerSiteID=t.TelecomCustomerSiteID,
# TelecomIncidentID=t.TelecomIncidentID, TelecomCRDT=t.TelecomCRDT, TelecomCSADT=t.TelecomCSADT, TelecomOSCCDT=t.TelecomOSCCDT,
# TelecomCCDT=t.TelecomCCDT, TelecomSER=t.TelecomSER, TelecomFCSN=t.TelecomFCSN, TelecomRCSN=t.TelecomRCSN,
# TelecomCCB=t.TelecomCCB, TelecomCADT=t.TelecomCADT, TelecomRSCD=t.TelecomRSCD FROM "cms_info_model_tmp" AS t WHERE f.call_no=t.call_no ;

#,call_no,call_type,call_severity,call_status,call_incident_date,call_log_date,call_planned_start_date,
# call_planned_end_date,customer_account_no,customer_name,customer_site_address,customer_contact_person,
# customer_contact_mobile,customer_distance_category,customer_city,customer_state,customer_pincode,zone,
# sr_group,sr_owner,fault_reported,customer_site_contactno,warranty_status,warranty_aspercustomer,contract_no,
# contract_status,contract_start_date,contract_end_date,contract_coverage_description,product_group,
# product_code,product_serialno,product_model,product_rating,call_activity,call_description,field_service_report_no,
# problem_code_description,resolution_code_description,resolution_summary,reason_of_pending,
# cancellation_reason,cms_type,customer_address1,customer_address2,customer_address3,product_installation_date,
# customer_contact_landline,customer_email,fsmlastupdated

def data_transformations(data):
    data = data.drop(columns=['SmartSubCat',
                              'sr_no', 'call_booked_by', 'call_logged_through',
                              'call_aging', 'site_no', 'sent_for_sr_creation',
                              'last_updated_by', 'last_update_date',
                              'interaction', 'call_back_date_time', 'eng_responded_intime', 'eng_behaviour',
                              'inconvenience_caused', 'service_rating', 'explanation', 'addi_site_info', 'call_logged_by',
                              'instance_no', 'service_channel', 'pm_visit_no', 'pm_visit_total',
                              'window_period', 'calllogdatetime', 'callattendeddatetime', 'callcloseddatetime',
                              'file_content', 'file_name', 'con_per_category', 'prefered_engineer', 'non_Emerson_product',
                              'sr_error', 'AlarmCodeId', 'Noofvisit',
                              'call_attended_date', 'call_closed_date',
                              'TelecomCustomerSiteID', 'TelecomIncidentID', 'TelecomCRDT', 'TelecomCSADT', 'TelecomOSCCDT',
                              'TelecomCCDT', 'TelecomSER', 'TelecomFCSN', 'TelecomRCSN', 'fsmlastupdated',
                              # 'prob_code_description', "resolution_code_description", "reason_of_pending",
                              'TelecomCCB', 'TelecomCADT', 'TelecomRSCD'
                              ])
    data = data.rename(columns={"severity": "call_severity",
                                "cusotmer_account_no": "customer_account_no",
                                "warrenty_status": "warranty_status",
                                "incident_date": "call_incident_date",
                                "planned_start_date": "call_planned_start_date",
                                "planned_end_date": "call_planned_end_date",
                                "site_address": "customer_site_address",
                                "cust_contact_person": "customer_contact_person",
                                "cust_contact_no": "customer_contact_mobile",
                                "distance_category": "customer_distance_category",
                                "city": "customer_city",
                                "state": "customer_state",
                                "pin": "customer_pincode",
                                "resolution_summery": "resolution_summary",
                                "contact_no": "customer_site_contactno",
                                "warrenty_asper_cust": "warranty_aspercustomer",
                                "coverage_description": "contract_coverage_description",
                                "model": "product_model",
                                "product_serial_no": "product_serialno",
                                "rating": "product_rating",
                                "fsr_no": "field_service_report_no",
                                "cancallation_reason": "cancellation_reason",
                                "prob_code_description": "problem_code_description",
                                "Address1": "customer_address1",
                                "Address2": "customer_address2",
                                "Address3": "customer_address3",
                                "InstallationDate": "product_installation_date",
                                "landline": "customer_contact_landline",
                                "cust_email": "customer_email"
                                })
    # print(data.columns)
    convert_ist_to_utc_asis(data, 'call_incident_date')
    convert_ist_to_utc_asis(data, 'call_log_date')
    convert_ist_to_utc_asis(data, 'call_planned_start_date')
    convert_ist_to_utc_asis(data, 'call_planned_end_date')
    convert_ist_to_utc_asis(data, 'contract_start_date')
    convert_ist_to_utc_asis(data, 'contract_end_date')
    convert_ist_to_utc_asis(data, 'product_installation_date')
    print(data)
    return data


def main(argv):
    ihost = 'localhost'
    ohost = 'localhost'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ihost=", "ohost="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        print('cmscalls.py -i mssqlhost -o postgreshost')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('cmscalls.py -i <mssqlhost> -o <postgreshost>')
            sys.exit()
        elif opt in ("-i", "--ihost"):
            ihost = arg
        elif opt in ("-o", "--ohost"):
            ohost = arg
    print('mssql host is ', ihost)
    print('postgres host is ', ohost)
    tap = setup_mssqltap(ihost)
    target = setup_pgtarget(ohost)
    # select call_no from cms_info_model where call_status='Open';
    df = tap_read_table_condition(tap, 'cms_master', "where call_status = 'Open'")
    df = data_transformations(df)
    target_save_csv(df, "cms_info_model")
    target_save_postgres(target, df, 'cms_info_model', 'call_no')

if __name__ == "__main__":
    main(sys.argv[1:])
