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
	if not filters.get("sales_person"):
		return

	if filters.get("sales_person"):
		sales_p = []
		sales_p.append("A")
		for ps in filters.get("sales_person"):
			lft, rgt = frappe.db.get_value("Sales Person", ps, ["lft", "rgt"])
			sales_pers = frappe.db.sql(
				"""
				select employee from `tabSales Person` where lft >= %s and rgt <= %s and is_group = 0
				""",
				(lft, rgt),
				as_dict=1,
			)
			for s in sales_pers:
				if s.employee:
					sales_p.append(s.employee)
		filters['sales_person'] = sales_p

	print(filters)

	conditions += " and posting_date between %(from_date)s and %(to_date)s and b.company = %(company)s"
	conditions += " and (select inv.employee from `tabSales Invoice` inv where inv.name = a.reference_name) in %(sales_person)s"

	data = frappe.db.sql(
		"""
		SELECT (select inv.employee from `tabSales Invoice` inv where inv.name = a.reference_name)employee,
		(SELECT sp.parent from `tabSales Person` sp where 
		sp.employee = (select employee from `tabSales Invoice` inv where inv.name = a.reference_name))sales_team,
		b.posting_date, b.name,a.reference_name,
		round(a.total_amount,2)total_amount,round(a.allocated_amount,2)allocated_amount,
		((round(a.allocated_amount,2)/round(a.total_amount,2))*100)rec_perce,
		(select status from `tabSales Invoice` inv where inv.name = a.reference_name)status,
		datediff(curdate(),(select inv.due_date from `tabSales Invoice` inv where inv.name = a.reference_name))due_age,
		(SELECT payment_terms FROM `tabCustomer` c where c.name = (select customer from `tabSales Invoice` 
		inv where inv.name = a.reference_name))payment_terms,
		round((select outstanding_amount from `tabSales Invoice` inv where inv.name = a.reference_name),2)outstanding_amount,
		(select employee_name from `tabSales Invoice` inv where inv.name = a.reference_name)employee_name
		FROM `tabPayment Entry Reference` a, `tabPayment Entry` b
		where a.parent = b.name and b.docstatus = 1 and b.party_type = 'Customer' {0}""".format(conditions),filters,as_dict=1)

	return data


def get_columns(filters):

	return [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 140,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 190,
		},
		{
			"label": _("Sales Team"),
			"fieldname": "sales_team",
			"fieldtype": "Link",
			"options": "Sales Team",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"label": _("Voucher No"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 150,
		},
		{
			"label": _("Sales Invoice"),
			"fieldname": "reference_name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 180,
		},
		{
			"label": _("Invoice Total"),
			"fieldname": "total_amount",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Paid Amount"),
			"fieldname": "allocated_amount",
			"fieldtype": "Float",
			"width": 140,
		},
		# {
		# 	"label": _("% Recieved"),
		# 	"fieldname": "rec_perce",
		# 	"fieldtype": "Percent",
		# 	"width": 100,
		# },
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Due Age"),
			"fieldname": "due_age",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Payment Terms"),
			"fieldname": "payment_terms",
			"fieldtype": "Data",
			"width": 140,
		},
	]
