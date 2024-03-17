from odoo import fields, models, api,_

class workbench_info(models.Model):
    _name = "workbench.info"
    _description = "Call activity details"
    _rec_name = "call_id"

    call_id=fields.Many2one('cms.info.model')
    call_no = fields.Char(related='call_id.call_no', store=1)
    task_no = fields.Integer(related='call_id.task_no', store=1)
    activity_type=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Call Activity')]")
    activity_type_value=fields.Char(related="activity_type.lov_value", store=1)
    activity_notes=fields.Text()
    activity_date=fields.Datetime()


class workbench_info_wizard(models.TransientModel):
    _name = "workbench.info.wizard"
    _description = "Call activity details"

    workbench_id=fields.Many2one('workbench.info')
    activity_type=fields.Many2one("lov.master",string="Category",domain="[('lov_name','=','Call Activity')]", related='workbench_id.activity_type', store=1)
    activity_notes=fields.Text(related="workbench_id.activity_notes", store=1)
    activity_date=fields.Datetime(related="workbench_id.activity_date", store=1)

    def change_workbench(self):
        call = self.workbench_id
        call.activity_type = self.activity_type
        call.activity_notes=self.activity_notes
        call.activity_date=self.activity_date

