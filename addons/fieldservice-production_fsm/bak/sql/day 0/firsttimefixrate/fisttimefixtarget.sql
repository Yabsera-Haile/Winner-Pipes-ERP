
   select first_time_fixed_call/total_calls as Target from( SELECT
        count(*) AS "total_calls",
        sum(CASE
            WHEN "source"."Duration" <=24 and "source"."Duration">0 and (call_status='Completed' or call_status='Closed') THEN 1
            ELSE 0.0
        END) AS "first_time_fixed_call"
    FROM
        (SELECT
            call_log_date,
            "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate",call_status,
            "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate",
            extract (epoch from ("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_actual_startdate"))/3600 AS "Duration"
        FROM
            "public"."cms_info_model"  where {{call_log_date}} ) "source") AS T