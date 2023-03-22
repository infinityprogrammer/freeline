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
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 200,
		},
		{
			"label": _("Employee Count"),
			"fieldname": "count",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Employees"),
			"fieldname": "employees",
			"fieldtype": "Data",
			"width": 200,
		},
	]

def get_data(filters):

	if not filters.get("company"):
		return

	data = frappe.db.sql(
		"""
		SELECT voucher_no,count(distinct employee )count,group_concat(employee_name)employees FROM (
		SELECT voucher_no,against_voucher,(select employee from `tabSales Invoice` inv where inv.name = against_voucher)employee,
		(select employee_name from `tabSales Invoice` inv where inv.name = against_voucher)employee_name
		FROM `tabGL Entry` WHERE voucher_no in
		(SELECT gl.voucher_no
		FROM `tabSales Invoice` si, `tabGL Entry` gl where si.name = gl.against_voucher and gl.voucher_no != gl.against_voucher
		and gl.voucher_type = 'Journal Entry' and gl.is_cancelled=0 and gl.company = %(company)s) and against_voucher is not null and against_voucher != ''
		)a1 where voucher_no not in (SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(content, '<p>', -1), '</p>', 1)val 
		FROM `tabComment` where comment_type = 'Comment' and reference_name = voucher_no)
		group by voucher_no having count(distinct employee)>1""",filters,as_dict=1)

	return data