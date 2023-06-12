# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.utils import flt, today



def execute(filters=None):
	columns, data = [], []

	data = get_data(filters)
	columns = get_columns(filters)

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
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 140,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 140,
		},
		{
			"label": _("Month"),
			"fieldname": "month1",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Year"),
			"fieldname": "year1",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Valuation Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Float",
			"width": 130,
		},
	]



def get_data(filters):
	
	conditions = ""
	if filters.get("item_code"):
		conditions += """ and item.item_code = %(item_code)s """

	if filters.get("item_group"):
		conditions += """ and item.item_group = %(item_group)s """

	if filters.get("brand"):
		conditions += """ and item.brand = %(brand)s """

	if filters.get("is_stock_item"):
		conditions += """ and item.is_stock_item = %(is_stock_item)s """

	data = frappe.db.sql(
		"""
		SELECT item_code, month1,year1,valuation_rate,
		(select item_name from `tabItem` where name = a1.item_code)item_name,
		(select item_group from `tabItem` where name = a1.item_code)item_group,
		(select brand from `tabItem` where name = a1.item_code)brand
		FROM (
		SELECT item.item_code,
		MONTH(sle.posting_date)month1,
		YEAR(sle.posting_date)year1,
		ifnull(round(avg(sle.valuation_rate), 2),0)valuation_rate
		FROM `tabItem` item 
		LEFT JOIN `tabStock Ledger Entry` sle
		ON item.name = sle.item_code
		where sle.is_cancelled = 0 and sle.company = %(company)s {0} 
		group by item.item_code,MONTH(sle.posting_date),YEAR(sle.posting_date)
		order by sle.item_code, sle.posting_date )a1""".format(conditions),filters,as_dict=1)

	return data
