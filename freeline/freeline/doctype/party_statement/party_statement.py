# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartyStatement(Document):
    
	@frappe.whitelist()
	def get_party_statement(self):
		
		gl_entries = frappe.db.sql(""" SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
									credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks 
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where gl.is_cancelled = 0 and inv.employee_name = %(employee)s and gl.posting_date between %(from_date)s and %(to_date)s order by 1""",
                                  {'employee': self.get("employee_name"),'from_date':self.get("from_date"),'to_date':self.get("to_date")}, as_dict=True)
		return gl_entries;

	@frappe.whitelist()
	def get_party_ageing(self):
		
		age_entries = frappe.db.sql("""SELECT party_type,party,sum(debit_in_account_currency - credit_in_account_currency)net_balance
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where inv.employee_name = %(employee)s and party_type = 'Customer' and gl.posting_date between %(from_date)s and %(to_date)s group by party_type,party 
         							having sum(debit_in_account_currency - credit_in_account_currency) != 0 """,
                                  {'employee': self.get("employee_name"),'from_date':self.get("from_date"),'to_date':self.get("to_date")}, as_dict=True)
		return age_entries;

@frappe.whitelist()
def get_statement_customer(doc_name):
	customer_list = frappe.db.sql("""SELECT party,party_name FROM `tabAgeing Details` where parent = %(parent)s""",
                                  {'parent': doc_name}, as_dict=True)
	return customer_list;

@frappe.whitelist()
def get_customer_statement_details(company,from_date,to_date,customer,employee):
	statement_details = frappe.db.sql("""SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
										credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks,inv.due_date
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where
										inv.employee_name = %(employee)s and gl.party_type ='Customer' and gl.party = %(customer)s 
          								and gl.posting_date between %(from_date)s and %(to_date)s and is_cancelled=0 and gl.company = %(company)s  order by 1""",
                                  		{'employee': employee,'customer':customer,'from_date':from_date,'to_date':to_date,'company':company}, as_dict=True)
	return statement_details;

@frappe.whitelist()
def get_customer_opening(company,employee, customer, from_date):
	opening_balance = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where
										inv.employee_name = %(employee)s and party_type = 'Customer' and gl.party = %(customer)s AND gl.posting_date < %(from_date)s and gl.company = %(company)s
										group by party_type,party """,
                                  {'employee': employee, 'customer':customer,'from_date':from_date,'company':company}, as_dict=True)
	
	return opening_balance;