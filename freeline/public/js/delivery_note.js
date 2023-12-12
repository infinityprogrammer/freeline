frappe.ui.form.on('Delivery Note', {
    // on refresh event
    refresh(frm) {

        if(frm.doc.docstatus==1 && !frm.doc.is_return && frm.doc.status!="Closed" && flt(frm.doc.per_billed) < 100){

            frm.add_custom_button(__("Create Sales Invoice"), function() {
                create_sales_inv(frm)
            }, "fa fa-money");
        }

        $.each(frm.doc["items"],function(i, items)
	    {
            if (items.pick_list_item){
                var df = frappe.meta.get_docfield("Delivery Note Item", "qty", cur_frm.doc.name);
                df.read_only = 1;
            }
	    });
        
    },
    setup(frm) {
        $.each(frm.doc["items"],function(i, items)
	    {
            if (items.pick_list_item){
                var df = frappe.meta.get_docfield("Delivery Note Item", "qty", cur_frm.doc.name);
                df.read_only = 1;
            }
	    });
    },
});

function create_sales_inv(frm) {
    frappe.model.open_mapped_doc({
        method: "freeline.freeline.events.make_sales_invoice",
        frm: frm
    })
}