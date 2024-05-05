SELECT
        "Question 99"."product_group" AS "Product Group",
        sum("source"."sum") AS "Sr.no wise calls",
        sum("Question 99"."sum") AS "Same Sr.no Same fault",
        sum("Question 111"."count") AS "Below 10 days"
    FROM
        (SELECT
            "source"."product_group" AS "product_group",
            sum("source"."count") AS "sum"
        FROM
            (SELECT
                "public"."cms_info_model"."product_group" AS "product_group",
                "public"."cms_info_model"."product_serialno" AS "product_serialno",
                date_trunc('month',
                "public"."cms_info_model"."call_log_date") AS "call_log_date",
                count(*) AS "count"
            FROM
                "public"."cms_info_model"
            where {{call_log_date}}
            GROUP BY
                "public"."cms_info_model"."product_group",
                "public"."cms_info_model"."product_serialno",
                date_trunc('month',
                "public"."cms_info_model"."call_log_date")
            ORDER BY
                "public"."cms_info_model"."product_group" ASC,
                "public"."cms_info_model"."product_serialno" ASC,
                date_trunc('month',
                "public"."cms_info_model"."call_log_date") ASC) "source"
        WHERE
            "source"."count" > 1
        GROUP BY
            "source"."product_group"
        ORDER BY
            "source"."product_group" ASC) "source"
        LEFT JOIN
            (
                SELECT
                    "source"."product_group" AS "product_group",
                    sum("source"."count") AS "sum"
                FROM
                    (SELECT
                        "public"."cms_info_model"."product_group" AS "product_group",
                        "public"."cms_info_model"."product_serialno" AS "product_serialno",
                        "public"."cms_info_model"."fault_reported" AS "fault_reported",
                        date_trunc('month',
                        "public"."cms_info_model"."call_log_date") AS "call_log_date",
                        count(*) AS "count"
                    FROM
                        "public"."cms_info_model"
                    GROUP BY
                        "public"."cms_info_model"."product_group",
                        "public"."cms_info_model"."product_serialno",
                        "public"."cms_info_model"."fault_reported",
                        date_trunc('month',
                        "public"."cms_info_model"."call_log_date")) "source"
                WHERE
                    "source"."count" > 1
                GROUP BY
                    "source"."product_group") "Question 99"
                        ON "source"."product_group" = "Question 99"."product_group"
                LEFT JOIN
                    (
                        SELECT
                            "source"."Question 97__product_group" AS "Question 97__product_group",
                            count(*) AS "count"
                        FROM
                            (SELECT
                                "Question 97"."call_log_date" AS "Question 97__call_log_date",
                                "source"."min" AS "min",
                                "Question 97"."product_group" AS "Question 97__product_group",
                                extract(epoch
                            from
                                ("Question 97"."call_log_date" - "source"."min"))/3600 AS "Delta",
                                "Question 97"."product_serialno" AS "Question 97__product_serialno"
                            FROM
                                (SELECT
                                    "public"."cms_info_model"."product_group" AS "product_group",
                                    "public"."cms_info_model"."product_serialno" AS "product_serialno",
                                    min("public"."cms_info_model"."call_log_date") AS "min"
                                FROM
                                    "public"."cms_info_model"
                                GROUP BY
                                    "public"."cms_info_model"."product_group",
                                    "public"."cms_info_model"."product_serialno"
                                ORDER BY
                                    "public"."cms_info_model"."product_group" ASC,
                                    "public"."cms_info_model"."product_serialno" ASC) "source"
                            INNER JOIN
                                (
                                    SELECT
                                        "public"."cms_info_model"."id" AS "id",
                                        "public"."cms_info_model"."call_no" AS "call_no",
                                        "public"."cms_info_model"."call_type" AS "call_type",
                                        "public"."cms_info_model"."call_status" AS "call_status",
                                        "public"."cms_info_model"."call_log_date" AS "call_log_date",
                                        "public"."cms_info_model"."zone" AS "zone",
                                        "public"."cms_info_model"."product_group" AS "product_group",
                                        "public"."cms_info_model"."product_serialno" AS "product_serialno"
                                    FROM
                                        "public"."cms_info_model"
                                ) "Question 97"
                                    ON (
                                        "source"."product_group" = "Question 97"."product_group"
                                        AND "source"."product_serialno" = "Question 97"."product_serialno"
                                    )
                                ) "source"
                        WHERE
                            "source"."Delta" < 10
                            and "source"."Delta" > 0
                        GROUP BY
                            "source"."Question 97__product_group"
                        ORDER BY
                            "source"."Question 97__product_group" ASC) "Question 111"
                                ON "source"."product_group" = "Question 111"."Question 97__product_group"
                        GROUP BY
                            "Question 99"."product_group"
                        ORDER BY
                            "Question 99"."product_group" ASC