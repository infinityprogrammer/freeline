// Copyright (c) 2022, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Picker Warehouse', {
	refresh: function(frm) {

		frm.set_query("warehouse", function(doc) {
			return {
				filters: {
					'is_group': 0
				}
			}
		});

	}
});
