SELECT count(*) AS "count"
FROM (
SELECT
"public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate" ,
"public"."cms_info_model"."call_status" as "call_status",
"public"."cms_info_model"."call_log_date" AS "call_log_date",
extract(epoch from("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_log_date"))/3600 AS "Duration"

FROM "public"."cms_info_model"
where {{call_log_date}}
) "source"
WHERE
        (
            (
                "source"."call_status" = 'Completed'
                OR "source"."call_status" = 'Closed'
            )
            AND "source"."Duration" <= 24

        )