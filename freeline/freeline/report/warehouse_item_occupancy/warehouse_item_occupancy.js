// Copyright (c) 2024, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Warehouse Item Occupancy"] = {
	"filters": [
		// {
		// 	"fieldname":"company",
		// 	"label": __("Company"),
		// 	"fieldtype": "MultiSelectList",
		// 	"options": "Company",
		// 	"reqd": 1,
		// 	"default": frappe.defaults.get_user_default("Company"),
		// 	get_data: function(txt) {
		// 		return frappe.db.get_link_options("Company", txt);
		// 	},
		// },
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
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "MultiSelectList",
			"options": "Item",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Item"),
			get_data: function(txt) {
				return frappe.db.get_link_options('Item', txt, {
					disabled: 0
				});
			},
		},
	]
};
