#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 14 HR Payroll Accounting Extend',
    'category': 'Human Resources',
    'author': 'VPerfectcs',
    'version': '14.0.1.1.0',
    'website': 'https://www.vperfectcs.com',
    'description': """
        Create Payment order and reconcile the payroll payable entries.
    """,
    'depends': ['om_hr_payroll_account'],
    'data': ['views/payslip_views.xml'],
    'images': ['static/description/banner.png'],
}
