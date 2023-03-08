frappe.ui.form.on("Stock Reconciliation", "onload", function(frm) {
    frm.set_query("warehouse", function() {
        return {
            "filters": {
                "is_group": 0,
            }
        };
    });

});


frappe.ui.form.on("Stock Reconciliation Item", {
    
    items_add(frm, cdt, cdn) { 

        frappe.model.set_value(cdt,cdn,"warehouse",frm.doc.warehouse);
	    refresh_field("warehouse", cdn, "items");
    },

    item_code:function(frm,cdt,cdn){

    	frappe.model.set_value(cdt,cdn,"warehouse",frm.doc.warehouse);
	    refresh_field("warehouse", cdn, "items");

    },

    add_item_code: function(frm,cdt,cdn) {

       frappe.model.set_value(cdt,cdn,"warehouse",frm.doc.warehouse);
	   refresh_field("warehouse", cdn, "items");

    }
});