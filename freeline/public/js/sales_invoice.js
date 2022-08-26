frappe.ui.form.on("Sales Invoice", {
    
    before_save:function(frm){
        
        if(frm.doc.employee_name == "" || !frm.doc.employee_name){
            cur_frm.clear_table("sales_team");
            msgprint("No Sales Rep in this invoice, Due to no Sales person allocated.")
            show_alert('No Sales Rep in this invoice, Due to no Sales person allocated.', 10);
        }else{
            sales_team(frm);
        }
        
    },
});

function sales_team(frm){
    cur_frm.clear_table("sales_team");
    var child = cur_frm.add_child("sales_team");
    frappe.model.set_value(child.doctype, child.name, "sales_person", cur_frm.doc.employee_name);
    frappe.model.set_value(child.doctype, child.name, "allocated_percentage", 100);
    cur_frm.refresh_field("sales_team");
}