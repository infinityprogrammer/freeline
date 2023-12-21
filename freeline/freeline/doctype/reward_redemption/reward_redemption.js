// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reward Redemption', {
	refresh: function(frm) {

	},
	get_points: function(frm){
    	// first try to test by uncommenting 
    	frm.clear_table("points");
    	frm.call({
			method: "get_redeemable_points",
			doc:frm.doc,
			freeze: true,
			freeze_message: "Fetching Data...",
			callback: function(r) {
				if(r.message.length > 0){
					frm.clear_table("points");
					let invs = r.message
					let total_points = 0
					for(let i=0; i < invs.length; i++) {
						total_points += invs[i].balance_point
					  	let row = frm.add_child('points', {
						    date: invs[i].posting_date,
						    total_point: invs[i].balance_point,
						    reward_program: invs[i].program_name,
						    sales_invoice: invs[i].sales_invoice,
						    program_name: invs[i].name,
						});
					}
					frm.set_value("total_redeem_point", total_points);
					// frappe.msgprint(__('Data present'));
				}else{
					frappe.msgprint(__('No data found for the applier filters'));
				}
				frm.refresh_field('points');
			}
		});
    },
});
