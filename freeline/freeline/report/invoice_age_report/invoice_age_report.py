# Copyright (c) 2023, RAFI and contributors
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
			"label": _("Sales Invoice"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Sales Rep"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 140,
		},
		{
			"label": _("Branch ID"),
			"fieldname": "site_id",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Sales Team"),
			"fieldname": "sales_team",
			"fieldtype": "Data",
			"width": 100,
		},
		{"label": _("Invoice Date"), "fieldname": "posting_date", "fieldtype": "Date","width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data","width": 100},
		{"label": _("Currency"), "fieldname": "currency","fieldtype": "Link", "options": "Currency","width": 80},
		{"label": _("Brand"), "fieldname": "brand","fieldtype": "Link", "options": "Brand","width": 80},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 110,
		},
		{
			"label": _("Base Grand Total"),
			"fieldname": "base_grand_total",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 110,
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"label": _("Last Payment Date"),
			"fieldname": "last_payment",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Last Payment Voucher"),
			"fieldname": "last_payment_id",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Last Payment Amount"),
			"fieldname": "last_payment_amt",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Age"),
			"fieldname": "pay_age",
			"fieldtype": "Int",
			"width": 100,
		}
	]

def get_data(filters):

	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and inv.posting_date between %(from_date)s and %(to_date)s"
	
	if filters.get("customer"):
		conditions += " and inv.customer = %(customer)s"

	if filters.get("employee"):
		conditions += " and inv.employee = %(employee)s"

	data = frappe.db.sql(
		"""
		SELECT name, customer, employee, posting_date, status,currency,grand_total,outstanding_amount,inv.brand,inv.base_grand_total,
		(SELECT gl.posting_date FROM `tabGL Entry` gl where against_voucher = inv.name
		and is_cancelled = 0 and gl.voucher_no != gl.against_voucher order by gl.posting_date desc limit 1)last_payment,
		(SELECT gl.voucher_no FROM `tabGL Entry` gl where against_voucher = inv.name
		and is_cancelled = 0 and gl.voucher_no != gl.against_voucher order by gl.posting_date desc limit 1)last_payment_id, 
		(SELECT abs((sum(debit_in_account_currency - credit_in_account_currency))) 
		FROM `tabGL Entry` gl where against_voucher = inv.name
		and is_cancelled = 0 and gl.voucher_no != gl.against_voucher 
		order by gl.posting_date desc limit 1)last_payment_amt,
		(SELECT customer_group FROM `tabCustomer` c where c.name = inv.customer)customer_group, inv.site_id,
		(SELECT group_concat(distinct sp.parent_sales_person) FROM `tabSales Person` sp where 
		sp.employee = inv.employee)sales_team,
		DATEDIFF(ifnull((SELECT gl.posting_date FROM `tabGL Entry` gl where against_voucher = inv.name
		and is_cancelled = 0 and gl.voucher_no != gl.against_voucher order by gl.posting_date desc limit 1), curdate()),inv.posting_date)pay_age
		FROM `tabSales Invoice` inv where inv.docstatus = 1 and inv.is_return = 0 {0}""".format(conditions),filters,as_dict=1)

	return data