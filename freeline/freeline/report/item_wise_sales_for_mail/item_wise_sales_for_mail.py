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
		inv_item.brand,inv_item.item_group,inv.name as invoice,inv.conversion_rate,
		inv.posting_date,inv.customer,inv.customer_name,inv.customer_group,inv.debit_to as receivable_account, inv.territory, inv.employee, inv.employee_name,
		inv_item.sales_order, 
		inv_item.delivery_note,
		inv_item.income_account, inv.cost_center, inv_item.stock_qty,inv_item.base_rate,inv_item.base_amount,
		inv_item.stock_uom, inv_item.qty, inv_item.uom, inv_item.rate, inv_item.amount, (inv_item.discount_amount*inv_item.qty)discount_amount, inv_item.batch_no,
		((inv_item.amount/ inv.total)*inv.discount_amount) as invoice_discount_amount,
		(SELECT group_concat(supplier_part_no) FROM `tabItem Supplier` supp where supp.parent = inv_item.item_code) as supplier_no,
		(SELECT GROUP_CONCAT(barcode) FROM `tabItem Barcode` tb where tb.parent = inv_item.item_code) as barcode,
		(SELECT GROUP_CONCAT(name) FROM `tabSales Person` sp where sp.employee = inv.employee)sales_person,
		(SELECT GROUP_CONCAT(parent) FROM `tabSales Person` sp where sp.employee = inv.employee)sales_team,
		(SELECT weight_per_unit FROM `tabItem` where name = inv_item.item_code)weight_per_unit,
		(SELECT collation FROM `tabItem` where name = inv_item.item_code)collation,inv.branch,
		(SELECT branch_id FROM `tabBranch` br where br.name = inv.customer_branch)branch_id,
		(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = inv_item.item_code order by conversion_factor desc limit 1)highest_uom,
		(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = inv_item.item_code 
		order by conversion_factor desc limit 1)highest_uom_factor,
		round((inv_item.stock_qty/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = inv_item.item_code 
		order by conversion_factor desc limit 1)), 2)qty_highest_uom,
		(SELECT longitude FROM `tabCustomer` cust where cust.name = inv.customer)customer_longitude,
		(SELECT latitude FROM `tabCustomer` cust where cust.name = inv.customer)customer_latitude,
		(SELECT order_longitude FROM `tabSales Order` so where so.name = inv_item.sales_order)order_longitude,
		(SELECT order_latitude FROM `tabSales Order` so where so.name = inv_item.sales_order)order_latitude,
		(SELECT parent_item_group FROM `tabItem Group` ig where ig.name = inv_item.item_group)item_group_parent_1,
		(SELECT parent_item_group FROM `tabItem Group` 
		WHERE name = (SELECT parent_item_group FROM `tabItem Group` ig where ig.name = inv_item.item_group))item_group_parent_2
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
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 130,
		},
		{
			"label": _("Item Group Parent 1"),
			"fieldname": "item_group_parent_1",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 160,
		},
		{
			"label": _("Item Group Parent 2"),
			"fieldname": "item_group_parent_2",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 160,
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
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 130,
		},
		{
			"label": _("Branch ID"),
			"fieldname": "branch_id",
			"fieldtype": "Data",
			"width": 100,
		},
		# {
		# 	"label": _("Branch"),
		# 	"fieldname": "branch",
		# 	"fieldtype": "Data",
		# 	"width": 130,
		# },
		{
			"label": _("Receivable Account"),
			"fieldname": "receivable_account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 160,
		},
		{
			"label": _("Territory"),
			"fieldname": "territory",
			"fieldtype": "Link",
			"options": "Territory",
			"width": 100,
		},
		{
			"label": _("Sales Person"),
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"options": "Sales Team",
			"width": 120,
		},
		{
			"label": _("Sales Team"),
			"fieldname": "sales_team",
			"fieldtype": "Link",
			"options": "Sales Team",
			"width": 120,
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
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 100,
		},
		{
			"label": _("Delivery Note"),
			"fieldname": "delivery_note",
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 100,
		},
		# {
		# 	"label": _("DN Number"),
		# 	"fieldname": "dn_number",
		# 	"fieldtype": "Link",
		# 	"options": "Delivery Note",
		# 	"width": 100,
		# },
		{
			"label": _("Income Account"),
			"fieldname": "income_account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 100,
		},
		{
			"label": _("Cost Center"),
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 100,
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
			"label": _("Highest UOM"),
			"fieldname": "highest_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Hi-UOM Factor"),
			"fieldname": "highest_uom_factor",
			"fieldtype": "Float",
			"width": 140,
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
		},
		{
			"label": _("Barcode"),
			"fieldname": "barcode",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Supplier Ref No"),
			"fieldname": "supplier_no",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Collation"),
			"fieldname": "collation",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Batch No"),
			"fieldname": "batch_no",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Weight Per Unit"),
			"fieldname": "weight_per_unit",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Order Longitude"),
			"fieldname": "order_longitude",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Order Latitude"),
			"fieldname": "order_latitude",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Customer Longitude"),
			"fieldname": "customer_longitude",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Customer Latitude"),
			"fieldname": "customer_latitude",
			"fieldtype": "Float",
			"width": 140,
		},
	]

	return columns