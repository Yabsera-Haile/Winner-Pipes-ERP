SELECT "source"."Engineer" AS "Engineer", "source"."call_type" AS "Call Type", count(*) AS "Calls", extract(epoch from(sum("source"."Duration")))/3600 AS "Time",to_char(SUM("source"."Duration"),'HH24:MI:SS') AS "Time in Char"
FROM (SELECT "public"."cms_info_model"."call_actual_enddate" AS "call_actual_enddate", "public"."cms_info_model"."call_actual_startdate" AS "call_actual_startdate", "hr_employee__via__engineerId"."name" AS "hr_employee__via__engineerId__name", "hr_employee__via__engineerId"."name" AS "Engineer", "public"."cms_info_model"."call_type" AS "call_type", ("public"."cms_info_model"."call_actual_enddate" - "public"."cms_info_model"."call_actual_startdate") AS "Duration", "public"."cms_info_model"."call_status" AS "call_status" FROM "public"."cms_info_model"
LEFT JOIN "public"."hr_employee" "hr_employee__via__engineerId" ON "public"."cms_info_model"."engineerId" = "hr_employee__via__engineerId"."id") "source"
WHERE (("source"."call_status" = 'Closed'
    OR "source"."call_status" = 'Completed' OR "source"."call_status" = 'Attended' OR "source"."call_status" = 'Working')
   AND "source"."Engineer" = 'Engineer 2')
GROUP BY "source"."Engineer", "source"."call_type"
ORDER BY "source"."Engineer" ASC, "source"."call_type" ASC