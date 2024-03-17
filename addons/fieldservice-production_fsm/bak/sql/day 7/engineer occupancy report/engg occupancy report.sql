SELECT "source"."Engineer" AS "Engineer", "source"."call_type" AS "call_type", count(*) AS "count", extract(epoch from(sum("source"."duration")))/3600 AS "sum",to_char(SUM(source.duration),'HH24:MI:SS')
FROM (SELECT "hr_employee__via__engineerId"."name" AS "hr_employee__via__engineerId__name", "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate", "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate", "hr_employee__via__engineerId"."name" AS "Engineer", "public"."cms_info_model"."call_type" AS "call_type", ("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_actual_startdate") AS "duration", "public"."cms_info_model"."call_status" AS "call_status", "public"."cms_info_model"."call_log_date" AS "call_log_date" FROM "public"."cms_info_model"
LEFT JOIN "public"."hr_employee" "hr_employee__via__engineerId" ON "public"."cms_info_model"."engineerId" = "hr_employee__via__engineerId"."id") "source"
WHERE (("source"."call_status" = 'Completed'
    OR "source"."call_status" = 'Closed' OR "source"."call_status" = 'Working' OR "source"."call_status" = 'Attended')
   AND "source"."call_log_date" >= CAST((CAST(now() AS timestamp) + (INTERVAL '-30 day')) AS date) AND "source"."call_log_date" < CAST(now() AS date))
GROUP BY "source"."Engineer", "source"."call_type"
ORDER BY "source"."Engineer" ASC, "source"."call_type" ASC