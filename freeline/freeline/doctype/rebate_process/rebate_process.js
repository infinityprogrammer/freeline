// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rebate Process', {
	refresh: function(frm) {

		frm.set_query("item_group", "rebate_details", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					'is_group': 0
				}
			}
		});

	}
});
