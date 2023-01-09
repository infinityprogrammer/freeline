# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _
from frappe.utils import flt, today



def execute(filters=None):
	if not filters.get("company"):
		return 0;
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters):
	
	conditions = ""
	if filters.get("item_group"):
		conditions += """ and item_group = %(item_group)s """

	data = frappe.db.sql(
		"""
		SELECT name as item_code,item_name,description,item_group, 'No' seasonal,
		(SELECT sum(actual_qty) FROM `tabBin` bin where bin.item_code = item.name and 
		warehouse in (SELECT name FROM `tabWarehouse` where company = %(company)s))current_stock,
		(SELECT stock_value FROM `tabStock Ledger Entry` sle where is_cancelled = 0 and sle.item_code = item.name 
		and company = %(company)s
		order by posting_date desc limit 1)cost, 
		(select datediff(curdate(),sle.posting_date)age_day from `tabStock Ledger Entry` sle where 
		sle.voucher_type in ('Purchase Receipt','Purchase Invoice')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s order by posting_date desc limit 1)average_ageing,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 30)sold_m1,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 60)sold_m2,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 90)sold_m3,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 120)sold_m4,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 150)sold_m5,
		(SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 180)sold_m6, 
		(SELECT abs(sum(actual_qty))/6 FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 180)avg_qty_m6, 
		round(((SELECT sum(actual_qty) FROM `tabBin` bin where bin.item_code = item.name and 
		warehouse in (SELECT name FROM `tabWarehouse` where company = %(company)s))/
		(SELECT abs(sum(actual_qty))/6 FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
		and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
		and datediff(curdate(),sle.posting_date) <= 180)),2)stock_cover,
		(SELECT sum(amount) FROM `tabSales Invoice` sl, `tabSales Invoice Item` it
		where sl.name = it.parent and sl.docstatus = 1 and it.item_code = item.name and company=  %(company)s)turnover
		FROM tabItem item where 1=1 {0}""".format(conditions),filters,as_dict=1)

	return data

def get_columns():
	return [
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 100},
		{"label": _("Description"), "fieldname": "description", "width": 200},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100,
		},
		{"label": _("Seasonal"), "fieldname": "seasonal", "width": 200},
		{
			"label": _("Current Stock"),
			"fieldname": "current_stock",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Cost"),
			"fieldname": "cost",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Average Ageing"),
			"fieldname": "average_ageing",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Sold M1"),
			"fieldname": "sold_m1",
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"label": _("Sold M2"),
			"fieldname": "sold_m2",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Sold M3"),
			"fieldname": "sold_m3",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Sold M4"),
			"fieldname": "sold_m4",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Sold M5"),
			"fieldname": "sold_m5",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Sold M6"),
			"fieldname": "sold_m6",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Stock Cover"),
			"fieldname": "stock_cover",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Turnover"),
			"fieldname": "turnover",
			"fieldtype": "Float",
			"width": 100
		}
	]

