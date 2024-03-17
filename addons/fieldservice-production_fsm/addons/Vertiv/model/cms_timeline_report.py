from odoo import fields, models, api,tools


class CmsTimeline(models.Model):
    _name="cms.report"
    _auto=False
    _description="Cms Time view report"
    _rec_name="call_no"
    _order = 'call_log_date desc'

    call_no = fields.Char("Call No")
    call_type = fields.Char("Call Type")
    call_log_date = fields.Datetime('Call Log Date')
    call_actual_startdate = fields.Datetime("Actual Start Date")
    call_actual_enddate = fields.Datetime("Actual End Date")
    customer_distance_category=fields.Char('Distance category')
    call_status = fields.Selection([
        ('Unassigned', 'Unassigned'),
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Working', 'Working'),
        ('Attended', 'Attended'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed')], store=1, default='Open', track_visibility='onchange')

    response_time = fields.Float('Response time',group_operator = 'avg' )
    engineerId = fields.Many2one("hr.employee", "Engineer")
    tat = fields.Float('TAT',group_operator = 'avg')
    distance_category = fields.Char()
    status_of_call = fields.Char()
    product_group = fields.Char()
    product_rating = fields.Char('Rating')
    zone = fields.Char("Zone")

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT row_number() OVER () as id, call_no as call_no,
                 call_type as call_type,
                 call_log_date,
                 call_actual_startdate,
                 call_actual_enddate,
                 customer_distance_category,
                 call_status,
                 extract(epoch from(call_actual_startdate -call_log_date))/3600 AS response_time,
                  extract(epoch from(call_actual_enddate -call_log_date))/3600 AS tat,
                   CASE 
                WHEN "customer_distance_category" = 'A (0-30km)' THEN 'Local' 
                WHEN "customer_distance_category" = 'A (0-50km)' THEN 'Local' 
                ELSE 'Up Country' 
            END AS distance_category,
             CASE 
                WHEN "call_status" = 'Completed' THEN 'Closed' 
                WHEN "call_status" = 'Closed' THEN 'Closed' 
                ELSE 'Open' 
            END AS "status_of_call" ,
                 "zone","engineerId",
                 product_group,
                 product_rating from cms_info_model
                          )
        """ % (self._table)
                         )

class CmsTimeline_new(models.Model):
    _name = "cms.report2"
    _auto = False
    _description = "Cms Time view report"
    _rec_name = "zone"
    _order = 'zone'

    zone = fields.Char("Zone")
    loggedcalls=fields.Integer('Logged Calls')
    opencalls=fields.Integer('Open Calls',group_operator = 'sum')
    closedcalls=fields.Integer('Closed Calls', group_operator = 'sum')
    localcalls=fields.Integer('Local Calls' ,group_operator = 'sum')
    localtat=fields.Float('TAT Local')
    localrt = fields.Float('RT Local')
    upcountrycalls = fields.Integer('Up Country Calls', group_operator='sum')
    upcountrytat = fields.Float('TAT Upcountry')
    upcountryrt=fields.Float('RT Upcountry')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                select row_number() OVER () as id, zone,count(*) AS loggedcalls,
COUNT(CASE WHEN (status_of_call='Open') then call_no else NULL END)  AS openCalls ,
COUNT(CASE WHEN (status_of_call='Closed') then call_no else NULL END)  AS  closedcalls ,
    COUNT(CASE WHEN (distance_category='Local') then call_no else NULL END)  AS localCalls ,
     AVG(CASE WHEN (distance_category='Local') then response_time else NULL END)  AS  localrt ,
AVG(CASE WHEN (distance_category='Local') then tat else NULL END)  AS  localtat ,
COUNT(CASE WHEN (distance_category='Up Country') then call_no else NULL END)  AS  upcountrycalls ,
          AVG(CASE WHEN (distance_category='Up Country') then response_time else NULL END)  AS upcountryrt,
AVG(CASE WHEN (distance_category='Up Country') then tat else NULL END)  AS upcountrytat 


from (SELECT call_no as call_no,
         call_type as call_type,
         call_log_date,
         call_actual_startdate,
         call_actual_enddate,
         customer_distance_category,
         call_status,
         extract(epoch from(call_actual_startdate -call_log_date))/3600 AS response_time,
          extract(epoch from(call_actual_enddate -call_log_date))/3600 AS tat,
           CASE 
        WHEN "customer_distance_category" = 'A (0-30km)' THEN 'Local' 
        WHEN "customer_distance_category" = 'A (0-50km)' THEN 'Local' 
        ELSE 'Up Country' 
    END AS distance_category,
     CASE 
        WHEN "call_status" = 'Completed' THEN 'Closed' 
        WHEN "call_status" = 'Closed' THEN 'Closed' 
        ELSE 'Open' 
    END AS "status_of_call" ,
         "zone","engineerId",
         product_group,
         product_rating from cms_info_model)as t 
                           group by zone
                           ORDER BY zone
                          )
        """ % (self._table)         )

class EngTimeline(models.Model):
        _name = "engg.cms.report2"
        _auto = False
        _description = "Response time report"
        _rec_name = "engineerId"
        _order = 'engineerId'

        engineerId = fields.Many2one("hr.employee", "Engineer")
        loggedcalls = fields.Integer('Logged Calls')
        opencalls = fields.Integer('Open Calls', group_operator='sum')
        closedcalls = fields.Integer('Closed Calls', group_operator='sum')
        localcalls = fields.Integer('Local Calls', group_operator='sum')
        localtat = fields.Float('TAT Local')
        localrt = fields.Float('RT Local')
        upcountrycalls = fields.Integer('Up Country Calls', group_operator='sum')
        upcountrytat = fields.Float('TAT Upcountry')
        upcountryrt = fields.Float('RT Upcountry')
        product_group = fields.Char()
        call_log_date = fields.Datetime('Call Log Date')


        def init(self):
            tools.drop_view_if_exists(self._cr, self._table)
            self._cr.execute("""
                CREATE OR REPLACE VIEW %s AS (
                      SELECT row_number() OVER () as id, 
    "source"."engineerId" AS "engineerId", CAST("source"."call_log_date" AS date) as call_log_date,
    "source"."product_group" AS "product_group",count(*) AS loggedcalls,
    COUNT(CASE 
        WHEN (status_of_call='Open') then call_no 
        else NULL 
    END)  AS OpenCalls ,
    COUNT(CASE 
        WHEN (status_of_call='Closed') then call_no 
        else NULL 
    END)  AS  Closedcalls ,
    COUNT(CASE 
        WHEN (distance_category='Local') then call_no 
        else NULL 
    END)  AS LocalCalls ,
    AVG(CASE 
        WHEN (distance_category='Local') then "source"."RT"
        else NULL 
    END)  AS  Localrt ,
    AVG(CASE 
        WHEN (distance_category='Local') then "source"."TAT" 
        else NULL 
    END)  AS  Localtat ,
    COUNT(CASE 
        WHEN (distance_category='Up Country') then call_no 
        else NULL 
    END)  AS  upcountrycalls ,
    AVG(CASE 
        WHEN (distance_category='Up Country') then "source"."RT" 
        else NULL 
    END)  AS upcountryrt,
    AVG(CASE 
        WHEN (distance_category='Up Country') then "source"."TAT" 
        else NULL 
    END)  AS upcountrytat           
FROM
    (SELECT
      "public"."cms_info_model"."call_no" AS "call_no",
        "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate",
        "public"."cms_info_model"."call_log_date" AS "call_log_date",
        "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate",
        "public"."cms_info_model"."call_status" AS "call_status",
        "public"."cms_info_model"."engineerId" AS "engineerId",
        "public"."cms_info_model"."product_group" AS "product_group",
        "public"."cms_info_model"."zone" AS "zone",
        extract(epoch from("public"."cms_info_model"."call_actual_startdate" - "public"."cms_info_model"."call_log_date"))/3600 AS "RT",
        extract(epoch from("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_log_date"))/3600 AS "TAT",
        CASE                  
            WHEN "customer_distance_category" = 'A (0-30km)' THEN 'Local'                  
            WHEN "customer_distance_category" = 'A (0-50km)' THEN 'Local'                  
            ELSE 'Up Country'              
        END AS distance_category,
        CASE                  
            WHEN "call_status" = 'Completed' THEN 'Closed'                  
            WHEN "call_status" = 'Closed' THEN 'Closed'                  
            ELSE 'Open'              
        END AS "status_of_call" 
    FROM
        "public"."cms_info_model") "source" 
WHERE
    (
        (
            "source"."call_status" = 'Completed'     
            OR "source"."call_status" = 'Closed'
        )    
        AND "source"."call_log_date" IS NOT NULL 
        AND "source"."call_actual_startdate" IS NOT NULL 
        AND "source"."call_actual_enddate" IS NOT NULL
    ) 
GROUP BY
    "source"."engineerId",
    "source"."product_group",
    "source"."zone", CAST("source"."call_log_date" AS date)
ORDER BY
    "source"."engineerId" ASC,
    "source"."product_group" ASC, CAST("source"."call_log_date" AS date) ASC
            )""" % (self._table)

                             )