frappe.ui.form.on('Material Request Item', {
	
	item_code: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_from_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "source_wh_qty", r.actual_qty/row.conversion_factor);
        });
        
        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "target_wh_qty", r.actual_qty/row.conversion_factor);
        });
    },

    conversion_factor: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_from_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "source_wh_qty", r.actual_qty/row.conversion_factor);
        });
        
        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "target_wh_qty", r.actual_qty/row.conversion_factor);
        });

    },

    from_warehouse: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_from_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "source_wh_qty", r.actual_qty/row.conversion_factor);
        });

        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "target_wh_qty", r.actual_qty/row.conversion_factor);
        });

    },

    warehouse: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "target_wh_qty", r.actual_qty/row.conversion_factor);
        });

        frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": frm.doc.set_from_warehouse}, ["actual_qty"], (r) => {

            frappe.model.set_value(cdt, cdn, "source_wh_qty", r.actual_qty/row.conversion_factor);
        });

    },
})