// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Valuation Details"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"filters":{
				is_group :0
			}
		}

	]
};
