function hide_sales_popup_divs() {
	$('#payment_details').css('display', 'none');
	$('#add_salesman').css('display', 'none');
	$('#add_customer').css('display', 'none');
	$('#bank_account_details').css('display', 'none');
	$('#transaction_reference_no_details').css('display', 'none');
	$('#dialogue_popup').css('display', 'none');
	$('#dialogue_popup_container').css('display', 'none');
	$('#popup_overlay').css('display', 'none');
}
function hide_estimate_popup_divs() {
	$('#payment_details').css('display', 'none');
	$('#add_salesman').css('display', 'none');
	$('#dialogue_popup').css('display', 'none');
	$('#dialogue_popup_container').css('display', 'none');
	$('#popup_overlay').css('display', 'none');
}
function SalesController($scope, $http){
	$scope.current_sales_item = [];
	$scope.choosed_item = [];
	$scope.product_name = '';
	$scope.no_customer_msg = "";
	$scope.select_all_price_type = false;
	$scope.bank_account = '';
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.sales = {
			'invoice_no': '',
			'invoice_date': '',
			'discount': 0,
			'payment_mode': 'cash',
			'customer': '',
			'salesman': '',
			'grant_total': 0,
			'tax_exclusive_total': 0,
			'do_no': '',
			'items': [
				{
					'id': '',
		            'name': '',
		            'code': '',
		            'batch_name': '',
		            'batch_id': '',
		            'stock': '',
		            'stock_unit': '',
		            'selling_units':[],
		            'uom': '',
		            'quantity': '',
		            'net_amount': '',
		            'tax_exclusive_amount': '',
		            'mrp': '',
		            'current_item_price': '',
		            'selling_unit': '',
		            'purchase_unit': '',
		            'relation': '',
		            'price_type': false,
		            'tax': '',
		        },
			],
			'quantity_choosed': '',
			'bank_name': '',
			'branch': '',
			'cheque_no': '',
			'card_no': '',
			'card_holder_name': '',
			'cheque_date': '',
			'bill_type': 'Receipt',
			'bank_account_ledger': '',
			'round_off': ''
		}
		console.log($scope.sales);
	}
	$scope.add_new_sales_item = function(){
		$scope.sales.items.push({
			'id': '',
			'name': '',
            'code': '',
            'batch_name': '',
            'batch_id': '',
            'stock': '',
            'stock_unit': '',
            'selling_units':[],
            'uom': '',
            'quantity': '',
            'net_amount': '',
            'tax_exclusive_amount': '',
            'mrp': '',
            'current_item_price': '',
            'selling_unit': '',
            'purchase_unit': '',
            'relation': '',
            'whole_sale_price': '',
			'retail_price': '',
			'price_type': $scope.select_all_price_type,
			'tax': '',
		});
		$scope.selling_units = {
			'unit': '',
		}
	}
	$scope.search_items = function(item){
		$scope.current_sales_item = item;
		$scope.item_name = item.name;
		$scope.current_sales_item.code = "";
		$scope.current_sales_item.id = "";
		get_item_search_list($scope, $http);
	}
	$scope.get_item_details = function(item){
		$scope.current_sales_item.name = item.name;
		$scope.current_sales_item.id = item.id;
		$scope.current_sales_item.code = item.code;
		$scope.items = "";
	}
	$scope.search_salesman = function(){
		if($scope.salesman_name.length == 0){
			$scope.salesmen = "";
			$scope.no_salesman_message = "";
		}
		else{
			$scope.sales.salesman = "";
			search_salesmen($scope,$http);
		}	
	}
	$scope.select_salesman = function(salesman){
		$scope.salesman_name = salesman.name;
		$scope.sales.salesman = salesman.id;
		$scope.salesmen = "";
		$scope.select_salesman_flag = false;
		$scope.no_salesman_message = "";
	}
	$scope.search_batch = function(item){
		if(item.id != ''){
			$scope.no_batch_msg = "";
			$scope.current_sales_item = item;
			$scope.batch_name = item.batch_name;
			$scope.item = item.id;
			get_batch_items_list($scope, $http);

		} else
			$scope.no_batch_msg = "Please choose an item";
	}
	$scope.new_salesman = function(sales) {
		$scope.current_sales = sales;
		$scope.salesman = {
			'first_name': '',
			'last_name': '',
			'address': '',
			'contact_no': '',
			'email': '',
		}
	    hide_sales_popup_divs();
	    $('#add_salesman').css('display', 'block');
	    create_popup();
	}
	$scope.save_salesman = function() {
		save_salesman($scope, $http, 'sales');
		$scope.no_salesman_message = "";
	}
	$scope.save_customer = function(){
		save_customer($scope, $http, 'sales');	
		$scope.no_customer_msg = "";
	}
	$scope.hide_popup = function() {
        $scope.salesman = {
            'name': '',
            'address': '',
            'mobile': '',
            'telephone_number': '',
            'email': '',
        }
        $scope.validate_salesman_error_msg = "";
        $('#dialogue_popup_container').css('display', 'none');
        $('#popup_overlay').css('display', 'none');
    }
	$scope.select_batch = function(batch){
		$scope.current_sales_item.batch_name = batch.batch_name;
		$scope.current_sales_item.batch_id = batch.batch_id;
		$scope.batch_items_list = "";
		if ($scope.current_sales_item.id) {
			$scope.get_batch($scope.current_sales_item);
		}
		$scope.current_sales_item.batches = "";
	}
	$scope.change_bill_type = function(bill_type){
		console.log(bill_type);
		for(var i = 0; i < $scope.sales.items.length; i++){
			if($scope.sales.items[i].uom != '' && $scope.sales.items[i].quantity.length > 0){
				$scope.sales.items[i].net_amount = parseFloat( $scope.sales.items[i].quantity) * parseFloat($scope.sales.items[i].current_item_price);
				$scope.sales.items[i].tax_exclusive_amount = $scope.sales.items[i].net_amount;
				if(bill_type == 'Invoice')
					$scope.sales.items[i].net_amount = parseFloat($scope.sales.items[i].net_amount) + (parseFloat($scope.sales.items[i].net_amount) * parseFloat($scope.sales.items[i].tax/100))	
			}
		}
		$scope.calculate_total_amount();
	}
	$scope.change_price_type = function(){
		for(var i = 0; i < $scope.sales.items.length; i++){
			if($scope.select_all_price_type == true){
				$scope.sales.items[i].price_type = false;
				$scope.sales.items[i].mrp = $scope.sales.items[i].retail_price;
			}
			else{
				$scope.sales.items[i].price_type = true;
				$scope.sales.items[i].mrp = $scope.sales.items[i].whole_sale_price;
			}
			if($scope.sales.items[i].uom == $scope.sales.items[i].stock_unit){
				$scope.sales.items[i].current_item_price = $scope.sales.items[i].mrp
			} else if($scope.sales.items[i].uom == $scope.sales.items[i].purchase_unit){
				$scope.sales.items[i].current_item_price = parseFloat($scope.sales.items[i].mrp) * parseFloat($scope.sales.items[i].relation);
			}
			if($scope.sales.items[i].quantity != '' && Number($scope.sales.items[i].quantity) && $scope.sales.items[i].uom != ""){
				$scope.sales.items[i].net_amount = parseFloat( $scope.sales.items[i].quantity) * parseFloat($scope.sales.items[i].current_item_price);
				$scope.sales.items[i].tax_exclusive_amount = $scope.sales.items[i].net_amount
				if($scope.sales.bill_type == 'Invoice')
					$scope.sales.items[i].net_amount = parseFloat($scope.sales.items[i].net_amount) + (parseFloat($scope.sales.items[i].net_amount) * parseFloat($scope.sales.items[i].tax/100))
			}
			else if($scope.sales.items[i].quantity.length == 0){
				$scope.sales.items[i].net_amount = "";
				$scope.sales.items[i].tax_exclusive_amount = "";
			}
		}
		$scope.calculate_total_amount();
	}
	$scope.get_batch = function(item){
		$http.get('/inventory/batch_item_details/?batch_id='+item.batch_id+'&item_id='+item.id).success(function(data){
        	item.stock = data.quantity;
        	item.stock_unit = data.stock_unit;
        	item.selling_units = [];
        	item.selling_units.push({
        		'unit': data.selling_unit,
        	})
        	item.selling_units.push({
        		'unit': data.purchase_unit,
        	})
        	item.selling_unit = data.selling_unit;
        	item.purchase_unit = data.purchase_unit;
        	item.relation = data.relation;
        	item.whole_sale_price = data.whole_sale_price_sales;
        	item.retail_price = data.retail_price_sales;
        	item.tax = data.tax;
        	item.offer_quantity = data.offer_quantity;
        	if(item.price_type == false)
        		item.mrp = data.retail_price_sales;
        	if(item.price_type == true)
        		item.mrp = data.whole_sale_price_sales;
	    }).error(function(data, status) {
	    	console.log('Request failed' || data);
	    });
	}
	$scope.calculate_quantity_from_uom = function(item){
		$scope.validate_sales_msg = "";
	    if(item.price_type == false)
    		item.mrp = item.retail_price
    	if(item.price_type == true)
    		item.mrp = item.whole_sale_price
		if(item.uom == item.stock_unit){
			item.current_item_price = item.mrp
			if(item.quantity > item.stock){
				$scope.validate_sales_msg = "Out of Stock";
			}
		} else if(item.uom == item.purchase_unit){
			item.current_item_price = parseFloat(item.mrp) * parseFloat(item.relation);
			if(item.quantity*item.relation > item.stock){
				$scope.validate_sales_msg = "Out of Stock";
			}
		}
		if(item.quantity != '' && Number(item.quantity) && item.uom != ""){
			item.net_amount = parseFloat(item.quantity) * parseFloat(item.current_item_price);
			item.tax_exclusive_amount = item.net_amount;
			if($scope.sales.bill_type == 'Invoice')
				item.net_amount = parseFloat(item.net_amount) + (parseFloat(item.net_amount) * parseFloat(item.tax/100))
		}
		else if(item.quantity.length == 0)
			item.net_amount = "";
		$scope.calculate_total_amount();
	}
	$scope.calculate_total_amount = function(){
		$scope.sales.grant_total = 0;
		$scope.sales.tax_exclusive_total = 0;
		for(var i = 0; i < $scope.sales.items.length; i++){
			if(Number($scope.sales.items[i].net_amount)){
				$scope.sales.grant_total = parseFloat($scope.sales.grant_total) + parseFloat($scope.sales.items[i].net_amount);
				$scope.sales.tax_exclusive_total = parseFloat($scope.sales.tax_exclusive_total) + parseFloat($scope.sales.items[i].tax_exclusive_amount);
			}
		}
		if($scope.sales.discount.length != 0 && Number($scope.sales.discount)){
			$scope.sales.grant_total = parseFloat($scope.sales.grant_total) - parseFloat($scope.sales.discount)
			$scope.sales.tax_exclusive_total = parseFloat($scope.sales.tax_exclusive_total) - parseFloat($scope.sales.discount)
		}
		if ($scope.sales.round_off != Number($scope.sales.round_off)) {
			$scope.sales.round_off = 0;
		}
		if($scope.sales.round_off.length != 0 && Number($scope.sales.round_off)){
			$scope.sales.grant_total = parseFloat($scope.sales.grant_total) - parseFloat($scope.sales.round_off)
			$scope.sales.tax_exclusive_total = parseFloat($scope.sales.tax_exclusive_total) - parseFloat($scope.sales.round_off)
		}
	}
	$scope.search_customer = function(){
		if($scope.customer_name.length == 0){
			$scope.customers = "";
			$scope.no_customer_msg = "";
		}
		else{
			$scope.sales.customer = "";
			get_customer_search_list($scope, $http);
		}		
	}
	$scope.select_customer = function(customer){
		$scope.customer_name = customer.name;
		$scope.sales.customer = customer.id;
		$scope.customers = "";
		$scope.select_customer_flag = false;
		$scope.no_customer_msg = "";
	}
	$scope.new_customer = function(sales) {
		$scope.current_sales = sales;
	    $scope.customer= {
	        'name': '',
	        'address': '',
	        'mobile': '',
	        'telephone_number': '',
	        'email': '',
	    }
	    hide_sales_popup_divs();
	    $('#add_customer').css('display', 'block');
	    create_popup();
	}
	$scope.payment_mode_details = function(payment_mode) {
		hide_sales_popup_divs();
		$('#payment_details').css('display', 'block');
		create_popup();
		if (payment_mode == 'cheque') {
			$scope.is_cheque_payment = true;
		} else if (payment_mode == 'card') {
			$scope.is_cheque_payment = false;
		} else {
			hide_sales_popup_divs();
		}
	}
	$scope.bank_account_details = function(payment_mode) {
		get_bank_account_details($scope, $http);
		$scope.sales.payment_mode = payment_mode;
		hide_sales_popup_divs();
		$('#bank_account_details').css('display', 'block');
		$scope.other_bank_account = false;
		$scope.bank_account_error = '';
		$scope.bank_account = '';
		$scope.bank_account_name = '';
		if ($scope.sales.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();
	}
	$scope.add_bank_account_details = function() {
		if($scope.bank_account != ''){
			$scope.sales.bank_account_ledger = $scope.bank_account;
			$scope.payment_mode_details($scope.sales.payment_mode);
		}
	}
	$scope.create_new_bank_acount = function() {
		if ($scope.bank_account_name == '' || $scope.bank_account_name == undefined) {
			$scope.bank_account_error = 'Please enter the Bank account name';
		} else {
			create_new_bank_acount($scope, $http, 'sales');
		}
	}
	$scope.validate_sales = function(){
		$scope.validate_sales_msg = "";
		if($scope.sales.do_no == ""){
			$scope.validate_sales_msg = "Please enter the DO No";
			return false;
		} else if($scope.salesman_name == '' || $scope.sales.salesman == ''){
			$scope.validate_sales_msg = "Please select a salesman from the list";
			return false;
		} else if($scope.no_customer_msg != ""){
			$scope.validate_sales_msg = "Please select a valid customer or leave the field empty";
			return false;
		} else if (($scope.sales.payment_mode == 'card' || $scope.sales.payment_mode == 'cheque' ) && ($scope.sales.bank_name == '' || $scope.sales.bank_name == undefined)) {
			$scope.validate_sales_msg = 'Please enter bank name';
			return false;
		} else if (($scope.sales.payment_mode == 'card') && ($scope.sales.card_no == '' || $scope.sales.card_no == undefined)) {
			$scope.validate_sales_msg = 'Please enter Card No';
			return false;
		} else if (($scope.sales.payment_mode == 'card') && ($scope.sales.card_holder_name == '' || $scope.sales.card_holder_name == undefined)) {
			$scope.validate_sales_msg = 'Please enter Card Holder Name';
			return false;
		} else if (($scope.sales.payment_mode == 'cheque') && ($scope.sales.branch == '' || $scope.sales.branch == undefined)) {
			$scope.validate_sales_msg = 'Please enter Branch';
			return false;
		} else if (($scope.sales.payment_mode == 'cheque') && $scope.sales.cheque_date == '') {
			$scope.validate_sales_msg = 'Please choose Cheque Date';
			return false;
		} else if (($scope.sales.payment_mode == 'cheque') && ($scope.sales.cheque_no == '' || $scope.sales.cheque_no == undefined)) {
			$scope.validate_sales_msg = 'Please choose Cheque Number';
			return false;
		} for(var i = 0; i < $scope.sales.items.length; i++){
			if ($scope.sales.items[i].code == '') {
				$scope.validate_sales_msg = 'Item code cannot be null in row' + (i+1);
				return false;
			} else if ($scope.sales.items[i].name == '') {
				$scope.validate_sales_msg = 'Item name cannot be null in row' + (i+1);
				return false;
			} else if ($scope.sales.items[i].batch_id == '') {
				$scope.validate_sales_msg = 'Please choose batch for the item in row '+ (i+1);
				return false;
			} else if ($scope.sales.items[i].uom == '') {
				$scope.validate_sales_msg = 'Please choose the unit of measurement in row '+ (i+1);
				return false;
			} else if ($scope.sales.items[i].quantity == '') {
				$scope.validate_sales_msg = 'Please enter the quantity in row '+ (i+1);
				return false;
			} 
			if($scope.sales.items[i].uom == $scope.sales.items[i].stock_unit){
				if($scope.sales.items[i].quantity > $scope.sales.items[i].stock){
					$scope.validate_sales_msg = "Out of Stock quantity in row " + (i+1);
					return false;
				}
			} else if($scope.sales.items[i].uom == $scope.sales.items[i].purchase_unit){
				if($scope.sales.items[i].quantity*$scope.sales.items[i].relation > $scope.sales.items[i].stock){
					$scope.validate_sales_msg = "Out of Stock in row " + (i+1);
					return false;
				}
			}
		} return true;
	}
	$scope.save_sales = function(){
		if($scope.validate_sales()){
			$scope.sales.invoice_date = $('#invoice_date').val();
			console.log($scope.sales);
			for(var i = 0; i < $scope.sales.items.length; i++){
				if($scope.sales.items[i].price_type == true)
					$scope.sales.items[i].price_type = "true"
				else
					$scope.sales.items[i].price_type = "false"
			}	
			params = {
				'sales_details': angular.toJson($scope.sales),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			console.log($scope.sales);
			show_loader();
			$http({
				method: 'post',
				url: '/sales/sales_entry/',
				data: $.param(params),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				if(data.result == 'ok'){
					hide_sales_popup_divs($scope, $http);
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Sales ';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				} else {
					$scope.validate_sales_msg = data.message;
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			})
		}
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/sales/sales_entry?transaction_ref_no='+$scope.transaction_reference_no;
	}
	$scope.remove_item = function(item) {
		var index = $scope.sales.items.indexOf(item);
		$scope.sales.items.splice(index, 1);
		$scope.calculate_total_amount();
	}
	$scope.hide_popup_payment_details = function(){
		$scope.sales.bank_name = $scope.bank_name;
		$scope.sales.branch = $scope.branch;
		$scope.sales.cheque_no = $scope.cheque_no;
		$scope.sales.card_no = $scope.card_no;
		$scope.sales.card_holder_name = $scope.card_holder_name;
		$scope.sales.cheque_date = document.getElementById("cheque_date").value;
		hide_sales_popup_divs();
	}
}

function SalesReceiptsController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.select_all = false;
		$scope.sales_receipts  = {
			'sales_invoice_number': '',
			'auto_invoice_no': '',
			'transaction_reference_no': '',
			'sales_invoice_date': '',
			'amount': '',
			'invoice': false,
		}
	}
	$scope.search_receipts = function(){
		var start_date = $('#start_date').val();
		var end_date = $('#end_date').val();
		var date_value = start_date.split('/');
        var start = new Date(date_value[2],date_value[1]-1, date_value[0]);
        var date_value = end_date.split('/');
        var end = new Date(date_value[2],date_value[1]-1, date_value[0]);
		if (start_date == '' || start_date == undefined) {
			$scope.validate_msg = 'Please Choose start date';
		} else if (end_date == '' || end_date == undefined) {
			$scope.validate_msg = 'Please Choose end date';
		} else if(start > end){
          $scope.validate_msg = 'Please check the dates';
        } else {
			$http.get('/sales/sales_receipts/?start_date='+start_date+'&end_date='+end_date).success(function(data){
				if(data.result == 'ok'){
					$scope.sales_receipts = data.sales_receipts;
					for(var i = 0; i < $scope.sales_receipts.length; i++)
						$scope.sales_receipts[i].invoice = false;
					if($scope.sales_receipts.length == 0)
						$scope.validate_msg = 'No Receipts found';
				} else{
					$scope.validate_msg = data.message;
				}

			}).error(function(data, status) {
	    	console.log('Request failed' || data);
	  	  	});
		}
	}
	$scope.convert_all = function(){
		for(var i = 0; i < $scope.sales_receipts.length; i++){		
			if($scope.select_all == true){
				$scope.sales_receipts[i].invoice = false;
			}
			else{
				$scope.sales_receipts[i].invoice = true;
			}
		}
	}
	$scope.convert_to_invoice = function(){
		for(var i = 0; i < $scope.sales_receipts.length; i++){
			if($scope.sales_receipts[i].invoice == true)
				$scope.sales_receipts[i].invoice = 'true'
			else
				$scope.sales_receipts[i].invoice = 'false'
		}
		params = {
			'sales_receipts': angular.toJson($scope.sales_receipts),
			'csrfmiddlewaretoken': $scope.csrf_token,
		}
		$http({
				method: 'post',
				url: '/sales/sales_receipts/',
				data: $.param(params),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
		}).success(function(data){
			document.location.href = '/sales/sales_receipts/';
		}).error(function(data, status){
			console.log('Request failed' || data);
		})
	}
}

function SalesReportController($scope, $http) {
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.generate_report = function(type) {
		var start_date = $('#start_date').val();
		var end_date = $('#end_date').val();
		if (start_date == '' || start_date == undefined) {
			$scope.report_mesg = 'Please Choose start date';
		} else if (end_date == '' || end_date == undefined) {
			$scope.report_mesg = 'Please Choose end date';
		} else {
			if (type == 'view') { 
				$http.get('/sales/sales_report/?start_date='+start_date+'&end_date='+end_date).success(function(data){
					$scope.sales_details = data.sales_details;
				}).error(function(data, status){
					console.log(data);
				});
			} else
				document.location.href = '/sales/sales_report/?start_date='+start_date+'&end_date='+end_date;
		}
	}
}
function SalesReturnController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.sales_invoice = '';
		$scope.items = [];
		$scope.sales_return = {
			'sales_id': '',
			'sales_invoice': '',
			'return_invoice': '',
			'return_invoice_date': '',
			'customer': '',
			'salesman': '',
			'grant_total': 0,
			'discount': 0,
			'items': [],
			'return_balance': 0,
			'bill_type': '',
			'total_tax': 0,
		}
	}
	$scope.get_sales_details = function(){
		$scope.no_sales_message = '';
		$scope.sales_return = {
			'sales_id': '',
			'sales_invoice': '',
			'return_invoice': '',
			'return_invoice_date': '',
			'customer': '',
			'salesman': '',
			'grant_total': 0,
			'discount': 0,
			'items': [],
			'return_balance': 0,
			'bill_type': '',
			'total_tax': 0,
		}
		if ($scope.sales_invoice.length > 0) {
			$http.get('/sales/sales_return_entry/?sales_invoice_no='+$scope.sales_invoice).success(function(data){
				if (data.result == 'ok') {
					console.log(data);
					if (data.sales_details.length == 0) {
						$scope.no_sales_message = 'No such Sales';
						$scope.sales_return.customer = '';
						$scope.sales_return.salesman = '';
					} else {
						$scope.items = data.sales_details[0].sales_items;
						$scope.sales_return.customer = data.sales_details[0].customer;
						$scope.sales_return.salesman = data.sales_details[0].salesman;
						$scope.sales_return.sales_id = data.sales_details[0].id;
						$scope.sales_return.sales_invoice = data.sales_details[0].sales_invoice;
						$scope.sales_return.grant_total = data.sales_details[0].grant_total;
						$scope.sales_return.discount = data.sales_details[0].discount;
						$scope.sales_return.return_balance = 0;
						$scope.sales_return.bill_type = data.sales_details[0].bill_type;
						console.log($scope.sales_return);
						for(var i = 0; i < $scope.items.length; i++){
							$scope.sales_return.items.push({
								'id': $scope.items[i].id,
								'name': $scope.items[i].item_name,
								'code': $scope.items[i].item_code,
								'purchased_quantity': $scope.items[i].item_quantity,
								'uom': $scope.items[i].uom,
								'returned_qty': 0,
								'net_amount': $scope.items[i].net_amount,
								'balance': 0,
								'tax_on_sales': $scope.items[i].tax,
								'tax_on_return': 0,
								'price': parseFloat($scope.items[i].net_amount)/parseFloat($scope.items[i].item_quantity),
								'mrp': $scope.items[i].mrp,
								'return_history': $scope.items[i].returned_qty,
							})
						}
					}
					console.log($scope.sales_return);
				}
			}).error(function(data, status) {
				console.log('Request failed' || data);
			});
		}
	}
	$scope.calculate_balance = function(item){
		$scope.validate_sales_return_msg = "";
		if(item.returned_qty > (item.purchased_quantity - item.return_history)){
			$scope.validate_sales_return_msg = "Return Quantity exceeds Purchased Quantity"
		} else{
			if(item.returned_qty.length > 0){
				item.balance = parseFloat(item.price) * parseFloat(item.returned_qty);
				item.net_amount = (parseFloat(item.purchased_quantity) - parseFloat(item.returned_qty)) * parseFloat(item.price);
				item.tax_on_return = parseFloat(item.net_amount) - ((parseFloat(item.purchased_quantity) - parseFloat(item.returned_qty)) * parseFloat(item.mrp))
			} else if(item.returned_qty == ''){
				item.balance = 0;
				item.net_amount = parseFloat(item.purchased_quantity) * parseFloat(item.price);
			}
			$scope.calculate_total_amount();
		}
	}
	$scope.calculate_total_amount = function(){
		$scope.sales_return.grant_total = 0;
		$scope.sales_return.return_balance = 0;
		$scope.sales_return.total_tax = 0;
		for(var i = 0; i < $scope.sales_return.items.length; i++){
			$scope.sales_return.grant_total = parseFloat($scope.sales_return.grant_total) + parseFloat($scope.sales_return.items[i].net_amount);
			$scope.sales_return.return_balance = parseFloat($scope.sales_return.return_balance) + parseFloat($scope.sales_return.items[i].balance);
			$scope.sales_return.total_tax = parseFloat($scope.sales_return.total_tax) + parseFloat($scope.sales_return.items[i].tax_on_return);
		}
		if($scope.sales_return.discount.length != 0 && Number($scope.sales_return.discount)){
			$scope.sales_return.grant_total = parseFloat($scope.sales_return.grant_total) - parseFloat($scope.sales_return.discount)
		}
	}
	$scope.validate_sales_return = function(){
		$scope.validate_sales_return_msg = "";
		console.log($scope.sales_return.sales_invoice);
		if ($scope.sales_return.sales_invoice == '') {
			$scope.validate_sales_return_msg = 'Please enter the Sales Invoice No';
			return false;
		} else if ($scope.sales_return.return_invoice == '') {
			$scope.validate_sales_return_msg = 'Please enter the Return Invoice No';
			return false;
		} else if ($scope.sales_return.return_invoice_date == '') {
			$scope.validate_sales_return_msg = 'Please enter the Return Invoice Date';
			return false;
		}
		for(var i = 0; i < $scope.sales_return.items.length; i++){
			console.log($scope.sales_return.items[i].returned_qty);
			/*if($scope.sales_return.items[i].returned_qty == '' || $scope.sales_return.items[i].returned_qty === '0'){
				$scope.validate_sales_return_msg = 'Please enter the quantity to be returned in row ' + (i+1);
				return false;
			} else*/ if($scope.sales_return.items[i].returned_qty && !Number($scope.sales_return.items[i].returned_qty)){
				$scope.validate_sales_return_msg = 'Please enter a valid quantity in row ' + (i+1);
				return false;
			} else if($scope.sales_return.items[i].returned_qty > ($scope.sales_return.items[i].purchased_quantity - $scope.sales_return.items[i].return_history)){
				$scope.validate_sales_return_msg = "Return Quantity exceeds Purchased Quantity in row " + (i+1);
				return false;
			}
		} return true;
		//console.log($scope.sales_return);
	}
	$scope.save_sales_return = function(){
		$scope.sales_return.return_invoice_date = $('#invoice_date').val();
		if($scope.validate_sales_return()){
			console.log($scope.sales_return);
			params = {
				'sales_return': angular.toJson($scope.sales_return),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			show_loader();
			$http({
				method: 'post',
				url: '/sales/sales_return_entry/',
				data: $.param(params),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				if(data.result == 'ok'){
					hide_sales_popup_divs($scope, $http);
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Sales ';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				} else {
					$scope.validate_sales_return_msg = data.message;
				}

			}).error(function(data, status){
				console.log('Request failed' || data);
			})
		}
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/sales/sales_return_entry/';
	}
}
function EstimateController($scope, $http){
	$scope.current_estimate_item = [];
	$scope.choosed_item = [];
	$scope.product_name = '';
	$scope.no_customer_msg = "";
	$scope.select_all_price_type = false;
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.estimate = {
			'estimate_no': '',
			'estimate_date': '',
			'discount': 0,
			// 'payment_mode': 'cash',
			'customer': '',
			'salesman': '',
			'grant_total': 0,
			'tax_exclusive_total': 0,
			'do_no': '',
			'items': [
				{
					'id': '',
		            'name': '',
		            'code': '',
		            'batch_name': '',
		            'batch_id': '',
		            'stock': '',
		            'stock_unit': '',
		            'selling_units':[],
		            'uom': '',
		            'quantity': '',
		            'net_amount': '',
		            'tax_exclusive_amount': '',
		            'mrp': '',
		            'current_item_price': '',
		            'selling_unit': '',
		            'purchase_unit': '',
		            'relation': '',
		            'price_type': false,
		            'tax': '',
		        },
			],
			'quantity_choosed': '',
			// 'bank_name': '',
			// 'branch': '',
			// 'cheque_no': '',
			// 'card_no': '',
			// 'card_holder_name': '',
			// 'cheque_date': '',
			'bill_type': 'NonTaxable',
		}
		console.log($scope.estimate);
	}
	$scope.add_new_estimate_item = function(){
		$scope.estimate.items.push({
			'id': '',
			'name': '',
            'code': '',
            'batch_name': '',
            'batch_id': '',
            'stock': '',
            'stock_unit': '',
            'selling_units':[],
            'uom': '',
            'quantity': '',
            'net_amount': '',
            'tax_exclusive_amount': '',
            'mrp': '',
            'current_item_price': '',
            'selling_unit': '',
            'purchase_unit': '',
            'relation': '',
            'whole_sale_price': '',
			'retail_price': '',
			'price_type': $scope.select_all_price_type,
			'tax': '',
		});
		$scope.selling_units = {
			'unit': '',
		}
	}
	$scope.search_items = function(item){
		$scope.current_estimate_item = item;
		$scope.item_name = item.name;
		$scope.current_estimate_item.code = "";
		$scope.current_estimate_item.id = "";
		get_item_search_list($scope, $http);
	}
	$scope.get_item_details = function(item){
		$scope.current_estimate_item.name = item.name;
		$scope.current_estimate_item.id = item.id;
		$scope.current_estimate_item.code = item.code;
		$scope.items = "";
	}
	$scope.search_salesman = function(){
		if($scope.salesman_name.length == 0){
			$scope.salesmen = "";
			$scope.no_salesman_message = "";
		}
		else{
			$scope.estimate.salesman = "";
			search_salesmen($scope,$http);
		}	
	}
	$scope.select_salesman = function(salesman){
		$scope.salesman_name = salesman.name;
		$scope.estimate.salesman = salesman.id;
		$scope.salesmen = "";
		$scope.select_salesman_flag = false;
	}
	$scope.search_batch = function(item){
		if(item.id != ''){
			$scope.no_batch_msg = "";
			$scope.current_estimate_item = item;
			$scope.batch_name = item.batch_name;
			$scope.item = item.id;
			get_batch_items_list($scope, $http);

		} else
			$scope.no_batch_msg = "Please choose an item";
	}
	$scope.new_salesman = function(estimate) {
		$scope.current_estimate = estimate;
		$scope.salesman = {
			'first_name': '',
			'last_name': '',
			'address': '',
			'contact_no': '',
			'email': '',
		}
	    hide_estimate_popup_divs();
	    $('#add_salesman').css('display', 'block');
	    create_popup();
	}
	$scope.save_salesman = function() {
		save_salesman($scope, $http, 'sales');
	}
	$scope.hide_popup = function() {
        $scope.salesman = {
            'name': '',
            'address': '',
            'mobile': '',
            'telephone_number': '',
            'email': '',
        }
        $scope.validate_salesman_error_msg = "";
        $('#dialogue_popup_container').css('display', 'none');
        $('#popup_overlay').css('display', 'none');
    }
	$scope.select_batch = function(batch){
		$scope.current_estimate_item.batch_name = batch.batch_name;
		$scope.current_estimate_item.batch_id = batch.batch_id;
		$scope.batch_items_list = "";
		if ($scope.current_estimate_item.id) {
			$scope.get_batch($scope.current_estimate_item);
		}
		$scope.current_estimate_item.batches = "";
	}
	$scope.change_bill_type = function(bill_type){
		console.log(bill_type);
		for(var i = 0; i < $scope.estimate.items.length; i++){
			if($scope.estimate.items[i].uom != '' && $scope.estimate.items[i].quantity.length > 0){
				$scope.estimate.items[i].net_amount = parseFloat( $scope.estimate.items[i].quantity) * parseFloat($scope.estimate.items[i].current_item_price);
				$scope.estimate.items[i].tax_exclusive_amount = $scope.estimate.items[i].net_amount;
				if(bill_type == 'Taxable')
					$scope.estimate.items[i].net_amount = parseFloat($scope.estimate.items[i].net_amount) + (parseFloat($scope.estimate.items[i].net_amount) * parseFloat($scope.estimate.items[i].tax/100))	
			}
		}
		$scope.calculate_total_amount();
	}
	$scope.change_price_type = function(){
		for(var i = 0; i < $scope.estimate.items.length; i++){
			if($scope.select_all_price_type == true){
				$scope.estimate.items[i].price_type = false;
				$scope.estimate.items[i].mrp = $scope.estimate.items[i].retail_price;
			}
			else{
				$scope.estimate.items[i].price_type = true;
				$scope.estimate.items[i].mrp = $scope.estimate.items[i].whole_sale_price;
			}
			if($scope.estimate.items[i].uom == $scope.estimate.items[i].stock_unit){
				$scope.estimate.items[i].current_item_price = $scope.estimate.items[i].mrp
			} else if($scope.estimate.items[i].uom == $scope.estimate.items[i].purchase_unit){
				$scope.estimate.items[i].current_item_price = parseFloat($scope.estimate.items[i].mrp) * parseFloat($scope.estimate.items[i].relation);
			}
			if($scope.estimate.items[i].quantity != '' && Number($scope.estimate.items[i].quantity) && $scope.estimate.items[i].uom != ""){
				$scope.estimate.items[i].net_amount = parseFloat( $scope.estimate.items[i].quantity) * parseFloat($scope.estimate.items[i].current_item_price);
				$scope.estimate.items[i].tax_exclusive_amount = $scope.estimate.items[i].net_amount
				if($scope.estimate.bill_type == 'Invoice')
					$scope.estimate.items[i].net_amount = parseFloat($scope.estimate.items[i].net_amount) + (parseFloat($scope.estimate.items[i].net_amount) * parseFloat($scope.estimate.items[i].tax/100))
			}
			else if($scope.estimate.items[i].quantity.length == 0){
				$scope.estimate.items[i].net_amount = "";
				$scope.estimate.items[i].tax_exclusive_amount = "";
			}
		}
		$scope.calculate_total_amount();
	}
	$scope.get_batch = function(item){
		$http.get('/inventory/batch_item_details/?batch_id='+item.batch_id+'&item_id='+item.id).success(function(data){
        	item.stock = data.quantity;
        	item.stock_unit = data.stock_unit;
        	item.selling_units = [];
        	item.selling_units.push({
        		'unit': data.selling_unit,
        	})
        	item.selling_units.push({
        		'unit': data.purchase_unit,
        	})
        	item.selling_unit = data.selling_unit;
        	item.purchase_unit = data.purchase_unit;
        	item.relation = data.relation;
        	item.whole_sale_price = data.whole_sale_price_sales;
        	item.retail_price = data.retail_price_sales;
        	item.tax = data.tax;
        	item.offer_quantity = data.offer_quantity;
        	if(item.price_type == false)
        		item.mrp = data.retail_price_sales;
        	if(item.price_type == true)
        		item.mrp = data.whole_sale_price_sales;
	    }).error(function(data, status) {
	    	console.log('Request failed' || data);
	    });
	}
	$scope.calculate_quantity_from_uom = function(item){
		$scope.validate_sales_msg = "";
	    if(item.price_type == false)
    		item.mrp = item.retail_price
    	if(item.price_type == true)
    		item.mrp = item.whole_sale_price
		if(item.uom == item.stock_unit){
			item.current_item_price = item.mrp
			if(item.quantity > item.stock){
				$scope.validate_sales_msg = "Out of Stock";
			}
		} else if(item.uom == item.purchase_unit){
			item.current_item_price = parseFloat(item.mrp) * parseFloat(item.relation);
			if(item.quantity*item.relation > item.stock){
				$scope.validate_sales_msg = "Out of Stock";
			}
		}
		if(item.quantity != '' && Number(item.quantity) && item.uom != ""){
			item.net_amount = parseFloat(item.quantity) * parseFloat(item.current_item_price);
			item.tax_exclusive_amount = item.net_amount;
			if($scope.estimate.bill_type == 'Taxable')
				item.net_amount = parseFloat(item.net_amount) + (parseFloat(item.net_amount) * parseFloat(item.tax/100))
		}
		else if(item.quantity.length == 0)
			item.net_amount = "";
		$scope.calculate_total_amount();
	}
	$scope.calculate_total_amount = function(){
		$scope.estimate.grant_total = 0;
		$scope.estimate.tax_exclusive_total = 0;
		for(var i = 0; i < $scope.estimate.items.length; i++){
			if(Number($scope.estimate.items[i].net_amount)){
				$scope.estimate.grant_total = parseFloat($scope.estimate.grant_total) + parseFloat($scope.estimate.items[i].net_amount);
				$scope.estimate.tax_exclusive_total = parseFloat($scope.estimate.tax_exclusive_total) + parseFloat($scope.estimate.items[i].tax_exclusive_amount);
			}
		}
		if($scope.estimate.discount.length != 0 && Number($scope.estimate.discount)){
			$scope.estimate.grant_total = parseFloat($scope.estimate.grant_total) - parseFloat($scope.estimate.discount)
			$scope.estimate.tax_exclusive_total = parseFloat($scope.estimate.tax_exclusive_total) - parseFloat($scope.estimate.discount)
		}
	}
	$scope.search_customer = function(){
		if($scope.customer_name.length == 0){
			$scope.customers = "";
			$scope.no_customer_msg = "";
		}
		else{
			$scope.estimate.customer = "";
			get_customer_search_list($scope, $http);
		}		
	}
	$scope.select_customer = function(customer){
		$scope.customer_name = customer.name;
		$scope.estimate.customer = customer.id;
		$scope.customers = "";
	}
	// $scope.payment_mode_details = function(payment_mode) {
	// 	hide_estimate_popup_divs();
	// 	$('#payment_details').css('display', 'block');
	// 	create_popup();
	// 	if (payment_mode == 'cheque') {
	// 		$scope.is_cheque_payment = true;
	// 	} else if (payment_mode == 'card') {
	// 		$scope.is_cheque_payment = false;
	// 	} else {
	// 		hide_estimate_popup_divs();
	// 	}
	// }
	$scope.validate_sales = function(){
		$scope.validate_sales_msg = "";
		if($scope.estimate.do_no == ""){
			$scope.validate_estimate_msg = "Please enter the DO No";
			return false;
		} else if($scope.salesman_name == '' || $scope.estimate.salesman == ''){
			$scope.validate_estimate_msg = "Please select a salesman from the list";
			return false;
		} else if($scope.no_customer_msg != ""){
			$scope.validate_estimate_msg = "Please select a valid customer or leave the field empty";
			return false;
		} else if (($scope.estimate.payment_mode == 'card' || $scope.estimate.payment_mode == 'cheque' ) && ($scope.estimate.bank_name == '' || $scope.estimate.bank_name == undefined)) {
			$scope.validate_estimate_msg = 'Please enter bank name';
			return false;
		} else if (($scope.estimate.payment_mode == 'card') && ($scope.estimate.card_no == '' || $scope.estimate.card_no == undefined)) {
			$scope.validate_estimate_msg = 'Please enter Card No';
			return false;
		} else if (($scope.estimate.payment_mode == 'card') && ($scope.estimate.card_holder_name == '' || $scope.estimate.card_holder_name == undefined)) {
			$scope.validate_estimate_msg = 'Please enter Card Holder Name';
			return false;
		} else if (($scope.estimate.payment_mode == 'cheque') && ($scope.estimate.branch == '' || $scope.estimate.branch == undefined)) {
			$scope.validate_estimate_msg = 'Please enter Branch';
			return false;
		} else if (($scope.estimate.payment_mode == 'cheque') && $scope.estimate.cheque_date == '') {
			$scope.validate_estimate_msg = 'Please choose Cheque Date';
			return false;
		} else if (($scope.estimate.payment_mode == 'cheque') && ($scope.estimate.cheque_no == '' || $scope.sales.cheque_no == undefined)) {
			$scope.validate_estimate_msg = 'Please choose Cheque Number';
			return false;
		} for(var i = 0; i < $scope.estimate.items.length; i++){
			if ($scope.estimate.items[i].code == '') {
				$scope.validate_estimate_msg = 'Item code cannot be null in row' + (i+1);
				return false;
			} else if ($scope.estimate.items[i].name == '') {
				$scope.validate_estimate_msg = 'Item name cannot be null in row' + (i+1);
				return false;
			} else if ($scope.estimate.items[i].batch_id == '') {
				$scope.validate_estimate_msg = 'Please choose batch for the item in row '+ (i+1);
				return false;
			} else if ($scope.estimate.items[i].uom == '') {
				$scope.validate_estimate_msg = 'Please choose the unit of measurement in row '+ (i+1);
				return false;
			} else if ($scope.estimate.items[i].quantity == '') {
				$scope.validate_estimate_msg = 'Please enter the quantity in row '+ (i+1);
				return false;
			} 
			if($scope.estimate.items[i].uom == $scope.estimate.items[i].stock_unit){
				if($scope.estimate.items[i].quantity > $scope.estimate.items[i].stock){
					$scope.validate_estimate_msg = "Out of Stock quantity in row " + (i+1);
					return false;
				}
			} else if($scope.estimate.items[i].uom == $scope.estimate.items[i].purchase_unit){
				if($scope.estimate.items[i].quantity*$scope.estimate.items[i].relation > $scope.estimate.items[i].stock){
					$scope.validate_estimate_msg = "Out of Stock in row " + (i+1);
					return false;
				}
			}
		} return true;
	}
	$scope.save_estimate = function(){
		if($scope.validate_sales()){
			$scope.estimate.estimate_date = $('#estimate_date').val();
			console.log($scope.estimate);
			for(var i = 0; i < $scope.estimate.items.length; i++){
				if($scope.estimate.items[i].price_type == true)
					$scope.estimate.items[i].price_type = "true"
				else
					$scope.estimate.items[i].price_type = "false"
			}	
			params = {
				'estimate_details': angular.toJson($scope.estimate),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			show_loader();
			$http({
				method: 'post',
				url: '/sales/estimate_entry/',
				data: $.param(params),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				if(data.result == 'ok'){
					hide_estimate_popup_divs($scope, $http);
					document.location.href = '/sales/estimate_pdf/'+data.id+'/';
				} else {
					$scope.validate_estimate_msg = data.message;
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			})
		}
	}
	
	$scope.remove_item = function(item) {
		var index = $scope.estimate.items.indexOf(item);
		$scope.estimate.items.splice(index, 1);
		$scope.calculate_total_amount();
	}
	$scope.hide_popup_payment_details = function(){
		$scope.estimate.bank_name = $scope.bank_name;
		$scope.estimate.branch = $scope.branch;
		$scope.estimate.cheque_no = $scope.cheque_no;
		$scope.estimate.card_no = $scope.card_no;
		$scope.estimate.card_holder_name = $scope.card_holder_name;
		$scope.estimate.cheque_date = document.getElementById("cheque_date").value;
		hide_estimate_popup_divs();
	}
}
function EstimateViewController($scope, $http) {
	$scope.estimate_no = '';
	$scope.estimate = {
			'estimate_no': '',
			'estimate_date': '',
			'discount': 0,
			'customer': '',
			'salesman': '',
			'grant_total': 0,
			'tax_exclusive_total': 0,
			'do_no': '',
			'items': [
				{
					'id': '',
		            'name': '',
		            'code': '',
		            'batch_name': '',
		            'batch_id': '',
		            'stock': '',
		            'stock_unit': '',
		            'selling_units':[],
		            'uom': '',
		            'quantity': '',
		            'net_amount': '',
		            'tax_exclusive_amount': '',
		            'mrp': '',
		            'current_item_price': '',
		            'selling_unit': '',
		            'purchase_unit': '',
		            'relation': '',
		            'price_type': false,
		            'tax': '',
		        },
			],
			'quantity_choosed': '',
			'bill_type': 'NonTaxable',
		}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.get_estimate_details = function() {
		$http.get('/sales/estimate_view/?estimate_no='+$scope.estimate_no).success(function(data) {
			$scope.estimate_error_message = '';
			if (data.result == 'ok') {
				$scope.estimate = data.estimate;
			} else {
				$scope.estimate_error_message = data.message;
				$scope.estimate = data.estimate;
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		});
	}
}

function SalesViewController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.ref_no = '';
		$scope.sales_view = {
			'do_no': '',
			'sales_invoice': '',
			'invoice_date': '',
			'salesman': '',
			'customer': '',
			'bill_type': '',
			'payment_mode': '',
	        'bank_name': '',
            'cheque_date': '',
            'cheque_number': '',
            'branch': '',
            'card_number': '',
            'card_holder_name': '',
			'items': {
				'name': '',
				'code': '',
				'batch': '',
				'item_quantity': '',
				'mrp': '',
				'tax': '',
				'net_amount': '',
			},
			'discount': '',
			'grant_total': '',
		}
	}
	$scope.get_sales_details = function(){
		if($scope.ref_no != ''){
			$http.get('/sales/sales_view/?ref_no='+$scope.ref_no).success(function(data) {
				if (data.result == 'ok') {
					$scope.sales_view = data.sales_view;
					$scope.sales_error_message = '';
				} else{
					$scope.sales_error_message = "No sales found";
					$scope.sales_view = '';
				}					
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		} else{
			$scope.sales_view = "";
		}
	}
	$scope.show_payment_details = function(){
		if ($scope.sales_view.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();
		$scope.bank_name = $scope.sales_view.bank_name;
		$scope.cheque_date = $scope.sales_view.cheque_date;
		$scope.cheque_no = $scope.sales_view.cheque_number;
		$scope.branch = $scope.sales_view.branch;
		$scope.card_no = $scope.sales_view.card_number;
		$scope.card_holder_name = $scope.sales_view.card_holder_name;
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.change_discount = function() {
		$scope.edit_discount = true;
		$scope.sales_view.new_discount = $scope.sales_view.discount;
	}
	$scope.save_sales = function() {
		balance = (parseFloat($scope.sales_view.grant_total) + parseFloat($scope.sales_view.roundoff)) - (parseFloat($scope.sales_view.discount) + parseFloat($scope.sales_view.round_off));
		if ($scope.sales_view.round_off != Number($scope.sales_view.round_off)) {
			$scope.sales_view.round_off = 0;
		}
		if (balance <= 0) {
			$scope.validate_sales_msg = 'Please check the New Discount with the Grant Total';
		} else {
			params = {
				'csrfmiddlewaretoken': $scope.csrf_token,
				'sales_id': $scope.sales_view.id,
				'round_off': $scope.sales_view.round_off,
			}
			$http({
				method: 'post',
				data: $.param(params),
				url: '/sales/change_sales_discount/',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				document.location.href = '/sales/sales_view/';
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}

}

function SalesReturnViewController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.ref_no = '';
		$scope.sales_view = {
			'do_no': '',
			'sales_invoice': '',
			'invoice_date': '',
			'salesman': '',
			'customer': '',
			'bill_type': '',
			'payment_mode': '',
	        'bank_name': '',
            'cheque_date': '',
            'cheque_number': '',
            'branch': '',
            'card_number': '',
            'card_holder_name': '',
			'items': {
				'name': '',
				'code': '',
				'batch': '',
				'item_quantity': '',
				'mrp': '',
				'tax': '',
				'net_amount': '',
			},
			'discount': '',
			'grant_total': '',
		}
	}
	$scope.get_sales_details = function(){
		if($scope.ref_no != ''){
			$http.get('/sales/sales_return_view/?ref_no='+$scope.ref_no).success(function(data) {
				if (data.result == 'ok') {
					$scope.sales_view = data.sales_view;
					$scope.sales_error_message = '';
					if($scope.sales_view.length == 0){
						$scope.sales_error_message = "No sales found";
						$scope.sales_view = '';
					} 
				}		
				else{
					$scope.sales_error_message = "No sales found";
					$scope.sales_view = '';
				}			
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		} else{
			$scope.sales_view = "";
		}
	}
	$scope.show_payment_details = function(){
		if ($scope.sales_view.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();
		$scope.bank_name = $scope.sales_view.bank_name;
		$scope.cheque_date = $scope.sales_view.cheque_date;
		$scope.cheque_no = $scope.sales_view.cheque_number;
		$scope.branch = $scope.sales_view.branch;
		$scope.card_no = $scope.sales_view.card_number;
		$scope.card_holder_name = $scope.sales_view.card_holder_name;
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.change_discount = function() {
		$scope.edit_discount = true;
		$scope.sales_view.new_discount = $scope.sales_view.discount;
	}
	$scope.save_sales = function() {
		balance = (parseFloat($scope.sales_view.grant_total) + parseFloat($scope.sales_view.roundoff)) - (parseFloat($scope.sales_view.discount) + parseFloat($scope.sales_view.round_off));
		if ($scope.sales_view.round_off != Number($scope.sales_view.round_off)) {
			$scope.sales_view.round_off = 0;
		}
		if (balance <= 0) {
			$scope.validate_sales_msg = 'Please check the New Discount with the Grant Total';
		} else {
			params = {
				'csrfmiddlewaretoken': $scope.csrf_token,
				'sales_id': $scope.sales_view.id,
				'round_off': $scope.sales_view.round_off,
			}
			$http({
				method: 'post',
				data: $.param(params),
				url: '/sales/change_sales_discount/',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				document.location.href = '/sales/sales_return_view/';
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}

}