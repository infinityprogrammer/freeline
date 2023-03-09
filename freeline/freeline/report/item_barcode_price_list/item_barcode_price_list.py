# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	return [
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 140,
		},
		# {
		# 	"label": _("Item Group Parent"),
		# 	"fieldname": "item_group_parent",
		# 	"fieldtype": "Link",
		# 	"options": "Item Group",
		# 	"width": 140,
		# },
		{"label": _("Item Name"), "fieldname": "item_name", "width": 250},
		{"label": _("Item Arabic Name"), "fieldname": "item_arabic_name", "width": 250},
		{
			"label": _("Highest UOM"),
			"fieldname": "highest_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 110,
		},
		{
			"label": _("Highest UOM Factor"),
			"fieldname": "conversion_factor",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Price List Rate"),
			"fieldname": "price_list_rate",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 100,
		},
		{
			"label": _("Barcode"),
			"fieldname": "barcode",
			"fieldtype": "Data",
			"width": 100,
		},
	]

def get_data(filters):

	conditions = ""
	if not filters.get("price_list"):
		return

	if filters.get("item_code"):
		conditions += " and item.item_code = %(item_code)s"
	
	if filters.get("is_stock_item"):
		conditions += " and item.is_stock_item = %(is_stock_item)s"
	
	if filters.get("item_group"):
		conditions += " and item.item_group = %(item_group)s"


	data = frappe.db.sql(
		"""
		SELECT name,item_code,item_name,item_group,item_arabic_name,brand,
		(SELECT group_concat(bc.barcode) FROM `tabItem Barcode` bc where bc.parent = item.name)barcode,collation, 
		(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = item.name order by conversion_factor desc limit 1)highest_uom,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = item.name order by conversion_factor desc limit 1)conversion_factor,
		(SELECT group_concat(supplier) FROM `tabItem Supplier` s where s.parent = item.name)supplier,
		(SELECT group_concat(supplier_part_no) FROM `tabItem Supplier` s where s.parent = item.name)supplier_part_no,
		(SELECT parent_item_group FROM `tabItem Group` where name = item.item_group)item_group_parent,
		(SELECT price_list_rate FROM `tabItem Price` p where p.item_code = item.item_code 
		and p.uom =  (SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = item.name order by conversion_factor desc limit 1)
		and price_list = %(price_list)s)price_list_rate
		FROM `tabItem` item where item.disabled = 0 {0}""".format(conditions),filters,as_dict=1)

	return data