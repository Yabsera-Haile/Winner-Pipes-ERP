
from odoo import fields, models, api, _
from datetime import date, datetime, time
from odoo.exceptions import UserError, ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    date_payment = fields.Date('Payment Date', states={'draft': [('readonly', False)],'done': [('readonly', False)]}, readonly=True,
        help="Keep empty to use the period of the Payment(Payslip) date.")
    payment_order_count = fields.Integer(compute='_get_payment_order_count')
    payment_order_journal_id = fields.Many2one('account.journal', 'Payment Journal', readonly=True, required=True,
        states={'draft': [('readonly', False)],'done': [('readonly', False)]}, default=lambda self: self.env['account.journal'].search([('type', '=', 'bank')], limit=1))
    state = fields.Selection(selection_add=[('paid', 'Paid')])

    @api.depends('move_id')
    def _get_payment_order_count(self):
        for payslip in self:
            payment_order_ids = self.env['account.payment'].search([('payslip_id', '=', payslip.id)])
            payslip.payment_order_count = len(payment_order_ids)

    def create_payment_order(self):
        PaymentOrderObj = self.env['account.payment']
        for payslip in self:
            payment_date = fields.Date.to_string(date.today().replace(day=1))
            if payslip.date_payment:
                payment_date = payslip.date_payment
            move_line_ids = payslip.move_id.line_ids.filtered(lambda l:l.account_id.user_type_id.type == 'payable')
            partner_id = self.env['res.partner'].search([('email', '=', payslip.employee_id.work_email)], limit=1)
            if not partner_id:
                raise ValidationError(_("Partner not found for this employee"))

            for line in move_line_ids:
                payorder_id = PaymentOrderObj.create({
                    'date': payment_date,
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'partner_id': partner_id.id,
                    'amount': line.credit,
                    'journal_id': payslip.payment_order_journal_id.id,
                    'destination_account_id': line.account_id.id,
                    'ref': line.name,
                    'payslip_id': payslip.id
                    })

                payorder_id.action_post()
                to_reconcile_line = payorder_id.move_id.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'payable')

                (line + to_reconcile_line).reconcile()

            payslip.write({'state': 'paid'})


class PaymentOrder(models.Model):
    _inherit = 'account.payment'

    payslip_id = fields.Many2one('hr.payslip')