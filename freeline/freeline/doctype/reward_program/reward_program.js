// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reward Program', {
	refresh: function(frm) {

		frm.set_query("document_type", "distribution", function (doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					name: ["in", ["Brand", "Item"]],
				},
			};
		});

		frm.set_query("customer", function() {
            return {
                filters: {
					disabled: 0,
				},
            };
        });

	}
});
