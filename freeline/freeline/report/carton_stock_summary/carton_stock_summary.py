# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):

	if not filters:
		filters = {}
	columns = get_columns()
	stock = get_total_stock(filters)

	return columns, stock


def get_columns():
	columns = [
		_("Company") + ":Link/Company:250",
		_("Warehouse") + ":Link/Warehouse:150",
		_("Item") + ":Link/Item:150",
		_("Description") + "::300",
		_("Current Qty") + ":Float:100",
		_("Barcode") + ":Data:100",
		_("Supplier Ref") + ":Data:100",
		_("Qty in Carton") + ":Float:100",
		_("Highest UOM") + ":Link/UOM:130",
		_("Highest UOM Factor") + ":Float:140",
	]

	return columns


def get_total_stock(filters):
	conditions = ""
	columns = ""

	if filters.get("group_by") == "Warehouse":
		if filters.get("company"):
			conditions += " AND warehouse.company = %s" % frappe.db.escape(
				filters.get("company"), percent=False
			)

		conditions += " GROUP BY ledger.warehouse, item.item_code"
		columns += "'' as company, ledger.warehouse"
	else:
		conditions += " GROUP BY warehouse.company, item.item_code"
		columns += " warehouse.company, '' as warehouse"

	return frappe.db.sql(
		"""
			SELECT
				%s,
				item.item_code,
				item.description,
				sum(ledger.actual_qty) as actual_qty,
				(SELECT GROUP_CONCAT(barcode) FROM `tabItem Barcode` where `tabItem Barcode`.parent = item.name) as barcode,
				(select GROUP_CONCAT(supplier_part_no) from `tabItem Supplier` where `tabItem Supplier`.parent = item.name) as supplier_no,
				-- (SELECT conversion_factor FROM `tabUOM Conversion Detail` uf where uf.parent = item.item_code and uf.uom = 'Carton') as carton_factor,
    			((sum(ledger.actual_qty))/ (SELECT conversion_factor FROM `tabUOM Conversion Detail` uf where uf.parent = item.item_code and uf.uom = 'Carton')) as qty_in_carton,
				(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = item.item_code order by conversion_factor desc limit 1)highest_uom,
				(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = item.item_code order by conversion_factor desc limit 1)highest_uom_factor
			FROM
				`tabBin` AS ledger
			INNER JOIN `tabItem` AS item
				ON ledger.item_code = item.item_code
			INNER JOIN `tabWarehouse` warehouse
				ON warehouse.name = ledger.warehouse
			WHERE
				ledger.actual_qty != 0 %s"""
		% (columns, conditions)
	)
