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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

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
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"freeline.tasks.all"
# 	],
# 	"daily": [
# 		"freeline.tasks.daily"
# 	],
# 	"hourly": [
# 		"freeline.tasks.hourly"
# 	],
# 	"weekly": [
# 		"freeline.tasks.weekly"
# 	]
# 	"monthly": [
# 		"freeline.tasks.monthly"
# 	]
# }

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
# override_doctype_dashboards = {
# 	"Task": "freeline.task.get_dashboard_data"
# }

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
                "Sales Order-picker_warehouse"
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
    ]
}