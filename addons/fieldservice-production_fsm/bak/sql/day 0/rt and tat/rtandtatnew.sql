 select  row_number() OVER () as id,zone,count(*),
 COUNT(CASE WHEN (status_of_call='Open') then call_no else NULL END)  AS OpenCalls ,
        COUNT(CASE WHEN (status_of_call='Closed') then call_no else NULL END)  AS  Closedcalls ,
            COUNT(CASE WHEN (distance_category='Local') then call_no else NULL END)  AS LocalCalls ,
             AVG(CASE WHEN (distance_category='Local') then response_time else NULL END)  AS  Localrt ,
 AVG(CASE WHEN (distance_category='Local') then tat else NULL END)  AS  Localtat ,
     COUNT(CASE WHEN (distance_category='Up Country') then call_no else NULL END)  AS  Upcountry ,
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
                 product_rating from cms_info_model
               where {{call_log_date}} and "cms_info_model"."product_group" = 'POWER' AND ("public"."cms_info_model"."zone" = 'EAST'
    OR "public"."cms_info_model"."zone" = 'NORTH' OR "public"."cms_info_model"."zone" = 'SOUTH-EAST' OR "public"."cms_info_model"."zone" = 'SOUTH-WEST' OR "public"."cms_info_model"."zone" = 'WEST'))as t
                                   group by ROLLUP(ZONE)
                                   ORDER BY ZONE

