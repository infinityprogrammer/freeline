// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attachment Purchase Invoice"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
	]
};
