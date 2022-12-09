frappe.ui.form.on("Payment Reconciliation", {

    get_employee: function(frm){
    	$.each(frm.doc["invoices"],function(i, invoices)
	    {
            if (invoices.invoice_type == "Sales Invoice"){
                frappe.db.get_value("Sales Invoice", {"name": invoices.invoice_number}, "employee_name", (r) => {
                    frappe.model.set_value(invoices.doctype,invoices.name,"employee_name",r.employee_name);
                });
            }
	    });
        
        $.each(frm.doc["allocation"],function(i, allocation)
	    {
            if (allocation.invoice_type == "Sales Invoice"){
                frappe.db.get_value("Sales Invoice", {"name": allocation.invoice_number}, "employee_name", (r) => {
                    frappe.model.set_value(allocation.doctype,allocation.name,"employee_name",r.employee_name);
                });
            }
	    });

        $.each(frm.doc["payments"],function(i, payments)
	    {
            if (payments.reference_type == "Payment Entry"){
                frappe.db.get_value("Payment Entry", {"name": payments.reference_name}, "employee_name", (r) => {
                    frappe.model.set_value(payments.doctype,payments.name,"employee_name",r.employee_name);
                });
            }
	    });
    },
    
});