import logging
from datetime import date, datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID


_logger = logging.getLogger(__name__)

class CallXls(models.AbstractModel):
    _name = 'report.module_name.report_name'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        _logger.info("Logging for reports")
        current_time=datetime.now()
        date_format=current_time.day+current_time.month
        _logger.info('Date format %s',date_format)
        bold = workbook.add_format({'bold': 1})
        sheet = workbook.add_worksheet('Calls')
        sheet.set_column(0, 0, 25)
        sheet.write(0, 0, 'Call No',bold)
        sheet.set_column(0, 1, 35)
        sheet.write(0, 1, 'Call Type',bold)
        sheet.set_column(0, 2, 60)
        sheet.write(0, 2, 'Fault reported',bold)
        sheet.set_column(0, 3, 25)
        sheet.write(0, 3, 'Call Log Date',bold)
        sheet.set_column(0, 4, 70)
        sheet.write(0, 4, 'Customer Name',bold)
        sheet.set_column(0, 5, 25)
        sheet.write(0, 5, 'City',bold)
        sheet.set_column(0, 6, 20)
        sheet.write(0,6, 'State',bold)
        sheet.set_column(0, 7, 20)
        sheet.write(0, 7, 'SR Group',bold)
        sheet.set_column(1, 8, 20)
        sheet.write(0, 8, 'SR Owner',bold)
        sheet.set_column(1, 9, 20)
        sheet.write(0, 9, 'Zone',bold)
        sheet.set_column(1, 10, 20)
        sheet.write(0, 10, 'Engineer',bold)
        sheet.set_column(1, 11, 20)
        sheet.write(0, 11, 'Team lead',bold)
        sheet.set_column(1, 12, 20)
        sheet.write(0, 12, 'Call Status',bold)
        sheet.set_column(0, 13, 25)
        sheet.write(0, 13, 'Call Completed Date',bold)
        sheet.set_column(0, 14, 25)
        sheet.write(0, 14, 'Call Close Date',bold)

        i=1
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        for obj in partners:
            report_name = obj.call_no
            # One sheet by partner
            sheet.write( i, 0, obj.call_no)
            sheet.write(i, 1, obj.call_type)
            sheet.write(i, 2, obj.fault_reported)
            sheet.write(i, 3, obj.call_log_date,date_format)
            sheet.write(i, 4, obj.customer_name)
            sheet.write(i, 5, obj.customer_city)
            sheet.write(i, 6, obj.customer_state)
            sheet.write(i, 7, obj.sr_group)
            sheet.write(i, 8, obj.sr_owner)
            sheet.write(i, 9, obj.zone)
            sheet.write(i, 10, obj.engineerId.name)
            sheet.write(i, 11, obj.engineerId.parent_id.name)
            sheet.write(i, 12, obj.call_status)
            sheet.write(i, 13, obj.call_actual_enddate,date_format)
            sheet.write(i, 14, obj.call_closed_date,date_format)
            i+=1
