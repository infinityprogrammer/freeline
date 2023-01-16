# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.utils import flt, today


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	
	return [
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 140,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Item Arabic Name"),
			"fieldname": "item_arabic_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Valuation Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 140,
		},
	]

def get_data(filters):
	
	condition = ""
	if filters.get("item_code"):
		condition += " and item.item_code = %(item_code)s "

	if filters.get("item_group"):
		condition += " and item.item_group = %(item_group)s "

	data = frappe.db.sql(""" SELECT item_code,item_name,item_group,stock_uom,ifnull((select round(valuation_rate, 2) from `tabStock Ledger Entry` sle force index (item_code)
							where sle. item_code = item.item_code AND valuation_rate > 0 AND is_cancelled = 0
							order by posting_date desc, posting_time desc, name desc limit 1),0) as valuation_rate
							FROM `tabItem` item where 1=1 {condition}""".format(condition=condition),filters,as_dict=1)
	return data