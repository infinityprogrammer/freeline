# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	data = SalesInvoiceData(filters).generate()
	columns = get_columns()

	return columns, data

class SalesInvoiceData:

	def __init__(self, filters, data = None):
		self.filters = filters
		self.data = data

	def generate(self):
		self.data = self.get_outstanding_invoice()
		return self.data

	def get_outstanding_invoice(self):

		conditions = ""

		if self.filters.get("from_date") and self.filters.get("to_date"):
			conditions += " and inv.posting_date between %(from_date)s and %(to_date)s"

		if self.filters.get("sales_person"):
			sales_p = []
			sales_p.append("A")
			for ps in self.filters.get("sales_person"):
				lft, rgt = frappe.db.get_value("Sales Person", ps, ["lft", "rgt"])
				sales_pers = frappe.db.sql(
					"""
					select employee from `tabSales Person` where lft >= %s and rgt <= %s and is_group = 0
					""",
					(lft, rgt),
					as_dict=1,
				)
				for s in sales_pers:
					sales_p.append(s.employee)
			self.filters['sales_person'] = sales_p
			conditions += " and inv.employee in %(sales_person)s"
		
		if self.filters.get("company"):
			conditions += " and inv.company in %(company)s"

		data = frappe.db.sql(
		"""
		SELECT inv.company,inv.name,inv.posting_date,employee,employee_name,currency,due_date,
		grand_total,outstanding_amount,status,acc.account_currency, 
		--
		IF(acc.account_currency = 'IQD', (round(inv.outstanding_amount * inv.conversion_rate, 2)), inv.outstanding_amount)outstanding_base
		--
		FROM `tabSales Invoice` inv, `tabAccount` acc 
		where inv.debit_to = acc.name
		and inv.docstatus = 1 and round(inv.outstanding_amount, 2) != 0 {0}""".format(conditions),self.filters,as_dict=1)
		
		return data


def get_columns():
	from frappe import get_roles
	roles = get_roles()
	
	has_system_manager_role = 'System Manager' in roles
	
	col =  [
		{
			"label": _("Sales Invoice"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 170,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 170,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 100,
		},
		{
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "currency",
			"width": 140,
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "currency",
			"width": 160,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		}
	]

	if has_system_manager_role:
		col += [
		{
			"label": _("Outstanding Base Currency (USD)"),
			"fieldname": "outstanding_base",
			"fieldtype": "Currency",
			"width": 180,
		}]
	return col
