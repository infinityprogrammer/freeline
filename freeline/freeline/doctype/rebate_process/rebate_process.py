# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe import _
import json
import datetime

from frappe.model.document import Document

class RebateProcess(Document):
	
	def validate(self):
		exist = frappe.db.sql(""" SELECT name FROM `tabRebate Process` where customer = %(customer)s and rebate_type = %(rebate_type)s 
									and name != %(name)s""",
								{'customer': self.customer, 'rebate_type': self.rebate_type,'name':self.name}, as_dict=True)

		if not self.rebate_details:
			frappe.throw("Rebate details is mandatory")
		if exist:
			frappe.throw("Rebate is already is exist in this customer with rebate type {0}".format(self.rebate_type))
		
		for grp in self.rebate_details:
			exist_item_group = frappe.db.sql("""SELECT customer,item_group 
											FROM `tabRebate Process` r, `tabRebate Definition` d
											where r.name = d.parent and r.customer = %(customer)s and d.item_group = %(item_group)s and r.name != %(name)s""",
											{'customer': self.customer,'item_group': grp.item_group,'name':self.name}, as_dict=True)
			
			if exist_item_group:
				frappe.throw("Item group already defined in other rebate of this customer.")

				