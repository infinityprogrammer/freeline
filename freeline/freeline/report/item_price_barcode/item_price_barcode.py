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
	
	conditions = ""
	if filters.get("item_code"):
		conditions += """ and p.item_code = %(item_code)s """

	if filters.get("price_list"):
		conditions += """ and p.price_list = %(price_list)s """


	data = frappe.db.sql(
		"""
		SELECT item_code,item_name,uom,brand,price_list,price_list_rate,valid_from,valid_upto, 
		(SELECT group_concat(barcode) FROM `tabItem Barcode` b where b.parent = p.item_code)barcode,
		(SELECT item_arabic_name FROM `tabItem` i where i.name = p.item_code)item_arabic_name,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = p.item_code and um.uom = 'Carton')carton_factor,
		(SELECT collation FROM `tabItem` i where i.name = p.item_code)collation
		FROM `tabItem Price` p where 1=1 {0}""".format(conditions),filters,as_dict=1)

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
		{"label": _("Item Arabic Name"), "fieldname": "item_arabic_name", "width": 150},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Carton Factor"),
			"fieldname": "carton_factor",
			"fieldtype": "Data",
			"width": 100,
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
			"label": _("Barcode"),
			"fieldname": "barcode",
			"fieldtype": "Data",
			"width": 100,
		}
	]
