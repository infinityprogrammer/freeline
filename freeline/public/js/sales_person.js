frappe.ui.form.on('Sales Person', {
    // on refresh event
    refresh(frm) {
        
        frm.set_query("distribution_id", "target_definition", function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                filters: {
                    'employee': frm.doc.employee,
                    'brand': row.brand,
                }
            }
        });
    },
});
