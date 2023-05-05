# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	
	return [
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
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Payment Entry"),
			"fieldname": "payment_entry",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 160,
		},
		{
			"label": _("Sales Invoice"),
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 170,
		},
		# {
		# 	"label": _("Allocated Amount"),
		# 	"fieldname": "allocated_amount",
		# 	"fieldtype": "Float",
		# 	"width": 110,
		# },
		{
			"label": _("From Currency"),
			"fieldname": "paid_from_currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 120,
		},
		{
			"label": _("To Currency"),
			"fieldname": "paid_to_currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 100,
		},
		# {
		# 	"label": _("Paid Amount (USD)"),
		# 	"fieldname": "base_paid_amount",
		# 	"fieldtype": "Float",
		# 	"width": 100,
		# },
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 130,
		},
		{
			"label": _("Amount EL (USD)"),
			"fieldname": "amt_el",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Exchange Loss (USD)"),
			"fieldname": "loss",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Final Collection (USD)"),
			"fieldname": "fin_amt",
			"fieldtype": "Float",
			"width": 130,
		}
	]

def get_data(filters):

	if not filters.get("company") or not filters.get("from_date") or not filters.get("to_date"):
		return
	
	if not filters.get("sales_person"):
		return
	
	conditions = ""

	if filters.get("brand"):
		conditions += " and sit.brand in %(brand)s"

	conditions += " and (select inv.employee from `tabSales Invoice` inv where inv.name = ref.reference_name) in %(sales_person)s"
	conditions += " and pe.company = %(company)s and pe.posting_date between %(from_date)s and %(to_date)s"

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

	data = frappe.db.sql(
		"""
		SELECT pe.name as payment_entry,inv.employee, pe.posting_date,pe.party as customer,pe.party_name as customer_name,ref.parent, ref.reference_name,ref.allocated_amount,
		pe.paid_from_account_currency as paid_from_currency,pe.paid_to_account_currency as paid_to_currency,
		pe.base_paid_amount,received_amount,sit.brand,sit.base_amount,sit.amount,inv.base_grand_total,sit.item_code,ref.reference_name as sales_invoice,
		-- ((pe.base_paid_amount/inv.base_grand_total))pro,
		-- (((pe.base_total_allocated_amount)/inv.base_grand_total)*sit.base_amount)pro_amt,
		-- (SELECT ifnull(sum(amount),0) FROM `tabPayment Entry Deduction` pd where pd.parent = pe.name)el,
		-- (((SELECT ifnull(sum(amount),0) FROM `tabPayment Entry Deduction` pd 
		-- where pd.parent = pe.name)/pe.base_paid_amount)*((((pe.base_paid_amount-pe.unallocated_amount)/inv.base_grand_total)*sit.base_amount)))loss,
		--
		((((pe.base_total_allocated_amount)/inv.base_grand_total)*sit.base_amount))amt_el,
		--
		round(((((pe.base_total_allocated_amount)/inv.base_grand_total)*sit.base_amount)) - 
		(((SELECT ifnull(sum(amount),0) FROM `tabPayment Entry Deduction` pd 
		where pd.parent = pe.name)/pe.base_paid_amount)*((((pe.base_total_allocated_amount)/inv.base_grand_total)*sit.base_amount))), 2)fin_amt
		--
		FROM `tabPayment Entry` pe, `tabPayment Entry Reference` ref, `tabSales Invoice Item` sit, `tabSales Invoice` inv 
		where pe.name = ref.parent and ref.reference_name = sit.parent and sit.parent = inv.name
		and pe.docstatus = 1
		and pe.payment_type = 'Receive'
		and ref.reference_doctype = 'Sales Invoice' and pe.posting_date = curdate() {0}""".format(conditions),filters,as_dict=1)

	return data