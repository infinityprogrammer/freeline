from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "freeline"
app_title = "Freeline"
app_publisher = "RAFI"
app_description = "freeline"
app_icon = "octicon octicon-file-directory"
app_color = "White"
app_email = "freeline@freeline.ae"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/freeline/css/freeline.css"
# app_include_js = "/assets/freeline/js/freeline.js"

# include js, css files in header of web template
# web_include_css = "/assets/freeline/css/freeline.css"
# web_include_js = "/assets/freeline/js/freeline.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "freeline/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Payment Entry" : "public/js/payment_entry.js",
    "Payment Reconciliation" : "public/js/payment_reconciliation.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Price List" : "public/js/price_list.js",
    "Sales Order" : "public/js/sales_order.js",
    "Pick List" : "public/js/pick_list.js",
    "Delivery Note" : "public/js/delivery_note.js",
	"Stock Reconciliation" : "public/js/stock_reconciliation.js",
	"Sales Person" : "public/js/sales_person.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "freeline.install.before_install"
# after_install = "freeline.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "freeline.uninstall.before_uninstall"
# after_uninstall = "freeline.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "freeline.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Pick List": "freeline.freeline.override.OverridePickList"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# },
    "Delivery Note":{
        "before_save": "freeline.freeline.globalapi.get_picklist_in_dn",
        "on_change": "freeline.freeline.globalapi.update_pick_list_status",
        "before_insert": "freeline.freeline.events.update_dn_with_pick_list",
    },
    "Stock Entry":{
        "validate": "freeline.freeline.globalapi.validate_same_batch",
    },
    "Sales Order":{
        "before_submit": [
            "freeline.freeline.globalapi.validate_picker_warehouse_mandatory",
            "freeline.freeline.events.validate_overdue_limit",
        ],
        "validate": "freeline.freeline.events.validate_same_warehouse",
    },
    "Sales Invoice":{
        "on_cancel": [
            "freeline.freeline.events.set_rebate_empty",
            "freeline.freeline.events.reward_point_entry_process_cancel",
        ],
        "on_trash": "freeline.freeline.events.set_rebate_empty",
        "on_submit": "freeline.freeline.events.reward_point_entry_process",
    },
    "Pick List":{
        "validate": [
            "freeline.freeline.events.set_pick_list_barcode",
            "freeline.freeline.events.set_sales_order_pick_list",
        ]
    },
}


# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"freeline.tasks.all"
	# ],
	# "daily": [
	# 	"freeline.tasks.daily"
	# ],
	# "hourly": [
	# 	"freeline.tasks.hourly"
	# ],
	# "weekly": [
	# 	"freeline.tasks.weekly"
	# ]
	# "monthly": [
	# 	"freeline.tasks.monthly"
	# ],
    "cron": {
		"10 0 1 * *": [
			"freeline.freeline.globalapi.generate_rebate_process",
		],
		"10 4 1 * *": [
			"freeline.freeline.globalapi.generate_shelf_rentals",
		],
        "0 1 * * *": [
			"freeline.freeline.events.expire_reward_point",
		],
	},
}

# Testing
# -------

# before_tests = "freeline.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "freeline.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps

override_doctype_dashboards = {
	"Pick List": "freeline.freeline.custom_dashboard.get_so_pick_list_connection"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"freeline.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []

fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "name", "in", [
                "Sales Order-picker_warehouse",
                "Pick List-employee_driver_id",
                "Pick List-employee_driver_name",
                "Pick List Item-hand_picked_qty",
                "Sales Invoice-rebate_duration",
                "Stock Reconciliation-warehouse",
                "Warehouse-branch",
                "Warehouse-branch_id",
                "Purchase Order-supplier_references",
                "Purchase Order-supplier_code_ref",
                "Purchase Order-supplier_po_ref",
                "Purchase Order-col_brk_01",
                "Purchase Order-shipper_pi_ref",
                "Purchase Invoice-related_purchase_invoice",
                "Sales Invoice-brand",
                "Sales Invoice-supplier_details",
                "Sales Invoice-supplier_id",
                "Sales Invoice-supplier_name",
                "Sales Invoice-column_break_35",
                "Sales Invoice-supplier_inv_ref",
                "Sales Invoice-shipper_inv_no",
                "Sales Invoice-shipper_invoice_date",
                "Sales Order-col_brk_02",
                "Sales Order-brand",
                "Purchase Invoice-brand",
                "Purchase Order-brand",
                "Sales Invoice-payment_receipt",
                "Delivery Note-employee_id",
                "Delivery Note-employee_name",
                "Sales Order-total_weight",
                "Sales Invoice-total_weight",
                "Customer-is_sister_company_customer",
                "Pick List-delivery_status",
                "Customer-overdue_days",
                "Pick List Item-barcode",
                "Pick List Item-partial_barcode",
                "Pick List-sales_order",
                "Warehouse-pallet_capacity_on_floor",
                "Warehouse-pallet_capacity_on_rack",
                "Item-hi_uom_volume",
                "Item-hi_uom_pallets_capacity",
                "Item-stacking_height",
                "Monthly Distribution-employee",
                "Monthly Distribution-employee_name",
                "Sales Person-target_definition",
                "Monthly Distribution-brand"
            ]
        ]
    ]},
]

jenv = {
    "methods": [
        "get_statement_customer:freeline.freeline.doctype.party_statement.party_statement.get_statement_customer",
        "get_customer_statement_details:freeline.freeline.doctype.party_statement.party_statement.get_customer_statement_details",
        "get_customer_opening:freeline.freeline.doctype.party_statement.party_statement.get_customer_opening",
        "get_dist_employee:freeline.freeline.doctype.party_statement.party_statement.get_dist_employee",
        "sales_rep_statement_details:freeline.freeline.doctype.party_statement.party_statement.sales_rep_statement_details",
        "emp_null_statement_details:freeline.freeline.doctype.party_statement.party_statement.emp_null_statement_details",
        "get_emp_null_opening:freeline.freeline.doctype.party_statement.party_statement.get_emp_null_opening",
        "get_item_barcode:freeline.freeline.globalapi.get_item_barcode",
        "get_line_total_disc:freeline.freeline.globalapi.get_line_total_disc",
        "get_gross_total_amt:freeline.freeline.globalapi.get_gross_total_amt",
        "get_line_total_disc_order:freeline.freeline.globalapi.get_line_total_disc_order",
        "get_gross_total_amt_order:freeline.freeline.globalapi.get_gross_total_amt_order",
        "get_customer_and_currency:freeline.freeline.globalapi.get_customer_and_currency",
        "get_customer_statement_by_currency:freeline.freeline.globalapi.get_customer_statement_by_currency",
		"get_uom_qty_sum:freeline.freeline.globalapi.get_uom_qty_sum",
		"get_uom_qty_sum_inv:freeline.freeline.globalapi.get_uom_qty_sum_inv",
        "get_unallocated_payment:freeline.freeline.doctype.party_statement.party_statement.get_unallocated_payment",
        "get_unallocated_payment_not_in_ageing:freeline.freeline.doctype.party_statement.party_statement.get_unallocated_payment_not_in_ageing",
        "get_unallocated_payment_not_in_ageing_iqd:freeline.freeline.doctype.party_statement.party_statement.get_unallocated_payment_not_in_ageing_iqd",
        "get_not_due_amount:freeline.freeline.doctype.party_statement.party_statement.get_not_due_amount",
        "get_uom_qty_sum_order:freeline.freeline.globalapi.get_uom_qty_sum_order",
    ]
}