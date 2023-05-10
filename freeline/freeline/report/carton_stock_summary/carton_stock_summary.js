// Copyright (c) 2022, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Carton Stock Summary"] = {
	"filters": [
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"width": "80",
			"reqd": 1,
			"options": ["Warehouse", "Company"],
			"default": "Warehouse",
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company"),
			"depends_on": "eval: doc.group_by != 'Company'",
			get_data: function(txt) {
				// return frappe.db.get_link_options("Sales Person", txt);
				// frappe.query_report.set_filter_value('is_group', 0);
				return frappe.db.get_link_options("Company", txt);
			},
		},
		{
			"fieldname": "brand",
			"label": __("Brand"),
			"fieldtype": "MultiSelectList",
			"options": "Brand",
			get_data: function(txt) {
				return frappe.db.get_link_options("Brand", txt);
			},
		},
	]
}