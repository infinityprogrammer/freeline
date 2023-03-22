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
			"label": _("User"),
			"fieldname": "usr",
			"fieldtype": "Link",
			"options": "User",
			"width": 200,
		},
		{
			"label": _("Role"),
			"fieldname": "role",
			"fieldtype": "Link",
			"options": "Role",
			"width": 180,
		},
		{
			"label": _("Type"),
			"fieldname": "parenttype",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Doctype"),
			"fieldname": "doc",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("If Owner"),
			"fieldname": "if_owner",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Select"),
			"fieldname": "select",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Read"),
			"fieldname": "read",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Write"),
			"fieldname": "write",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Create"),
			"fieldname": "create",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Submit"),
			"fieldname": "submit",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Cancel"),
			"fieldname": "cancel",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Amend"),
			"fieldname": "amaned",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Report"),
			"fieldname": "report",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Export"),
			"fieldname": "export",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Import"),
			"fieldname": "import",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Share"),
			"fieldname": "share",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Print"),
			"fieldname": "print",
			"fieldtype": "Check",
			"width": 90,
		},
		{
			"label": _("Email"),
			"fieldname": "email",
			"fieldtype": "Check",
			"width": 90,
		},

	]

def get_data(filters):

	condition = ""

	if filters.get("user"):
		condition += " and usr = %(user)s"

	if filters.get("role"):
		condition += " and role = %(role)s"
	
	if filters.get("doctype"):
		condition += " and doc = %(doctype)s"
	
	if filters.get("report_only"):
		condition += " and parenttype = 'Report'"
	
	if filters.get("doctype_only"):
		condition += " and parenttype = 'DocType'"

	data = frappe.db.sql(
		"""
		SELECT * FROM (
		SELECT r.parent as usr,p.role,p.parenttype,p.parent doc,
		if_owner,
		p.select,p.read,p.write,p.create,p.delete
		submit,cancel,amend,report,p.export,import,share,print,email 
		FROM `tabCustom DocPerm` p, `tabHas Role` r 
		where p.role = r.role
		and p.parenttype = 'DocType' and r.parenttype = 'User'
		union all
		SELECT r.parent as usr,p.role,p.parenttype,p.parent doc,
		if_owner,
		p.select,p.read,p.write,p.create,p.delete
		submit,cancel,amend,report,p.export,import,share,print,email 
		FROM `tabDocPerm` p, `tabHas Role` r 
		where p.role = r.role
		and p.parenttype = 'DocType' and r.parenttype = 'User'
		union all
		SELECT usr,a.role,a.parenttype,parent,0,1,1,0,0,0,0,0,1,1,0,1,1,1 from `tabHas Role` a,
		(SELECT r.parent as usr, r.role FROM `tabHas Role` r where r.parenttype = 'User')b 
		where a.role = b.role
		and a.parenttype = 'Report')a1 where 1=1 {0}""".format(condition),filters,as_dict=1)

	return data