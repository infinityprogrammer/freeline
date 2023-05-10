// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Batch Expiry"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("Expiry From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"to_date",
			"label": __("Expiry To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
	]
};
