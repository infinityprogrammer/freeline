# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _
from frappe.utils import flt, today
from erpnext import get_company_currency, get_default_company


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns(filters)

	return columns, data


def get_data(filters):

	conditions = ""

	if not filters.get("company") or not filters.get("from_date") or not filters.get("to_date"):
		return
	if not filters.get("customer_branch") or not filters.get("account"):
		return

	if filters.get("warehouse"):
		conditions += " and si.set_warehouse = %(warehouse)s"

	conditions += " and gl.account IN %(account)s"

	data = frappe.db.sql(
		"""
		SELECT si.company,si.posting_date,si.set_warehouse,si.name,customer,customer_name,gl.account,
		grand_total,outstanding_amount,si.currency,(gl.debit_in_account_currency - gl.credit_in_account_currency)recieved_amount
		FROM `tabSales Invoice` si ,`tabGL Entry` gl where si.name = gl.voucher_no
		and gl.voucher_type = 'Sales Invoice' and si.company = %(company)s and si.posting_date 
		between %(from_date)s and %(to_date)s {0}""".format(conditions),filters,as_dict=1)

	return data

def get_columns(filters):

	return [
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 140,
		},
		{
			"label": _("Sales Invoice"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "set_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 100,
		},
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Data",
			"width": 190,
		},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Float",
			"width": 190,
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Float",
			"width": 190,
		},
		{
			"label": _("Recieved Amount"),
			"fieldname": "recieved_amount",
			"fieldtype": "Float",
			"width": 190,
		},
	]