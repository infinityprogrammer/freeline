frappe.ui.form.on('Pick List', {
    // on refresh event
    refresh(frm) {
        var df = frappe.meta.get_docfield("Pick List Item", "qty", cur_frm.doc.name);
        df.read_only = 1;
    },
    setup(frm) {
        var df = frappe.meta.get_docfield("Pick List Item", "qty", cur_frm.doc.name);
        df.read_only = 1;
    },
});

// frappe.ui.form.on("Pick List", "onload", function (frm, cdt, cdn) {
//     var df = frappe.meta.get_docfield("Pick List Item", "qty", cur_frm.doc.name);
//     df.read_only = 1;
// });
