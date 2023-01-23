frappe.ui.form.on('Sales Order', {
    // on refresh event
    refresh(frm) {
        if(frappe.user.has_role("Picker") && frm.doc.docstatus ==1){

            frm.add_custom_button(__("Create Pick List"), function() {
                create_pick_list(frm)
            }, "fa fa-money");
        }
    },
});

function create_pick_list(frm) {
    frappe.model.open_mapped_doc({
        method: "erpnext.selling.doctype.sales_order.sales_order.create_pick_list",
        frm: frm
    })
}