// Copyright (c) 2022, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Party Statement', {
	refresh: function(frm) {

		frm.set_query("party_type", function(doc) {
			return {
				filters: {
					'name': ['in',['Supplier',"Customer"]]
				}
			}
		});
	},

	party: function(frm){

		if(frm.doc.party_type == "Customer"){
			frappe.db.get_value("Customer", {"name": frm.doc.party}, ["customer_name","name"], (r) => {
				frm.set_value("party_name",r.customer_name);
				frm.refresh_field("party_name");
			});
		}

		if(frm.doc.party_type == "Supplier"){
			frappe.db.get_value("Supplier", {"name": frm.doc.party}, ["supplier_name","name"], (r) => {
				frm.set_value("party_name",r.supplier_name);
				frm.refresh_field("party_name");
			});
		}
	},

	get_statement: function(frm){
    	// first try to test by uncommenting 
    	frm.clear_table("statement_details");
    	frm.call({
			method: "get_party_statement",
			doc:frm.doc,
			freeze: true,
			freeze_message: "Fetching Statements...",
			callback: function(r) {
				if(r.message.length > 0){
					frm.clear_table("statement_details");
					let invs = r.message
					for(let i=0; i < invs.length; i++) {
					  	let row = frm.add_child('statement_details', {
						    purchase_invoice: invs[i].name,
						    company: invs[i].company,
						    supplier: invs[i].supplier,
						    bill_no: invs[i].bill_no,
						    grand_total: invs[i].grand_total,
						    outstanding_amount: invs[i].outstanding_amount,
						    allocated_amount: invs[i].outstanding_amount,
						    cost_center: invs[i].cost_center,
						    credit_to: invs[i].credit_to,
						    paid_to: invs[i].paid_to,
						    account_name: invs[i].account_name
						});
					}
					// frappe.msgprint(__('Data present'));
				}else{
					frappe.msgprint(__('No data found for the applier filters'));
				}
				frm.refresh_field('statement_details');
			}
		});
    },
});
