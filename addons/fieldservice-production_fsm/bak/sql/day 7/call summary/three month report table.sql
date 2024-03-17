SELECT "public"."cms_info_model"."zone" AS "zone", to_char("public"."cms_info_model"."call_log_date",'Month, YYYY') AS "Call Log Date", count(*) AS "count"
FROM "public"."cms_info_model"
WHERE ("public"."cms_info_model"."call_log_date" >= date_trunc('month', CAST((CAST(now() AS timestamp) + (INTERVAL '-3 month')) AS timestamp))
   AND "public"."cms_info_model"."call_log_date" < date_trunc('month', CAST(now() AS timestamp)) AND "public"."cms_info_model"."zone" IS NOT NULL AND ("public"."cms_info_model"."zone" <> ''
    OR "public"."cms_info_model"."zone" IS NULL) AND "public"."cms_info_model"."product_group" = 'AIR')
GROUP BY "public"."cms_info_model"."zone", to_char("public"."cms_info_model"."call_log_date",'Month, YYYY')
ORDER BY to_date(to_char("public"."cms_info_model"."call_log_date",'Month, YYYY'),'Month, YYYY') ASC, "public"."cms_info_model"."zone" ASC