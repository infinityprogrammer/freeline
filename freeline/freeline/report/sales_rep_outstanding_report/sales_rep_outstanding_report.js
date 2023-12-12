// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Rep Outstanding Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			"reqd":1,
			get_data: function(txt) {
				// return frappe.db.get_link_options("Sales Person", txt);
				// frappe.query_report.set_filter_value('is_group', 0);
				return frappe.db.get_link_options("Company", txt);
			},
			"reqd": 1,
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "MultiSelectList",
			"options": "Sales Person",
			get_data: function(txt) {
				// return frappe.db.get_link_options("Sales Person", txt);
				// frappe.query_report.set_filter_value('is_group', 0);
				return frappe.db.get_link_options("Sales Person", txt);
			},
			"reqd": 1,
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
