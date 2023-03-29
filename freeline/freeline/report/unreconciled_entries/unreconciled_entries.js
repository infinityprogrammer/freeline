// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Unreconciled Entries"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default('company')
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
	]
};
