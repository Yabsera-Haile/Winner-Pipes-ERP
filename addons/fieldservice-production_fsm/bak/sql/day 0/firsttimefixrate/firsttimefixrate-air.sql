SELECT "source"."zone" AS "zone", count(*) AS "count"
FROM (SELECT "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate", "public"."cms_info_model"."call_log_date" AS "call_log_date", "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate", "public"."cms_info_model"."call_status" AS "call_status", "public"."cms_info_model"."customer_distance_category" AS "customer_distance_category",
extract(epoch from("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_log_date"))/3600 AS "Tat", "public"."cms_info_model"."product_group" AS "product_group", "public"."cms_info_model"."zone" AS "zone" FROM "public"."cms_info_model" WHERE {{call_log_date}}) "source"
WHERE (("source"."call_status" = 'Completed'
    OR "source"."call_status" = 'Closed')
   AND "source"."Tat" <= 24 AND "source"."product_group" = 'AIR')
GROUP BY "source"."zone"
ORDER BY "source"."zone" ASC