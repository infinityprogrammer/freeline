// Copyright (c) 2024, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Warehouse Pallet Capacity"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company"),
			get_data: function(txt) {
				return frappe.db.get_link_options("Company", txt);
			},
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Warehouse"),
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse', txt, {
					is_group: 0
				});
			},
		},
	]
};
