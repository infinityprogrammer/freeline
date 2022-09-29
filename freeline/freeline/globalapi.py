from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe import _
import json
import datetime

# Number Card APIs for Dashboard

@frappe.whitelist()
def get_total_sale_ytd(filters=None):
    
    # yr =[]
    now_year = datetime.datetime.now().year
    # yr.append(now_year)
    # filters['year_dt'] = yr
    context = {}
    # print(filters)
    
    ytd_sale = frappe.db.sql(""" SELECT ifnull(round(sum(grand_total),2),0)sale FROM `tabSales Invoice` where YEAR(posting_date) = %(year)s
                                and docstatus = 1""",
                                {'year': now_year}, as_dict=True)
    context['value'] = ytd_sale[0].sale
    context['fieldtype'] = "Currency"
    ytd_sale_value = ytd_sale[0].sale
    return ytd_sale_value

@frappe.whitelist()
def get_total_sale_mtd():
    currentDate = datetime.date.today()
    firstDayOfMonth = datetime.date(currentDate.year, currentDate.month, 1)
    context = {}
    # print("filters ")
    # print(filters)
    mtd_sale = frappe.db.sql(""" SELECT ifnull(round(sum(grand_total),2),0)sale FROM `tabSales Invoice` where posting_date between %(start_date)s and %(end_date)s
                                and docstatus = 1""",
                                {'start_date': firstDayOfMonth,'end_date':currentDate}, as_dict=True)
    context['value'] = mtd_sale[0].sale
    context['fieldtype'] = "Currency"
    mtd_sale_value = mtd_sale[0].sale
    return mtd_sale_value

@frappe.whitelist()
def get_total_sale_order_mtd():
    currentDate = datetime.date.today()
    firstDayOfMonth = datetime.date(currentDate.year, currentDate.month, 1)
    context = {}
    mtd_sale = frappe.db.sql(""" SELECT ifnull(sum(grand_total),0)sale FROM `tabSales Order` where status != 'Closed'
                                and per_delivered = 100 and per_billed < 100
                                and docstatus = 1 AND transaction_date between %(start_date)s and %(end_date)s""",
                                {'start_date': firstDayOfMonth,'end_date':currentDate}, as_dict=True)
    context['value'] = mtd_sale[0].sale
    context['fieldtype'] = "Currency"
    mtd_sale_value = mtd_sale[0].sale
    return mtd_sale_value

# custom APIs for SFA

@frappe.whitelist()
def get_all_order_items_by_name():
    sale_order_name = frappe.db.sql(""" SELECT name FROM `tabSales Order` 
                                where docstatus = 1""", as_dict=True)
    sales_order_items = []
    for d in sale_order_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        items = frappe.db.sql(""" SELECT item_code,qty FROM `tabSales Order Item` b
                                where b.parent =  %(parent)s
                                and b.docstatus = 1""",{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_order_items.append(item_details)
    return sales_order_items

@frappe.whitelist()
def get_all_invoice_items_by_name():
    sale_invoice_name = frappe.db.sql(""" SELECT name FROM `tabSales Invoice`
                                where docstatus = 1""", as_dict=True)
    sales_invoice_items = []
    for d in sale_invoice_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        items = frappe.db.sql(""" SELECT item_code,qty FROM `tabSales Invoice Item` b
                                    where b.parent =  %(parent)s
                                    and b.docstatus = 1""",{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_invoice_items.append(item_details)
    return sales_invoice_items

@frappe.whitelist()
def get_overdue_outstanding(filters):
    overdue_outstand = frappe.db.sql(""" SELECT ifnull(sum(outstanding_amount),0)amount FROM `tabSales Invoice` where company = %(company)s and docstatus = 1""",{'company':'INFINITY'}, as_dict=True)
    
    overdue_outstand_val = overdue_outstand[0].amount
    return overdue_outstand_val

@frappe.whitelist()
def get_item_barcode(item_code):
    barcode = frappe.db.sql(""" SELECT GROUP_CONCAT(barcode)barcode_str FROM `tabItem Barcode` where `tabItem Barcode`.parent = %(item_code)s  """,{'item_code':item_code}, as_dict=True)
    
    barcode_val = barcode[0].barcode_str
    return barcode_val


@frappe.whitelist()
def get_invoice_items_by_driver(driver=None):
    
    condition =""
    if driver:
        condition += " and driver = %(driver)s"
    
    sale_invoice_name = frappe.db.sql(""" SELECT name,posting_date,customer,driver FROM `tabSales Invoice`
                                where docstatus = 1 {condition}""".format(condition=condition),{'driver':driver}, as_dict=True)
    sales_invoice_items = []
    for d in sale_invoice_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        item_details['customer'] = d.customer
        item_details['posting_date'] = d.posting_date
        item_details['driver'] = d.driver
        items = frappe.db.sql(""" SELECT item_code,qty,uom,delivered_qty FROM `tabSales Invoice Item` b
                                    where b.parent =  %(parent)s
                                    and b.docstatus = 1 """,{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_invoice_items.append(item_details)
    return sales_invoice_items