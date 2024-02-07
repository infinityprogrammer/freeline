# Copyright (c) 2024, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	return [
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 160,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 190,
		},
		{
			"label": _("Branch ID"),
			"fieldname": "branch_id",
			"fieldtype": "Data",
			"width": 85,
		},
		{"label": _("Pallet Capacity (Floor)"), "fieldname": "pallet_capacity_on_floor", "width": 180},
		{"label": _("Pallet Capacity (Rack)"), "fieldname": "pallet_capacity_on_rack", "width": 180},
		{
			"label": _("Total Pallet Capacity"),
			"fieldname": "total_capacity",
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
			"label": _("Pallets Occupancy"),
			"fieldname": "pallet_occupancy",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Empty Pallets"),
			"fieldname": "empty_pallet",
			"fieldtype": "Float",
			"width": 160,
		}
	]

def get_data(filters):

	conditions = ""

	if filters.get("company"):
		conditions += " and wh.company in %(company)s"
	
	if filters.get("warehouse"):
		conditions += " and wh.name = %(warehouse)s"

	data = frappe.db.sql(
		"""
		SELECT company, name, branch_id, pallet_capacity_on_floor, pallet_capacity_on_rack,
		(pallet_capacity_on_floor + pallet_capacity_on_rack)total_capacity, 0 total_pallet_occuppied 
		FROM `tabWarehouse` wh where is_group = 0 {0}""".format(conditions),filters,as_dict=1)

	for row in data:
		wh_data = get_warehouse_occupied(row.name)

		row['volumetric_occupancy'] = wh_data[0].volumetric_occupancy
		row['pallet_occupancy'] = wh_data[0].pallet_req
		row['empty_pallet'] = flt(row.total_capacity) - wh_data[0].pallet_req

	return data

def get_warehouse_occupied(wh):

	pallet = frappe.db.sql(
		"""
		SELECT ifnull(sum(volumetric_occupancy), 0)volumetric_occupancy, ifnull(sum(pallet_req), 0)pallet_req FROM (
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
		FROM `tabBin` bin where actual_qty > 0
		and warehouse = %(wh)s)a1""",{'wh': wh},as_dict=1)

	return pallet