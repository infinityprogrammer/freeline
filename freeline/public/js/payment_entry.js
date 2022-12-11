frappe.ui.form.on("Payment Entry", {
    get_employee: function(frm){
    	$.each(frm.doc["references"],function(i, references)
	    {
            frappe.db.get_value("Sales Invoice", {"name": references.reference_name}, "employee_name", (r) => {
                frappe.model.set_value(references.doctype,references.name,"employee_name",r.employee_name);
            });
	    });
        //frm.save();
        // frm.reload_doc();
        //frm.set_value('description', 'New description')
    },

    before_save:function(frm){
        if(frm.doc.payment_type == "Receive"){
            // frm.set_value("employee_id","");
            $.each(frm.doc["references"],function(i, references)
            {
                if(references.employee_name != ""){
                    frm.set_value("employee_name",references.employee_name);
                }
            });
        }
        
    },
});