// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Collection"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default":frappe.defaults.get_user_default("company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "customer_branch",
			"label": __("Customer Branch"),
			"fieldtype": "Link",
			"options": "Customer Site",
		},
		{
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "MultiSelectList",
			"options": "Account",
			get_data: function(txt) {
				return frappe.db.get_link_options('Account', txt, {
					company: frappe.query_report.get_filter_value("company"),
					account_number : ["in", ["10121", "10122","10131", "10132","10141","10152"]]
				});
			}
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse', txt, {
					company: frappe.query_report.get_filter_value("company"),
					is_group: 0
				});
			}
		}
	]
};
