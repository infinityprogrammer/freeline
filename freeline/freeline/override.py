import frappe
from frappe.model.document import Document

from erpnext.stock.doctype.pick_list.pick_list import PickList
from frappe.utils.nestedset import get_descendants_of
from frappe.utils import cint, floor, flt, today
from erpnext.stock.doctype.pick_list.pick_list import (
    get_available_item_locations
)

class OverridePickList(PickList):
    
    @frappe.whitelist()
    def set_item_locations(self, save=False):
        self.validate_for_qty()
        items = self.aggregate_item_qty()
        self.item_location_map = frappe._dict()

        from_warehouses = None
        if self.parent_warehouse:
            from_warehouses = get_descendants_of("Warehouse", self.parent_warehouse)

        # Create replica before resetting, to handle empty table on update after submit.
        locations_replica = self.get("locations")

        # reset
        self.delete_key("locations")
        for item_doc in items:
            wh = []
            item_code = item_doc.item_code
            warehouse = item_doc.warehouse

            wh.append(warehouse)

            self.item_location_map.setdefault(
                item_code,
                get_available_item_locations(
                    item_code, wh, self.item_count_map.get(item_code), self.company
                ),
            )

            locations = get_items_with_location_and_quantity(
                item_doc, self.item_location_map, self.docstatus
            )

            item_doc.idx = None
            item_doc.name = None

            for row in locations:
                location = item_doc.as_dict()
                location.update(row)
                self.append("locations", location)

        # If table is empty on update after submit, set stock_qty, picked_qty to 0 so that indicator is red
        # and give feedback to the user. This is to avoid empty Pick Lists.
        if not self.get("locations") and self.docstatus == 1:
            for location in locations_replica:
                location.stock_qty = 0
                location.picked_qty = 0
                self.append("locations", location)
            frappe.msgprint(
                _(
                    "Please Restock Items and Update the Pick List to continue. To discontinue, cancel the Pick List."
                ),
                title=_("Out of Stock"),
                indicator="red",
            )

        if save:
            self.save()
    
    @frappe.whitelist()
    def update_pick_list_status_manually(self, dn_status):
        
        frappe.db.sql(""" UPDATE `tabPick List` SET delivery_status = %(delivery_status)s where name = %(pick_name)s""",
                                                    {'delivery_status': dn_status, 'pick_name':self.name}, as_list=True)


def get_items_with_location_and_quantity(item_doc, item_location_map, docstatus):
	available_locations = item_location_map.get(item_doc.item_code)
	locations = []

	# if stock qty is zero on submitted entry, show positive remaining qty to recalculate in case of restock.
	remaining_stock_qty = (
		item_doc.qty if (docstatus == 1 and item_doc.stock_qty == 0) else item_doc.stock_qty
	)

	while remaining_stock_qty > 0 and available_locations:
		item_location = available_locations.pop(0)
		item_location = frappe._dict(item_location)

		stock_qty = (
			remaining_stock_qty if item_location.qty >= remaining_stock_qty else item_location.qty
		)
		qty = stock_qty / (item_doc.conversion_factor or 1)

		uom_must_be_whole_number = frappe.db.get_value("UOM", item_doc.uom, "must_be_whole_number")
		if uom_must_be_whole_number:
			qty = floor(qty)
			stock_qty = qty * item_doc.conversion_factor
			if not stock_qty:
				continue

		serial_nos = None
		if item_location.serial_no:
			serial_nos = "\n".join(item_location.serial_no[0 : cint(stock_qty)])

		locations.append(
			frappe._dict(
				{
					"qty": qty,
					"stock_qty": stock_qty,
					"warehouse": item_location.warehouse,
					"serial_no": serial_nos,
					"batch_no": item_location.batch_no,
				}
			)
		)

		remaining_stock_qty -= stock_qty

		qty_diff = item_location.qty - stock_qty
		# if extra quantity is available push current warehouse to available locations
		if qty_diff > 0:
			item_location.qty = qty_diff
			if item_location.serial_no:
				# set remaining serial numbers
				item_location.serial_no = item_location.serial_no[-int(qty_diff) :]
			available_locations = [item_location] + available_locations

	# update available locations for the item
	item_location_map[item_doc.item_code] = available_locations
	return locations
