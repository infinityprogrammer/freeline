# Copyright (c) 2022, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartyStatement(Document):

	def get_opening_balance(self,customer, currency):
		opening_balance = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where inv.employee = %(employee)s and party_type = 'Customer' and gl.party = %(customer)s 
          								AND gl.posting_date < %(from_date)s and gl.company = %(company)s and gl.is_cancelled = 0 and inv.currency = %(currency)s """,
                                  	{'employee': self.get("employee"), 'customer':customer,'from_date':self.get("from_date"),'company':self.get("company"),'currency':currency}, as_dict=True)
		return opening_balance;

	def get_customer_opening_balance(self,customer, currency_val):
		opening_balance = frappe.db.sql(""" SELECT ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
											sum(debit_in_account_currency - credit_in_account_currency), SUM(debit_in_account_currency/conversion_rate - 
											credit_in_account_currency/conversion_rate)), 0)net_balance
											FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
											where party_type = 'Customer' and gl.party = %(customer)s and gl.is_cancelled = 0
											AND gl.posting_date < %(from_date)s and gl.company = %(company)s and inv.currency = %(currency_val)s """,
                                  	{'customer': self.get("customer"), 'customer':customer,'from_date':self.get("from_date"),'company':self.get("company"),'currency_val':currency_val}, as_dict=True)
		return opening_balance;

	def get_customer_age_days(self,days,customer, currency):
		condition = ""
		if days == "1":
			condition += " and DATEDIFF(CURDATE(),due_date) between 0 and 30"
		elif days == "2":
			condition += " and DATEDIFF(CURDATE(),due_date) between 31 and 59"
		elif days == "3":
			condition += " and DATEDIFF(CURDATE(),due_date) between 60 and 89"
		else:
			condition += " and DATEDIFF(CURDATE(),due_date) > 89"

		age_day = frappe.db.sql(""" SELECT ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
									SUM(outstanding_amount), SUM(outstanding_amount/conversion_rate)), 0)age_balance FROM `tabSales Invoice`
									WHERE outstanding_amount != 0 and currency = %(currency)s and customer = %(customer)s and company = %(company)s and employee = %(employee)s and docstatus=1 {condition}""".format(condition=condition),
                                  	{'customer': customer, 'employee':self.get("employee"),'company':self.get("company"),'currency':currency}, as_dict=True)
		return age_day

	def get_customer_statement_age_days(self,days,customer, currency_val):
		condition = ""
		if days == "1":
			condition += " and DATEDIFF(CURDATE(),due_date) <= 30"
		elif days == "2":
			condition += " and DATEDIFF(CURDATE(),due_date) between 31 and 59"
		elif days == "3":
			condition += " and DATEDIFF(CURDATE(),due_date) between 60 and 89"
		else:
			condition += " and DATEDIFF(CURDATE(),due_date) > 89"

		age_day = frappe.db.sql(""" SELECT ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
									SUM(outstanding_amount), SUM(outstanding_amount/conversion_rate)), 0)age_balance FROM `tabSales Invoice`
									WHERE outstanding_amount != 0 AND docstatus = 1 and currency = %(currency_val)s and customer = %(customer)s and company = %(company)s {condition}""".format(condition=condition),
                                  	{'customer': customer,'company':self.get("company"),'currency_val':currency_val}, as_dict=True)
		return age_day
 
	@frappe.whitelist()
	def get_party_statement(self):
		
		gl_entries = frappe.db.sql(""" SELECT gl.posting_date,voucher_no,party,debit_in_account_currency,
									credit_in_account_currency,against_voucher,employee_name,voucher_type,gl.remarks,
									(SELECT user_remark FROM `tabJournal Entry` j where j.name = gl.voucher_no)jv_remarks
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where gl.is_cancelled = 0 and inv.employee = %(employee)s and gl.company = %(company)s and gl.posting_date between %(from_date)s and %(to_date)s order by 1""",
                                  {'employee': self.get("employee"),'from_date':self.get("from_date"),'to_date':self.get("to_date"),'company':self.get("company")}, as_dict=True)
		return gl_entries;

	@frappe.whitelist()
	def get_party_ageing(self, doc, currency_val):
		
		age_entries = frappe.db.sql("""SELECT party_type,party,inv.currency,sum(debit_in_account_currency - credit_in_account_currency)net_balance
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where inv.employee = %(employee)s and inv.currency = %(currency_val)s and party_type = 'Customer' and gl.is_cancelled=0 
									and gl.company = %(company)s and gl.posting_date between %(from_date)s and %(to_date)s group by party_type,party 
         							having round(sum(debit_in_account_currency - credit_in_account_currency),1) != 0""",
                                  {'employee': self.get("employee"),'from_date':self.get("from_date"),'to_date':self.get("to_date"),'company':self.get("company"),'currency_val':currency_val}, as_dict=True)
		
		for age_ent in age_entries:
			age_ent['opening'] = "0"
			opening_amt = self.get_opening_balance(age_ent.party, age_ent.currency)
			age_ent['opening'] = opening_amt[0].net_balance

			age_ent['first'] = "0"
			first_age = self.get_customer_age_days("1",age_ent.party, age_ent.currency)
			age_ent['first'] = first_age[0].age_balance

			age_ent['second'] = "0"
			first_age = self.get_customer_age_days("2",age_ent.party, age_ent.currency)
			age_ent['second'] = first_age[0].age_balance
   
			age_ent['third'] = "0"
			first_age = self.get_customer_age_days("3",age_ent.party, age_ent.currency)
			age_ent['third'] = first_age[0].age_balance
   
			age_ent['ext'] = "0"
			first_age = self.get_customer_age_days("4",age_ent.party, age_ent.currency)
			age_ent['ext'] = first_age[0].age_balance

		return age_entries;

	@frappe.whitelist()
	def get_customer_statement(self):
		
		gl_entries = frappe.db.sql(""" SELECT gl.posting_date,party_type,party,debit_in_account_currency,credit_in_account_currency,voucher_no,voucher_type,
										against_voucher_type,against_voucher,employee,employee_name,gl.remarks 
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where party_type = 'Customer' and party =  %(customer)s and gl.is_cancelled = 0
										and gl.company = %(company)s and gl.posting_date between %(from_date)s and %(to_date)s order by 1""",
                                  {'customer': self.get("customer"),'from_date':self.get("from_date"),'to_date':self.get("to_date"),'company':self.get("company")}, as_dict=True)
		return gl_entries;

	@frappe.whitelist()
	def get_customer_ageing(self, doc, currency_val):
		age_entries = frappe.db.sql("""SELECT party_type,party,ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
										sum(debit_in_account_currency - credit_in_account_currency), SUM(debit_in_account_currency/conversion_rate - 
										credit_in_account_currency/conversion_rate)), 0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where gl.party = %(customer)s and party_type = 'Customer' AND inv.currency = %(currency_val)s and gl.company = %(company)s and gl.is_cancelled = 0 and gl.posting_date between %(from_date)s and %(to_date)s group by party_type,party 
										having sum(debit_in_account_currency - credit_in_account_currency) != 0""",
                                  {'customer': self.get("customer"),'from_date':self.get("from_date"),'to_date':self.get("to_date"),'company':self.get("company"),'currency_val':currency_val}, as_dict=True)
  
		for age_ent in age_entries:
			age_ent['opening'] = "0"
			opening_amt = self.get_customer_opening_balance(age_ent.party, currency_val)
			age_ent['opening'] = opening_amt[0].net_balance

			age_ent['first'] = "0"
			first_age = self.get_customer_statement_age_days("1",age_ent.party, currency_val)
			age_ent['first'] = first_age[0].age_balance

			age_ent['second'] = "0"
			first_age = self.get_customer_statement_age_days("2",age_ent.party, currency_val)
			age_ent['second'] = first_age[0].age_balance
   
			age_ent['third'] = "0"
			first_age = self.get_customer_statement_age_days("3",age_ent.party, currency_val)
			age_ent['third'] = first_age[0].age_balance
   
			age_ent['ext'] = "0"
			first_age = self.get_customer_statement_age_days("4",age_ent.party, currency_val)
			age_ent['ext'] = first_age[0].age_balance

		return age_entries;
		
		
@frappe.whitelist()
def get_statement_customer(doc_name):
	customer_list = frappe.db.sql("""SELECT party,party_name FROM `tabAgeing Details` WHERE parent = %(parent)s
									UNION ALL
									SELECT party,party_name  FROM `tabAgeing Details IQD` WHERE parent = %(parent)s""",
                                  {'parent': doc_name}, as_dict=True)
	
	return customer_list;

@frappe.whitelist()
def get_customer_statement_details(company,from_date,to_date,customer,employee,s_currency):
	statement_details = frappe.db.sql("""SELECT gl.posting_date,voucher_no,party,debit_in_account_currency as dbt,
										credit_in_account_currency as crt,
										(CASE
											WHEN (SELECT acc.account_currency FROM `tabAccount` acc WHERE acc.name = inv.debit_to) = inv.currency THEN debit_in_account_currency
											ELSE debit_in_account_currency / inv.conversion_rate
										END) AS debit_in_account_currency,
										(CASE
											WHEN (SELECT acc.account_currency FROM `tabAccount` acc WHERE acc.name = inv.debit_to) = inv.currency THEN credit_in_account_currency
											ELSE credit_in_account_currency / inv.conversion_rate
										END) AS credit_in_account_currency,
										against_voucher,employee_name,voucher_type,gl.remarks,inv.due_date,
										(SELECT user_remark FROM `tabJournal Entry` j where j.name = gl.voucher_no)jv_remarks
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where
										inv.employee = %(employee)s and gl.party_type ='Customer' and gl.party = %(customer)s AND inv.currency = %(s_currency)s
          								and gl.posting_date between %(from_date)s and %(to_date)s and is_cancelled=0 and gl.company = %(company)s  order by 1""",
                                  		{'employee': employee,'customer':customer,'from_date':from_date,'to_date':to_date,'company':company,'s_currency':s_currency}, as_dict=True)
	return statement_details;

@frappe.whitelist()
def get_customer_opening(company,employee, customer, from_date, s_currency):
	opening_balance = frappe.db.sql(""" SELECT ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
										sum(debit_in_account_currency - credit_in_account_currency), SUM(debit_in_account_currency/conversion_rate - 
										credit_in_account_currency/conversion_rate)), 0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where inv.employee = %(employee)s and party_type = 'Customer' and gl.party = %(customer)s 
          								AND gl.posting_date < %(from_date)s and gl.company = %(company)s and gl.is_cancelled = 0 AND inv.currency = %(s_currency)s""",
                                  	{'employee': employee, 'customer':customer,'from_date':from_date,'company':company,'s_currency':s_currency}, as_dict=True)
	return opening_balance;


@frappe.whitelist()
def get_dist_employee(customer,from_date,to_date,company):
	emp_list = frappe.db.sql("""SELECT ifnull(employee,'Z')employee,count(*)count
									FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
									where party_type = 'Customer' and party = %(customer)s and is_cancelled = 0 and gl.posting_date between %(from_date)s and %(to_date)s
									and gl.company = %(company)s group by employee having count(*) >0 order by 1""",
                                  {'customer': customer,'from_date':from_date,'to_date':to_date,'company':company}, as_dict=True)
	return emp_list;

@frappe.whitelist()
def sales_rep_statement_details(company,from_date,to_date,customer,employee,s_currency):
	statement_details = frappe.db.sql("""SELECT gl.posting_date,party_type,party,round(debit_in_account_currency/inv.conversion_rate,2)debit_in_account_currency1,
										round(credit_in_account_currency/inv.conversion_rate,2)credit_in_account_currency1,voucher_no,voucher_type,
										(CASE
											WHEN (SELECT acc.account_currency FROM `tabAccount` acc WHERE acc.name = inv.debit_to) = inv.currency THEN debit_in_account_currency
											ELSE debit_in_account_currency / inv.conversion_rate
										END) AS debit_in_account_currency,
										(CASE
											WHEN (SELECT acc.account_currency FROM `tabAccount` acc WHERE acc.name = inv.debit_to) = inv.currency THEN credit_in_account_currency
											ELSE credit_in_account_currency / inv.conversion_rate
										END) AS credit_in_account_currency,
										against_voucher_type,against_voucher,employee,employee_name,gl.remarks 
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where party_type = 'Customer' and party = %(customer)s and is_cancelled = 0 and gl.company = %(company)s AND inv.currency = %(s_currency)s
										and gl.posting_date between %(from_date)s and %(to_date)s and employee = %(employee)s order by 1""",
										{'customer': customer,'company':company,'from_date':from_date,'to_date':to_date,'employee':employee,'s_currency':s_currency}, as_dict=True)
	return statement_details;

@frappe.whitelist()
def emp_null_statement_details(company,from_date,to_date,customer, s_currency):
	statement_details = frappe.db.sql("""SELECT gl.posting_date,party_type,party,round(debit_in_account_currency,2)debit_in_account_currency,
                                   				round(credit_in_account_currency,2)credit_in_account_currency,voucher_no,voucher_type,
												against_voucher_type,against_voucher,employee,employee_name,gl.remarks 
												FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
												where party_type = 'Customer' and party = %(customer)s and is_cancelled = 0 and gl.company = %(company)s and inv.currency = %(s_currency)s
												and gl.posting_date between %(from_date)s and %(to_date)s and (employee is null or employee ='') order by 1""",
                                  				{'customer': customer,'company':company,'from_date':from_date,'to_date':to_date,'s_currency':s_currency}, as_dict=True)
	return statement_details;

@frappe.whitelist()
def get_emp_null_opening(company, customer, from_date, s_currency):
	opening_balance = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0)net_balance
										FROM `tabGL Entry` gl LEFT JOIN `tabSales Invoice` inv ON inv.name = gl.against_voucher
										where party_type = 'Customer' and gl.party = %(customer)s and gl.is_cancelled = 0 AND inv.currency = %(s_currency)s
          								AND gl.posting_date < %(from_date)s and gl.company = %(company)s and (employee is null or employee ='')""",
                                  	{'customer':customer,'from_date':from_date,'company':company,'s_currency':s_currency}, as_dict=True)
	return opening_balance;

@frappe.whitelist()
def get_unallocated_payment(company, customer, employee, s_currency):
	unallocated_amount = frappe.db.sql(""" SELECT ifnull(unallocated_amount, 0)unallocated_amount FROM `tabPayment Entry` where paid_from_account_currency = %(s_currency)s 
										AND unallocated_amount > 0 AND employee_id = %(employee)s AND party_type = 'Customer'
										and party = %(customer)s and docstatus=1 and company = %(company)s """,
                                  	{'customer':customer,'company':company,'s_currency':s_currency,'employee':employee}, as_dict=True)
	
	if not unallocated_amount:
		zero_amt = {"unallocated_amount": 0.00 }
		unallocated_amount.append(zero_amt)
		
		return unallocated_amount
	
	return unallocated_amount;

@frappe.whitelist()
def get_unallocated_payment_not_in_ageing(company, employee, s_currency, parent):
	unallocated_amount = frappe.db.sql(""" SELECT party,sum(ifnull(unallocated_amount, 0))unallocated_amount FROM `tabPayment Entry` where paid_from_account_currency = %(s_currency)s
											AND unallocated_amount > 0 AND employee_id = %(employee)s AND party_type = 'Customer'
											and docstatus=1 and company = %(company)s and party not in
											(SELECT party FROM `tabAgeing Details` where parent = %(parent)s AND party_type = 'Customer') group by party""",
                                  	{'company':company,'s_currency':s_currency,'employee':employee,'parent':parent}, as_dict=True)
	
	return unallocated_amount;

@frappe.whitelist()
def get_not_due_amount(company, customer, employee, s_currency, posting_date):
	not_due_amount = frappe.db.sql(""" SELECT ifnull(IF ((SELECT account_currency from `tabAccount` where name = debit_to) = currency, 
										SUM(outstanding_amount), SUM(outstanding_amount/conversion_rate)), 0)no_due FROM `tabSales Invoice`
										WHERE outstanding_amount != 0 and currency = %(currency)s and customer = %(customer)s and company = %(company)s 
										and employee = %(employee)s and docstatus=1 and DATEDIFF(CURDATE(),due_date) < 0 and posting_date <= %(posting_date)s """,
										{'customer': customer, 'employee':employee,'company':company,'currency':s_currency,'posting_date':posting_date}, as_dict=True)
	return not_due_amount;