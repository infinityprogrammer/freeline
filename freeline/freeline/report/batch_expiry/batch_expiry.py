# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	
	conditions = ""
	# if not filters.get("company"):
	# 	return

	if filters.get("item_code"):
		conditions += " and b.item = %(item_code)s"
	
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and b.expiry_date between %(from_date)s and %(to_date)s"
	

	data = frappe.db.sql(
		"""
		SELECT led.company,b.batch_id, b.item, b.item_name,b.manufacturing_date,
		b.batch_qty, b.stock_uom,b.expiry_date,led.warehouse,led.actual_qty,
		datediff(b.expiry_date, curdate())day_dif,stock_value,
		(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = b.item order by conversion_factor desc limit 1)highest_uom,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = b.item 
		order by conversion_factor desc limit 1)highest_uom_factor,
		(led.actual_qty/ (SELECT conversion_factor FROM `tabUOM Conversion Detail` um 
		where um.parent = b.item order by conversion_factor desc limit 1)) as qty_in_huom,
		(select GROUP_CONCAT(supplier) from `tabItem Supplier` where `tabItem Supplier`.parent = b.item) as supplier
		FROM `tabBatch` b,
		(select sle.company,sle.batch_no,sle.item_code,sle.warehouse,sum(sle.actual_qty)actual_qty,
		sum(stock_value_difference)stock_value
		FROM `tabStock Ledger Entry` sle
		where sle.is_cancelled = 0 and sle.batch_no <> '' and sle.batch_no is not null
		group by sle.company,sle.batch_no,sle.item_code,sle.warehouse
		having sum(sle.actual_qty) <> 0)led 
		where b.batch_id = led.batch_no and b.item = led.item_code AND b.expiry_date is not null {0}""".format(conditions),filters,as_dict=1)

	return data

def get_columns():
	
	return [
		{
			"label": _("Item Code"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch_id",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 140,
		},
		{
			"label": _("Batch Qty"),
			"fieldname": "batch_qty",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 120,
		},
		{
			"label": _("Manufacturing Date"),
			"fieldname": "manufacturing_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Expiry Date"),
			"fieldname": "expiry_date",
			"fieldtype": "Date",
			"width": 160,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"label": _("Actual Qty WH"),
			"fieldname": "actual_qty",
			"fieldtype": "Float"
		},
		{
			"label": _("Exprire in Days"),
			"fieldname": "day_dif",
			"fieldtype": "Float"
		},
		{
			"label": _("Stock Value"),
			"fieldname": "stock_value",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Highest UOM"),
			"fieldname": "highest_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 110,
		},
		{
			"label": _("Highest UOM Factor"),
			"fieldname": "highest_uom_factor",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Qty in Hi UOM"),
			"fieldname": "qty_in_huom",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150,
		},
	]