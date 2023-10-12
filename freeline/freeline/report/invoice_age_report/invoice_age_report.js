// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Invoice Age Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "employee",
			"label": __("Sales Rep"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		
	]
};
