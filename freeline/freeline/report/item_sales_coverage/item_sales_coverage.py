# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _



def execute(filters=None):
	columns, data = [], []

	if not filters.sales_person or not filters.company:
		return

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_columns(filters):
	return [
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
			"width": 140,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 140,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 110,
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Month"),
			"fieldname": "mnt",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Sold Qty"),
			"fieldname": "stock_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 140,
		},
		{
			"label": _("Stock In WH Stock UOM"),
			"fieldname": "actual_qty",
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"label": _("Hi UOM"),
			"fieldname": "highest_uom",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Hi UOM Factor"),
			"fieldname": "highest_uom_factor",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Qty in Hi UOM"),
			"fieldname": "qty_highest_uom",
			"fieldtype": "Data",
			"width": 140,
		},
	]

def get_data(filters):

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
	
	qry = """SELECT a2.employee, a2.item_code, concat(month1,'-', year1)mnt , customer, stock_qty,
			(SELECT employee_name from `tabEmployee` where name = a2.employee)employee_name,
			(SELECT customer_name from `tabCustomer` where name = customer)customer_name,
			(SELECT customer_group from `tabCustomer` where name = customer)customer_group,
			(SELECT item_name from `tabItem` where name = a2.item_code)item_name,
			(SELECT brand from `tabItem` where name = a2.item_code)brand,
			(SELECT sum(actual_qty) FROM `tabBin` bin where bin.item_code = a2.item_code and bin.warehouse in 
			(select name from `tabWarehouse` wh where wh.company = %(company)s))actual_qty,
			(SELECT uom FROM `tabUOM Conversion Detail` um where um.parent = a2.item_code order by conversion_factor desc limit 1)highest_uom,
			(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = a2.item_code 
			order by conversion_factor desc limit 1)highest_uom_factor,
			ifnull(round(((SELECT sum(actual_qty) FROM `tabBin` bin where bin.item_code = a2.item_code and bin.warehouse in 
			(select name from `tabWarehouse` wh where wh.company = %(company)s))/(SELECT conversion_factor FROM `tabUOM Conversion Detail` um where um.parent = a2.item_code 
			order by conversion_factor desc limit 1)), 2), 0)qty_highest_uom
			FROM (
			WITH RECURSIVE dates AS (
			SELECT DATE('2022-05-01') AS date
			UNION ALL
			SELECT DATE_ADD(date, INTERVAL 1 MONTH)
			FROM dates
			WHERE DATE_ADD(date, INTERVAL 1 MONTH) <= curdate()
			),
			cross_join AS (
			SELECT it.item_code, emp.employee
			FROM `tabItem` it
			CROSS JOIN (
				SELECT DISTINCT a.employee
				FROM `tabSales Invoice` a
				INNER JOIN `tabSales Invoice Item` b ON a.name = b.parent
				WHERE a.docstatus = 1 and a.company = %(company)s
			) emp where it.is_stock_item = 1 and it.disabled = 0
			)
			SELECT cross_join.employee, cross_join.item_code, d1.year1, d1.month1
			FROM cross_join
			CROSS JOIN (
			SELECT MONTH(date) AS month1, YEAR(date) AS year1
			FROM dates
			) d1)a2 
			LEFT JOIN 
			(select month(a.posting_date)mnt,year(a.posting_date)yrs, a.customer, a.employee, 
			b.item_code, sum(b.stock_qty)stock_qty
			from `tabSales Invoice` a, `tabSales Invoice Item` b
			where a.name = b.parent and a.docstatus = 1
			group by month(a.posting_date),year(a.posting_date), a.customer, a.employee, b.item_code)s1
			on s1.employee = a2.employee
			and s1.mnt = a2.month1
			and s1.yrs = a2.year1
			and s1.item_code = a2.item_code
			where a2.employee in %(sales_person)s """
	
	data = frappe.db.sql(qry, filters,as_dict=1)
	
	return data