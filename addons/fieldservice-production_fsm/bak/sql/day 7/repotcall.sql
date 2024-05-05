select "source"."zone",
            "monthlist"."month",
            sum("source"."Repeated_calls") as Repeated_calls from (select "zonelist"."zone" as zone, "source"."call_log_date" as call_log_date,
            "source"."Repeated_calls" as "Repeated_calls"  from (select   "source"."zone" AS "zone", "source"."call_log_date",  count("source"."Repeated_calls") AS "Repeated_calls"
           from (SELECT
                "public"."cms_info_model"."product_group" AS "product_group",
                "public"."cms_info_model"."product_serialno" AS "product_serialno",
                 to_char ("cms_info_model"."call_log_date", 'Month') AS "call_log_date",
                "public"."cms_info_model"."zone" AS "zone",
                count(*) AS "Repeated_calls"
            FROM
                "public"."cms_info_model"

            GROUP BY
                "public"."cms_info_model"."product_group",
                "public"."cms_info_model"."product_serialno",
                 to_char ("cms_info_model"."call_log_date", 'Month'),
                "public"."cms_info_model"."zone"
            ORDER BY
                "public"."cms_info_model"."product_group" ASC,
                "public"."cms_info_model"."product_serialno" ASC,
                 to_char ("cms_info_model"."call_log_date", 'Month') ASC,
                "public"."cms_info_model"."zone" ASC ) source
            WHERE
            (
                "source"."Repeated_calls" > 1
                AND "source"."product_group" = 'DCPS'            )
             GROUP BY
            "source"."zone",
            "source"."call_log_date"
        ORDER BY
            "source"."zone" ASC,
            "source"."call_log_date" ASC) source
         right JOIN
            (
                select
                    zone
                from
                   ( VALUES
                    ('NORTH'),
                    ('SOUTH-WEST'),
                    ('SOUTH-EAST'),
                    ('EAST'),
                    ('WEST')
                   )  AS t (zone)
            ) "zonelist"
                ON trim("source"."zone") = trim("zonelist"."zone")
              GROUP BY
            "source"."zone",
            "zonelist"."zone", "source"."call_log_date",
            "source"."Repeated_calls" )source
          FULL JOIN
            (
                select
                    month
                from
                    (
                VALUES
                    ('January'),
                    ('February'),
                    ('March'),
                    ('April'),
                    ('May'),
                    ('June'),
                    ('July'),
                    ('August'),
                    ('September'),
                    ('October'),
                    ('November'),
                    ('December')) AS t (Month)
            ) "monthlist"
                ON trim("source"."call_log_date") = trim("monthlist"."month")
                       GROUP BY
            "source"."zone",
            "monthlist"."month", "source"."call_log_date",
            "source"."Repeated_calls"
            ORDER BY
             to_char(to_date("monthlist"."month", 'Month'), 'mm') asc
