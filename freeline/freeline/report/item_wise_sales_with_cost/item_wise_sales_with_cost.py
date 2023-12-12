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
	
	condition = ""
	if not filters.get("company"):
		return

	if filters.get("item_group"):
		condition += " and inv_item.item_group = %(item_group)s"

	if filters.get("customer"):
		condition += " and inv.customer = %(customer)s"
	
	if filters.get("brand"):
		condition += " and inv_item.brand in %(brand)s"
	
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
				sales_p.append(s.employee)

		filters['sales_person'] = sales_p
		condition += " and inv.employee in %(sales_person)s"

	data = frappe.db.sql(
		"""
		SELECT inv.company, inv_item.item_code, inv_item.item_name, inv.currency as invoice_currency, 
		inv_item.brand,inv.name as invoice,inv.conversion_rate,
		inv.posting_date,inv.customer, inv.employee, inv.employee_name, inv_item.stock_qty,inv_item.base_rate,inv_item.base_amount,
		inv_item.stock_uom, inv_item.qty, inv_item.uom, inv_item.rate, inv_item.amount, (inv_item.discount_amount*inv_item.qty)discount_amount,
		((inv_item.amount/ inv.total)*inv.discount_amount) as invoice_discount_amount,inv.branch,
		(SELECT branch_id FROM `tabBranch` br where br.name = inv.customer_branch)branch_id,
		round((inv_item.stock_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = inv_item.item_code 
		order by conversion_factor desc limit 1)), 2)qty_highest_uom,
		(SELECT ifnull(round(valuation_rate, 4), 0)
		FROM `tabStock Ledger Entry` where item_code = inv_item.item_code and is_cancelled = 0
		and posting_date <= inv.posting_date
		order by posting_date desc limit 1)valuation_rate,
		(inv_item.stock_qty * (SELECT ifnull(round(valuation_rate, 4), 0)
		FROM `tabStock Ledger Entry` where item_code = inv_item.item_code and is_cancelled = 0
		and posting_date <= inv.posting_date
		order by posting_date desc limit 1))valuation_uom_rate
		FROM `tabSales Invoice` inv, `tabSales Invoice Item` inv_item
		where inv.name = inv_item.parent and inv.docstatus = 1 and inv.company in %(company)s {0} and inv.posting_date between %(from_date)s and %(to_date)s
		order by posting_date desc""".format(condition),filters,as_dict=1)

	return data

def get_columns():

	columns = [

		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 100,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Invoice Currency"),
			"fieldname": "invoice_currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 100,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 100,
		},
		{
			"label": _("Invoice"),
			"fieldname": "invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100,
		},
		{
			"label": _("Branch ID"),
			"fieldname": "branch_id",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{"label": _("Stock Qty"), "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Qty in Hi-UOM"),
			"fieldname": "qty_highest_uom",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Float",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Base Rate (USD)"),
			"fieldname": "base_rate",
			"fieldtype": "Float",
			"options": "currency",
			"width": 140,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Base Amount (USD)"),
			"fieldname": "base_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140,
		},
		{
			"label": _("Valuation Stock UOM (USD)"),
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140,
		},
		{
			"label": _("Valuation UOM (USD)"),
			"fieldname": "valuation_uom_rate",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140,
		},
		{
			"label": _("Discount Amount"),
			"fieldname": "discount_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Exchange Rate"),
			"fieldname": "conversion_rate",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Invoice Discount Amount"),
			"fieldname": "invoice_discount_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		}
	]

	return columns