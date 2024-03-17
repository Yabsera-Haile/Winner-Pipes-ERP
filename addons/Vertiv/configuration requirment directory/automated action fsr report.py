4null = "-"
log('fsr', 'info')
query = "select row_to_json(cms) \
    from\
        (select\
            cm.customer_email as to,\
            concat(\'Automated Field Service report for your call no:\',\
            cm.call_no)  subject,\
            concat('Please find the automatic generated Field service report for your call no ',cm.call_no) as text,\
            cm.id,\
            cm.call_no,\
            cm.\"engineerId\",\
            hr.name as engineername,\
            cm.call_engineer_mobilenumber,\
            cm.customer_name,\
            cm.customer_address1,\
            cm.customer_address2,\
            cm.customer_address3,\
            cm.customer_state,\
            cm.customer_pincode,\
                        cm.call_actual_startdate as reporting_date,\
            cm.call_actual_enddate as completion_date,\
            concat(cm.customer_contact_person,\':\',cm.customer_contact_mobile) contact,\
            cm.alarmcodeid serviceprovider,\
            cm.alarmcodeid servicetype,\
            cm.product_code,\
            cm.product_model,cm.product_group,\
            cm.product_rating,\
            cm.product_serialno,\
            cm.customer_email,\
            to_char(to_timestamp((cm.tat)), \'D, HH:MI:SS\') as break_time,\
            cm.call_log_date,\
             cm.contract_status,\
             cm.contract_no,\
            cm.warranty_status equipment_status,\
            cm.sr_group as servicebranch,\
            cm.call_type as faultcode,\
            cm.fault_reported as problemstatement,\
            cm.params,\
                        (( travetime.duration)) travel_time ,\
            (( travetime.tst)) travel_start_time ,\
            (( onsite.tst)) on_site_time ,\
            (( face_time.tst)) equipment_facetime_info,\
            (( visit.visits)) visits,\
            ((( onsite.tst+travetime.duration))) total_time ,\
            to_json(array_agg(distinct t.*)) timesheet,\
            to_json(array_agg(distinct m.*)) material,\
            to_json(array_agg(distinct w.*)) workbench\
        from\
            cms_info_model cm ,\
            hr_employee hr,\
            call_timesheet_info t,\
            call_material_activities m ,\
             (SELECT v.call_id,v.call_no,count(*) AS \"visits\" FROM call_timesheet_info v WHERE (v.punch_category = \'Callpunchin\') group by v.call_id,v.call_no) visit, \
             (select\
                tsc.call_id, sum(duration)tst \
            from\
                (select \
                    t.punch_category,\
                    t.call_id,\
                    (t.end_time-t.start_time) duration \
                from\
                    call_timesheet_info t \
                where\
                    t.punch_category ='Callpunchin') tsc \
            group by\
                tsc.call_id)onsite,\
                (select\
                    tsc.call_id,\
                    sum(duration)tst \
                from\
                    (select\
                        t.punch_category,\
                        t.call_id,\
                        (t.end_time-t.start_time) duration \
                    from\
                        call_timesheet_info t \
                    where\
                        t.punch_category ='Equipmentfacetime') tsc \
                group by\
                    tsc.call_id)face_time,\
                    (select\
                        travetime.call_id,\
                        sum(travetime. duration) duration,\
                        min(travetime.start_time) as tst \
                    from\
                        (select\
                            start_notes,\
                            punch_category,\
                            start_time,\
                            (t.end_time-t.start_time) duration,\
                            call_id \
                        from\
                            call_timesheet_info t)travetime \
                    where\
                        punch_category='Labourtime'\
                        and start_notes = 'TIME-ON THE ROAD FOR ENPI'  \
                    group by\
                        travetime.call_id)travetime,\
                        workbench_info w \
                    where\
                        cm.id=t.call_id \
                        and cm.id=w.call_id \
                        and cm.id=m.call_id \
                        and cm.call_no=\'%s\' \
                        and  hr.id=cm.\"engineerId\"  \
                        and cm.id=travetime.call_id \
                        and cm.id=onsite.call_id \
                        and cm.id=face_time.call_id \
                        and cm.id=visit.call_id\
                    group by\
                        hr.name,visits,total_time,equipment_facetime_info, on_site_time,travel_start_time,travel_time,\
                        cm.id)cms" % record.call_no
# query="select row_to_json(cms) from (select cm.customer_email as to, concat('Automated Field Service report for your call no:',cm.call_no)  subject,cm.call_no as text,cm.id,cm.call_no,cm.\"engineerId\", hr.name,cm.call_engineer_mobilenumber,cm.customer_name,cm.customer_address1, cm.customer_address2,cm.customer_address3,cm.customer_state, cm.customer_pincode,cm.product_code,cm.product_model,cm.product_rating,cm.product_serialno,cm.customer_email, cm.tat as break_time,cm.call_actual_startdate as reporting_date,cm.call_actual_enddate as completion_date,cm.params,to_json(array_agg(distinct t.*)) timesheet,to_json(array_agg(distinct m.*)) material, to_json(array_agg(distinct w.*)) workbench,to_json(array_agg(distinct travetime.duration)) travel_time ,to_json(array_agg(distinct travetime.tst)) travel_start_time ,to_json(array_agg(distinct onsite.tst)) on_site_time , to_json(array_agg(distinct face_time.tst)) equipment_facetime_info,to_json(array_agg(distinct( onsite.tst+ travetime.duration)))total_time from cms_info_model cm , hr_employee hr,call_timesheet_info t, call_material_activities m ,(select tsc.call_id,sum(duration)tst from (select t.punch_category,t.call_id,(t.end_time-t.start_time) duration from call_timesheet_info t where t.punch_category ='Callpunchin') tsc group by tsc.call_id)onsite, (select tsc.call_id,sum(duration)tst from (select t.punch_category,t.call_id,(t.end_time-t.start_time) duration from call_timesheet_info t where t.punch_category ='Equipmentfacetime') tsc group by tsc.call_id)face_time, (select travetime.call_id,sum(travetime. duration) duration,min(travetime.start_time) as tst from (select start_notes,punch_category,start_time,(t.end_time-t.start_time) duration,call_id from call_timesheet_info t)travetime where punch_category='Labourtime'and start_notes = 'TIME-ON THE ROAD FOR ENPI'  group by travetime.call_id)travetime, workbench_info w where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\' and  hr.id=cm.\"engineerId\"  and cm.id=travetime.call_id and cm.id=onsite.call_id and cm.id=face_time.call_id group by  hr.name,cm.id)cms" %record.call_no
# query="select row_to_json(cms) from (select  cm.customer_email as to, concat('Automated Field Service report for your call no:',cm.call_no) subject,cm.call_no as text,cm.id,cm.call_no,cm.customer_name,cm.customer_address1, cm.customer_address2,cm.customer_address3,cm.customer_state, cm.customer_pincode,cm.product_code,cm.product_model,cm.product_rating,cm.product_serialno,cm.customer_email, cm.tat as break_time,cm.call_actual_startdate as reporting_date,cm.call_actual_enddate as completion_date,cm.params,to_json(array_agg(distinct t.*)) timesheet,to_json(array_agg(distinct m.*)) material, to_json(array_agg(distinct w.*)) workbench,to_json(array_agg(distinct travetime.duration)) travel_time ,to_json(array_agg(distinct travetime.tst)) travel_start_time ,to_json(array_agg(distinct onsite.tst)) on_site_time , to_json(array_agg(distinct face_time.tst)) equipment_facetime_info,to_json(array_agg(distinct( onsite.tst+ travetime.duration)))total_time from cms_info_model cm , call_timesheet_info t, call_material_activities m ,(select tsc.call_id,sum(duration)tst from (select t.punch_category,t.call_id,(t.end_time-t.start_time) duration from call_timesheet_info t where t.punch_category ='Callpunchin') tsc group by tsc.call_id)onsite, (select tsc.call_id,sum(duration)tst from (select t.punch_category,t.call_id,(t.end_time-t.start_time) duration from call_timesheet_info t where t.punch_category ='Equipmentfacetime') tsc group by tsc.call_id)face_time, (select travetime.call_id,sum(travetime. duration) duration,min(travetime.start_time) as tst from (select start_notes,punch_category,start_time,(t.end_time-t.start_time) duration,call_id from call_timesheet_info t)travetime where punch_category='Labourtime'and start_notes = 'TIME-ON THE ROAD FOR ENPI'  group by travetime.call_id)travetime, workbench_info w where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\' and cm.id=travetime.call_id and cm.id=onsite.call_id and cm.id=face_time.call_id group by cm.id)cms" % record.call_no
# query="select row_to_json(cms) from ( select cm.call_no,cm.customer_name,cm.customer_address1,cm.customer_address2,cm.customer_address3,cm.customer_state,cm.customer_pincode,cm.product_code,cm.product_model,cm.product_rating,cm.product_serialno,cm.no_of_visits, cm.call_punch_time as on_site_time, cm.customer_email, cm.call_actual_startdate as travel_start_time, cast(cm.call_actual_startdate as timestamp) as travel_time, cm.tat as break_time, cm.tat as total_time_spent, cm.call_face_time as equipment_facetime_info, cm.call_actual_startdate as reporting_date,cm.call_actual_enddate as completion_date,cm.params,to_json(array_agg(distinct t.*)) timesheet, to_json(array_agg(distinct m.*)) material, to_json(array_agg(distinct w.*)) workbench from cms_info_model cm ,  call_timesheet_info t, call_material_activities m ,workbench_info w where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\' group by cm.id )cms" % record.call_no
# query="select row_to_json(cms) from (select cm.call_no,cm.customer_name,cm.customer_address1,cm.customer_address2,cm.customer_address3,cm.customer_state,cm.customer_pincode,cm.product_code,cm.product_model,cm.product_rating,cm.product_serialno,cm.params,to_json(array_agg(distinct t.*)) timesheet, to_json(array_agg(distinct m.*)) material, to_json(array_agg(distinct w.*)) workbench from cms_info_model cm ,  call_timesheet_info t, call_material_activities m , workbench_info w where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\' group by cm.id )cms" % record.call_no
# query="select row_to_json(cms) from (select  cm.call_no,cm.customer_name,cm.customer_address1,cm.customer_address2,cm.customer_address3,cm.customer_state,cm.customer_pincode,cm.product_code,cm.product_model,cm.product_rating,cm.product_serialno, cm.params, to_json(array_agg(t.*)) timesheet,to_json(array_agg(m.*)) material, to_json(array_agg(w.*)) workbench from cms_info_model cm ,  call_timesheet_info t, call_material_activities m ,workbench_info w where cm.id=t.call_id and cm.id=w.call_id and cm.id=m.call_id and cm.call_no=\'%s\'group by cm.id )cms" % record.call_no
env.cr.execute(query)
s = env.cr.fetchone()
log(query)

# refmodel=env['notification']
# newrecord=refmodel.create({
#   "notification_type":"E-mail",
#     "notification_to":'mani@mongrov.com',
#     "subject":"Automated Field Service report for your call no:"+record.call_no,
#     "body":s[0],

# })

#   #  "notification_to":record.engineerId.work_email,

Parameters = env['ir.config_parameter'].sudo()
HTML = Parameters.get_param('vertiv_collab_reference_id')
WEBHOOK = HTML + "/api/v1/notification.report"

make_request("POST", WEBHOOK, data=s[0])  