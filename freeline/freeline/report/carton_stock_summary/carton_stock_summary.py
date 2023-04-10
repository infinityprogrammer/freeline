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
		_("Branch ID") + ":Data:120",
		_("Item") + ":Link/Item:150",
		_("Item Name") + ":Data:150",
		_("Arabic Item Name") + ":Data:150",
		_("Description") + "::300",
		_("Brand") + ":Link/Brand:150",
		_("Current Qty") + ":Float:100",
		_("Barcode") + ":Data:100",
		_("Supplier Ref") + ":Data:100",
		# _("Qty in Carton") + ":Float:100",
		_("Highest UOM") + ":Link/UOM:130",
		_("Hi-UOM Factor") + ":Float:140",
		_("QTY Hi-UOM") + ":Float:140",
	]

	return columns


def get_total_stock(filters):
	conditions = ""
	columns = ""

	if filters.get("group_by") == "Warehouse":
		if filters.get("company"):
			company_list = filters.get("company")
			print(company_list)

			conditions += " AND warehouse.company in %(company)s"

		conditions += " GROUP BY ledger.warehouse, item.item_code"
		columns += "'' as company, ledger.warehouse, (select branch_id FROM `tabWarehouse` w where w.name = ledger.warehouse)branch_id"
	else:
		conditions += " GROUP BY warehouse.company, item.item_code"
		columns += " warehouse.company, '' as warehouse, '' as branch_id"

	return frappe.db.sql(
		"""
			SELECT
				{0},
				item.item_code,
				item.item_name,
				item.item_arabic_name,
				item.description,
				item.brand,
				sum(ledger.actual_qty) as actual_qty,
				(SELECT GROUP_CONCAT(barcode) FROM `tabItem Barcode` where `tabItem Barcode`.parent = item.name) as barcode,
				(select GROUP_CONCAT(supplier_part_no) from `tabItem Supplier` where `tabItem Supplier`.parent = item.name) as supplier_no,
				-- (SELECT conversion_factor FROM `tabUOM Conversion Detail` uf where uf.parent = item.item_code and uf.uom = 'Carton') as carton_factor,
    			-- ((sum(ledger.actual_qty))/ (SELECT conversion_factor FROM `tabUOM Conversion Detail` uf where uf.parent = item.item_code and uf.uom = 'Carton')) as qty_in_carton,
				(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = item.item_code order by conversion_factor desc limit 1)highest_uom,
				(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = item.item_code order by conversion_factor desc limit 1)highest_uom_factor,
				((sum(ledger.actual_qty))/ (SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = item.item_code order by conversion_factor desc limit 1)) as qty_in_huom
			FROM
				`tabBin` AS ledger
			INNER JOIN `tabItem` AS item
				ON ledger.item_code = item.item_code
			INNER JOIN `tabWarehouse` warehouse
				ON warehouse.name = ledger.warehouse
			WHERE
				ledger.actual_qty != 0 {1}""".format(columns, conditions), filters)
