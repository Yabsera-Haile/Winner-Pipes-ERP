from odoo import fields, models, api,tools,_
from datetime import date,datetime,timedelta
import logging

_logger = logging.getLogger(__name__)

class FacetimeReport(models.Model):
    _name="facetime.report"
    _auto=False
    _description="Equipment Facetime report"
    _rec_name="id"

    call_count = fields.Integer("Calls")
    engineerId = fields.Many2one("hr.employee", "Engineer")
    face_time=fields.Float(string="Call Face Time", group_operator='sum')
    productive_time = fields.Float(string="Productive Hours", group_operator='sum')
    worked_hours = fields.Float(string="Working Hours" ,group_operator = 'avg')
    percentage=fields.Float(string="Percentage")
    start_time = fields.Datetime(string="Date Attended")


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
               CREATE OR REPLACE VIEW %s AS (
                  SELECT  row_number() OVER () as id,
        "source"."engineerId" AS "engineerId",
        CAST("source"."Question 249__start_time" AS date) AS "start_time",
         (sum(abs("source"."Facetime")) /  sum(abs("source"."Productive Time"))) as percentage,
        sum("source"."Productive Time") AS "productive_time",
        sum("source"."Facetime") AS "face_time",
        avg("source"."Total Hrs") AS "worked_hours",
        count(distinct "source"."call_no") AS "call_count" 
    FROM
        (SELECT
            "public"."cms_info_model"."call_status" AS "call_status",
             extract(epoch from("Question 249"."Facetime"))/3600 AS "Facetime" , 
             extract(epoch from("Question 248"."Productive time"))/3600 AS "Productive Time" , 
            "public"."cms_info_model"."engineerId" AS "engineerId",
            "Question 249"."start_time" AS "Question 249__start_time",
            "Question 242"."Total Hrs" AS "Total Hrs",
            "public"."cms_info_model"."call_no" AS "call_no" 
        FROM
            "public"."cms_info_model" 
        INNER JOIN
            (
                SELECT
                    "source"."call_id" AS "call_id",
                    CAST("source"."start_time" AS date) AS "start_time",
                    sum("source"."Duration") AS "Facetime" 
                FROM
                    (SELECT
                        "public"."call_timesheet_info"."end_time" AS "end_time",
                        "public"."call_timesheet_info"."start_time" AS "start_time",
                        "public"."call_timesheet_info"."punch_category" AS "punch_category",
                        "public"."call_timesheet_info"."call_id" AS "call_id",
                        ("public"."call_timesheet_info"."end_time" - "public"."call_timesheet_info"."start_time") AS "Duration" 
                    FROM
                        "public"."call_timesheet_info") "source" 
                WHERE
                    "source"."punch_category" = 'Equipmentfacetime' 
                GROUP BY
                    "source"."call_id",
                    CAST("source"."start_time" AS date) 
                ORDER BY
                    "source"."call_id" ASC,
                    CAST("source"."start_time" AS date) ASC) "Question 249" 
                        ON "public"."cms_info_model"."id" = "Question 249"."call_id" 
                INNER JOIN
                    (
                        SELECT
                            "source"."call_id" AS "call_id",
                            CAST("source"."start_time" AS date) AS "start_time",
                            sum(("source"."end_time" - "source"."start_time")) AS "Productive time" 
                        FROM
                            (SELECT
                                "public"."call_timesheet_info"."end_time" AS "end_time",
                                "public"."call_timesheet_info"."start_time" AS "start_time",
                                "public"."call_timesheet_info"."punch_category" AS "punch_category",
                                "public"."call_timesheet_info"."call_id" AS "call_id" 
                            FROM
                                "public"."call_timesheet_info") "source" 
                        WHERE
                            "source"."punch_category" = 'Labourtime' 
                        GROUP BY
                            "source"."call_id",
                            CAST("source"."start_time" AS date)) "Question 248" 
                                ON ("public"."cms_info_model"."id" = "Question 248"."call_id"    
                                AND CAST("Question 249"."start_time" AS date) = CAST("Question 248"."start_time" AS date)) 
                        LEFT JOIN
                            (
                                SELECT
                                    "public"."hr_employee"."id" AS "id",
                                    "public"."hr_employee"."parent_id" AS "parent_id",
                                    "public"."hr_employee"."name" AS "Engineer",
                                    "Hr Employee - Parent"."name" AS "Manager",
                                    "Question 65"."employee_id" AS "Question 65__employee_id",
                                    "Question 65"."check_out" AS "Check out Date",
                                    "Question 65"."sum" AS "Total Hrs" 
                                FROM
                                    "public"."hr_employee" 
                                LEFT JOIN
                                    "public"."hr_employee" "Hr Employee - Parent" 
                                        ON "public"."hr_employee"."parent_id" = "Hr Employee - Parent"."id" 
                                LEFT JOIN
                                    (
                                        SELECT
                                            "public"."hr_attendance"."employee_id" AS "employee_id",
                                            CAST("public"."hr_attendance"."check_out" AS date) AS "check_out",
                                            count(*) AS "count",
                                            sum("public"."hr_attendance"."worked_hours") AS "sum" 
                                        FROM
                                            "public"."hr_attendance" 
                                        GROUP BY
                                            "public"."hr_attendance"."employee_id",
                                            CAST("public"."hr_attendance"."check_out" AS date)
                                    ) "Question 65" 
                                        ON "public"."hr_employee"."id" = "Question 65"."employee_id" 
                                ORDER BY
                                    "public"."hr_employee"."name" ASC LIMIT 1048575) "Question 242" 
                                        ON ("public"."cms_info_model"."engineerId" = "Question 242"."Question 65__employee_id" 
                                        AND CAST("Question 249"."start_time" AS date) = CAST("Question 242"."Check out Date" AS date))
                                ) "source" 
                        WHERE
                            (
                                (
                                    "source"."call_status" <> 'Unassigned'     
                                    OR "source"."call_status" IS NULL
                                ) 
                                AND (
                                    "source"."call_status" <> 'Open' 
                                    OR "source"."call_status" IS NULL
                                )
                            ) 
                        GROUP BY
                            "source"."engineerId",
                            CAST("source"."Question 249__start_time" AS date) 
                        ORDER BY
                            "source"."engineerId" ASC,
                            CAST("source"."Question 249__start_time" AS date) ASC
            
            
              /* -- AND "source"."start_time" >= date_trunc('month', CAST(now() AS timestamp)) 
                -- AND "source"."start_time" < date_trunc('month', CAST((CAST(now() AS timestamp)+(INTERVAL '1 month')) AS timestamp))*/
                )""" % (self._table))


# class Timesheetreport(models.Model):
#     _name = "timesheet.report"
#     _auto = False
#     _description = "Timesheet report"
#     _rec_name = "id"
#
#     name=fields.Char("Engineer Name")
#     engineerId = fields.Many2one("hr.employee", "Engineer")
#     sr_group = fields.Char()
#     product_group = fields.Char()
#     zone = fields.Char()
#     worked_hours=fields.Float()
#     travel = fields.Float()
#     pm_enpi = fields.Float()
#     breakdown = fields.Float('Breakdown')
#     bs = fields.Float('Breakdown Scheduled ')
#     tmenpi = fields.Float('T&M')
#     startup = fields.Float('Startup')
#     sales = fields.Float()
#     collection = fields.Float()
#     customer_meeting = fields.Float()
#     training = fields.Float()
#     leave = fields.Float()
#     office_work = fields.Float()
#     internal_meeting = fields.Float()
#     break_time = fields.Float()
#
#
#     def init(self):
#         tools.drop_view_if_exists(self._cr, self._table)
#         self._cr.execute("""
#                CREATE OR REPLACE VIEW %s AS (
#                   SELECT  row_number() OVER () as id, hr.name as Name,cm.eng as "engineerId",
#                     cm.sr_group,
#                     cm.product_group,
#                     cm.zone,
#                     sum(d.worked_hours)worked_hours,
#                     sum(cm.travel)travel,
#                     sum(cm.PM_ENPI)pm_enpi,
#                     sum(cm.BREAKDOWN_ENPI)as breakdown,
#                     sum(cm.BREAKDOWN_SCHEDULED) as bs,
#                     sum(cm.TM_ENPI)as tmenpi,
#                     sum(cm.STARTUP_GENERAL_ENPI)startup,
#                     sum(d.sales)sales,
#                     sum(d.collection)collection,
#                     sum(d.customer_meeting)customer_meeting,
#                       sum(d.Training)training,
#                       sum(d.leave)leave,
#                       sum(d.office_work)office_work,
#                       sum(d.internal_meeting)internal_meeting,
#                       sum(d.break_time)break_time  from
# (select cm.call_no,cm.call_status,cm."engineerId" eng,cm.call_actual_startdate,cm.call_actual_enddate,cm.sr_group,cm.product_group,cm.zone,
#             SUM(extract(epoch from(PM_ENPI.CALL_time)))/3600 PM_ENPI,
#             sum(extract(epoch from(BREAKDOWN_ENPI.CALL_time)))/3600 BREAKDOWN_ENPI,
#             sum(extract(epoch from(BREAKDOWN_SCHEDULED.CALL_time)))/3600 BREAKDOWN_SCHEDULED,
#             sum(extract(epoch from(BATTERY_ENPI.CALL_time)))/3600 BATTERY_ENPI,
#             sum(extract(epoch from (STARTUP_GENERAL_ENPI.CALL_time)))/3600 STARTUP_GENERAL_ENPI,
#             sum(extract(epoch from (TM_ENPI.CALL_time)))/3600 TM_ENPI,
#             sum(extract(epoch from(travel.travel_time)))/3600 travel from cms_info_model cm
# left join (select cm.call_no,(t1.end_time-t1.start_time)travel_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where t1.punch_category='Labourtime')travel on travel.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='PM_ENPI' and t1.punch_category='Callpunchin') PM_ENPI on PM_ENPI.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='BREAKDOWN_ENPI' and t1.punch_category='Callpunchin')BREAKDOWN_ENPI on BREAKDOWN_ENPI.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='BREAKDOWN_SCHEDULED' and t1.punch_category='Callpunchin')BREAKDOWN_SCHEDULED on BREAKDOWN_SCHEDULED.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='BATTERY_ENPI' and t1.punch_category='Callpunchin') BATTERY_ENPI on BATTERY_ENPI.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='STARTUP_GENERAL_ENPI' and t1.punch_category='Callpunchin')STARTUP_GENERAL_ENPI on STARTUP_GENERAL_ENPI.call_no=cm.call_no
# left join (select cm.call_no,cm.call_type,(t1.end_time-t1.start_time)call_time from cms_info_model cm left join call_timesheet_info t1 on cm.id=t1.call_id where cm.call_type='T&M_ENPI' and t1.punch_category='Callpunchin')TM_ENPI on TM_ENPI.call_no=cm.call_no
# where cm.call_status != 'Open' or cm.call_status!='Unassigned' or cm.call_status!='Accepted'
# group by cm.call_no,cm."engineerId",cm.call_actual_enddate,cm.call_actual_startdate,cm.call_status,cm.sr_group,cm.product_group,cm.zone)cm
# left join (select hr.employee_id,hr.check_in,hr.check_out,sum(hr.worked_hours)worked_hours,sum(a.break_hours)sales,
#                       sum(b.break_hours)collection,
#                       sum(c.break_hours)customer_meeting,
#                       sum(d.break_hours)Training,
#                       sum(e.break_hours)leave,
#                       sum(f.break_hours)office_work,
#                       sum(g.break_hours)internal_meeting,
#                       sum(h.break_hours)break_time from hr_attendance hr
# left join attendance_break a on hr.id=a.attendance_id and a.break_type='Sales'
# left join attendance_break b on hr.id=b.attendance_id and b.break_type='Collection'
# left join attendance_break c on hr.id=c.attendance_id and c.break_type='Customer Meeting'
# left join attendance_break d on hr.id=d.attendance_id and d.break_type='Training'
# left join attendance_break e on hr.id=e.attendance_id and e.break_type='Leave'
# left join attendance_break f on hr.id=f.attendance_id and f.break_type='Office Work'
# left join attendance_break g on hr.id=g.attendance_id and g.break_type='Internal Meeting'
# left join attendance_break h on hr.id=h.attendance_id and h.break_type='Break Time'
# group by hr.employee_id,hr.check_in,hr.check_out order by hr.employee_id asc)d  on d.employee_id=cm.eng
# left join hr_employee hr on cm.eng=hr.id
# group by cm.eng,hr.name,hr.job_title,hr.parent_id,cm.sr_group,cm.product_group,cm.zone   )""" % (self._table))