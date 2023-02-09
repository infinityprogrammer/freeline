// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shelf Rental Agreement', {
	refresh: function(frm) {

	},

	validate: function(frm) {

		let frm_date = frm.doc.from_date
		var myDate = new Date(frm_date);
		var firstDay = new Date(myDate.getFullYear(), myDate.getMonth(), 1);
		let dt_from_time = new Date(firstDay).toLocaleDateString('en-CA');

		if (frm.doc.from_date > frm.doc.from_date){
			frappe.throw("From date not greate than to date.")
		}
		
		if(frm_date != dt_from_time){
			frappe.throw("From date must be first day of the month")
		}

		let to_date1 = frm.doc.to_date
		var to_dt = new Date(to_date1);
		var lastDay = new Date(to_dt.getFullYear(), to_dt.getMonth() + 1, 0);
		let dt_to_date = new Date(lastDay).toLocaleDateString('en-CA');
		
		if (dt_to_date != to_date1){
			frappe.throw("To date must be last day of the month")
		}
	},

});
