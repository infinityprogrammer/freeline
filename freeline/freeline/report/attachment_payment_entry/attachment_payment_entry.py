# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe

# import frappe
import frappe
from frappe import _
from frappe.utils import flt, today


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	return columns, data



def get_data(filters):
	
	conditions = ""
	if not filters.get("company"):
		return;

	if filters.get("company"):
		conditions += """ and company = %(company)s """

	if filters.get("from_date") and filters.get("to_date"):
		conditions += """ and posting_date between %(from_date)s and %(to_date)s"""

	data = frappe.db.sql(
		"""
		SELECT company,p.name,posting_date,paid_amount,
		(
		CASE
			WHEN ifnull(file_url, '') = '' THEN '<span style="color:red">No Attachment</span>'
			ELSE concat("<a target ='_blank' href='",file_url,"'>Attachment</a>")
		END
		)file_url
		FROM `tabPayment Entry` p left join `tabFile` f on p.name = f.attached_to_name where 1=1
		{0} order by posting_date desc""".format(conditions),filters,as_dict=1)

	return data

def get_columns():
	return [
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 140,
		},
		{
			"label": _("Name"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"label": _("Paid Amount"),
			"fieldname": "paid_amount",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Attachment"),
			"fieldname": "file_url",
			"fieldtype": "Data",
			"width": 300,
		}
	]