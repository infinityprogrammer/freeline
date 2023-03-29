# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns()
	return columns, data


def get_data(filters):
	conditions = ""
	if filters.get("employee"):
		conditions = " and employee = %(employee)s"

	if not filters.get("company"):
		return
	
	data = frappe.db.sql(
		"""
		SELECT * FROM (
		SELECT 'Payment Entry' voucher_type, name as voucher_no,company,posting_date,party,party_name,employee,
		employee_name,status,unallocated_amount FROM `tabPayment Entry` where unallocated_amount > 0
		and payment_type = 'Receive' and party_type = 'Customer' and docstatus = 1 and company = %(company)s
		union all
		SELECT 'Sales Invoice' voucher_type,name as voucher_no,company,posting_date,customer,customer_name,employee,employee_name,status,outstanding_amount 
		FROM `tabSales Invoice` where outstanding_amount != 0 and docstatus = 1 and company = %(company)s)a1 where 1=1 {0}""".format(conditions),filters,as_dict=1)

	return data

def get_columns():
	return [
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 120},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Customer"),
			"fieldname": "party",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 130,
		},
		{
			"label": _("Customer Name"),
			"fieldname": "party_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 200,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Pending Amount"),
			"fieldname": "unallocated_amount",
			"fieldtype": "Float",
			"width": 160,
		},
	]