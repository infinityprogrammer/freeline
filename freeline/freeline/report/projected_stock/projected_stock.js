// Copyright (c) 2022, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Projected Stock"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		// {
		// 	"fieldname":"warehouse",
		// 	"label": __("Warehouse"),
		// 	"fieldtype": "MultiSelectList",
		// 	"options": "Warehouse",
		// 	"get_query": () => {
		// 		return {
		// 			filters: {
		// 				company: frappe.query_report.get_filter_value('company')
		// 			}
		// 		}
		// 	}
		// },
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			get_data: function(txt) {
				return frappe.db.get_link_options("Warehouse", txt);
			}
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			},
			"hidden": 1
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "MultiSelectList",
			"options": "Brand",
			get_data: function(txt) {
				return frappe.db.get_link_options("Brand", txt);
			}
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		}
	]
}