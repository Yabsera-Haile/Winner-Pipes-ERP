SELECT
        "source"."product_group" AS "product_group",
        "source"."call_log_date" AS "call_log_date",
        "source"."count" AS "count"
    FROM
        (SELECT
            "public"."cms_info_model"."product_group" AS "product_group",
            date_trunc('month',
            "public"."cms_info_model"."call_log_date") AS "call_log_date",
            count(*) AS "count"
        FROM
            "public"."cms_info_model"
        GROUP BY
            "public"."cms_info_model"."product_group",
            date_trunc('month',
            "public"."cms_info_model"."call_log_date")
        ORDER BY
            "public"."cms_info_model"."product_group" ASC,
            date_trunc('month',
            "public"."cms_info_model"."call_log_date") ASC) "source"
    WHERE
        {{call_log_date}}
        and  (
            "source"."product_group" IS NOT NULL
            AND (
                "source"."product_group" <> ''
                OR "source"."product_group" IS NULL
            )
        ) LIMIT 1048575