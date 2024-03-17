from odoo import fields, models, api,tools

class FacetimeZoneReport(models.Model):
    _name="facetimezone.report"
    _auto=False
    _description="Equipment Facetime report"
    _rec_name="id"


    call_count = fields.Integer("Calls")
    productive_time = fields.Float(string="Productive Hours", group_operator='sum')
    face_time=fields.Float(string="Face Time", group_operator='sum')
    worked_hours = fields.Float(string="Working Hours" )
    percentage=fields.Float(string="Percentage")
    start_time = fields.Datetime(string="Date Attended")
    zone = fields.Char("Zone")
    sr_group=fields.Char("SR Group")


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                  CREATE OR REPLACE VIEW %s AS (
                 SELECT  row_number() OVER () as id,
        "source"."zone" AS "zone",
        "source"."sr_group" AS "sr_group",
        CAST("source"."Question 249__start_time" AS date) AS "start_time",
        (sum(abs("source"."Facetime")) /  sum(abs("source"."Productive Time"))) as percentage,
        sum("source"."Productive Time") AS "productive_time" ,
        sum("source"."Facetime") AS  "face_time" , 
        avg("source"."Total Hrs") AS "worked_hours",
        count(distinct "source"."call_no") AS "call_count" 
    FROM
        (SELECT
            "public"."cms_info_model"."call_status" AS "call_status",
            extract(epoch from("Question 249"."Facetime"))/3600 AS "Facetime" , 
             extract(epoch from("Question 248"."Productive time"))/3600 AS "Productive Time" , 
            "public"."cms_info_model"."zone" AS "zone",
            "public"."cms_info_model"."sr_group" AS "sr_group",
            "Question 249"."start_time" AS "Question 249__start_time",   "Question 242"."Total Hrs" AS "Total Hrs",
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
                            "source"."zone",
                            "source"."sr_group",
                            CAST("source"."Question 249__start_time" AS date) 
                        ORDER BY
                            "source"."zone" ASC,
                            "source"."sr_group" ASC,
                            CAST("source"."Question 249__start_time" AS date) ASC
 
        )""" % (self._table))


class Repeatanalysic(models.Model):
    _name = "repeatanalysis.report"
    _auto = False
    _description = "Repeat call analysis report"
    _rec_name = "id"

    call_type=fields.Char("Call Type")
    zone = fields.Char("Zone")
    product_group = fields.Char()
    Last_Month=fields.Integer()
    Previous_Month=fields.Integer()
    Difference=fields.Integer()

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                      CREATE OR REPLACE VIEW %s AS (

                      SELECT row_number() OVER () as id,
                  "source"."call_type" AS "call_type","source"."zone" AS "zone",
    "source"."Last Month" AS "Last_Month","source"."Previous Month" AS "Previous_Month",
    "source"."Difference" AS "Difference" ,
     "source"."product_group" AS "product_group"
    FROM
    (SELECT
        "source"."Last Month" AS "Last Month",
        "source"."Previous Month" AS "Previous Month",
        "source"."product_group" AS "product_group",
        "source"."zone" AS "zone",
        "source"."call_type" AS "call_type",
        "source"."Last Month" AS "Last Month_2",
        "source"."Previous Month" AS "Previous Month_2",
        ("source"."Last Month" - "source"."Previous Month") AS "Difference" 
    FROM
        (SELECT
            "public"."cms_info_model"."product_group" AS "product_group",
            "public"."cms_info_model"."zone" AS "zone",
            "public"."cms_info_model"."call_type" AS "call_type",
            sum(CASE 
                WHEN "public"."cms_info_model"."call_actual_enddate" BETWEEN date_trunc('month', CAST((CAST(now() AS timestamp) + (INTERVAL '-2 month')) AS timestamp))   AND date_trunc('month', CAST((CAST(now() AS timestamp) + (INTERVAL '-1 month')) AS timestamp)) THEN 1 
                ELSE 0.0 
            END) AS "Last Month",
            sum(CASE 
                WHEN "public"."cms_info_model"."call_actual_enddate" BETWEEN date_trunc('month', CAST((CAST(now() AS timestamp) + (INTERVAL '-1 month')) AS timestamp)) AND date_trunc('month', CAST((CAST(now() AS timestamp)) AS timestamp)) THEN 1 
                ELSE 0.0 
            END) AS "Previous Month" 
        FROM
            "public"."cms_info_model" 
        WHERE
            (
                "public"."cms_info_model"."product_group" IS NOT NULL 
                AND (
                    "public"."cms_info_model"."product_group" <> ''     
                    OR "public"."cms_info_model"."product_group" IS NULL
                ) 
                AND "public"."cms_info_model"."zone" IS NOT NULL 
                AND (
                    "public"."cms_info_model"."zone" <> '' 
                    OR "public"."cms_info_model"."zone" IS NULL
                ) 
                 
            ) 
        GROUP BY
            "public"."cms_info_model"."product_group",
            "public"."cms_info_model"."zone",
            "public"."cms_info_model"."call_type" 
        ORDER BY
            "public"."cms_info_model"."call_type" DESC,
            "public"."cms_info_model"."product_group" ASC,
            "public"."cms_info_model"."zone" ASC) "source") "source" LIMIT 1048575


            )""" % (self._table))

