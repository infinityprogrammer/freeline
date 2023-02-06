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



def get_data(filters):
	
	if not filters.get("fiscal_year"):
		return

	conditions = ""
	if filters.get("item_code"):
		conditions += """ and item.item_code = %(item_code)s """

	if filters.get("item_group"):
		conditions += """ and item.item_group = %(item_group)s """

	if filters.get("brand"):
		conditions += """ and item.brand = %(brand)s """
	

	data = frappe.db.sql(
		"""
		SELECT item_code,item_name,item_group,brand,
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=1 
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)jan,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=2 
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)feb,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=3
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)mar,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=4 
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)apr,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=5
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)may,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=6 
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)jun,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=7
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)july,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=8 
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)aug,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=9
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)sep,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=10
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)oct,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=11
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)nov,
		--
		(SELECT ifnull(round(avg(valuation_rate), 2),0)
		FROM `tabStock Ledger Entry` sle where YEAR(sle.posting_date) = %(fiscal_year)s and MONTH(sle.posting_date)=12
		and sle.is_cancelled=0 and sle.item_code = item.item_code AND company = %(company)s)dece
		--
		FROM `tabItem` item where 1=1 {0}""".format(conditions),filters,as_dict=1)

	return data



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
			"label": _("January {0}".format(filters.get('fiscal_year'))),
			"fieldname": "jan",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("February {0}".format(filters.get('fiscal_year'))),
			"fieldname": "feb",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("March {0}".format(filters.get('fiscal_year'))),
			"fieldname": "mar",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("April {0}".format(filters.get('fiscal_year'))),
			"fieldname": "apr",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("May {0}".format(filters.get('fiscal_year'))),
			"fieldname": "may",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("June {0}".format(filters.get('fiscal_year'))),
			"fieldname": "jun",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("July {0}".format(filters.get('fiscal_year'))),
			"fieldname": "july",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("August {0}".format(filters.get('fiscal_year'))),
			"fieldname": "aug",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("September {0}".format(filters.get('fiscal_year'))),
			"fieldname": "sep",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("October {0}".format(filters.get('fiscal_year'))),
			"fieldname": "oct",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("November {0}".format(filters.get('fiscal_year'))),
			"fieldname": "nov",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Decemeber {0}".format(filters.get('fiscal_year'))),
			"fieldname": "dece",
			"fieldtype": "Float",
			"width": 130,
		},
	]
