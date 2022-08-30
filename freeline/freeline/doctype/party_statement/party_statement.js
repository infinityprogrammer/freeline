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
				if(r.message){
					console.log(r)
					frm.clear_table("statement_details");
					let invs = r.message
					let bal = 0
					for(let i=0; i < invs.length; i++) {
						bal += (invs[i].debit_in_account_currency - invs[i].credit_in_account_currency)
					  	let row = frm.add_child('statement_details', {
						    posting_date: invs[i].posting_date,
						    reference_name: invs[i].voucher_no,
						    customer: invs[i].party,
						    debit_amount: invs[i].debit_in_account_currency,
						    credit_amount: invs[i].credit_in_account_currency,
						    balance: bal,
						    document_type: invs[i].voucher_type,
						    remarks: invs[i].remarks,
							against_voucher: invs[i].against_voucher,
						});
					}
					//frappe.msgprint(__('Data present'));
				}else{
					frappe.msgprint(__('No data found for the applier filters'));
				}
				frm.refresh_field('statement_details');
			}
		});
    },

	get_ageing: function(frm){
    	// first try to test by uncommenting 
    	frm.clear_table("ageing_details");
    	frm.call({
			method: "get_party_ageing",
			doc:frm.doc,
			freeze: true,
			freeze_message: "Fetching Ageing...",
			callback: function(r) {
				if(r.message){
					console.log(r)
					frm.clear_table("ageing_details");
					let invs = r.message
					for(let i=0; i < invs.length; i++) {
					  	let row = frm.add_child('ageing_details', {
							party_type: "Customer",
						    party: invs[i].party,
						    party_name: invs[i].party_name,
						    balance: invs[i].net_balance
						});
					}
					//frappe.msgprint(__('Data present'));
				}else{
					frappe.msgprint(__('No data found for the applier filters'));
				}
				frm.refresh_field('ageing_details');
			}
		});
    },

	before_save:function(frm){
        frm.trigger("net_employee_balance");
    },

	net_employee_balance:function(frm){
        var dr= 0
        var cr= 0
        $.each(frm.doc["statement_details"],function(i, statement_details)
	    {
             dr += statement_details.debit_amount;
             cr += statement_details.credit_amount;
	    });
		let diff = dr-cr
        frm.set_value("party_balance",diff);
    },
});
