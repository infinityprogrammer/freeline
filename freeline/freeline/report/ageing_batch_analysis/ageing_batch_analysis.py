# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from operator import itemgetter
from typing import Dict, List, Tuple, Union

import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt

from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

Filters = frappe._dict


def execute(filters: Filters = None) -> Tuple:
	to_date = filters["to_date"]
	columns = get_columns(filters)

	item_details = FIFOSlots(filters).generate()
	data = format_report_data(filters, item_details, to_date)
	
	# chart_data = get_chart_data(data, filters)
	
	if filters.get("supplier"):
		supp_id = filters.get("supplier")
		data = list(filter(lambda data: data[-1] == supp_id, data))
	
	return columns, data, None


def format_report_data(filters: Filters, item_details: Dict, to_date: str) -> List[Dict]:
	"Returns ordered, formatted data with ranges."
	_func = itemgetter(1)
	data = []

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision", cache=True))

	for item, item_dict in item_details.items():
		
		# if not flt(item_dict.get("total_qty"), precision):
		# 	continue
		

		earliest_age, latest_age = 0, 0
		details = item_dict["details"]

		fifo_queue = sorted(filter(_func, item_dict["fifo_queue"]), key=_func)
		
		average_age = 0
		earliest_age = 0
		latest_age = 0
		range1, range2, range3,range4,above_range4 = 0,0,0,0,0

		if fifo_queue:
			average_age = get_average_age(fifo_queue, to_date)
			earliest_age = date_diff(to_date, fifo_queue[0][1])
			latest_age = date_diff(to_date, fifo_queue[-1][1])
			range1, range2, range3,range4,above_range4 = get_range_age(filters, fifo_queue, to_date, item_dict)

		
		cost_and_sale = get_item_sale_info(details.name, filters)

		row = [details.name, details.item_name, details.description, details.item_group, details.brand]

		if filters.get("show_warehouse_wise_stock"):
			row.append(details.warehouse)
		
		usage_rate = 0.0
		six_month_qty = 0.0
		usage_rate += cost_and_sale[0].m1 + cost_and_sale[0].m2 + cost_and_sale[0].m3 + cost_and_sale[0].m4 + cost_and_sale[0].m5 + cost_and_sale[0].m6
		six_month_qty += cost_and_sale[0].m1 + cost_and_sale[0].m2 + cost_and_sale[0].m3 + cost_and_sale[0].m4 + cost_and_sale[0].m5 + cost_and_sale[0].m6
		usage_rate = (usage_rate/6)
		usage_rate_div = 0.0
		if usage_rate:
			usage_rate_div = usage_rate
		else:
			usage_rate_div = 1

		avail_qty = flt(item_dict.get("total_qty"), precision)
		stock_cover = (avail_qty/usage_rate_div)
		turnover_rate = 0.0
		if stock_cover:
			turnover_rate = (12/stock_cover)
		else:
			turnover_rate = 0

		last_rec_date,last_rec_qty,supplier_code  = get_last_reciept_date(details.name, filters)
		
		row.extend(
			[
				flt(item_dict.get("total_qty"), precision),
				average_age,
				cost_and_sale[0].stock_value,
				range1,
				range2,
				range3,
				range4,
				above_range4,
				earliest_age,
				latest_age,
				last_rec_date,
				last_rec_qty,
				details.stock_uom,
				cost_and_sale[0].m1,
				cost_and_sale[0].m2,
				cost_and_sale[0].m3,
				cost_and_sale[0].m4,
				cost_and_sale[0].m5,
				cost_and_sale[0].m6,
				six_month_qty,
				usage_rate,
				stock_cover,
				turnover_rate,
				supplier_code
			]
		)

		data.append(row)

	return data

def get_last_reciept_date(item_code, filters):
	last_rec_date = 0
	last_rec_qty = 0
	supplier_code = ""
	cmp = filters.get("company")

	last_rec = frappe.db.sql(""" SELECT posting_date,b.stock_qty FROM `tabPurchase Receipt` a, `tabPurchase Receipt Item` b
									where a.name = b.parent and a.docstatus=1 and b.item_code= '{0}' and company = '{1}'
									order by posting_date desc limit 1 """.format(item_code, cmp), as_dict=True)
	if last_rec:
		last_rec_date = last_rec[0].posting_date
		last_rec_qty = last_rec[0].stock_qty
	
	supp_qry = frappe.db.sql(""" SELECT supplier FROM `tabItem Supplier` where parent = '{0}';""".format(item_code), as_dict=True)
	if supp_qry:
		supplier_code = supp_qry[0].supplier

	return last_rec_date, last_rec_qty, supplier_code

def get_item_sale_info(item_code_name, filters):

	filters['item_code_name'] = item_code_name

	sale_detl = frappe.db.sql(""" SELECT name,
								(SELECT sum(stock_value)stock_value from `tabBin` bin where bin.item_code = %(item_code_name)s and 
								warehouse in (SELECT name FROM `tabWarehouse` where company = %(company)s ))stock_value,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 0 and 30), 0)m1,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 31 and 60), 0)m2,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 61 and 90), 0)m3,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 91 and 120), 0)m4,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 121 and 150), 0)m5,
								--
								ifnull((SELECT sum(actual_qty *-1) FROM `tabStock Ledger Entry` sle where sle.voucher_type in ('Sales Invoice','Delivery Note')
								and is_cancelled = 0 and sle.item_code = item.name and company = %(company)s
								and datediff(curdate(),sle.posting_date) between 151 and 180), 0)m6
								--
								from `tabItem` item where item.name = %(item_code_name)s """,filters,as_dict=True)
	return sale_detl

def get_average_age(fifo_queue: List, to_date: str) -> float:
	batch_age = age_qty = total_qty = 0.0
	for batch in fifo_queue:
		batch_age = date_diff(to_date, batch[1])
		
		if isinstance(batch[0], (int, float)):
			age_qty += batch_age * batch[0]
			total_qty += batch[0]
		else:
			age_qty += batch_age * 1
			total_qty += 1
		
	return flt(age_qty / total_qty, 2) if total_qty else 0.0


def get_range_age(filters: Filters, fifo_queue: List, to_date: str, item_dict: Dict) -> Tuple:

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision", cache=True))

	range1 = range2 = range3 = range4 = above_range4 = 0.0

	for item in fifo_queue:
		age = date_diff(to_date, item[1])
		qty = flt(item[0]) if not item_dict["has_serial_no"] else 1.0

		if age <= filters.range1:
			range1 = flt(range1 + qty, precision)
		elif age <= filters.range2:
			range2 = flt(range2 + qty, precision)
		elif age <= filters.range3:
			range3 = flt(range3 + qty, precision)
		elif age <= filters.range3:
			range4 = flt(range4 + qty, precision)
		else:
			above_range4 = flt(above_range4 + qty, precision)

	return range1, range2, range3,range4, above_range4


def get_columns(filters: Filters) -> List[Dict]:
	range_columns = []
	setup_ageing_columns(filters, range_columns)
	columns = [
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 100},
		{"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100,
		},
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 100,
		},
	]

	if filters.get("show_warehouse_wise_stock"):
		columns += [
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 100,
			}
		]

	columns.extend(
		[
			{"label": _("Qty on Hand"), "fieldname": "qty", "fieldtype": "Float", "width": 140},
			{"label": _("Average Age (D)"), "fieldname": "average_age", "fieldtype": "Float", "width": 140},
			{"label": _("Cost"), "fieldname": "stock_value", "fieldtype": "Float", "width": 100},
		]
	)
	columns.extend(range_columns)
	columns.extend(
		[
			{"label": _("Earliest reciept days"), "fieldname": "earliest", "fieldtype": "Int", "width": 160},
			{"label": _("Latest reciept days"), "fieldname": "latest", "fieldtype": "Int", "width": 160},
			{"label": _("Latest reciept date"), "fieldname": "last_rec_date", "fieldtype": "Date", "width": 160},
			{"label": _("Latest reciept qty"), "fieldname": "last_rec_qty", "fieldtype": "Int", "width": 160},
			{"label": _("UOM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 100},
			{"label": _("Sale (0-30)"), "fieldname": "m1", "fieldtype": "Float", "width": 140},
			{"label": _("Sale (31-60)"), "fieldname": "m2", "fieldtype": "Float", "width": 140},
			{"label": _("Sale (61-90)"), "fieldname": "m3", "fieldtype": "Float", "width": 140},
			{"label": _("Sale (91-120)"), "fieldname": "m4", "fieldtype": "Float", "width": 140},
			{"label": _("Sale (121-150)"), "fieldname": "m5", "fieldtype": "Float", "width": 140},
			{"label": _("Sale (151-180)"), "fieldname": "m6", "fieldtype": "Float", "width": 140},
			{"label": _("Total Qty Sold in 6 M"), "fieldname": "six_month_qty", "fieldtype": "Float", "width": 160},
			{"label": _("Usage Rate (Q)"), "fieldname": "usage_rate", "fieldtype": "Float", "width": 140},
			{"label": _("Stock Cover (M)"), "fieldname": "stock_cover", "fieldtype": "Float", "width": 140},
			{"label": _("Turnover Rate"), "fieldname": "turnover_rate", "fieldtype": "Float", "width": 140},
			{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link","options": "Supplier", "width": 140},
		]
	)

	return columns


def get_chart_data(data: List, filters: Filters) -> Dict:
	if not data:
		return []

	labels, datapoints = [], []

	if filters.get("show_warehouse_wise_stock"):
		return {}

	data.sort(key=lambda row: row[6], reverse=True)

	if len(data) > 10:
		data = data[:10]

	for row in data:
		labels.append(row[0])
		datapoints.append(row[6])

	return {
		"data": {"labels": labels, "datasets": [{"name": _("Average Age"), "values": datapoints}]},
		"type": "bar",
	}


def setup_ageing_columns(filters: Filters, range_columns: List):
	ranges = [
		f"0 - {filters['range1']}",
		f"{cint(filters['range1']) + 1} - {cint(filters['range2'])}",
		f"{cint(filters['range2']) + 1} - {cint(filters['range3'])}",
		f"{cint(filters['range3']) + 1} - {cint(filters['range4'])}",
		f"{cint(filters['range4']) + 1} - {_('Above')}",
	]
	for i, label in enumerate(ranges):
		fieldname = "range" + str(i + 1)
		add_column(range_columns, label=f"Age ({label})", fieldname=fieldname)


def add_column(
	range_columns: List, label: str, fieldname: str, fieldtype: str = "Float", width: int = 140
):
	range_columns.append(dict(label=label, fieldname=fieldname, fieldtype=fieldtype, width=width))


class FIFOSlots:
	"Returns FIFO computed slots of inwarded stock as per date."

	def __init__(self, filters: Dict = None, sle: List = None):
		self.item_details = {}
		self.transferred_item_details = {}
		self.serial_no_batch_purchase_details = {}
		self.filters = filters
		self.sle = sle

	def generate(self) -> Dict:
		"""
		Returns dict of the foll.g structure:
		Key = Item A / (Item A, Warehouse A)
		Key: {
		        'details' -> Dict: ** item details **,
		        'fifo_queue' -> List: ** list of lists containing entries/slots for existing stock,
		                consumed/updated and maintained via FIFO. **
		}
		"""
		if self.sle is None:
			self.sle = self.__get_stock_ledger_entries()

		for d in self.sle:
			key, fifo_queue, transferred_item_key = self.__init_key_stores(d)

			if d.voucher_type == "Stock Reconciliation":
				# get difference in qty shift as actual qty
				prev_balance_qty = self.item_details[key].get("qty_after_transaction", 0)
				d.actual_qty = flt(d.qty_after_transaction) - flt(prev_balance_qty)

			serial_nos = get_serial_nos(d.serial_no) if d.serial_no else []

			if d.actual_qty > 0:
				self.__compute_incoming_stock(d, fifo_queue, transferred_item_key, serial_nos)
			else:
				self.__compute_outgoing_stock(d, fifo_queue, transferred_item_key, serial_nos)

			self.__update_balances(d, key)

		if not self.filters.get("show_warehouse_wise_stock"):
			# (Item 1, WH 1), (Item 1, WH 2) => (Item 1)
			self.item_details = self.__aggregate_details_by_item(self.item_details)
		
		return self.item_details

	def __init_key_stores(self, row: Dict) -> Tuple:
		"Initialise keys and FIFO Queue."

		key = (row.name, row.warehouse)
		self.item_details.setdefault(key, {"details": row, "fifo_queue": []})
		fifo_queue = self.item_details[key]["fifo_queue"]

		transferred_item_key = (row.voucher_no, row.name, row.warehouse)
		self.transferred_item_details.setdefault(transferred_item_key, [])

		return key, fifo_queue, transferred_item_key

	def __compute_incoming_stock(
		self, row: Dict, fifo_queue: List, transfer_key: Tuple, serial_nos: List
	):
		"Update FIFO Queue on inward stock."

		transfer_data = self.transferred_item_details.get(transfer_key)
		if transfer_data:
			# inward/outward from same voucher, item & warehouse
			# eg: Repack with same item, Stock reco for batch item
			# consume transfer data and add stock to fifo queue
			self.__adjust_incoming_transfer_qty(transfer_data, fifo_queue, row)
		else:
			if not serial_nos:
				if fifo_queue and flt(fifo_queue[0][0]) <= 0:
					# neutralize 0/negative stock by adding positive stock
					fifo_queue[0][0] += flt(row.actual_qty)
					fifo_queue[0][1] = row.posting_date
				else:
					fifo_queue.append([flt(row.actual_qty), row.posting_date])
				return

			for serial_no in serial_nos:
				if self.serial_no_batch_purchase_details.get(serial_no):
					fifo_queue.append([serial_no, self.serial_no_batch_purchase_details.get(serial_no)])
				else:
					self.serial_no_batch_purchase_details.setdefault(serial_no, row.posting_date)
					fifo_queue.append([serial_no, row.posting_date])

	def __compute_outgoing_stock(
		self, row: Dict, fifo_queue: List, transfer_key: Tuple, serial_nos: List
	):
		"Update FIFO Queue on outward stock."
		if serial_nos:
			fifo_queue[:] = [serial_no for serial_no in fifo_queue if serial_no[0] not in serial_nos]
			return

		qty_to_pop = abs(row.actual_qty)
		while qty_to_pop:
			slot = fifo_queue[0] if fifo_queue else [0, None]
			if 0 < flt(slot[0]) <= qty_to_pop:
				# qty to pop >= slot qty
				# if +ve and not enough or exactly same balance in current slot, consume whole slot
				qty_to_pop -= flt(slot[0])
				self.transferred_item_details[transfer_key].append(fifo_queue.pop(0))
			elif not fifo_queue:
				# negative stock, no balance but qty yet to consume
				fifo_queue.append([-(qty_to_pop), row.posting_date])
				self.transferred_item_details[transfer_key].append([qty_to_pop, row.posting_date])
				qty_to_pop = 0
			else:
				# qty to pop < slot qty, ample balance
				# consume actual_qty from first slot
				slot[0] = flt(slot[0]) - qty_to_pop
				self.transferred_item_details[transfer_key].append([qty_to_pop, slot[1]])
				qty_to_pop = 0

	def __adjust_incoming_transfer_qty(self, transfer_data: Dict, fifo_queue: List, row: Dict):
		"Add previously removed stock back to FIFO Queue."
		transfer_qty_to_pop = flt(row.actual_qty)

		def add_to_fifo_queue(slot):
			if fifo_queue and flt(fifo_queue[0][0]) <= 0:
				# neutralize 0/negative stock by adding positive stock
				fifo_queue[0][0] += flt(slot[0])
				fifo_queue[0][1] = slot[1]
			else:
				fifo_queue.append(slot)

		while transfer_qty_to_pop:
			if transfer_data and 0 < transfer_data[0][0] <= transfer_qty_to_pop:
				# bucket qty is not enough, consume whole
				transfer_qty_to_pop -= transfer_data[0][0]
				add_to_fifo_queue(transfer_data.pop(0))
			elif not transfer_data:
				# transfer bucket is empty, extra incoming qty
				add_to_fifo_queue([transfer_qty_to_pop, row.posting_date])
				transfer_qty_to_pop = 0
			else:
				# ample bucket qty to consume
				transfer_data[0][0] -= transfer_qty_to_pop
				add_to_fifo_queue([transfer_qty_to_pop, transfer_data[0][1]])
				transfer_qty_to_pop = 0

	def __update_balances(self, row: Dict, key: Union[Tuple, str]):
		self.item_details[key]["qty_after_transaction"] = row.qty_after_transaction

		if "total_qty" not in self.item_details[key]:
			self.item_details[key]["total_qty"] = row.actual_qty
		else:
			self.item_details[key]["total_qty"] += row.actual_qty

		self.item_details[key]["has_serial_no"] = row.has_serial_no

	def __aggregate_details_by_item(self, wh_wise_data: Dict) -> Dict:
		"Aggregate Item-Wh wise data into single Item entry."
		item_aggregated_data = {}
		for key, row in wh_wise_data.items():
			item = key[0]
			if not item_aggregated_data.get(item):
				item_aggregated_data.setdefault(
					item,
					{"details": frappe._dict(), "fifo_queue": [], "qty_after_transaction": 0.0, "total_qty": 0.0},
				)
			item_row = item_aggregated_data.get(item)
			item_row["details"].update(row["details"])
			item_row["fifo_queue"].extend(row["fifo_queue"])
			item_row["qty_after_transaction"] += flt(row["qty_after_transaction"])
			item_row["total_qty"] += flt(row["total_qty"])
			item_row["has_serial_no"] = row["has_serial_no"]

		return item_aggregated_data

	def __get_stock_ledger_entries(self) -> List[Dict]:
		sle = frappe.qb.DocType("Stock Ledger Entry")
		item = self.__get_item_query()  # used as derived table in sle query

		sle_query = (
			frappe.qb.from_(sle)
			.from_(item)
			.select(
				item.name,
				item.item_name,
				item.item_group,
				item.brand,
				item.description,
				item.stock_uom,
				item.has_serial_no,
				sle.actual_qty,
				sle.posting_date,
				sle.voucher_type,
				sle.voucher_no,
				sle.serial_no,
				sle.batch_no,
				sle.qty_after_transaction,
				sle.warehouse,
			)
			.where(
				(sle.item_code == item.name)
				& (sle.company == self.filters.get("company"))
				& (sle.posting_date <= self.filters.get("to_date"))
				& (sle.is_cancelled != 1)
			)
		)

		if self.filters.get("warehouse"):
			sle_query = self.__get_warehouse_conditions(sle, sle_query)

		sle_query = sle_query.orderby(sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty)

		return sle_query.run(as_dict=True)

	def __get_item_query(self) -> str:
		item_table = frappe.qb.DocType("Item")

		# item = frappe.qb.from_("Item").leftJoin("Item Supplier", "Item.name","=","Item Supplier.parent").select(
		# 	"name", "item_name", "description", "stock_uom", "brand", "item_group", "has_serial_no"
		# )
		item = frappe.qb.from_("Item").select(
			"name", "item_name", "description", "stock_uom", "brand", "item_group", "has_serial_no"
		)

		if self.filters.get("item_code"):
			item = item.where(item_table.item_code == self.filters.get("item_code"))
			
		if self.filters.get("brand"):
			item = item.where(item_table.brand == self.filters.get("brand"))
			
		if self.filters.get("supplier"):
			pass
		
		return item

	def __get_warehouse_conditions(self, sle, sle_query) -> str:
		warehouse = frappe.qb.DocType("Warehouse")
		lft, rgt = frappe.db.get_value("Warehouse", self.filters.get("warehouse"), ["lft", "rgt"])

		warehouse_results = (
			frappe.qb.from_(warehouse)
			.select("name")
			.where((warehouse.lft >= lft) & (warehouse.rgt <= rgt))
			.run()
		)
		warehouse_results = [x[0] for x in warehouse_results]

		return sle_query.where(sle.warehouse.isin(warehouse_results))
