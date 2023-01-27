# Copyright (c) 2023, RAFI and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.utils import flt, today



def execute(filters=None):
	columns, data = [], []
	
	if not filters.get("company"):
		return

	data = get_data(filters)
	columns = get_columns()

	for row in data:
		three_month_avg = (row.sold_m1 + row.sold_m2 + row.sold_m3)/3
		batches = get_item_batch_by_lead_days(row.item_code)
		row.update(
				{
					"three_month_avg":three_month_avg
				})
		i = 0;
		batch_avg = 0;
		for b in batches:
			i +=1
			batch_val = get_batch_val(row.item_code, b.batch_no)
			batch_avg += batch_val
		if i:
			row_avg = (batch_avg/i)
			row.update(
				{
					"ttts":row_avg
				})
		else:
			row.update(
				{
					"ttts":0
				})

	return columns, data

def get_data(filters):

	data = frappe.db.sql(""" SELECT name,item_code,item_name,item_group,
							(SELECT sum(actual_qty) FROM `tabBin` bin where bin.item_code = item.name and 
							warehouse in (SELECT name FROM `tabWarehouse` where company = %(company)s))current_stock,
							0 ttts,
							(SELECT stock_value FROM `tabStock Ledger Entry` sle where is_cancelled = 0 and sle.item_code = item.name 
							and company = %(company)s order by posting_date desc limit 1)cost,
							ifnull((SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
							and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
							and datediff(curdate(),sle.posting_date) between 0 and 30), 0)sold_m1,
							ifnull((SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
							and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
							and datediff(curdate(),sle.posting_date) between 31 and 60), 0)sold_m2,
							ifnull((SELECT abs(sum(actual_qty)) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
							and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
							and datediff(curdate(),sle.posting_date) between 61 and 90), 0)sold_m3,0 stock_cover,
							(SELECT sum(amount) FROM `tabSales Invoice` sl, `tabSales Invoice Item` it
							where sl.name = it.parent and sl.docstatus = 1 and it.item_code = item.name and company=  %(company)s)turnover
							FROM `tabItem` item """,filters,as_dict=True)
	return data

def get_item_batch_by_lead_days(item_code):
	item_batches = frappe.db.sql(""" SELECT distinct batch_no FROM `tabStock Ledger Entry` sle 
									where item_code = %(item)s and sle.is_cancelled=0 and batch_no != ''
									AND sle.voucher_type in ('Sales Invoice','Delivery Note')""",{'item': item_code}, as_dict=True)

	return item_batches

def get_batch_reception_date(batch, item):
	batch_rec_date = frappe.db.sql(""" SELECT MIN(pr.posting_date)posting_date FROM `tabPurchase Receipt` pr, `tabPurchase Receipt Item` pt 
										where pr.name = pt.parent
										and pt.item_code = %(item)s and pr.docstatus=1
										and pt.batch_no = %(batch)s """,{'item': item_code,'batch':batch}, as_dict=True)

	if batch_rec_date:
		return batch_rec_date[0].posting_date
	else:
		return

def get_batch_val(item_code, batch):

	batch_val = frappe.db.sql("""SELECT ifnull(round(sum(batch_val)/sum(actual_qty),2) , 0)batch_val FROM (
								SELECT a1.*,(actual_qty * diff_days)batch_val FROM (
								SELECT item_code,posting_date,batch_no,sum(actual_qty *-1)actual_qty,
								datediff(sle.posting_date, 
								(SELECT MIN(pr.posting_date)posting_date FROM `tabPurchase Receipt` pr, `tabPurchase Receipt Item` pt 
								where pr.name = pt.parent
								and pt.item_code = %(item)s and pr.docstatus=1
								and pt.batch_no = %(batch)s))diff_days
								FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Delivery Note', 'Sales Invoice')
								and sle.item_code = %(item)s and sle.batch_no = %(batch)s
								and sle.is_cancelled = 0
								group by item_code,posting_date,batch_no)a1)a2 """,{'item': item_code,'batch':batch}, as_dict=True)
	return batch_val[0].batch_val


def get_columns():
	return [
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Item Name"), 
			"fieldname": "item_name", 
			"width": 190
		},
		{
			"label": _("Current Stock"), 
			"fieldname": "current_stock", 
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Cost"), 
			"fieldname": "cost", 
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("TTTS (Age)"), 
			"fieldname": "ttts", 
			"fieldtype": "Float",
			"width": 130
		},
		{
			"label": _("Sold Qty (0 - 30)"), 
			"fieldname": "sold_m1", 
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Sold Qty (31 - 60)"), 
			"fieldname": "sold_m2", 
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Sold Qty (61 - 90)"), 
			"fieldname": "sold_m3",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Moving Average"), 
			"fieldname": "three_month_avg",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Stock Cover"),
			"fieldname": "stock_cover",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Turnover"),
			"fieldname": "turnover",
			"fieldtype": "Float",
			"width": 100
		}
	]
