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