frappe.ui.form.on('Delivery Note', {
    // on refresh event
    refresh(frm) {
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