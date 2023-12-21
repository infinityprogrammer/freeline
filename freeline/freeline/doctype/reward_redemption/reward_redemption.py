# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe.model.document import Document

class RewardRedemption(Document):

	def validate(self):
		pass

	def on_submit(self):
		si = frappe.new_doc("Sales Invoice")
		si.naming_series = 'CRN-.site_id.-.YY.-.####.'
		si.docstatus = 0
		si.customer = self.customer
		si.is_return = 1
		si.company = self.company
		si.posting_date = nowdate()
		si.set_posting_time = 1
		si.currency = self.currency
		si.update_stock = 0
		si.doctype = 'Sales Invoice'
		si.disable_rounded_total = 1
		si.reward_redemption = self.name

		cost_c = frappe.db.get_value('Company', self.company, 'cost_center')
		si.cost_center = cost_c

		si.remarks = 'LOYALTY REDEMPTION FROM {0} to {1}'.format(self.from_date, self.to_date)

		si.append("items",{
							"item_code" : 'REBATE',
							"description" : 'LOYALTY REDEMPTION FROM {0} to {1}'.format(self.from_date, self.to_date),
							"qty" : -1,
							"rate" : self.total_redeem_point * -1,
							"cost_center" :cost_c,
						})
		
		si.save(ignore_permissions=True)

		update_redeem = frappe.db.sql("""UPDATE `tabReward Point Entry` set redeem_status = 'Redeemed'
									where name in (select program_name from `tabRedemption Details` where parent = %(parent)s)""", 
									{'parent': self.name}, as_dict=True)
	def on_cancel(self):
		update_redeem = frappe.db.sql("""UPDATE `tabReward Point Entry` set redeem_status = 'Earned'
									where name in (select program_name from `tabRedemption Details` where parent = %(parent)s)""", 
									{'parent': self.name}, as_dict=True)

	@frappe.whitelist()
	def get_redeemable_points(self):

		conditons = ""
		if self.get("from_date") and self.get("to_date"):
			conditons += " AND posting_date between %(from_date)s and %(to_date)s"
		
		if self.get("reward_program"):
			conditons += " AND program_name = %(reward_program)s"

		programs = frappe.db.sql("""SELECT name, program_name, company, posting_date, redeem_status,
									sales_invoice, customer, total_point, balance_point FROM `tabReward Point Entry`
									where redeem_status = 'Earned' and company = %(company)s and balance_point != 0
						   			and customer = %(customer)s and currency = %(currency)s {0}""".format(conditons), 
									{'from_date': self.from_date, 'to_date': self.to_date, 
		  							'reward_program': self.reward_program, 'customer': self.customer, 
									'currency': self.currency, 'company': self.company}, as_dict=True)
		return programs