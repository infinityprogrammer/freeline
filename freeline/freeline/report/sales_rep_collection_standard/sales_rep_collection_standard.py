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

	# print(filters)

	conditions += " and posting_date between %(from_date)s and %(to_date)s and b.company = %(company)s"
	conditions += " and (select inv.employee from `tabSales Invoice` inv where inv.name = a.reference_name) in %(sales_person)s"

	data = frappe.db.sql(
		"""
		SELECT (select inv.employee from `tabSales Invoice` inv where inv.name = a.reference_name)employee,
		(SELECT parent_sales_person from `tabSales Person` sp where 
		sp.employee = (select employee from `tabSales Invoice` inv where inv.name = a.reference_name))sales_team,
		b.posting_date, b.name,a.reference_name,paid_from_account_currency, paid_to_account_currency,
		round(a.total_amount,2)total_amount,round(a.allocated_amount,2)allocated_amount,
		((round(a.allocated_amount,2)/round(a.total_amount,2))*100)rec_perce,
		(select status from `tabSales Invoice` inv where inv.name = a.reference_name)status,
		datediff(curdate(),(select inv.due_date from `tabSales Invoice` inv where inv.name = a.reference_name))due_age,
		(SELECT payment_terms FROM `tabCustomer` c where c.name = (select customer from `tabSales Invoice` 
		inv where inv.name = a.reference_name))payment_terms,paid_from_account_currency,
		round((select outstanding_amount from `tabSales Invoice` inv where inv.name = a.reference_name),2)outstanding_amount,
		(select employee_name from `tabSales Invoice` inv where inv.name = a.reference_name)employee_name,
		b.paid_to_account_currency as collection_currency,b.base_paid_amount,
		--
		round(IF(b.paid_from_account_currency = 'IQD' AND b.paid_to_account_currency = 'IQD',
		(SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry Deduction` d WHERE d.parent = b.name),
		((SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry Deduction` d WHERE d.parent = b.name) / b.base_paid_amount) * ROUND(a.allocated_amount, 2)), 3)exchange_loss_usd,
		--
		round((round(a.allocated_amount,3) - IF(b.paid_from_account_currency = 'IQD' AND b.paid_to_account_currency = 'IQD',
		(SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry Deduction` d WHERE d.parent = b.name),
		((SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry Deduction` d 
		WHERE d.parent = b.name) / b.base_paid_amount) * ROUND(a.allocated_amount, 2))), 3)net_recieved_after_el,
		--
		(received_amount/b.base_paid_amount)exchange_rate,
		--
		round(IF(b.paid_from_account_currency = 'IQD' AND b.paid_to_account_currency = 'IQD',
		round(((received_amount/b.paid_amount)*round(a.allocated_amount,2)), 3),
		round(((received_amount/b.base_paid_amount)*round(a.allocated_amount,2)), 3)), 3)recieved_bf_ded_el,
		--
		round(((received_amount/b.base_paid_amount)*round(a.allocated_amount,2)), 3)rec_bf_ded,
		--
		round(IF(b.paid_from_account_currency = 'IQD' AND b.paid_to_account_currency = 'IQD',
		((round(a.allocated_amount,2) - ((SELECT ifnull(sum(amount),0) FROM `tabPayment Entry Deduction` d 
		where d.parent = b.name)/b.base_paid_amount)*round(a.allocated_amount,2))*(received_amount/b.paid_amount)),
		((round(a.allocated_amount,2) - ((SELECT ifnull(sum(amount),0) FROM `tabPayment Entry Deduction` d 
		where d.parent = b.name)/b.base_paid_amount)*round(a.allocated_amount,2))*(received_amount/b.base_paid_amount))) , 2)act_ledger_amt
		--
		FROM `tabPayment Entry Reference` a, `tabPayment Entry` b
		where a.parent = b.name and b.docstatus = 1 and b.party_type = 'Customer' {0}""".format(conditions),filters,as_dict=1)

	for row in data:
		if row.paid_from_account_currency == "USD" and row.paid_to_account_currency == "IQD":
			pass

	return data

def get_invoice_ded(payment_entry, base_paid_amount, allocated_amount):
	
	data = frappe.db.sql(
		"""
		((SELECT sum(amount)exc_loss FROM `tabPayment Entry Deduction` 
		d where d.parent = {0})/{1})*round({2},2)""".format(payment_entry, base_paid_amount, allocated_amount),as_dict=1)
	
	if data:
		return data[0].exc_loss
	else:
		return 0

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
		{
			"label": _("Paid From Currency"),
			"fieldname": "paid_from_account_currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 140,
		},
		{
			"label": _("Collection Currency"),
			"fieldname": "collection_currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 140,
		},
		{
			"label": _("Exchange Loss (USD)"),
			"fieldname": "exchange_loss_usd",
			"fieldtype": "Float",
			"width": 120,
		},
		# {
		# 	"label": _("Net Recieved After EL"),
		# 	"fieldname": "net_recieved_after_el",
		# 	"fieldtype": "Float",
		# 	"width": 150,
		# },
		{
			"label": _("Recieved in CC Before EL"),
			"fieldname": "recieved_bf_ded_el",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Exchange Rate"),
			"fieldname": "exchange_rate",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Net Amount After EL"),
			"fieldname": "act_ledger_amt",
			"fieldtype": "Float",
			"width": 160,
		},
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
