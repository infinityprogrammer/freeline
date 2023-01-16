frappe.ui.form.on("Price List", {
	refresh: function(frm) {
		let me = this;
        if (frm.doc.name == 'Trade Price List'){
            frm.add_custom_button(__("Update Price"), function() {
                // frappe.msgprint(__('Document updated successfully'));
                var html_str = ""
                frappe.call({
                    method: "freeline.freeline.globalapi.get_trade_price_list",
                    freeze: true,
                    freeze_message: "Updating Prices...",
                    callback: function(r) {
                        
                        let response = r.message
                        console.log(response)
                        if(response.length > 0){
                            html_str += "<p>Prices are updated, see the below list of updated items and new price.</p>"
                            html_str += "<table class='table table-striped'><tr><th>Item Code</th><th>Old Price</th><th>New Price</th></tr>"
                            for (let index = 0; index < response.length; index++) {
                                const element = response[index];
                                html_str += "<tr>"
                                html_str += "<td>" +response[index].item_code+ "</td>"
                                html_str += "<td>" +response[index].price_list_rate+ "</td>"
                                html_str += "<td>" +response[index].val_rate+ "</td>"
                                html_str += "</tr>"
                            }
                            html_str += "<table>"
                        }else{
                            html_str += "<b>All prices are updated</b>"
                        }
                        frappe.msgprint(__(html_str));
                        
                    },
                    error: (r) => {
                        frappe.msgprint(__("Some error occured"));
                        console.log(r)
                    }
                });
            }, "fa fa-money");
        }
		
	}
});
