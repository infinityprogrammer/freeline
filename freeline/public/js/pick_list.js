frappe.ui.form.on('Pick List', {
    // on refresh event
    refresh(frm) {
        var df = frappe.meta.get_docfield("Pick List Item", "qty", cur_frm.doc.name);
        var df1 = frappe.meta.get_docfield("Pick List Item", "picked_qty", cur_frm.doc.name);
        df.read_only = 1;
        df1.read_only = 1;

        if(frappe.user.has_role("Picker") && frm.doc.docstatus ==1){

            frm.add_custom_button(__("Create Delivery Note"), function() {
                create_delivery_note(frm)
            }, "fa fa-money");
        }
    },
    setup(frm) {
        var df = frappe.meta.get_docfield("Pick List Item", "qty", cur_frm.doc.name);
        var df1 = frappe.meta.get_docfield("Pick List Item", "picked_qty", cur_frm.doc.name);
        df.read_only = 1;
        df1.read_only = 1;
    },
    
});

frappe.ui.form.on('Pick List Item', {
	refresh(frm) {
		// your code here
	},
	hand_picked_qty: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if(row.hand_picked_qty > row.qty){
            frappe.model.set_value(cdt, cdn, "hand_picked_qty", 0);
            frappe.throw(__("Picked qty cannot be greate than actual qty."))
        }

        let pick_qty = row.hand_picked_qty * row.conversion_factor 
        frappe.model.set_value(cdt, cdn, "picked_qty", pick_qty);

        refresh_field("picked_qty", cdn, cdt);
    },
})


function create_delivery_note(frm) {
    let emp_code = frm.doc.employee_driver_id
    frappe.model.open_mapped_doc({
        method: 'erpnext.stock.doctype.pick_list.pick_list.create_delivery_note',
        frm: frm
    }).then(delivery_note => {
        let arr = delivery_note.message
        frappe.db.set_value('Delivery Note', arr.name, 'employee_driver_id', emp_code)
    });
}
