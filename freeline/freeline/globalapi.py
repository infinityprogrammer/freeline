from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate, flt, cint, get_datetime_str, nowdate
from frappe import _
import json
import datetime


# Number Card APIs for Dashboard

@frappe.whitelist()
def get_total_sale_ytd(filters=None):
    
    # yr =[]
    now_year = datetime.datetime.now().year
    # yr.append(now_year)
    # filters['year_dt'] = yr
    context = {}
    # print(filters)
    
    ytd_sale = frappe.db.sql(""" SELECT ifnull(round(sum(grand_total),2),0)sale FROM `tabSales Invoice` where YEAR(posting_date) = %(year)s
                                and docstatus = 1""",
                                {'year': now_year}, as_dict=True)
    context['value'] = ytd_sale[0].sale
    context['fieldtype'] = "Currency"
    ytd_sale_value = ytd_sale[0].sale
    return ytd_sale_value

@frappe.whitelist()
def get_total_sale_mtd():
    currentDate = datetime.date.today()
    firstDayOfMonth = datetime.date(currentDate.year, currentDate.month, 1)
    context = {}
    # print("filters ")
    # print(filters)
    mtd_sale = frappe.db.sql(""" SELECT ifnull(round(sum(grand_total),2),0)sale FROM `tabSales Invoice` where posting_date between %(start_date)s and %(end_date)s
                                and docstatus = 1""",
                                {'start_date': firstDayOfMonth,'end_date':currentDate}, as_dict=True)
    context['value'] = mtd_sale[0].sale
    context['fieldtype'] = "Currency"
    mtd_sale_value = mtd_sale[0].sale
    return mtd_sale_value

@frappe.whitelist()
def get_total_sale_order_mtd():
    currentDate = datetime.date.today()
    firstDayOfMonth = datetime.date(currentDate.year, currentDate.month, 1)
    context = {}
    mtd_sale = frappe.db.sql(""" SELECT ifnull(sum(grand_total),0)sale FROM `tabSales Order` where status != 'Closed'
                                and per_delivered = 100 and per_billed < 100
                                and docstatus = 1 AND transaction_date between %(start_date)s and %(end_date)s""",
                                {'start_date': firstDayOfMonth,'end_date':currentDate}, as_dict=True)
    context['value'] = mtd_sale[0].sale
    context['fieldtype'] = "Currency"
    mtd_sale_value = mtd_sale[0].sale
    return mtd_sale_value

# custom APIs for SFA

@frappe.whitelist()
def get_all_order_items_by_name():
    sale_order_name = frappe.db.sql(""" SELECT name FROM `tabSales Order` 
                                where docstatus = 1""", as_dict=True)
    sales_order_items = []
    for d in sale_order_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        items = frappe.db.sql(""" SELECT item_code,qty FROM `tabSales Order Item` b
                                where b.parent =  %(parent)s
                                and b.docstatus = 1""",{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_order_items.append(item_details)
    return sales_order_items

@frappe.whitelist()
def get_all_invoice_items_by_name():
    sale_invoice_name = frappe.db.sql(""" SELECT name FROM `tabSales Invoice`
                                where docstatus = 1""", as_dict=True)
    sales_invoice_items = []
    for d in sale_invoice_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        items = frappe.db.sql(""" SELECT item_code,qty FROM `tabSales Invoice Item` b
                                    where b.parent =  %(parent)s
                                    and b.docstatus = 1""",{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_invoice_items.append(item_details)
    return sales_invoice_items

@frappe.whitelist()
def get_overdue_outstanding(filters):
    overdue_outstand = frappe.db.sql(""" SELECT ifnull(sum(outstanding_amount),0)amount FROM `tabSales Invoice` where company = %(company)s and docstatus = 1""",{'company':'INFINITY'}, as_dict=True)
    
    overdue_outstand_val = overdue_outstand[0].amount
    return overdue_outstand_val

@frappe.whitelist()
def get_item_barcode(item_code):
    barcode = frappe.db.sql(""" SELECT GROUP_CONCAT(barcode)barcode_str FROM `tabItem Barcode` where `tabItem Barcode`.parent = %(item_code)s  """,{'item_code':item_code}, as_dict=True)
    
    barcode_val = barcode[0].barcode_str
    return barcode_val

@frappe.whitelist()
def get_cogs_amount():
    cogs = frappe.db.sql(""" SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0) as cogs_amt FROM `tabGL Entry` 
                                where is_cancelled = 0 and company = 'Tiejan'
                                and account like '5%' """, as_dict=True)
    
    cogs_val = cogs[0].cogs_amt
    return cogs_val


@frappe.whitelist()
def get_gp_ratio():
    gp_ratio = frappe.db.sql(""" SELECT ((
                                        (SELECT round(sum(grand_total),2) FROM `tabSales Invoice` where docstatus = 1 and company = 'Tiejan')-(SELECT ifnull(round(sum(debit_in_account_currency - credit_in_account_currency),2),0) FROM `tabGL Entry` 
                                        where is_cancelled = 0 and company = 'Tiejan'
                                        and account like '5%'))/
                                        (SELECT round(sum(grand_total),2) FROM `tabSales Invoice` where docstatus = 1 and company = 'Tiejan'))*100 as gp""", as_dict=True)
    
    gp_ratio_val = gp_ratio[0].gp
    return gp_ratio_val

@frappe.whitelist()
def get_profit_amount():
    profit = frappe.db.sql(""" SELECT (
                                (SELECT round(sum(grand_total),2) FROM `tabSales Invoice` where docstatus = 1 and company = 'Tiejan') - (SELECT ifnull(sum(debit_in_account_currency - credit_in_account_currency),0) FROM `tabGL Entry` 
                                where is_cancelled = 0 and company = 'Tiejan'
                                and account like '5%')) AS profit """, as_dict=True)
    
    profit_val = profit[0].profit
    return profit_val

@frappe.whitelist()
def get_line_total_disc(inv):
    disc_amt = frappe.db.sql(""" SELECT round(ifnull(sum(qty*discount_amount),0),2)disc FROM `tabSales Invoice Item` where parent = %(inv)s  """,{'inv':inv}, as_dict=True)
    
    disc_amt_val = disc_amt[0].disc
    return disc_amt_val

@frappe.whitelist()
def get_gross_total_amt(inv):
    gross_total = frappe.db.sql(""" SELECT round(ifnull(sum(qty*price_list_rate),0),2)gross_total FROM `tabSales Invoice Item` where parent = %(inv)s  """,{'inv':inv}, as_dict=True)
    
    gross_total_val = gross_total[0].gross_total
    return gross_total_val

@frappe.whitelist()
def get_line_total_disc_order(inv):
    disc_amt = frappe.db.sql(""" SELECT round(ifnull(sum(qty*discount_amount),0),2)disc FROM `tabSales Order Item` where parent = %(inv)s  """,{'inv':inv}, as_dict=True)
    
    disc_amt_val = disc_amt[0].disc
    return disc_amt_val

@frappe.whitelist()
def get_gross_total_amt_order(inv):
    gross_total = frappe.db.sql(""" SELECT round(ifnull(sum(qty*price_list_rate),0),2)gross_total FROM `tabSales Order Item` where parent = %(inv)s  """,{'inv':inv}, as_dict=True)
    
    gross_total_val = gross_total[0].gross_total
    return gross_total_val


@frappe.whitelist()
def get_current_ratio():
    c_ratio = frappe.db.sql(""" SELECT round((asset_val/liab_val),2)curernt_ratio FROM (
                                (SELECT sum(debit_in_account_currency - credit_in_account_currency) asset_val
                                FROM `tabGL Entry` where account in 
                                (SELECT name FROM `tabAccount` where root_type = 'Asset' and is_group = 0 and company = 'Tiejan'))a1,
                                (SELECT sum(credit_in_account_currency - debit_in_account_currency)liab_val
                                FROM `tabGL Entry` where account in 
                                (SELECT name FROM `tabAccount` where root_type = 'Liability' and is_group = 0 and company = 'Tiejan'))a2) """, as_dict=True)
    
    c_ratio_val = c_ratio[0].curernt_ratio
    return c_ratio_val

@frappe.whitelist()
def get_working_capital():
    working_cap = frappe.db.sql(""" SELECT ifnull(round((asset_val-liab_val),2),0)working_capital FROM (
                                    (SELECT sum(debit_in_account_currency - credit_in_account_currency) asset_val
                                    FROM `tabGL Entry` where account in 
                                    (SELECT name FROM `tabAccount` where root_type = 'Asset' and is_group = 0 and company = 'Tiejan'))a1,
                                    (SELECT sum(credit_in_account_currency - debit_in_account_currency)liab_val
                                    FROM `tabGL Entry` where account in 
                                    (SELECT name FROM `tabAccount` where root_type = 'Liability' and is_group = 0 and company = 'Tiejan'))a2) """, as_dict=True)
    
    working_capital_val = working_cap[0].working_capital
    return working_capital_val

@frappe.whitelist()
def get_debt_ratio():
    debt_ratio = frappe.db.sql(""" SELECT ifnull(round((liab_val/asset_val),2),0)db_ratio FROM (
                                    (SELECT sum(debit_in_account_currency - credit_in_account_currency) asset_val
                                    FROM `tabGL Entry` where account in 
                                    (SELECT name FROM `tabAccount` where root_type = 'Asset' and is_group = 0 and company = 'Tiejan'))a1,
                                    (SELECT sum(credit_in_account_currency - debit_in_account_currency)liab_val
                                    FROM `tabGL Entry` where account in 
                                    (SELECT name FROM `tabAccount` where root_type = 'Liability' and is_group = 0 and company = 'Tiejan'))a2) """, as_dict=True)
    
    debt_ratio_val = debt_ratio[0].db_ratio
    return debt_ratio_val



@frappe.whitelist()
def get_invoice_items_by_driver(driver=None):
    
    log_user = frappe.session.user
    condition = ""
    # sales_person_head = frappe.db.get_value('User Permission', {'user': log_user,'allow':'Sales Person'}, ['for_value'],as_dict=1)
    # if sales_person_head:
    #     sales_p = []
    #     sales_p.append("A")
        
    #     lft, rgt = frappe.db.get_value("Sales Person", sales_person_head.for_value, ["lft", "rgt"])
    #     sales_pers = frappe.db.sql(
    #         """
    #         select employee from `tabSales Person` where lft >= %s and rgt <= %s and is_group = 0
    #         """,
    #         (lft, rgt),
    #         as_dict=1,
    #     )
    #     for s in sales_pers:
    #         sales_p.append(s.employee)
            
    #     condition += " and employee in %(employee_id)s"
        
    if driver:
        condition += " and employee_driver = %(driver)s"
    
    sale_invoice_name = frappe.db.sql(""" SELECT name,posting_date,customer,driver,employee_driver FROM `tabSales Invoice`
                                where docstatus = 1 {condition}""".format(condition=condition),{'driver':driver}, as_dict=True)
    sales_invoice_items = []
    for d in sale_invoice_name:
        item_details = frappe._dict()
        item_details['name'] = d.name
        item_details['customer'] = d.customer
        item_details['posting_date'] = d.posting_date
        item_details['driver'] = d.driver
        item_details['employee_driver'] = d.employee_driver
        items = frappe.db.sql(""" SELECT item_code,qty,uom,delivered_qty FROM `tabSales Invoice Item` b
                                    where b.parent =  %(parent)s
                                    and b.docstatus = 1 """,{'parent': d.name}, as_dict=True)
        items_dict = []
        for i in items:
            items_dict.append(i)
        item_details.update({"items": items_dict})
        sales_invoice_items.append(item_details)
    return sales_invoice_items



@frappe.whitelist()
def get_batch_qty_api(
	batch_no=None, warehouse=None, item_code=None, posting_date=None, posting_time=None
):
	"""Returns batch actual qty if warehouse is passed,
	        or returns dict of qty by warehouse if warehouse is None

	The user must pass either batch_no or batch_no + warehouse or item_code + warehouse

	:param batch_no: Optional - give qty for this batch no
	:param warehouse: Optional - give qty for this warehouse
	:param item_code: Optional - give qty for this item"""

	out = 0
	if batch_no and warehouse:
		cond = ""
		if posting_date and posting_time:
			cond = " and timestamp(posting_date, posting_time) <= timestamp('{0}', '{1}')".format(
				posting_date, posting_time
			)

		out = float(
			frappe.db.sql(
				"""select sum(actual_qty)
			from `tabStock Ledger Entry`
			where is_cancelled = 0 and warehouse=%s and batch_no=%s {0}""".format(
					cond
				),
				(warehouse, batch_no),
			)[0][0]
			or 0
		)

	if batch_no and not warehouse:
		out = frappe.db.sql(
			"""select warehouse, sum(actual_qty) as qty
			from `tabStock Ledger Entry`
			where is_cancelled = 0 and batch_no=%s
			group by warehouse""",
			batch_no,
			as_dict=1,
		)

	if not batch_no and item_code and warehouse:
		out = frappe.db.sql(
			"""select batch_no, sum(actual_qty) as qty
			from `tabStock Ledger Entry`
			where is_cancelled = 0 and item_code = %s and warehouse=%s
			group by batch_no""",
			(item_code, warehouse),
			as_dict=1,
		)

	return out

@frappe.whitelist()
def get_batch_warehouse_qty(item_code):
    
    batch_item = []
    
    batch_qty = frappe.db.sql(""" select batch_no,warehouse,
                    (select stock_uom from `tabBatch` b where b.batch_id = batch_no)stock_uom,
                    sum(actual_qty) as qty
                    from `tabStock Ledger Entry`
                    where is_cancelled = 0 and item_code = %(item_code)s
                    group by batch_no,warehouse
                    having sum(actual_qty) > 0 """,{'item_code':item_code}, as_dict=True)
    
    batch_details = frappe._dict()
    batch_details['item_code'] = item_code
    
    batch_items_dict = []
    for i in batch_qty:
        batch_items_dict.append(i)
    batch_details.update({"stock": batch_items_dict})
    batch_item.append(batch_details)
    
    return batch_details

def get_picklist_in_dn(self, arg):
    dn_wh = []
    
    lft = frappe.db.get_value("Warehouse", 'Erbil warehouse - TA', ["lft"])
    rgt = frappe.db.get_value("Warehouse", 'Erbil warehouse - TA', ["rgt"])
    if lft and rgt:
        res_wh = frappe.db.sql(
                    """
                    SELECT name FROM `tabWarehouse` where lft >= %s and rgt <= %s and is_group = 0
                    """,
                    (lft, rgt),
                    as_dict=1,
                )
        if res_wh:
            for s in res_wh:
                dn_wh.append(s.name)
    
    for data in self.items:
        if data.warehouse in dn_wh:
            if data.pick_list_item:
                p_qty = frappe.db.sql(""" SELECT picked_qty FROM `tabPick List Item` where name =  %(item)s""",
                                {'item': data.pick_list_item}, as_dict=True)
                                
                if p_qty[0].picked_qty != data.qty:
                    frappe.throw("Qty mistamch in DN and Picklist, Picklist have {0} qty.".format(p_qty[0].picked_qty))
            else:
                frappe.throw("Must create Pick List for this warehouse {0}.".format(data.warehouse))

def get_item_valuation_rate(item_code):
    
    item_val = frappe.db.sql(""" select round(valuation_rate, 2)valuation_rate from `tabStock Ledger Entry` force index (item_code) where
                                item_code = %(item)s AND valuation_rate > 0 AND is_cancelled = 0
                                order by posting_date desc, posting_time desc, name desc limit 1 """,{'item': item_code}, as_dict=True)
    if item_val:
        item_val_rate = item_val[0].valuation_rate
        return item_val_rate

@frappe.whitelist()
def get_trade_price_list():
    changed_price = []
    price_lists = frappe.db.get_list('Item Price',filters={'price_list': 'Trade Price List'},
                    fields=['name','item_code', 'uom','price_list_rate'])
    
    for i in price_lists:
        val_rate = get_item_valuation_rate(i.item_code)
        if val_rate and val_rate != i.price_list_rate:
            frappe.db.set_value('Item Price', i.name, 'price_list_rate', val_rate)
            i['val_rate'] = val_rate
            changed_price.append(i)
            doc = frappe.get_doc('Item Price', i.name)
            doc.add_comment('Comment', text='Price changed from {0} to {1}'.format(i.price_list_rate, val_rate))

    return changed_price;

def hello_world():
    text = "Results of the hello_world in hello.py module"
    return text
    
def generate_rebate_process():
    

    # month_last_day = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    # month_first_day = datetime.date.today().replace(day=1) - datetime.timedelta(days=month_last_day.day)
    

    month_last_day = '2023-03-31'
    month_first_day = '2023-03-01'

    rebate_customer = frappe.db.sql(""" SELECT * FROM `tabRebate Process` where rebate_start_from <= %(date)s and enabled = 1 and docstatus = 1 and status not in ('Completed')""",
                                        {'date': datetime.date.today()}, as_dict=True)
    
    for cust in rebate_customer:
        # check rebate is already processed
        net_sale = 0.0
        prev_rebate = already_process_rebate(cust.customer,month_last_day,cust.rebate_type,cust.company,cust.sales_rep)

        if cust.rebate_duration == "Monthly":
            net_sale = net_sale_in_period(cust.customer, month_first_day, month_last_day, cust.company, cust.sales_rep,cust.name,'Monthly')

        if cust.rebate_duration == "Quarterly":
            net_sale = net_sale_in_period(cust.customer, month_first_day, month_last_day, cust.company, cust.sales_rep,cust.name, 'Quarterly')

        if flt(net_sale) == 0 or flt(net_sale) < cust.initial_target:
            
            update_voucher_no('No target achievement', month_last_day, cust.name, 0)
            update_status_rebate(month_last_day,cust.name)
            continue
        
        if not prev_rebate:

            rebate_val = frappe.db.sql(""" SELECT brand,sum(rebate_amt*-1)rebate_amt FROM (
                                            SELECT inv.name,it.qty,it.rate,it.amount,it.brand,r.rebate_percentage,(it.base_amount*r.rebate_percentage/100)rebate_amt
                                            FROM `tabSales Invoice` inv, `tabSales Invoice Item` it, `tabRebate Definition` r,`tabRental Invoices` ri where 
                                            inv.name = it.parent and it.brand = r.brand and r.parent = ri.parent
                                            and inv.docstatus=1 and r.parent = %(rebate)s and it.item_code not in ('SHELF RENT', 'REBATE') 
                                            and employee = %(employee)s and customer = %(customer)s and inv.company = %(company)s
                                            and posting_date between %(start_date)s and %(end_date)s and ri.date = %(end_date)s)a1
                                            group by brand HAVING sum(rebate_amt) > 0""",
                                            {'employee': cust.sales_rep,'customer':cust.customer,'start_date':month_first_day,'end_date':month_last_day,'rebate':cust.name,'company':cust.company}, as_dict=True)
            if rebate_val:
                

                si = frappe.new_doc("Sales Invoice")
                si.naming_series = 'ACC-SINV-.YYYY.-'
                si.docstatus = 0
                si.customer = cust.customer
                si.employee = cust.sales_rep
                si.is_return = 1
                si.company = cust.company
                si.posting_date = month_last_day
                si.set_posting_time = 1
                si.currency = cust.currency
                si.update_stock = 0
                si.doctype = 'Sales Invoice'
                si.disable_rounded_total = 1
                si.rebate_type = cust.rebate_type

                cost_c = frappe.db.get_value('Company', cust.company, 'cost_center')
                si.cost_center = cost_c

                si.remarks = 'Rebate generated in the period of {0} and {1}. Rebate type : {2}, Ref - {3}, Duration : {4}.'.format(month_first_day,month_last_day,cust.rebate_type, cust.name,cust.rebate_duration)
                total_rebate_val = 0.00

                for rebate in rebate_val:
                    brand_obj = get_brand_sale(cust.name, cust.sales_rep, cust.customer, cust.company, month_first_day, month_last_day, rebate.brand)
                    
                    total_rebate_val += rebate.rebate_amt*-1
                    si.append("items",{
                                        "item_code" : 'REBATE',
                                        "description" : 'Brand : {0} - Period : {1} and {2} - Total Brand sale : {3} - Rebate Percentage : {4}'.format(rebate.brand,month_first_day,month_last_day,brand_obj[0].amount,brand_obj[0].rebate_percentage),
                                        "qty" : -1,
                                        "rate" : rebate.rebate_amt*-1,
                                        "amount" : rebate.rebate_amt,
                                        "cost_center" :cost_c,
                                        "brand" :rebate.brand,
                                    })
                
                slab_val = frappe.db.sql(""" SELECT extra_percentage FROM `tabRebate Slab` where {0} between total_sale_from and total_sale_to 
                                                    and parent = %(rebate)s AND extra_percentage > 0 """.format(net_sale),
                                                    {'rebate': cust.name}, as_dict=True)
                
                if slab_val:
                    total_rebate_val += (net_sale*slab_val[0].extra_percentage/100)
                    si.append("items",{
                                        "item_code" : 'REBATE',
                                        "description" : 'Rebate for exceed slab period {0} and {1}. Total brand sale {2}'.format(month_first_day,month_last_day,net_sale),
                                        "qty" : -1,
                                        "rate" : (net_sale*slab_val[0].extra_percentage/100),
                                        "amount" : net_sale*slab_val[0].extra_percentage/100,
                                        "cost_center" :cost_c
                                    })
                sp = get_sales_person_by_rep(cust.sales_rep)

                if sp:
                    si.append("sales_team",{
                                        "sales_person" : sp,
                                        "allocated_percentage" : 100,
                                    })
                si.save(ignore_permissions=True)
                # si.submit()
                
                update_voucher_no(si.name, month_last_day, cust.name, total_rebate_val)
                update_status_rebate(month_last_day,cust.name)

def update_status_rebate(month_last_day, reabte_ref):
    get_idx_qry = frappe.db.sql(""" SELECT idx from `tabRental Invoices` where parenttype = 'Rebate Process'
                                    and parent = %(reabte_ref)s and date = %(month_last_day)s""",
                                    {'month_last_day': month_last_day,'reabte_ref':reabte_ref}, as_dict=True)
    act_idx = 0
    if get_idx_qry:
        act_idx = get_idx_qry[0].idx
        if act_idx >= 1:
            update_start = frappe.db.sql(""" UPDATE `tabRebate Process` SET status = 'Running' where name = %(reabte_ref)s""",
                                        {'reabte_ref': reabte_ref}, as_dict=True)

        max_idx = get_max_idx(reabte_ref, 'Rebate Process')

        if max_idx and max_idx == act_idx:
            update_complete = frappe.db.sql(""" UPDATE `tabRebate Process` SET status = 'Completed' where name = %(reabte_ref)s""",
                                        {'reabte_ref': reabte_ref}, as_dict=True)


def update_voucher_no(voucher_no, month_last_day, reabte_ref, total_rebate_val):
    update_inv = frappe.db.sql(""" UPDATE `tabRental Invoices` SET voucher_no = %(voucher_no)s,is_generated = 1,amount = %(total_rebate_val)s WHERE date = %(month_last_day)s and parent = %(reabte_ref)s and parenttype = 'Rebate Process' """,
                                {'voucher_no': voucher_no,'total_rebate_val':total_rebate_val,'month_last_day':month_last_day,'reabte_ref':reabte_ref}, as_dict=True)
    return update_inv

def get_sales_person_by_rep(rep_id):
    sales_person = frappe.db.sql(""" SELECT name FROM `tabSales Person` where employee = %(employee)s and is_group = 0 """,
                            {'employee': rep_id}, as_dict=True)
    if sales_person:
        return sales_person[0].name
    else:
        return

def already_process_rebate(customer,posting_date,rebate_type,company,employee):
    rebate_inv = frappe.db.sql("""SELECT name FROM `tabSales Invoice` where customer = %(customer)s and posting_date = %(posting_date)s 
                                    and rebate_type = %(rebate_type)s and docstatus != 2 and company = %(company)s AND employee = %(employee)s""",
                                    {'customer': customer,'posting_date':posting_date,'rebate_type':rebate_type,'company':company,'employee':employee}, as_dict=True)
    if rebate_inv:
        return rebate_inv[0].name
    else:
        return

def net_sale_in_period(customer,from_date,to_date,company,employee,rebate, reb_period):
    net_sale = frappe.db.sql("""SELECT sum(inv.base_grand_total)base_grand_total FROM `tabSales Invoice` inv, `tabSales Invoice Item` it 
                                where inv.name = it.parent
                                and inv.company = %(company)s and inv.customer = %(customer)s
                                and inv.posting_date between %(from_date)s and %(to_date)s and inv.employee = %(employee)s and inv.docstatus=1
                                and it.brand in (select brand from `tabRebate Definition` rd where rd.parent = %(rebate)s)""",
                                {'customer': customer,'from_date':from_date,'to_date':to_date,'company':company,'employee':employee,'rebate':rebate}, as_dict=True)
    
    if net_sale:
        return net_sale[0].base_grand_total
    else:
        return 0


def generate_shelf_rentals():

    last_month_last_day = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    month_first_day = datetime.date.today().replace(day=1) - datetime.timedelta(days=last_month_last_day.day)

    last_month_last_day = '2024-01-31'
    month_first_day = '2024-01-01'
    
    shelf_rental_entries = frappe.db.sql("""SELECT a.name,a.company,a.currency,rent_type,description,from_date,to_date,a.amount,a.brand,a.sales_rep,a.customer,
                                            b.name as detl_name,is_generated,b.date,b.idx 
                                            FROM `tabShelf Rental Agreement` a, `tabRental Invoices` b
                                            where a.name = b.parent and b.date = %(date)s
                                            and a.docstatus=1 
                                            and a.enabled=1 and status not in ('Completed')
                                            and is_generated = 0 """,{'date': last_month_last_day}, as_dict=True)

    for entry in shelf_rental_entries:
        
        prev_rent = already_process_shelf_rental(entry.company, entry.customer, entry.sales_rep, last_month_last_day, entry.brand,entry.name)
        
        if not prev_rent:
            si = frappe.new_doc("Sales Invoice")
            si.naming_series = 'ACC-SINV-.YYYY.-'
            si.docstatus = 1
            si.customer = entry.customer
            si.employee = entry.sales_rep
            si.is_return = 1
            si.company = entry.company
            si.posting_date = last_month_last_day
            si.set_posting_time = 1
            si.currency = entry.currency
            si.update_stock = 0
            si.doctype = 'Sales Invoice'
            si.disable_rounded_total = 1
            si.shelf_rent_ref = entry.name

            cost_c = frappe.db.get_value('Company', entry.company, 'cost_center')
            si.cost_center = cost_c

            si.remarks = 'Shelf rental generated in the period of {0} and {1}. type : {2} - {3}'.format(month_first_day,last_month_last_day,entry.rent_type,entry.description)
            
            si.append("items",{
                                "item_code" : 'SHELF RENT',
                                "description" : 'Shelf rental generated in the period of {0} and {1}. Rebate type : {2} - {3}'.format(month_first_day,last_month_last_day,entry.rent_type,entry.description),
                                "qty" : -1,
                                "rate" : entry.amount,
                                "amount" : entry.amount,
                                "cost_center" :cost_c
                            })
            
            sp = get_sales_person_by_rep(entry.sales_rep)

            if sp:
                si.append("sales_team",{
                                    "sales_person" : sp,
                                    "allocated_percentage" : 100,
                                })
            si.save(ignore_permissions=True)
            update_invoice_genetrate(entry.name, entry.detl_name,si.name, entry.amount)
            update_shelf_status(entry.date, entry.from_date, entry.to_date, entry.detl_name,entry.name,entry.idx)
            print(si.name)

def update_invoice_genetrate(sr,detl_name, inv, amount):
    update_inv = frappe.db.sql(""" UPDATE `tabRental Invoices` SET voucher_no = %(inv)s,is_generated = 1,amount = %(amount)s WHERE name = %(detl_name)s and parent = %(sr)s and parenttype = 'Shelf Rental Agreement'""",
                                {'inv': inv,'detl_name':detl_name,'sr':sr,'amount':amount}, as_dict=True)
    return update_inv

def update_shelf_status(date, from_date,to_date,detl_name,name,idx):
    
    if idx == 1:
        update_start = frappe.db.sql(""" UPDATE `tabShelf Rental Agreement` SET status = 'Running' where name = %(name)s """,
                                {'name': name}, as_dict=True)
    max_idx = get_max_idx(name, 'Shelf Rental Agreement')
    if max_idx == idx:
        update_complete = frappe.db.sql(""" UPDATE `tabShelf Rental Agreement` SET status = 'Completed' where name = %(name)s """,
                                {'name': name}, as_dict=True)

def get_max_idx(name, parenttype):
    max_id = frappe.db.sql(""" SELECT max(idx)idx FROM `tabRental Invoices` where parent = %(name)s and parenttype = %(parenttype)s""",
                                {'name': name, 'parenttype':parenttype}, as_dict=True)
    if max_id:
        return max_id[0].idx
    else:
        return



def already_process_shelf_rental(company, customer, sales_rep, month_last_day, brand, shelf_rent_ref):
    rental_inv = frappe.db.sql("""SELECT name FROM `tabSales Invoice` where customer = %(customer)s and posting_date = %(posting_date)s 
                                    and shelf_rent_ref = %(shelf_rent_ref)s and docstatus=1 and company = %(company)s AND employee = %(employee)s""",
                                    {'customer': customer,'posting_date':month_last_day,'shelf_rent_ref':shelf_rent_ref,'company':company,'employee':sales_rep}, as_dict=True)
    if rental_inv:
        return rental_inv[0].name
    else:
        return


def get_brand_sale(rebate, sales_rep,customer,company, month_first_day,month_last_day, brand):
    brand_sale_val = frappe.db.sql(""" SELECT it.brand,r.rebate_percentage,sum(it.amount)amount,sum((it.base_amount*r.rebate_percentage/100))rebate_amt
                                    FROM `tabSales Invoice` inv, `tabSales Invoice Item` it, `tabRebate Definition` r where 
                                    inv.name = it.parent and it.brand = r.brand
                                    and inv.docstatus=1 
                                    and r.parent = %(rebate)s
                                    and it.item_code != 'REBATE' 
                                    and employee = %(employee)s and customer = %(customer)s and inv.company = %(company)s
                                    and posting_date between %(start_date)s and %(end_date)s and it.brand = %(brand)s
                                    group by it.brand,r.rebate_percentage """,
                                    {'rebate':rebate,'employee': sales_rep,'customer':customer,'company':company,'start_date':month_first_day,'end_date':month_last_day,'brand':brand}, as_dict=True)
    if brand_sale_val:
        return brand_sale_val
    else:
        return

# bench execute freeline.freeline.globalapi.generate_rebate_process

# bench execute freeline.freeline.globalapi.generate_shelf_rentals
