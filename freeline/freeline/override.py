import frappe
from frappe.model.document import Document

from erpnext.stock.doctype.pick_list.pick_list import PickList
from frappe.utils.nestedset import get_descendants_of
from erpnext.stock.doctype.pick_list.pick_list import (
    get_available_item_locations, get_items_with_location_and_quantity
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