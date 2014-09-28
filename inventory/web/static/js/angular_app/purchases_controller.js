function hide_purchase_popup_divs() {
	$('#payment_details').css('display', 'none');
	$('#cost_price_calculator').css('display', 'none');
	$('#new_batch').css('display', 'none');
	$('#add_item').css('display', 'none');
	$('#add_supplier').css('display', 'none');
	$('#transaction_reference_no_details').css('display', 'none');
	$('#bank_account_details').css('display', 'none');
	$('#cost_price_warning_message').css('display', 'none');
}
		
function get_bank_account_details($scope, $http) {
	$http.get('/accounting/bank_accounts/').success(function(data){
		$scope.bank_accounts = data.bank_accounts;
	}).error(function(data, status) {
		console.log('Request failed' || data);
	});
}

function create_new_bank_acount($scope, $http, from) {
	params = {
		'bank_account': $scope.bank_account_name,
		'csrfmiddlewaretoken': $scope.csrf_token,
	}
	$http({
		method: 'post',
		url: '/accounting/bank_accounts/',
		data: $.param(params),
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
	}).success(function(data) {
		if (data.result == 'ok') {
			if (from == 'purchase') {
				$scope.purchase.bank_account_ledger = data.bank_account.id;
				$scope.payment_mode_details($scope.purchase.payment_mode);
				$scope.bank_account_error = '';
			} else if (from == 'sales'){
				$scope.sales.bank_account_ledger = data.bank_account.id;
				$scope.payment_mode_details($scope.sales.payment_mode);
				$scope.bank_account_error = '';
			} 
		} else {
			$scope.bank_account_error = data.message;
		}
	}).error(function(data, status){
		console.log('Request failed' || data);
	});
}
function PurchaseController($scope, $http) {
	$scope.current_purchase_item = [];
	$scope.choosed_item = [];
	$scope.product_name = '';
	$scope.select_supplier_flag = false;
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;			
		$scope.purchase = {
			'invoice_no': '',
			'invoice_date': '',
			'discount': 0,
			'payment_mode': 'cash',
			'supplier': '',
			'bank_name': '',
			'branch': '',
			'cheque_no': '',
			'cheque_date': '',
			'card_no': '',
			'grant_total': 0,
			'do_no': '',
			'items': [
				{
					'id': '',
		            'name': '',
		            'code': '',
		            'batch': '',
		            'stock': '',
		            'uom': '',
		            'quantity': '',
		            'purchase_price': 0,
		            'cost_price': 0.00,
		            'net_amount': '',
		            'profit': '',
		            'whole_sale_price': 0,
					'retail_price': 0,
					'whole_sale_profit': 0.00,
					'retail_profit': 0.00,
		        },
			],
			'card_holder_name': '',
			'quantity_choosed': '',
			'purchase_tax': 0,
			'bank_account_ledger': '',
		}
		get_conversions($scope, $http);
	}
	$scope.search_batch = function(item) {
		$scope.current_purchase_item = item;
		$scope.batch_name = item.batch_name;
		get_batch_search_details($scope, $http, 'purchase');
	}
	$scope.select_batch = function(batch) {
		$scope.batch_selected = true;
		$scope.current_purchase_item.batch_name = batch.name;
		$scope.current_purchase_item.batch = batch.id;
		if ($scope.current_purchase_item.id) {
			$scope.get_batch($scope.current_purchase_item);
		} 
		$scope.calculate_profit($scope.current_purchase_item);
		$scope.current_purchase_item.batches = [];
		$scope.current_purchase_item.batch_search = false;
	}
	$scope.search_items = function(item) {
		// $scope.batch_selected = false;
		$scope.current_purchase_item.items = [];
		$scope.current_purchase_item = item;
		get_item_search_list($scope, $http, $scope.current_purchase_item.name, item.batch, 'purchase');
	}

	$scope.get_items = function() {
		get_item_search_list($scope, $http, $scope.item_name);
	}
	$scope.select_item_details = function(item) {
		$scope.current_purchase_item.name = item.name;
		$scope.current_purchase_item.code = item.code;
		$scope.current_purchase_item.id = item.id;
		$scope.current_purchase_item.items = [];
		if ($scope.current_purchase_item.batch) {
			$scope.select_batch($scope.current_purchase_item.batch);
		}
		hide_popup();
		$scope.calculate_profit($scope.current_purchase_item);
		$scope.current_purchase_item.item_search = false;
	}
	$scope.add_new_purchase_item = function() {
		$scope.purchase.items.push(
		{
			'id': '',
            'name': '',
            'code': '',
            'batch': '',
            'stock': '',
            'uom': '',
            'quantity': '',
            'purchase_price': 0,
            'cost_price': 0.00,
            'net_amount': '',
            'conversions': [],
            'whole_sale_price': 0,
			'retail_price': 0,
			'whole_sale_profit': 0.00,
			'retail_profit': 0.00,
        });
	}
	$scope.get_batch = function(item){
		$http.get('/inventory/batch_item_details/?batch_id='+item.batch+'&item_id='+item.id).success(function(data){
        	item.stock = data.stock;
        	item.purchase_unit = data.purchase_unit;
        	item.conversion_unit_name = data.conversion_unit_name;
        	item.conversion_unit = data.conversion_unit;
        	if (data.purchase_unit.length > 0) {
        		$scope.current_purchase_item.uom_exists = true;
        		item.cost_price  = data.cost_price;
        	} else
        		$scope.current_purchase_item.uom_exists = false;
			item.whole_sale_price  = data.whole_sale_price;
			item.purchase_price = data.purchase_price;
			item.retail_price  = data.retail_price;
			item.quantity = 0;
			$scope.calculate_profit($scope.current_purchase_item);
	    }).error(function(data, status) {
	    	console.log('Request failed' || data);
	    });
	}
	$scope.get_conversion_units = function(item) {
		$scope.current_purchase_item = item;
		get_conversions($scope, $http, item.purchase_unit, 'purchase_unit');
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.calculate_total_purchase_amount = function() {
		var total_amount = 0.00;
		for (var i=0; i< $scope.purchase.items.length; i++) {
			if ($scope.purchase.items[i].purchase_price != Number($scope.purchase.items[i].purchase_price)) {
				$scope.purchase.items[i].purchase_price = 0.00;
			} 
			if ($scope.purchase.items[i].quantity != Number($scope.purchase.items[i].quantity)) {
				$scope.purchase.items[i].quantity = 0.00;
			} 
			$scope.purchase.items[i].net_amount = $scope.purchase.items[i].quantity*$scope.purchase.items[i].purchase_price;
			total_amount = total_amount+$scope.purchase.items[i].net_amount;
		}
		if ($scope.purchase.discount != Number($scope.purchase.discount))
			$scope.purchase.discount = 0;
		$scope.purchase.grant_total = parseFloat(total_amount) - parseFloat($scope.purchase.discount);
	}
	$scope.calculate_net_amount = function(item) {
		if (item.purchase_price != Number(item.purchase_price)) {
			item.purchase_price = 0.00;
		} 
		if (item.quantity != Number(item.quantity)) {
			item.quantity = 0.00;
		} 
		item.net_amount = item.quantity*item.purchase_price;
		$scope.calculate_profit(item);
		$scope.calculate_total_purchase_amount();
	}
	$scope.send_request_for_save_purchase = function() {
		for(var i=0; i < $scope.purchase.items.length; i++) {
			if ($scope.purchase.items[i].batch_search == false) {
				$scope.purchase.items[i].batch_search = "false";
			} else {
				$scope.purchase.items[i].batch_search = "true";
			}
			if ($scope.purchase.items[i].item_search == false) {
				$scope.purchase.items[i].item_search = "false";
			} else {
				$scope.purchase.items[i].item_search = "true";
			}
			if ($scope.purchase.items[i].uom_exists == false) {
				$scope.purchase.items[i].uom_exists = "false";
			} else {
				$scope.purchase.items[i].uom_exists = "true";
			}
		}
		params = {
			'purchase_details': angular.toJson($scope.purchase),
			'csrfmiddlewaretoken': $scope.csrf_token,
		}
		show_loader();
		$http({
			method: 'post',
			url: '/purchases/purchase_entry/',
			data: $.param(params),
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		}).success(function(data){
			hide_loader();
			if (data.result == 'ok') {
				hide_purchase_popup_divs()
				$scope.transaction_reference_no = data.transaction_reference_no;
				$scope.transaction_name = ' Purchase ';
				$('#transaction_reference_no_details').css('display', 'block');
				create_popup();
			} else {
				$scope.validate_purchase_msg = data.message;
				for(var i=0; i < $scope.purchase.items.length; i++) {
					if ($scope.purchase.items[i].batch_search == "false") {
						$scope.purchase.items[i].batch_search = false;
					} else {
						$scope.purchase.items[i].batch_search = true;
					}
					if ($scope.purchase.items[i].item_search == "false") {
						$scope.purchase.items[i].item_search = false;
					} else {
						$scope.purchase.items[i].item_search = true;
					}
					if ($scope.purchase.items[i].uom_exists == "false") {
						$scope.purchase.items[i].uom_exists = false;
					} else {
						$scope.purchase.items[i].uom_exists = true;
					}
				}
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		})
	}
	$scope.save_purchase_without_cost_price = function() {
		hide_popup();
		$scope.send_request_for_save_purchase();
	}
	$scope.save_purchase = function() {
		$scope.purchase.invoice_date = $('#invoice_date').val();
		$scope.purchase.cheque_date = $('#cheque_date').val();
		if ($scope.validate_purchase()) {
			cost_price_enterd = false;
			for(var i=0; i < $scope.purchase.items.length; i++) {
				if ($scope.purchase.items[i].cost_price != 0) {
					cost_price_enterd = true;
				}
			}
			if (cost_price_enterd == true) {
				$scope.send_request_for_save_purchase();
			} else {
				hide_purchase_popup_divs();
				$('#cost_price_warning_message').css('display', 'block');
				create_popup();
			}
		}
	}
	$scope.payment_mode_details = function(payment_mode) {
		$scope.bank_name = '';
		$scope.branch = '';
		$scope.cheque_no = '';
		$scope.card_no = '';
		$scope.card_holder_name = '';
		hide_purchase_popup_divs();
		$('#payment_details').css('display', 'block');
		create_popup();
		if (payment_mode == 'cheque') {
			$scope.is_cheque_payment = true;
		} else if (payment_mode == 'card') {
			$scope.is_cheque_payment = false;
		} else {
			hide_purchase_popup_divs();
		}
	}
	$scope.bank_account_details = function(payment_mode) {

		get_bank_account_details($scope, $http);
		$scope.purchase.payment_mode = payment_mode;
		hide_purchase_popup_divs();
		$('#bank_account_details').css('display', 'block');
		$scope.other_bank_account = false;
		$scope.bank_account_error = '';
		$scope.bank_account = '';
		$scope.bank_account_name = '';
		if ($scope.purchase.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();

	}
	$scope.create_new_bank_acount = function() {
		if ($scope.bank_account_name == '' || $scope.bank_account_name == undefined) {
			$scope.bank_account_error = 'Please enter the Bank account name';
		} else {
			create_new_bank_acount($scope, $http, 'purchase');
		}
	}
	$scope.add_bank_account_details = function() {
		$scope.purchase.bank_account_ledger = $scope.bank_account;
		$scope.payment_mode_details($scope.purchase.payment_mode);
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/purchases/purchase_entry/';
	}
	$scope.hide_popup_payment_details = function() {
		$scope.purchase.bank_name = $scope.bank_name;
		$scope.purchase.branch = $scope.branch;
		$scope.purchase.cheque_no = $scope.cheque_no;
		$scope.purchase.card_no = $scope.card_no;
		$scope.purchase.card_holder_name = $scope.card_holder_name;
		hide_popup();
	}
	$scope.cost_price_calculator = function(item) {
		$scope.choosed_item = item;
		hide_purchase_popup_divs();
		$('#cost_price_calculator').css('display', 'block');
		create_popup();
	}
	$scope.save_quantity = function(item) {
		item.quantity_entered = item.quantity;
		$scope.calculate_net_amount(item);
	}
	$scope.calculate_unit_transportation_charge = function() {
		$scope.unit_transportation_charge = 0
		if ($scope.choosed_item.quantity != Number($scope.choosed_item.quantity)) {
			$scope.choosed_item.quantity = 0;
		}
		if ($scope.total_transportation_charge != Number($scope.total_transportation_charge)) {
			$scope.total_transportation_charge = 0;
		}
		if ($scope.choosed_item.quantity == 0) {
			$scope.unit_transportation_charge = 0
		} else {
			$scope.unit_transportation_charge =  parseFloat($scope.total_transportation_charge)/parseFloat($scope.choosed_item.quantity);
		}
		$scope.calculate_costprice();
	}
	$scope.calculate_unit_handling_charge = function() {
		if ($scope.choosed_item.quantity != Number($scope.choosed_item.quantity)) {
			$scope.choosed_item.quantity = 0;
		}
		if ($scope.total_handling_charge != Number($scope.total_handling_charge)) {
			$scope.total_handling_charge = 0;
		}
		if ($scope.choosed_item.quantity == 0) {
			$scope.unit_handling_charge = 0
		} else {
			$scope.unit_handling_charge =  parseFloat($scope.total_handling_charge)/parseFloat($scope.choosed_item.quantity);
		}
		$scope.calculate_costprice();
	}
	$scope.calculate_unit_expense_charge = function() {
		if ($scope.choosed_item.quantity != Number($scope.choosed_item.quantity)) {
			$scope.choosed_item.quantity = 0;
		}
		if ($scope.total_expense_charge != Number($scope.total_expense_charge)) {
			$scope.total_expense_charge = 0;
		}
		if ($scope.choosed_item.quantity == 0) {
			$scope.unit_expense_charge = 0
		} else {
			$scope.unit_expense_charge =  parseFloat($scope.total_expense_charge)/parseFloat($scope.choosed_item.quantity);
		}
		$scope.calculate_costprice();
	}
	$scope.calculate_costprice = function() {
		if ($scope.unit_expense_charge != Number($scope.unit_expense_charge) || $scope.unit_expense_charge == 0) {
			$scope.unit_expense_charge = 0;
		}
		if ($scope.unit_handling_charge != Number($scope.unit_handling_charge) || $scope.unit_handling_charge.length == 0) {
			$scope.unit_handling_charge = 0;
		}
		if ($scope.unit_transportation_charge != Number($scope.unit_transportation_charge) || $scope.unit_transportation_charge.length == 0) {
			$scope.unit_transportation_charge = 0;
		}
		var cost_price = (parseFloat($scope.unit_transportation_charge) + parseFloat($scope.unit_handling_charge) + parseFloat($scope.unit_expense_charge) + parseFloat($scope.choosed_item.purchase_price)).toFixed(2);
		if (cost_price == Number(cost_price)) {
			$scope.cost_price = cost_price;
		} else {
			$scope.cost_price = 0;
		}
	}
	$scope.close_cost_price_calculator = function() {
		if ($scope.cost_price != Number($scope.cost_price) || $scope.cost_price == undefined || $scope.cost_price.length == 0) {
			$scope.cost_price = 0.00
		}
		$scope.choosed_item.cost_price = $scope.cost_price;
		$scope.unit_handling_charge = '';
		$scope.total_handling_charge = '';
		$scope.unit_expense_charge = '';
		$scope.total_expense_charge = '';
		$scope.unit_transportation_charge = '';
		$scope.total_transportation_charge = '';
		$scope.cost_price = '';
		hide_popup();
		$scope.calculate_profit($scope.choosed_item);
	}
	$scope.calculate_profit = function(item) {
		if (item.whole_sale_price != Number(item.whole_sale_price))
			item.whole_sale_price = 0
		if (item.retail_price != Number(item.retail_price))
			item.retail_price = 0
		if (item.cost_price != Number(item.cost_price))
			item.cost_price = 0
		if (item.purchase_price != Number(item.purchase_price))
			item.purchase_price = 0
		console.log(item.cost_price);
		if (item.cost_price == 0){
			whole_sale_profit = parseFloat(item.whole_sale_price)-(parseFloat(item.purchase_price));
			retail_profit = parseFloat(item.retail_price)-(parseFloat(item.purchase_price));
		} else {
			whole_sale_profit = parseFloat(item.whole_sale_price)-(parseFloat(item.cost_price));
			retail_profit = parseFloat(item.retail_price)-(parseFloat(item.cost_price));
		}
		item.whole_sale_profit = whole_sale_profit;
		item.retail_profit = retail_profit;
	}
	$scope.new_batch = function(item) {
		$scope.batch = {
			'id': '',
			'name': '',
			'created_date':'',
			'expiry_date': '',
		}
		$scope.current_purchase_item = item;
		hide_purchase_popup_divs();
		$('#new_batch').css('display', 'block');
		create_popup();
	}
	$scope.save_batch = function() {
		save_batch($scope, $http, 'purchase');

	}
	$scope.search_supplier = function() {
		$scope.select_supplier_flag = true;
		$scope.purchase.supplier = '';
		get_supplier_search_list($scope, $http);
	}
	$scope.select_supplier = function(supplier) {
		$scope.purchase.supplier = supplier.id;
		$scope.suppliers = [];
		$scope.supplier_name = supplier.name;
		$scope.select_supplier_flag = false;
	}
	$scope.remove_purchase_item = function(item) {
		var index = $scope.purchase.items.indexOf(item);
		$scope.purchase.items.splice(index, 1);
	}
	$scope.validate_purchase = function() {
		if ($scope.purchase.do_no == '' || $scope.purchase.do_no == undefined) {
			$scope.validate_purchase_msg = 'Please enter DO Number';
			return false;
		} else if ($scope.purchase.invoice_no == '' || $scope.purchase.invoice_no == undefined) {
			$scope.validate_purchase_msg = 'Please enter Invoice Number';
			return false;
		} else if ($scope.purchase.invoice_date == '') {
			$scope.validate_purchase_msg = 'Please choose Invoice Date';
			return false;
		} else if ($scope.purchase.supplier == '' || $scope.purchase.supplier == undefined) {
			$scope.validate_purchase_msg = 'Please choose Supplier';
			return false;
		} else if ($scope.purchase.payment_mode == '' || $scope.purchase.payment_mode == undefined) { 
			$scope.validate_purchase_msg = 'Please choose Payment Mode';
			return false;
		} else if (($scope.purchase.payment_mode == 'cheque' || $scope.purchase.payment_mode == 'card') && ($scope.purchase.bank_account_ledger == '' || $scope.purchase.bank_account_ledger == undefined)) {
			$scope.validate_purchase_msg = 'Please choose Bank Account Details';
			$scope.bank_account_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'card' || $scope.purchase.payment_mode == 'cheque' ) && ($scope.purchase.bank_name == '' || $scope.purchase.bank_name == undefined)) {
			$scope.validate_purchase_msg = 'Please enter bank name';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'card') && ($scope.purchase.card_no == '' || $scope.purchase.card_no == undefined)) {
			$scope.validate_purchase_msg = 'Please enter Card No';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'card') && ($scope.purchase.card_holder_name == '' || $scope.purchase.card_holder_name == undefined)) {
			$scope.validate_purchase_msg = 'Please enter Card Holder Name';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'cheque') && ($scope.purchase.branch == '' || $scope.purchase.branch == undefined)) {
			$scope.validate_purchase_msg = 'Please enter Branch';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'cheque') && $scope.purchase.cheque_date == '') {
			$scope.validate_purchase_msg = 'Please choose Cheque Date';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if (($scope.purchase.payment_mode == 'cheque') && ($scope.purchase.cheque_no == '' || $scope.purchase.cheque_no == undefined)) {
			$scope.validate_purchase_msg = 'Please enter Cheque Number';
			$scope.payment_mode_details($scope.purchase.payment_mode);
			return false;
		} else if ($scope.purchase.items.length == 0) {
			$scope.validate_purchase_msg = 'Please choose Items';
			return false;
		} else if ($scope.purchase.purchase_tax != Number($scope.purchase.purchase_tax)) {
			$scope.validate_purchase_msg = 'Please enter valid Purchase Tax';
			return false;
		} else if ($scope.purchase.discount != Number($scope.purchase.discount)) {
			$scope.validate_purchase_msg = 'Please enter valid Discount';
			return false;
		} else if ($scope.purchase.items.length > 0) {
			for (var i =0; i<$scope.purchase.items.length; i++) {
				if ($scope.purchase.items[i].code == '') {
					$scope.validate_purchase_msg = 'Item code cannot be null'+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].batch == '') {
					$scope.validate_purchase_msg = 'Please choose batch for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].purchase_unit == '') {
					$scope.validate_purchase_msg = 'Please enter purchase unit for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].quantity == '' || $scope.purchase.items[i].quantity <= 0) {
					$scope.validate_purchase_msg = 'Please enter quantity for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].purchase_price == '') {
					$scope.validate_purchase_msg = 'Please enter unit purchase price for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].whole_sale_price == '') {
					$scope.validate_purchase_msg = 'Please enter unit whole sale price for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].retail_price == '') {
					$scope.validate_purchase_msg = 'Please enter unit retail price for the item in row '+ (i+1);
					return false;
				} else if (($scope.purchase.items[i].cost_price !=0 ) && ($scope.purchase.items[i].cost_price == '' || $scope.purchase.items[i].cost_price == undefined)) {
					$scope.validate_purchase_msg = 'Please enter unit cost price for the item in row '+ (i+1);
					return false;
				} else if ($scope.purchase.items[i].conversion_unit == '') {
					$scope.validate_purchase_msg = 'Please enter Sales unit conversion for the item in row '+ (i+1);
					return false;
				} 
			}
		} return true;
	} 
	$scope.get_products = function() {
        if($scope.product_name){
		  	get_product_search_list($scope, $http);
        }
	}
	$scope.select_product_details = function(product) {
		$scope.item.product = product.id;
		$scope.product_name = product.name + '-' + product.category_name;
		$scope.products = [];
	}
	$scope.add_new_item = function(item) {
		$scope.current_purchase_item = item;
		$scope.product_name = '';
		$scope.brand_name = '';
		$scope.vat_type = '';
		$scope.item = {
			'id': '',
			'name': '',
			'vat': '',
			'product': '',
			'brand': '',
			'description': '',
			'cess': '',
			'size':'',
			'barcode': '',
			'vat_type': '',
			'offer_quantity': '',
		}
		hide_purchase_popup_divs();
		$('#add_item').css('display', 'block');
		create_popup();
	}
	$scope.save_item = function() {
		save_item($scope, $http, 'purchase');
	}
	$scope.get_brands = function() {
		get_brand_search_list($scope, $http);
	}
	$scope.select_brand_details = function(brand) {
		$scope.item.brand = brand.id;
		$scope.brand_name = brand.name;
		$scope.brands = [];
	}
	$scope.get_vat_list = function() {
		get_vat_search_details($scope, $http);
	}
	$scope.select_vat_details = function(vat) {
		$scope.item.vat = vat.id;
		$scope.vat_type = vat.vat_name;
		$scope.vat_list = [];
	}
	$scope.new_supplier = function(purchase) {
		$scope.current_purchase = purchase;
		$scope.supplier= {
	        'name': '',
	        'address': '',
	        'mobile': '',
	        'telephone_number': '',
	        'email': '',
	    }
	    hide_purchase_popup_divs();
	    $('#add_supplier').css('display', 'block');
	    create_popup();
	}
	$scope.save_supplier = function() {
		save_supplier($scope, $http, 'purchase');
	}
}

function PurchaseReportController($scope, $http) {
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
				show_loader();
				$http.get('/purchases/purchase_report/?start_date='+start_date+'&end_date='+end_date).success(function(data){
					$scope.purchase_details = data.purchase_details;
					hide_loader();
				}).error(function(data, status){
					console.log(data);
				});
			} else
				document.location.href = '/purchases/purchase_report/?start_date='+start_date+'&end_date='+end_date;
		}
	}
}

function PurchaseReturnController($scope, $http) {
	$scope.purchase_return_items = [];
	$scope.purchase_return = {
		'purchase_id': '',
		'purchase_invoice': '',
		'return_invoice': '',
		'return_invoice_date': '',
		'grant_total': 0,
		'supplier': '',
		'items': [{
			'id': '',
			'name': '',
			'code': '',
			'purchased_quantity': 0,
			'quantity': 0,
			'returned_qty': 0,
			'purchase_price':0,
			'purchase_unit': '',
			'net_amount': 0,
			'stock': 0,
		}],
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.get_purchase_details = function() {
		$scope.no_purchase_message = '';
		$scope.selected_item = {
			'id': '',
			'name':'',
			'code': '',
			'purchased_quantity': 0,
			'quantity': 0,
			'returned_qty':0,
			'batch_name':'',
			'stock': 0,
			'purchase_unit':'',
			'purchase_price': 0,
			'items':[],
		}
		$scope.purchase_return.items = [];
		$scope.purchase_return.items.push($scope.selected_item);
		if ($scope.purchase_invoice != undefined && $scope.purchase_invoice.length > 0) {
			show_loader();
			$http.get('/purchases/purchase_return_entry/?purchase_invoice_no='+$scope.purchase_invoice).success(function(data){
				hide_loader();
				if (data.result == 'ok') {
					if (data.purchase_deatails.length == 0) {
						$scope.no_purchase_message = 'No such Purchase';
						$scope.purchase_return.supplier = '';
					} else {
						$scope.purchase_return.supplier = data.purchase_deatails[0].supplier;
						$scope.purchase_return.purchase_id = data.purchase_deatails[0].id;
						$scope.purchase_return.purchase_invoice = data.purchase_deatails[0].purchase_invoice;
					}

				}
			}).error(function(data, status) {
				console.log('Request failed' || data);
			});
		}
	}
	$scope.load_all_items = function() {
		if ($scope.purchase_return.purchase_invoice == '' || $scope.purchase_return.purchase_invoice == undefined) {
			$scope.no_purchase_message = 'Please enter the Purchase Invoice Number';
		} else {
			show_loader();
			$http.get('/purchases/purchase_items/?purchase_id='+$scope.purchase_invoice+'&all_items=true').success(function(data){
				$scope.purchase_return.items = [];
				for (var i=0; i<data.items.length; i++) {
					$scope.selected_item = {
						'id': data.items[i].id,
						'name':data.items[i].name,
						'code': data.items[i].code,
						'purchased_quantity': data.items[i].purchased_quantity,
						'quantity': 0,
						'returned_qty':data.items[i].returned_qty,
						'batch_name':data.items[i].batch_name,
						'stock': data.items[i].stock,
						'purchase_unit':data.items[i].purchase_unit,
						'purchase_price': data.items[i].purchase_price,
						'items':[],
					}
					$scope.purchase_return.items.push($scope.selected_item);
				}
				hide_loader();
			}).error(function(data, status) {
				console.log('Request failed' || data);
			});
		}
	}
	$scope.get_purchase_item_details = function(item) {
		$scope.no_purchase_message = '';
		item.id = '';
		item.code = '';
		item.batch_name = ''
		item.purchased_quantity = 0;
		item.quantity = 0;
		item.returned_qty = 0;
		item.purchase_price = 0;
		item.purchase_unit = '';
		item.net_amount = 0;
		item.stock = 0;
		if ($scope.purchase_return.purchase_invoice == '' || $scope.purchase_return.purchase_invoice == undefined) {
			$scope.no_purchase_message = 'Please enter the Purchase Invoice Number';
			item.name = '';
		} else {
			$scope.current_purchase_return_item  = item;
			show_loader();
			$http.get('/purchases/purchase_items/?purchase_id='+$scope.purchase_invoice+'&item_name='+item.name).success(function(data){
				item.items = data.items;
				hide_loader();
			}).error(function(data, status) {
				console.log('Request failed' || data);
			});
		}
	}
	$scope.select_purchase_item = function(purchase_item) {
		$scope.item_selected_msg = '';
		for (var i=0; i<$scope.purchase_return.items.length; i++) {
			if ($scope.purchase_return.items[i].id == purchase_item.id) {
				$scope.item_selected_msg = 'Item is already selected';
				$scope.current_purchase_return_item.items = [];
				$scope.current_purchase_return_item.name = '';
				$scope.current_purchase_return_item.id = '';
				$scope.current_purchase_return_item.purchased_quantity = 0;
				$scope.current_purchase_return_item.quantity = 0;
				$scope.current_purchase_return_item.returned_qty = 0;
				$scope.current_purchase_return_item.purchase_price = 0;
				$scope.current_purchase_return_item.purchase_unit = '';
				$scope.current_purchase_return_item.net_amount = 0;
				$scope.current_purchase_return_item.stock = 0;
			} 
		}
		if ($scope.item_selected_msg.length == 0) {
			$scope.current_purchase_return_item.id = purchase_item.id;
			$scope.current_purchase_return_item.name = purchase_item.name;
			$scope.current_purchase_return_item.code = purchase_item.code;
			$scope.current_purchase_return_item.purchased_quantity = purchase_item.purchased_quantity;
			$scope.current_purchase_return_item.quantity = 0;
			$scope.current_purchase_return_item.returned_qty = purchase_item.returned_qty;
			$scope.current_purchase_return_item.batch_name = purchase_item.batch_name;
			$scope.current_purchase_return_item.stock = purchase_item.stock;
			$scope.current_purchase_return_item.purchase_unit = purchase_item.purchase_unit;
			$scope.current_purchase_return_item.purchase_price = purchase_item.purchase_price;
			$scope.current_purchase_return_item.items = [];
		}
	}
	$scope.remove_purchase_return_item = function(item) {
		var index = $scope.purchase_return.items.indexOf(item);
		$scope.purchase_return.items.splice(index, 1);
	}
	$scope.add_new_purchase_return_item = function() {
		$scope.purchase_return.items.push(
		{
			'id': '',
            'name': '',
            'code': '',
            'batch': '',
            'stock': 0,
            'purchase_unit': '',
            'quantity': 0,
            'purchase_price': 0,
            'net_amount': 0,
            'items': [],
			'purchased_quantity': 0,
			'returned_qty': 0,
        });
	}
	
	$scope.validate_purchase_return = function() {
		if ($scope.purchase_return.purchase_invoice == '' || $scope.purchase_return.purchase_invoice == undefined) {
			$scope.validate_purchase_return_msg = 'Please enter the Purchase Invoice No';
			return false;
		} else if ($scope.purchase_return.return_invoice == '' || $scope.purchase_return.return_invoice == undefined) {
			$scope.validate_purchase_return_msg = 'Please enter the Return Invoice No';
			return false;
		} else if ($scope.purchase_return.return_invoice_date == '' || $scope.purchase_return.return_invoice_date == undefined) {
			$scope.validate_purchase_return_msg = 'Please choose the Return Invoice Date';
			return false;
		} else if ($scope.purchase_return.return_invoice_date == '' || $scope.purchase_return.return_invoice_date == undefined) {
			$scope.validate_purchase_return_msg = 'Please choose the Return Invoice Date';
			return false;
		} else if ($scope.purchase_return.items.length == 0) {
			$scope.validate_purchase_return_msg = 'Please add items';
			return false;
		} else if ($scope.purchase_return.items.length > 0) {
			for (var i=0; i<$scope.purchase_return.items.length; i++) {
				purchase_remaining_quantity = parseFloat($scope.purchase_return.items[i].purchased_quantity) - (parseFloat($scope.purchase_return.items[i].quantity) + parseFloat($scope.purchase_return.items[i].returned_qty));
				stock_remaining_quantity = parseFloat($scope.purchase_return.items[i].stock) - parseFloat($scope.purchase_return.items[i].quantity);
				if ($scope.purchase_return.items[i].code == '' || $scope.purchase_return.items[i].code == undefined) {
					$scope.validate_purchase_return_msg = 'Please enter the item name ';
					return false;
				} else if ($scope.purchase_return.items[i].quantity == '' || $scope.purchase_return.items[i].quantity == undefined) {
					$scope.validate_purchase_return_msg = 'Please enter the Quantity for the item '+$scope.purchase_return.items[i].name;
					return false;
				} else if ($scope.purchase_return.items[i].quantity == 0) {
					$scope.validate_purchase_return_msg = 'Please enter the Quantity for the item '+$scope.purchase_return.items[i].name;
					return false;
				} else if (purchase_remaining_quantity < 0) {
					$scope.validate_purchase_return_msg = 'Please quantity exceeds Remaining Purchased quantity for the item '+$scope.purchase_return.items[i].name;
					return false;
				} else if (stock_remaining_quantity < 0) {
					$scope.validate_purchase_return_msg = 'Please quantity exceeds Stock for the item '+$scope.purchase_return.items[i].name;
					return false;
				} 
			}
		} return true;
	}
	$scope.save_purchase_return = function() {
		$scope.purchase_return.return_invoice_date = $('#invoice_date').val();
		$scope.purchase_return.cheque_date = $('#cheque_date').val();
		if ($scope.validate_purchase_return()) {
			show_loader();
			params = {
				'purchase_return_details': angular.toJson($scope.purchase_return),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method: 'post',
				url: '/purchases/purchase_return_entry/',
				data: $.param(params),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				if (data.result == 'ok') {
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Purchase Return';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				} else {
					$scope.validate_purchase_return_msg = data.message;
				}
				
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}
	$scope.hide_popup_transaction_details = function() {
		hide_popup();
		document.location.href = '/purchases/purchase_return_entry/';
	}
	$scope.calculate_net_amount = function(item) {
		$scope.choosed_item = item;
		// $scope.calculate_costprice();
		// $scope.choosed_item.cost_price = $scope.cost_price;
		if (item.quantity != Number(item.quantity)) {
			item.quantity = 0;
		}
		item.net_amount = item.quantity*item.purchase_price;
		$scope.calculate_grant_total();

	}
	$scope.calculate_grant_total = function() {
		grant_total = 0;
		for (var i=0; i<$scope.purchase_return.items.length; i++) {
			if ($scope.purchase_return.items[i].net_amount == Number($scope.purchase_return.items[i].net_amount))
				grant_total = grant_total+$scope.purchase_return.items[i].net_amount;
		}
		$scope.purchase_return.grant_total = grant_total;
	}
}

function PurchaseReturnReportController($scope, $http) {
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
				show_loader();
				$http.get('/purchases/purchase_return_report/?start_date='+start_date+'&end_date='+end_date).success(function(data){
					$scope.purchase_return_details = data.purchase_return_details;
					hide_loader();
				}).error(function(data, status){
					console.log(data);
				});
			} else
				document.location.href = '/purchases/purchase_return_report/?start_date='+start_date+'&end_date='+end_date;
		}
	}
}

function PurchaseViewController($scope, $http) {
	$scope.purchase = {
		'invoice_no': '',
		'invoice_date': '',
		'discount': 0,
		'payment_mode': 'cash',
		'supplier': '',
		'bank_name': '',
		'branch': '',
		'cheque_no': '',
		'cheque_date': '',
		'card_no': '',
		'grant_total': 0,
		'do_no': '',
		'items': [
			{
	            'name': '',
	            'code': '',
	            'batch': '',
	            'stock': '',
	            'uom': '',
	            'purchase_price': 0,
	            'cost_price': 0.00,
	            'net_amount': '',
	            'whole_sale_price': 0,
				'retail_price': 0,
				'whole_sale_profit': 0.00,
				'retail_profit': 0.00,
	        },
		],
		'card_holder_name': '',
		'purchase_tax': 0,
		'bank_account_ledger': '',
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.get_purchase_details = function() {
		$http.get('/purchases/purchase_view/?invoice_no='+$scope.invoice_no).success(function(data) {
			$scope.purchase_error_message = '';
			if (data.result == 'ok') {
				$scope.purchase = data.purchase;
			} else {
				$scope.purchase_error_message = data.message;
				$scope.purchase = data.purchase;
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		});
	}
	$scope.show_payment_details = function() {
		if ($scope.purchase.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();
		$scope.bank_name = $scope.purchase.bank_name;
		$scope.cheque_date = $scope.purchase.cheque_date;
		$scope.cheque_no = $scope.purchase.cheque_number;
		$scope.branch = $scope.purchase.branch;
		$scope.card_no = $scope.purchase.card_number;
		$scope.card_holder_name = $scope.purchase.card_holder_name;
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
}

function PurchaseReturnViewController($scope, $http) {
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.get_purchase_return_details = function() {
		$http.get('/purchases/purchase_return_view/?invoice_no='+$scope.purchase_return_invoice).success(function(data) {
			$scope.purchase_error_message = '';
			if (data.result == 'ok') {
				$scope.purchase_return = data.purchase_return;
			} else {
				$scope.purchase_error_message = data.message;
				$scope.purchase_return = data.purchase_return;
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		});
	}
	$scope.show_payment_details = function() {
		if ($scope.purchase.payment_mode == 'cheque') {
			$scope.is_cheque = true;
		} else {
			$scope.is_cheque = false;
		}
		create_popup();
		$scope.bank_name = $scope.purchase.bank_name;
		$scope.cheque_date = $scope.purchase.cheque_date;
		$scope.cheque_no = $scope.purchase.cheque_number;
		$scope.branch = $scope.purchase.branch;
		$scope.card_no = $scope.purchase.card_number;
		$scope.card_holder_name = $scope.purchase.card_holder_name;
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
}