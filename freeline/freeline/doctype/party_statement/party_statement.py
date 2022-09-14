# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartyStatement(Document):

	def get_opening_balance(self,customer):
		opening_balance = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where inv.employee = %(employee)s and party_type = 'Customer' and gl.party = %(customer)s 
          								AND gl.posting_date < %(from_date)s and gl.company = %(company)s""",
                                  	{'employee': self.get("employee"), 'customer':customer,'from_date':self.get("from_date"),'company':self.get("company")}, as_dict=True)
		return opening_balance;

	def get_customer_age_days(self,days,customer):
		condition = ""
		if days == "1":
			condition += " and DATEDIFF(CURDATE(),due_date) <= 30"
		elif days == "2":
			condition += " and DATEDIFF(CURDATE(),due_date) between 31 and 59"
		elif days == "3":
			condition += " and DATEDIFF(CURDATE(),due_date) between 60 and 89"
		else:
			condition += " and DATEDIFF(CURDATE(),due_date) > 89"

		age_day = frappe.db.sql(""" SELECT IFNULL(SUM(outstanding_amount),0)age_balance FROM `tabSales Invoice`
									WHERE customer = %(customer)s and company = %(company)s and employee = %(employee)s {condition}""".format(condition=condition),
                                  	{'customer': customer, 'employee':self.get("employee"),'company':self.get("company")}, as_dict=True)
		return age_day

	@frappe.whitelist()
	def get_party_statement(self):
		
		gl_entries = frappe.db.sql(""" SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
									credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks,
									(SELECT user_remark FROM `tabJournal Entry` j where j.name = gl.voucher_no)jv_remarks
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where gl.is_cancelled = 0 and inv.employee = %(employee)s and gl.posting_date between %(from_date)s and %(to_date)s order by 1""",
                                  {'employee': self.get("employee"),'from_date':self.get("from_date"),'to_date':self.get("to_date")}, as_dict=True)
		return gl_entries;

	@frappe.whitelist()
	def get_party_ageing(self):
		
		age_entries = frappe.db.sql("""SELECT party_type,party,sum(debit_in_account_currency - credit_in_account_currency)net_balance
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where inv.employee = %(employee)s and party_type = 'Customer' and gl.posting_date between %(from_date)s and %(to_date)s group by party_type,party 
         							having sum(debit_in_account_currency - credit_in_account_currency) != 0 """,
                                  {'employee': self.get("employee"),'from_date':self.get("from_date"),'to_date':self.get("to_date")}, as_dict=True)
		for age_ent in age_entries:
			age_ent['opening'] = "0"
			opening_amt = self.get_opening_balance(age_ent.party)
			age_ent['opening'] = opening_amt[0].net_balance

			age_ent['first'] = "0"
			first_age = self.get_customer_age_days("1",age_ent.party)
			age_ent['first'] = first_age[0].age_balance

			age_ent['second'] = "0"
			first_age = self.get_customer_age_days("2",age_ent.party)
			age_ent['second'] = first_age[0].age_balance
   
			age_ent['third'] = "0"
			first_age = self.get_customer_age_days("3",age_ent.party)
			age_ent['third'] = first_age[0].age_balance
   
			age_ent['ext'] = "0"
			first_age = self.get_customer_age_days("4",age_ent.party)
			age_ent['ext'] = first_age[0].age_balance

		return age_entries;

@frappe.whitelist()
def get_statement_customer(doc_name):
	customer_list = frappe.db.sql("""SELECT party,party_name FROM `tabAgeing Details` where parent = %(parent)s""",
                                  {'parent': doc_name}, as_dict=True)
	return customer_list;

@frappe.whitelist()
def get_customer_statement_details(company,from_date,to_date,customer,employee):
	statement_details = frappe.db.sql("""SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
										credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks,inv.due_date,
										(SELECT user_remark FROM `tabJournal Entry` j where j.name = gl.voucher_no)jv_remarks
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where
										inv.employee = %(employee)s and gl.party_type ='Customer' and gl.party = %(customer)s 
          								and gl.posting_date between %(from_date)s and %(to_date)s and is_cancelled=0 and gl.company = %(company)s  order by 1""",
                                  		{'employee': employee,'customer':customer,'from_date':from_date,'to_date':to_date,'company':company}, as_dict=True)
	return statement_details;

@frappe.whitelist()
def get_customer_opening(company,employee, customer, from_date):
	opening_balance = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where inv.employee = %(employee)s and party_type = 'Customer' and gl.party = %(customer)s 
          								AND gl.posting_date < %(from_date)s and gl.company = %(company)s""",
                                  	{'employee': employee, 'customer':customer,'from_date':from_date,'company':company}, as_dict=True)
	return opening_balance;