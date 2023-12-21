# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RewardProgram(Document):

	def validate(self):
		if not self.get("__islocal"):
			old_doc = self.get_doc_before_save()
			if old_doc.customer != self.customer:
				frappe.throw("You are not allowed to change customer once the naming series get generated.")
