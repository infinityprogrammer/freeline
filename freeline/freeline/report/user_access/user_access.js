// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["User Access"] = {
	"filters": [
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "role",
			"label": __("Role"),
			"fieldtype": "Link",
			"options": "Role",
		},
		{
			"fieldname": "doctype",
			"label": __("DocType"),
			"fieldtype": "Link",
			"options": "DocType",
		},
		{
			"fieldname": "report_only",
			"label": __("Report Only"),
			"fieldtype": "Check",
			"default": 0,
		},
		{
			"fieldname": "doctype_only",
			"label": __("DocType Only"),
			"fieldtype": "Check",
			"default": 0,
		},

	]
};
