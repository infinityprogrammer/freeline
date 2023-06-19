// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Wise Sales For Mail"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			get_data: function(txt) {
				// return frappe.db.get_link_options("Sales Person", txt);
				// frappe.query_report.set_filter_value('is_group', 0);
				return frappe.db.get_link_options("Company", txt);
			},
			"reqd": 1,
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
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	}
};
