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


        var userRoles = frappe.user_roles;
        // console.log(userRoles);

        if (!frm.is_new()) {
            frappe.db.get_single_value("Tiejan Internal Settings", "pick_list_status_update_role").then((val) => {
                if (userRoles.includes(val)) {
                    // console.log("User is allowed to update bonus budget.");

                    frm.add_custom_button(__("Update Pick List Status"), function () {
                        let d = new frappe.ui.Dialog({
                            title: "Select Status",
                            fields: [
                                {
                                    label: "Delivery Note Status",
                                    fieldname: "dn_status",
                                    fieldtype: "Select",
                                    options: ["Draft", "To Bill", "Completed", "Return Issued", "Cancelled", "Closed"],
                                    reqd: 1,
                                    default: "Draft",
                                }
                            ],
                            size: "small", // small, large, extra-large
                            primary_action_label: "Update Status",
                            primary_action(values) {
                                console.log(values);

                                var dn_status = values.dn_status;

                                frm.call(
                                    "update_pick_list_status_manually",
                                    {
                                        dn_status: dn_status,
                                    },
                                    (r) => {
                                        console.log(r);
                                        frappe.show_alert({
                                            message: __("Pick List DN Status Updated"),
                                            indicator: "green",
                                        });
                                    }
                                );

                                d.hide();
                            },
                        });

                        d.show();
                    }).addClass("btn btn-danger");
                }
            });
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
