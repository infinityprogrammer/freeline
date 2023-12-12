from frappe import _


def get_so_pick_list_connection(data):

    return {
		"fieldname": "pick_list",
		"transactions": [
			{"items": ["Stock Entry", "Delivery Note"]},
            {
				"label": _("Reference"),
				"items": ["Sales Order"]
			},
		],
        "internal_links": {
			"Sales Order": ["locations", "sales_order"],
		},
	}
