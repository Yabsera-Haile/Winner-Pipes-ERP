from odoo import fields, models, api,tools

class Engg_occupancy_report(models.Model):
    _name="enggoccupancy.report"
    _auto=False
    _description="Engineer Occupancy report"
    _rec_name="id"

    Engineer=fields.Char()
    engineerId = fields.Many2one("hr.employee", "Engineer")
    call_type=fields.Char("Call Type")
    attended_date=fields.Date('Attended Date')
    calls=fields.Integer("No. of Calls", group_operator='sum')
    occupied_time=fields.Float("Occupied Time", group_operator='sum')
    # occupied_time2 = fields.Char()


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
               CREATE OR REPLACE VIEW %s AS (
                      SELECT
        row_number() OVER () as id,
        "source"."engineerId",
        "source"."Engineer" AS "Engineer",
        "source"."call_type" AS "call_type",
        to_date(to_char("source"."call_actual_startdate",'Dd mm,YY'),'Dd MM YY') AS "attended_date",
        count(*) AS "calls",
        extract(epoch from (sum("source"."duration")))/3600 AS "occupied_time",
        to_char(SUM(source.duration),
        'HH24:MI:SS') as occupied_time2 
    FROM
        (SELECT
            "hr_employee__via__engineerId"."name" AS "hr_employee__via__engineerId__name",
             "engineerId" AS "engineerId", 
            "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate",
            "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate",
            "hr_employee__via__engineerId"."name" AS "Engineer",
            "public"."cms_info_model"."call_type" AS "call_type",
            ("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_actual_startdate") AS "duration",
            "public"."cms_info_model"."call_status" AS "call_status",
            "public"."cms_info_model"."call_log_date" AS "call_log_date" 
        FROM
            "public"."cms_info_model" 
        LEFT JOIN
            "public"."hr_employee" "hr_employee__via__engineerId" 
                ON "public"."cms_info_model"."engineerId" = "hr_employee__via__engineerId"."id") "source" 
    WHERE
        (
            (
                "source"."call_status" = 'Completed'     
                OR "source"."call_status" = 'Closed' 
                OR "source"."call_status" = 'Working' 
                OR "source"."call_status" = 'Attended'
            )    
            AND "source"."call_log_date" >= CAST((CAST(now() AS timestamp) +  (INTERVAL '-30 day')) AS date) 
            AND "source"."call_log_date" < CAST(now() AS date)
        ) 
    GROUP BY
        "source"."Engineer",
        "source"."call_type",
        "source"."engineerId" , 
        "source"."call_actual_startdate" 
    ORDER BY
        "source"."Engineer" ASC,
        "source"."call_type" ASC
                         
                         
        )""" % (self._table))