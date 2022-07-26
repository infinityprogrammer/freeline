frappe.ui.form.on("Payment Entry", {

    filter: function(frm){

    	$.each(frm.doc["references"],function(i, references)
	    {
            console.log(references.reference_name);
            frappe.db.get_value("Sales Invoice", {"name": references.reference_name}, "employee", (r) => {
                // console.log(r.employee)
                references.employee = r.employee
                refresh_field("employee", i, "references");
            });
           // frm.get_field("references").grid.grid_rows[1].remove()
	    });
        // frm.save();  
    },
});