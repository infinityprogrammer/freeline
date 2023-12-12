from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe import _
import json
import datetime
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.doctype.delivery_note.delivery_note import get_returned_qty_map, get_delivery_note_serial_no, get_invoiced_qty_map
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values


def set_rebate_empty(self, args):
    if self.rebate_duration:
        invs = frappe.db.sql(""" UPDATE `tabRental Invoices` SET voucher_no = NULL, amount = 0  WHERE voucher_no = %(voucher_no)s""",
                                    {'voucher_no': self.name}, as_dict=True)

def validate_overdue_limit(self, args):
    
    overdue_limt_days = frappe.db.get_value('Customer', self.customer, 'overdue_days')
    role_allow = frappe.db.get_single_value('Tiejan Internal Settings', 'role_allowed_overdue_customer')
    alert_on_overdue = frappe.db.get_single_value('Tiejan Internal Settings', 'alert_on_overdue_in_days')
    
    user_roles = frappe.get_roles()

    over_due_day = get_over_due_days(self.customer, self.company)

    if over_due_day:
        if over_due_day >= alert_on_overdue:
            frappe.msgprint('Customer overdue day reached {0} days, Maximum {1}'.format(over_due_day, overdue_limt_days));
    

    if overdue_limt_days:
        if role_allow:
            
            over_due_inv = frappe.db.sql(""" SELECT name, customer ,posting_date, due_date, datediff(CURDATE(), due_date)diff 
                                            FROM `tabSales Invoice` where docstatus = 1 and status = 'Overdue'
                                            and outstanding_amount > 0 and is_return = 0 and customer = %(customer)s
                                            and company = %(company)s
                                            and datediff(CURDATE(), due_date) > %(overdue_limt_days)s""",
                                        {'customer': self.customer,'company': self.company,'overdue_limt_days':overdue_limt_days}, as_dict=True)
            
            for row in over_due_inv:
                if role_allow in user_roles:
                    frappe.msgprint("Invoice {0} exceed overdue limit days {1}".format(row.name, overdue_limt_days));
                else:
                    frappe.throw("Invoice {0} exceed overdue limit days {1}".format(row.name, overdue_limt_days))

def get_over_due_days(customer, company):
    over_due_inv = frappe.db.sql("""SELECT max(datediff(curdate(), due_date))days 
                                    FROM `tabSales Invoice` where docstatus = 1 and status = 'Overdue'
                                    and customer = %(customer)s and company = %(company)s""",
                                    {'customer': customer,'company': company}, as_dict=True)
    if over_due_inv:
        if over_due_inv[0].days:
            return over_due_inv[0].days
        else:
            return 0
    else: 
        return 0

def set_pick_list_barcode(self, args):

    for row in self.locations:
        barcode = get_item_barcode(row.item_code)
        if barcode:
            row.barcode = barcode
            row.partial_barcode = barcode[-5:]

def get_item_barcode(item_code):
    barcode = frappe.db.sql(""" SELECT GROUP_CONCAT(barcode)barcode_str FROM `tabItem Barcode` where `tabItem Barcode`.parent = %(item_code)s  """,{'item_code':item_code}, as_dict=True)
    if barcode:
        if barcode[0].barcode_str:
            return barcode[0].barcode_str
        else:
            return None
    return None

def set_sales_order_pick_list(self, args):
    
    for row in self.locations:
        if row.sales_order:
            self.sales_order = row.sales_order
            break

def update_dn_with_pick_list(self, args):
    
	for row in self.items:
		if row.pick_list_item:
			barcode = frappe.db.sql(""" SELECT parent FROM `tabPick List Item` where name = %(name)s """,{'name':row.pick_list_item}, as_dict=True)
			if barcode:
				if barcode[0].parent:
					emp_driver = frappe.db.get_value('Pick List', barcode[0].parent, 'employee_driver')
					vehicle = frappe.db.get_value('Pick List', barcode[0].parent, 'vehicle_')
					self.employee_driver = emp_driver
					self.vehicle_ = vehicle
					break
				else:
					return None
			return None


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
	doc = frappe.get_doc("Delivery Note", source_name)

	to_make_invoice_qty_map = {}
	returned_qty_map = get_returned_qty_map(source_name)
	invoiced_qty_map = get_invoiced_qty_map(source_name)

	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")

		if len(target.get("items")) == 0:
			frappe.throw(_("All these items have already been Invoiced/Returned"))

		target.run_method("calculate_taxes_and_totals")

		# set company address
		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = to_make_invoice_qty_map[source_doc.name]

		if source_doc.serial_no and source_parent.per_billed > 0 and not source_parent.is_return:
			target_doc.serial_no = get_delivery_note_serial_no(
				source_doc.item_code, target_doc.qty, source_parent.name
			)

	def get_pending_qty(item_row):
		pending_qty = item_row.qty - invoiced_qty_map.get(item_row.name, 0)

		returned_qty = 0
		if returned_qty_map.get(item_row.name, 0) > 0:
			returned_qty = flt(returned_qty_map.get(item_row.name, 0))
			returned_qty_map[item_row.name] -= pending_qty

		if returned_qty:
			if returned_qty >= pending_qty:
				pending_qty = 0
				returned_qty -= pending_qty
			else:
				pending_qty -= returned_qty
				returned_qty = 0

		to_make_invoice_qty_map[item_row.name] = pending_qty

		return pending_qty

	doc = get_mapped_doc(
		"Delivery Note",
		source_name,
		{
			"Delivery Note": {
				"doctype": "Sales Invoice",
				"field_map": {"is_return": "is_return", "employee_id": "employee"},
				"validation": {"docstatus": ["=", 1]},
			},
			"Delivery Note Item": {
				"doctype": "Sales Invoice Item",
				"field_map": {
					"name": "dn_detail",
					"parent": "delivery_note",
					"so_detail": "so_detail",
					"against_sales_order": "sales_order",
					"serial_no": "serial_no",
					"cost_center": "cost_center",
				},
				"postprocess": update_item,
				"filter": lambda d: get_pending_qty(d) <= 0
				if not doc.get("is_return")
				else get_pending_qty(d) > 0,
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {
				"doctype": "Sales Team",
				"field_map": {"incentives": "incentives"},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	automatically_fetch_payment_terms = cint(
		frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
	)
	if automatically_fetch_payment_terms:
		doc.set_payment_schedule()

	doc.set_onload("ignore_price_list", True)

	return doc