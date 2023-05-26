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


def get_data(filters):
	
	conditions = " where 1=1"
	if filters.get("item_code"):
		conditions += """ and p.item_code = %(item_code)s """

	if filters.get("price_list"):
		conditions += """ and p.price_list = %(price_list)s """


	data = frappe.db.sql(
		"""
		SELECT item_code, uom, item_name, brand,price_list_rate,currency,price_list,
		concat('<b>', round((price_list_rate/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = p.item_code and uom = p.uom) * (SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = p.item_code 
		order by conversion_factor desc limit 1)), 3),'</b>')price_in_hiuom,
		(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = p.item_code order by conversion_factor desc limit 1)highest_uom,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = p.item_code 
		order by conversion_factor desc limit 1)highest_uom_factor,
		(SELECT group_concat(barcode) FROM `tabItem Barcode` b where b.parent = p.item_code)barcode,
		(SELECT group_concat(supplier_part_no) FROM `tabItem Supplier` supp where supp.parent = p.item_code) as supplier_no
		FROM `tabItem Price` p {0}""".format(conditions),filters,as_dict=1)

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
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
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
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 90,
		},
		{
			"label": _("Price List"),
			"fieldname": "price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 130,
		},
		{
			"label": _("Price List Rate"),
			"fieldname": "price_list_rate",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("<b>Hi-UOM Rate</b>"),
			"fieldname": "price_in_hiuom",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Hi-UOM"),
			"fieldname": "highest_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 130,
		},
		{
			"label": _("Hi-UOM Factor"),
			"fieldname": "highest_uom_factor",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Barcode"),
			"fieldname": "barcode",
			"fieldtype": "Data",
			"width": 100,
		}
	]
