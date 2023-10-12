from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe import _
import json
import datetime

def set_rebate_empty(self, args):
    if self.rebate_duration:
        invs = frappe.db.sql(""" UPDATE `tabRental Invoices` SET voucher_no = NULL, amount = 0  WHERE voucher_no = %(voucher_no)s""",
                                    {'voucher_no': self.name}, as_dict=True)

def validate_overdue_limit(self, args):
    
    if self.docstatus == 1:
        return

    overdue_limt_days = frappe.db.get_value('Customer', self.customer, 'overdue_days')
    role_allow = frappe.db.get_single_value('Tiejan Internal Settings', 'role_allowed_overdue_customer')
    alert_on_overdue = frappe.db.get_single_value('Tiejan Internal Settings', 'alert_on_overdue_in_days')
    
    user_roles = frappe.get_roles()

    over_due_day = get_over_due_days(self.customer, self.company)

    if over_due_day:
        if over_due_day >= alert_on_overdue:
            frappe.msgprint('Customer overdue day reached {0} days, Maximum {1}'.format(over_due_day, overdue_limt_days));
    

    if overdue_limt_days:
        if role_allow:
            
            over_due_inv = frappe.db.sql(""" SELECT name, customer ,posting_date, due_date, datediff(CURDATE(), due_date)diff 
                                            FROM `tabSales Invoice` where docstatus = 1 and status = 'Overdue'
                                            and outstanding_amount > 0 and is_return = 0 and customer = %(customer)s
                                            and company = %(company)s
                                            and datediff(CURDATE(), due_date) > %(overdue_limt_days)s""",
                                        {'customer': self.customer,'company': self.company,'overdue_limt_days':overdue_limt_days}, as_dict=True)
            
            for row in over_due_inv:
                if role_allow in user_roles:
                    frappe.msgprint("Invoice {0} exceed overdue limit days {1}".format(row.name, overdue_limt_days));
                else:
                    frappe.throw("Invoice {0} exceed overdue limit days {1}".format(row.name, overdue_limt_days))

def get_over_due_days(customer, company):
    over_due_inv = frappe.db.sql("""SELECT max(datediff(curdate(), due_date))days 
                                    FROM `tabSales Invoice` where docstatus = 1 and status = 'Overdue'
                                    and customer = %(customer)s and company = %(company)s""",
                                    {'customer': customer,'company': company}, as_dict=True)
    if over_due_inv:
        if over_due_inv[0].days:
            return over_due_inv[0].days
        else:
            return 0
    else: 
        return 0

def set_pick_list_barcode(self, args):

    for row in self.locations:
        barcode = get_item_barcode(row.item_code)
        if barcode:
            row.barcode = barcode
            row.partial_barcode = barcode[-5:]

def get_item_barcode(item_code):
    barcode = frappe.db.sql(""" SELECT GROUP_CONCAT(barcode)barcode_str FROM `tabItem Barcode` where `tabItem Barcode`.parent = %(item_code)s  """,{'item_code':item_code}, as_dict=True)
    if barcode:
        if barcode[0].barcode_str:
            return barcode[0].barcode_str
        else:
            return None
    return None
