// Copyright (c) 2023, RAFI and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rebate Process', {
	refresh: function(frm) {

		frm.set_query("item_group", "rebate_details", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					'is_group': 0
				}
			}
		});

		frm.set_query("rebate_item", function(frm) {
			
			return {
				filters: {
					'item_group': 'Rebate and Shelf Items'
				}
			}
		});

	},
	validate: function(frm) {

		let frm_date = frm.doc.rebate_start_from
		var myDate = new Date(frm_date);
		var firstDay = new Date(myDate.getFullYear(), myDate.getMonth(), 2);
		let dt_from_time = new Date(firstDay).toISOString().split('T')[0]


		if (frm.doc.from_date > frm.doc.from_date){
			frappe.throw("From date not greate than to date.")
		}
		
		if(frm_date != dt_from_time){
			frappe.throw("From date must be first day of the month")
		}

		let to_date1 = frm.doc.rebate_end_date
		var to_dt = new Date(to_date1);
		var lastDay = new Date(to_dt.getFullYear(), to_dt.getMonth() + 1, 1);
		let dt_to_date = new Date(lastDay).toISOString().split('T')[0]
		
		if (dt_to_date != to_date1){
			frappe.throw("To date must be last day of the month")
		}
	},

	before_save: function(frm) {
		let total = 0
		

		if (frm.doc.docstatus == 0){
			
			frm.clear_table("rebates");

			let start = new Date(frm.doc.rebate_start_from);
			let end = new Date(frm.doc.rebate_end_date);

			if (frm.doc.rebate_duration == "Monthly"){
				
				let lastDays = getLastDaysOfMonths(start, end);
				lastDays.forEach((day) => {
					
					let dt_to_date = new Date(day).toISOString().split('T')[0]

					if(frm.doc.rebate_end_date >= dt_to_date){
						
					
						let row = frm.add_child('rebates', {
							date: dt_to_date,
						});

					}
					
				});

			}
			if (frm.doc.rebate_duration == "Quarterly"){


				let lastDaysqtr = getLastDaysOfQuarters(start, end);

				lastDaysqtr.forEach(day => {
					
					let dt_to_date = new Date(day).toISOString().split('T')[0]
					
					if(frm.doc.rebate_end_date >= dt_to_date){
						
						let row = frm.add_child('rebates', {
							date: dt_to_date,
						});
					}
				});

			}
			
			frm.set_value('total_amount', total)
			frm.refresh_field('total_amount');
		}

	}
});



function getLastDayOfMonth(year, month) {
    let date = new Date(year, month + 1, 1);
    date.setDate(date.getDate() - 0);
    return date;
}

function getLastDaysOfMonths(startDate, endDate) {
    let currentDate = startDate;
    let lastDays = [];
    while (currentDate <= endDate) {
        let year = currentDate.getFullYear();
        let month = currentDate.getMonth();
        lastDays.push(getLastDayOfMonth(year, month));
        currentDate.setMonth(month + 1);
    }
    return lastDays;
}

function getLastDaysOfQuarters(startDate, endDate) {
    let currentDate = new Date(startDate.getFullYear(), Math.floor(startDate.getMonth() / 3) * 3, 1);
	
    let lastDays = [];
    while (currentDate <= endDate) {
        let year = currentDate.getFullYear();
        let month = currentDate.getMonth() + 2;
        lastDays.push(getLastDayOfMonth(year, month));
        currentDate.setMonth(month +1);
    }
    return lastDays;
}

function getLastDaysOfYears(startDate, endDate) {
    let currentDate = new Date(startDate.getFullYear(), 0, 1);
    let lastDays = [];
    while (currentDate <= endDate) {
        let year = currentDate.getFullYear();
        lastDays.push(getLastDayOfMonth(year, 11));
        currentDate.setFullYear(year + 1);
    }
    return lastDays;
}
