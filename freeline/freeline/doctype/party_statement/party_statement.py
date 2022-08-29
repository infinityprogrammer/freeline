# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartyStatement(Document):
    
	@frappe.whitelist()
	def get_party_statement(self):
		
		filters_inv = {}
		filters_inv['company'] = ['=', self.get("company")]
		filters_inv['posting_date'] = ['between', [self.get("from_date")],[self.get("to_date")]]
		filters_inv['is_cancelled'] = ['=',0]

		filters_inv = frappe._dict(filters_inv)
		# print("filters_inv")
		print(filters_inv)
		gl_entries = frappe.db.sql(""" SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
									credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks 
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where gl.is_cancelled = 0 and inv.employee_name = %(employee)s and gl.posting_date between %(from_date)s and %(to_date)s order by 1""",
                                  {'employee': self.get("employee_name"),'from_date':self.get("from_date"),'to_date':self.get("to_date")}, as_dict=True)

		print("____________gl0----")
		print(gl_entries)
		# gl_entries = frappe.get_list("GL Entry", filters=filters_inv, order_by="posting_date",
		# 	fields=['company','party','debit_in_account_currency','credit_in_account_currency','voucher_type','voucher_no','against_voucher'])
		
		# for gl in gl_entries:
		# 	gl['paid_to'] = ""
		# 	gl['account_name'] = ""
		# 	if inv.company != self.company: 
		# 		r_company = self.get_related_party_account(inv.company,self.company)
		# 		if not r_company:
		# 			frappe.throw("Related party account not found for {0} to {}".format(inv.company,self.company))

		# 		inv['paid_to'] = r_company
		# 	inv['account_name'] = frappe.db.get_value('Account', inv['credit_to'], 'account_name')

		return gl_entries;
