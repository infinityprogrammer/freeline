// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Sales Coverage"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width" : 120
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width" : 120
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"width" : 120
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
			// "reqd": 1,
		},
		// {
		// 	"fieldname": "brand",
		// 	"label": __("Brand"),
		// 	"fieldtype": "MultiSelectList",
		// 	"options": "Brand",
		// 	get_data: function(txt) {
		// 		// return frappe.db.get_link_options("Sales Person", txt);
		// 		// frappe.query_report.set_filter_value('is_group', 0);
		// 		return frappe.db.get_link_options("Brand", txt);
		// 	},
		// 	// "reqd": 1,
		// },

	]
};


