frappe.ui.form.on("Payment Entry", {
    get_employee: function(frm){
    	$.each(frm.doc["references"],function(i, references)
	    {
            frappe.db.get_value("Sales Invoice", {"name": references.reference_name}, "employee_name", (r) => {
                references.employee_name = r.employee_name
                refresh_field("employee_name", i, "references");
            });
	    });
    },
});