# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
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
		{"label": _("Item Name"), "fieldname": "item_name", "width": 250},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 170,
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 140,
		},
		{
			"label": _("Qty in WH"),
			"fieldname": "actual_qty_in_wh",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Qty in WH HiUOM"),
			"fieldname": "actual_qty_huom",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("WH Reorder Level"),
			"fieldname": "warehouse_reorder_level",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("WH Reorder Qty"),
			"fieldname": "warehouse_reorder_qty",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("WH Reorder Qty HiUOM"),
			"fieldname": "warehouse_reorder_qty_hiuom",
			"fieldtype": "Float",
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
			"fieldname": "conversion_factor",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Collation"),
			"fieldname": "collation",
			"fieldtype": "Data",
			"width": 100,
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
		{
			"label": _("Supplier Part No"),
			"fieldname": "supplier_part_no",
			"fieldtype": "Data",
			"width": 130,
		}
	]



def get_data(filters):

	conditions = ""
	
	if filters.get("item_group"):
		conditions += " and it.item_group = %(item_group)s"
	
	if filters.get("brand"):
		conditions += " and it.brand = %(brand)s"

	data = frappe.db.sql(
		"""
		SELECT r.parent as item_code,it.item_name,it.item_group, r.warehouse, warehouse_reorder_level, 
		warehouse_reorder_qty,actual_qty as actual_qty_in_wh,it.brand, it.collation, 
		(SELECT group_concat(bc.barcode) FROM `tabItem Barcode` bc where bc.parent = it.name)barcode,
		(SELECT branch FROM `tabWarehouse` where name = r.warehouse)branch,
		(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = it.name order by conversion_factor desc limit 1)highest_uom,
		(actual_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = it.name order by conversion_factor desc limit 1))actual_qty_huom,
		(warehouse_reorder_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = it.name order by conversion_factor desc limit 1))warehouse_reorder_qty_hiuom,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = it.name order by conversion_factor desc limit 1)conversion_factor,
		(SELECT group_concat(supplier_part_no) FROM `tabItem Supplier` s where s.parent = it.name)supplier_part_no
		FROM `tabItem Reorder` r
		INNER JOIN `tabItem` it ON r.parent = it.name
		LEFT JOIN `tabBin` bin ON bin.item_code = r.parent and r.warehouse = bin.warehouse 
		where 1=1 {0}""".format(conditions),filters,as_dict=1)

	return data