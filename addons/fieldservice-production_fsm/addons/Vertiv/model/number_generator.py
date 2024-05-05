from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
import random
import threading
from datetime import date, datetime, timedelta
from psycopg2 import sql
import requests
import json
from requests import Request, Session


class ReportSerialGenerator(models.Model):

    _name = "report.serial.generator"
    _description = "Report number generator"
    _rec_name='group_name'

    group_name = fields.Char("Group Name")
    last_gen_date=fields.Date()
    last_used_number=fields.Integer()








