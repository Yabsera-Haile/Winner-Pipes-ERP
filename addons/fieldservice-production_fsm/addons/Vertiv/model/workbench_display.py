from odoo import fields, models, api

class workbenchObservationInfo(models.Model):
    _name = "workbench.observation.info"
    _description = "Workbench Observation details"
    _rec_name = "call_id"

    call_id=fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no', store=1)
    activity_type=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Call Activity')]")
    activity_type_value=fields.Char(related="activity_type.lov_value", store=1)
    activity_notes=fields.Text()
    activity_date=fields.Datetime()


class workbench_Action_Taken_info(models.Model):
    _name = "workbench.action.taken.info"
    _description = "Workbench Action Taken details"
    _rec_name = "call_id"

    call_id=fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no', store=1)
    activity_type=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Call Activity')]")
    activity_type_value=fields.Char(related="activity_type.lov_value", store=1)
    activity_notes=fields.Text()
    activity_date=fields.Datetime()



class workbench_RecommendationInfo(models.Model):
    _name = "workbench.recommendation.info"
    _description = "Workbench Recommendation details"
    _rec_name = "call_id"

    call_id=fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no', store=1)
    activity_type=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Call Activity')]")
    activity_type_value=fields.Char(related="activity_type.lov_value", store=1)
    activity_notes=fields.Text()
    activity_date=fields.Datetime()






