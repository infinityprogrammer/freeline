// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["HiUOM Item Price"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"default": "Trade Price List"
		}
	]
};
