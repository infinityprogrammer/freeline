# Copyright (c) 2024, RAFI and contributors
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
			"width": 160,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 190,
		},
		{
			"label": _("Actual Qty"),
			"fieldname": "actual_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "width": 130},
		{
			"label": _("QTY in Hi UOM"),
			"fieldname": "hi_uom_qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Hi UOM Volume (1 Unit)"),
			"fieldname": "hi_uom_volume",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Volumetric Occupancy"),
			"fieldname": "volumetric_occupancy",
			"fieldtype": "Data",
			"width": 170,
		},
		{
			"label": _("Volumetric in One Pallet"),
			"fieldname": "volume_one_pallet",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Pallet Required"),
			"fieldname": "pallet_req",
			"fieldtype": "Float",
			"width": 160,
		}
	]

def get_data(filters):

	conditions = ""
	
	if filters.get("warehouse"):
		conditions += " and bin.warehouse = %(warehouse)s"
	
	if filters.get("item_code"):
		conditions += " and bin.item_code = %(item_code)s"

	data = frappe.db.sql(
		"""
		SELECT item_code, warehouse, actual_qty, stock_uom,
		round(actual_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = bin.item_code 
		order by conversion_factor desc limit 1), 3)hi_uom_qty,
		(select hi_uom_volume from `tabItem` item where item.item_code = bin.item_code)hi_uom_volume,
		round(actual_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = bin.item_code 
		order by conversion_factor desc limit 1), 3)*
		(select hi_uom_volume from `tabItem` item where item.item_code = bin.item_code)volumetric_occupancy,
		(select hi_uom_volume * hi_uom_pallets_capacity from `tabItem` item where item.item_code = bin.item_code)volume_one_pallet,
		CEIL(round(actual_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = bin.item_code 
		order by conversion_factor desc limit 1), 3)*
		ifnull((select hi_uom_volume from `tabItem` item where item.item_code = bin.item_code)/
		(select hi_uom_volume * hi_uom_pallets_capacity from `tabItem` item where item.item_code = bin.item_code), 0))pallet_req
		FROM `tabBin` bin where actual_qty > 0 {0} order by item_code""".format(conditions),filters,as_dict=1)

	return data

