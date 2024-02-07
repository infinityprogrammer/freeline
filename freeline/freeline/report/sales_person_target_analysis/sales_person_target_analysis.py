# Copyright (c) 2024, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	columns, data = [], []

	period_list = get_period_list(
		filters.fiscal_year,
		filters.fiscal_year,
		"",
		"",
		"Fiscal Year",
		"Monthly",
		company=filters.company,
	)

	columns = get_columns(filters, period_list)

	data = get_data(filters, period_list)

	return columns, data

def get_columns(filters, period_list):
	
	columns =  [
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
			"width": 180,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 140,
		},
		# {
		# 	"label": _("Fiscal Year"),
		# 	"fieldname": "fiscal_year",
		# 	"fieldtype": "Link",
		# 	"options": "Fiscal Year",
		# 	"width": 140,
		# },
		# {
		# 	"label": _("Target Amount"),
		# 	"fieldname": "target_amount",
		# 	"fieldtype": "Float",
		# 	"width": 140,
		# }
	]
	fieldtype, options = "Currency", "currency"

	for period in period_list:
		target_key = "target_{}".format(period.key)
		variance_key = "variance_{}".format(period.key)

		columns.extend(
			[
				{
					"fieldname": target_key,
					"label": _("Target ({})").format(period.label),
					"fieldtype": fieldtype,
					"options": options,
					"width": 150,
				},
				{
					"fieldname": period.key,
					"label": _("Achieved ({})").format(period.label),
					"fieldtype": fieldtype,
					"options": options,
					"width": 150,
				},
				{
					"fieldname": variance_key,
					"label": _("Variance ({})").format(period.label),
					"fieldtype": fieldtype,
					"options": options,
					"width": 150,
				},
			]
		)

	columns.extend(
		[
			{
				"fieldname": "total_target",
				"label": _("Total Target"),
				"fieldtype": fieldtype,
				"options": options,
				"width": 150,
			},
			{
				"fieldname": "total_achieved",
				"label": _("Total Achieved"),
				"fieldtype": fieldtype,
				"options": options,
				"width": 150,
			},
			{
				"fieldname": "total_variance",
				"label": _("Total Variance"),
				"fieldtype": fieldtype,
				"options": options,
				"width": 150,
			},
		]
	)

	return columns

def get_data(filters, period_list):

	conditions = ""

	if filters.get("fiscal_year"):
		conditions += " and b.fiscal_year = %(fiscal_year)s"
	
	if filters.get("employee"):
		conditions += " and a.employee = %(employee)s"

	if not filters.get("company"):
		return
	
	company = filters.get("company")

	data = frappe.db.sql(
		"""
		SELECT a.employee, b.brand, b.fiscal_year, b.target_amount, b.distribution_id,
		(select employee_name from `tabEmployee` where `tabEmployee`.name = a.employee)employee_name 
		FROM `tabSales Person` a, `tabTarget Detail Definition` b
		where a.name = b.parent {0} order by 1""".format(conditions),filters,as_dict=1)

	for row in data:
		total_achieved = 0.0
		total_target = 0.0
		for month in period_list:
			
			target_key = "target_{}".format(month.key)
			variance_key = "variance_{}".format(month.key)

			row[month.key] = get_brand_sales_in_period(row.employee, row.brand, month.from_date, month.to_date, company)
			row[target_key] = get_monthly_target(month.from_date, row.target_amount, row.distribution_id)
			row[variance_key] =  row[month.key] - row[target_key]

			row["total_target"] =  row.target_amount
			total_achieved += row[month.key]
			total_target += row[target_key]

		row["total_achieved"] =  total_achieved
		row["total_target"] =  total_target
		row["total_variance"] =  total_achieved - total_target

	return data

def get_brand_sales_in_period(employee, brand, start_date, end_date, company):
	sales_amount = frappe.db.sql(
		"""
		SELECT ifnull(sum(base_net_amount), 0)base_net_amount 
		FROM `tabSales Invoice` a, `tabSales Invoice Item` b
		where a.name = b.parent and a.employee = %(employee)s and a.company = %(company)s
		and b.brand = %(brand)s and a.posting_date 
		between %(start_date)s and %(end_date)s""",
		{'employee': employee, 'brand': brand, 'start_date': start_date, 'end_date': end_date, 'company': company},as_dict=1)
	
	return sales_amount[0].base_net_amount

def get_monthly_target(start_date, target_amount, distribution_id):
	
	month_name = start_date.strftime("%B")

	target = frappe.db.sql(
		"""
		SELECT ifnull(percentage_allocation, 0)percentage_allocation
		FROM `tabMonthly Distribution Percentage` 
		where parent = %(distribution_id)s and month = %(month)s""",
		{'distribution_id': distribution_id, 'month': month_name,},as_dict=1)
	
	result = target_amount * (target[0].percentage_allocation/100)
	return result