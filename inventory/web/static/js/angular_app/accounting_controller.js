

/************************************ Accounting - common js methods ****************************************/
function get_accounting_ledgers($scope, $http) {
    show_loader();
    $http.get('/accounting/ledgers/').success(function(data){
        hide_loader();
        if (data.result == 'ok') {
        	if (data.ledgers.length > 0) {
            	$scope.ledgers = data.ledgers;
            	paginate($scope.ledgers, $scope, 10);
            }
        } else{
            $scope.message = data.message;
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_ledger_search_list($scope, $http, ledger) {
    $scope.no_ledger_msg = '';
    $scope.ledgers_list = [];
    var ledger_name;
    var request_flag = false;
    if(ledger == 'debit_ledger'){
		if(($scope.debit_ledger_name != '' && $scope.debit_ledger_name.length > 0)) {
			ledger_name = $scope.debit_ledger_name;
			request_flag = true;
		}
	} else if(ledger == 'credit_ledger'){
		if(($scope.credit_ledger_name != '' && $scope.credit_ledger_name.length > 0)) {
			ledger_name = $scope.credit_ledger_name;
			request_flag = true;
		}
	} else {
    	if(($scope.ledger_name != undefined && $scope.ledger_name != '' && $scope.ledger_name.length > 0)) {
	        	ledger_name = $scope.ledger_name;
	        	request_flag = true;
	    }else if(($scope.opening_balance.ledger_name != undefined && $scope.opening_balance.ledger_name != '' && $scope.opening_balance.ledger_name.length > 0)){
	    		ledger_name = $scope.opening_balance.ledger_name;
	        	request_flag = true;
	    }
    }
    if(request_flag){
    	show_loader();
    	var filter = true;
    	if($scope.ledger_filter != undefined){
    		if(!$scope.ledger_filter){
    			var filter = false;
    		}
    	} 
    	$http.get('/accounting/search_ledger/?name='+ledger_name+'&filter='+filter).success(function(data){
            hide_loader();
            if (data.ledgers.length == 0) {
            	if(ledger == 'debit_ledger'){
            		$scope.no_debit_ledger_msg = 'No such ledger';
	                $scope.debit_ledgers = [];
            	} else if(ledger == 'credit_ledger'){
					$scope.no_credit_ledger_msg = 'No such ledger';
	                $scope.credit_ledgers = [];
            	} else if(ledger == 'search_ledger'){
	                $scope.no_ledger_msg = 'No such ledger';
	                $scope.ledgers = [];
	                paginate($scope.ledgers, $scope, 10);
            	} else{
            		$scope.no_ledger_msg = 'No such ledger';
	                $scope.ledgers_list = [];
            	}
            } else {
            	if(ledger == 'debit_ledger')
            		$scope.debit_ledgers = data.ledgers;
            	else if(ledger == 'credit_ledger')
            		$scope.credit_ledgers = data.ledgers;
            	else if(ledger == 'search_ledger') {
                	$scope.ledgers = data.ledgers;
                	paginate($scope.ledgers, $scope, 10)
               	} else
               		$scope.ledgers_list = data.ledgers;
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}
function get_ledger_subledger_list($scope, $http) {
    $http.get('/accounting/ledgers_tree_view/').success(function(data){
        $scope.ledgers = data.ledgers;
        for (var i=0; i<$scope.ledgers.length; i++) {
            $scope.ledgers[i].is_closed = true;
        }
    }).error(function(data, status){
        console.log('Request failed' || data);
    })
}
function get_subledger_list($scope, $http, ledger_id, view_type) {
    $http.get('/accounting/subledger_list/'+ledger_id+'/').success(function(data){
        if (view_type == 'edit') {
            $scope.ledger_details = data.ledger_details[0];
        } else {
            $scope.current_ledger.subledgers = data.subledgers;
            $scope.current_ledger.temp_subledgers = data.subledgers;
        }
    }).error(function(data, status){
        console.log('Request failed' || data);
    })
}
function validate_ledger($scope){
        if ($scope.no_ledger_msg) {
            $scope.validate_ledger_error_msg = 'Please select the parent ledger or leave as null';
            return false;
        } else if ($scope.ledger.name == '' || $scope.ledger.name == undefined) {
            $scope.validate_ledger_error_msg = 'Please enter the name';
            return false;
        } return true;
    }
function save_ledger($scope, $http, view_type) {
        if($scope.ledger.parent == null)
            $scope.ledger.parent = "";
        params = {
            'ledger': angular.toJson($scope.ledger),
            "csrfmiddlewaretoken": $scope.csrf_token,
        }
        if (validate_ledger($scope)) {
            show_loader();
            $http({
                method: 'post',
                url: '/accounting/add_ledger/',
                data : $.param(params),
                headers : {
                    'Content-Type' : 'application/x-www-form-urlencoded'
                }
            }).success(function(data){
                hide_loader();
                $scope.validate_ledger_error_msg = '';
                if (data.result == 'error') {
                    $scope.validate_ledger_error_msg = data.message;
                } else {
                	hide_ledger_popup($scope, $http);
					if (view_type == 'tree') {
	                    if($scope.selected_parent_ledger){
	                        if (data.new_ledger.parent != '')
	                            $scope.selected_parent_ledger.subledgers.push(data.new_ledger);
	                        else {
	                            $scope.ledgers.push(data.new_ledger);
	                            paginate($scope.ledgers, $scope, 10);
	                        }
	                    } else {
	                        $scope.ledgers.push(data.new_ledger);
	                        paginate($scope.ledgers, $scope, 10);
	                    }
                } else if(view_type == 'transaction'){
                	hide_ledger_popup($scope, $http);
                } else{
                    document.location.href = '/accounting/ledgers/';
                }
/*					if($scope.selected_parent_ledger){
						$scope.selected_parent_ledger.subledgers.push(data.new_ledger);
					}*/
                }
            }).error(function(data, status) {   
                console.log('Request failed' || data);
            });
        }
	}
function hide_ledger_popup($scope, $http) {
		$scope.ledger = {
			'parent':'',
			'name': '',
			'id': '',
		}
		$scope.ledger_name = "";
		$scope.no_ledger_msg = "";
		$scope.validate_ledger_error_msg = "";
		$('#dialogue_popup_container').css('display', 'none');
		$('#popup_overlay').css('display', 'none');
	}
/************************************ Accouting - common js methods - end ************************************/

function LedgerController($scope, $http) {
	$scope.ledger = {
		'parent': '',
		'name': '',
	}
	$scope.init = function(csrf_token, ledger_id) {
		$scope.ledger_id = ledger_id;
		$scope.csrf_token = csrf_token;
		$scope.ledger_details = [];
		$scope.ledger_filter = false;
		get_accounting_ledgers($scope, $http);
		if (ledger_id) {
			$http.get('/accounting/subledger_list/'+ledger_id+'/').success(function(data){
				$scope.ledger_details = data.ledger_details[0];
				paginate($scope.ledger_details.sub_ledgers, $scope, 10);
			}).error(function(data, status){
				console.log('Request failed' || data);
			})
		}
	}
	$scope.select_page = function(page){
		if ($scope.ledger_details.sub_ledgers != undefined && $scope.ledger_details.sub_ledgers.length > 0) {
			select_page(page, $scope.ledger_details.sub_ledgers, $scope, 10);
		} else {
			select_page(page, $scope.ledgers, $scope, 15);
		}	
    }
    $scope.range = function(n) {
        return new Array(n);
    }
	$scope.get_ledger_list = function(ledger) {
		$scope.ledgers = [];
		get_ledger_search_list($scope, $http, ledger);
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger.parent = ledger.id;
		$scope.ledger_name = ledger.name;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.create_ledger = function() {
		$scope.ledger = {
			'parent': '',
			'name': '',
		}
		$('#popup_overlay').css('display', 'block');
		$('#dialogue_popup_container').css('height', '100%');
		$('#dialogue_popup_container').css('display', 'block');
		$('#dialogue_popup').css('display', 'block');
	}
	$scope.save_ledger = function() {
		save_ledger($scope, $http, 'list');
	}
	$scope.view_ledger_details = function(ledger){
		document.location.href = '/accounting/subledger_details/'+ledger.id+'/';
	}
	$scope.edit_ledger_details = function(ledger){
		$scope.ledger = ledger;
		$scope.create_ledger();
	}
	$scope.delete_ledger = function(ledger) {
		document.location.href = '/accounting/delete_ledger/?ledger_id='+ledger.id;
	}
	$scope.edit_subledger = function(subledger, ledger) {
		$scope.ledger.parent = ledger.id;
		$scope.ledger.name = subledger.name;
		$scope.ledger.id = subledger.id;
		$scope.ledger_name = ledger.name;
		$scope.create_ledger();
	}
	$scope.hide_popup = function() {
		hide_ledger_popup($scope, $http);
	}
	$scope.delete_subledger = function(subledger) {
		document.location.href = '/accounting/delete_subledger/?ledger_id='+subledger.id;
	}
}

function LedgerTreeController($scope, $http){
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		$scope.ledger_filter = false;
		get_ledger_subledger_list($scope, $http);
	}
	$scope.get_ledger_list = function() {
		get_ledger_search_list($scope, $http);
	}
	$scope.show_ledger_details = function(ledger) {
		$scope.current_ledger = ledger;
		get_subledger_list($scope, $http, ledger.id,'subledger');			
	}
	$scope.toggle_ledger_view = function(event, ledger) {
        var target = $(event.currentTarget);
        var element = target.parent().find('ul').first();
        var height_property = element.css('height');
        if(height_property == '0px') {
            element.animate({'height': '100%'}, 500);
            target.text('-');
            if(ledger.subledgers.length == 0){
            	$scope.show_ledger_details(ledger);
            }
        } else {
            element.animate({'height': '0px'}, 500);
            target.text('+');
        }
    }     
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger.parent = ledger.id;
		$scope.ledger_name = ledger.name;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.add_subledger = function(ledger) {
		$scope.ledger = {
			'parent': '',
			'name': '',
		}
		$scope.ledger_name = ledger.name;
		$scope.ledger.parent = ledger.id;
		$scope.selected_parent_ledger = ledger;
		create_popup();
	}
	$scope.hide_popup = function() {
		hide_ledger_popup($scope, $http);
	}
	$scope.create_ledger= function() {
		$scope.ledger = {
			'parent': '',
			'name': '',
		}
		create_popup();
	}	
	$scope.save_ledger = function() {
		save_ledger($scope, $http, 'tree');
	}	
	$scope.edit_subledger = function(ledger){
		console.log(ledger);	
		$scope.ledger = {
			'parent': '',
			'name': '',
		}
		$scope.ledger_name = ledger.parent_name;
		$scope.ledger.parent = ledger.parent;
		$scope.ledger.name = ledger.name;
		$scope.ledger.id = ledger.id;
		create_popup();
	}
}
function PaymentController($scope, $http){
	$scope.payment = {
		'transaction_date': '',
		'amount': '',
		'mode': '',
		'cheque_number': '',
		'cheque_date': '',
		'card_no': '',
		'card_holder_name': '',
		'bank_name': '',
		'branch': '',
		'narration': '',
		'vendor': '',
		'bank_account': '',
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_bank_account_details($scope, $http);
	}
	$scope.get_ledger_list = function(ledger) {
		$scope.ledgers = [];
		get_ledger_search_list($scope, $http,ledger);
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger_name = ledger.name;
		$scope.payment.ledger = ledger.id;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.validate_payment = function(){
		$scope.validate_error_msg = "";
		if($scope.payment.transaction_date == '' || $scope.payment.transaction_date == undefined){
			$scope.validate_error_msg = 'Please select the date of payment';
			return false;
		} else if($scope.payment.amount == '' || $scope.payment.amount == undefined){
			$scope.validate_error_msg = 'Please enter the amount';
			return false;
		} else if($scope.payment.amount !== '0' && !Number($scope.payment.amount)){
			$scope.validate_error_msg = 'Please enter a valid amount';
			return false;
		} else if($scope.payment.mode == '' || $scope.payment.mode == undefined){
			$scope.validate_error_msg = 'Please choose the mode of payment';
			return false;
		} else if(($scope.payment.mode == 'card' || $scope.payment.mode == 'cheque') && ($scope.payment.bank_account == '')){
			$scope.validate_error_msg = 'Please select the Bank Account';
			return false;
		} else if($scope.payment.mode == 'card' && ($scope.payment.card_no == '' || $scope.payment.card_no == undefined)){
			$scope.validate_error_msg = 'Please enter the card number';
			return false;
		} else if($scope.payment.mode == 'card' && ($scope.payment.card_no !== '0' && !Number($scope.payment.card_no))){
			$scope.validate_error_msg = 'Please enter a valid card number';
			return false;
		} else if($scope.payment.mode == 'card' && ($scope.payment.card_holder_name == '' || $scope.payment.card_holder_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of card holder';
			return false;
		}  else if(($scope.payment.mode == 'card' || $scope.payment.mode == 'cheque') && ($scope.payment.bank_name == '' || $scope.payment.bank_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the bank';
			return false;
		} else if($scope.payment.mode == 'cheque' && ($scope.payment.cheque_number == '' || $scope.payment.cheque_number == undefined)){
			$scope.validate_error_msg = 'Please enter the cheque number';
			return false;
		} else if($scope.payment.mode == 'cheque' && ($scope.payment.cheque_number !== '0' && !Number($scope.payment.cheque_number))){
			$scope.validate_error_msg = 'Please enter a valid cheque number';
			return false;
		} else if($scope.payment.mode == 'cheque' && ($scope.payment.cheque_date == '' || $scope.payment.cheque_date == undefined)){
			$scope.validate_error_msg = 'Please select the cheque date';
			return false;
		} else if($scope.payment.mode == 'cheque' && ($scope.payment.branch == '' || $scope.payment.branch == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the branch';
			return false;
		} else if($scope.payment.ledger == '' || $scope.payment.ledger == undefined || $scope.ledger_name == '' || $scope.ledger_name == undefined){
			$scope.validate_error_msg = 'Please select an Account';
			return false;
		} 
		var start_date = new Date();
        var date_value = $scope.payment.transaction_date.split('/');
        var end_date = new Date(date_value[2],date_value[1]-1, date_value[0]);
        if(start_date < end_date){
          $scope.validate_error_msg = 'Please check the date of payment';
          return false;
        }
		return true;
	}
	$scope.save_payment = function(){
		if($scope.validate_payment()){
			show_loader();
			console.log($scope.payment);
			params = {
				'payment': angular.toJson($scope.payment),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method: 'post',
				url: '/accounting/create_payment/',
				data: $.param(params),
				headers: {
					'Content-Type' : 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				$scope.validate_error_msg = "";
				if(data.result == 'error'){
					$scope.validate_error_msg = data.message;
				} else{
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Payment ';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/accounting/create_payment/';
		$scope.validate_error_msg = "";
		$scope.payment = "";
		$scope.supplier_name = "";
	}
}
function ReceiptController($scope, $http){
	$scope.receipt = {
		'transaction_date': '',
		'amount': '',
		'mode': '',
		'cheque_number': '',
		'cheque_date': '',
		'card_no': '',
		'card_holder_name': '',
		'bank_name': '',
		'branch': '',
		'narration': '',
		'customer': '',
		'bank_ledger': '',
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_bank_account_details($scope, $http);
	}
	$scope.get_ledger_list = function(ledger) {
		$scope.ledgers = [];
		get_ledger_search_list($scope, $http,ledger);
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger_name = ledger.name;
		$scope.receipt.ledger = ledger.id;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.validate_receipt = function(){
		$scope.validate_error_msg = "";
		console.log($scope.receipt);
		if($scope.receipt.transaction_date == '' || $scope.receipt.transaction_date == undefined){
			$scope.validate_error_msg = 'Please select the date of receipt';
			return false;
		} else if($scope.receipt.amount == '' || $scope.receipt.amount == undefined){
			$scope.validate_error_msg = 'Please enter the amount';
			return false;
		} else if($scope.receipt.amount !== '0' && !Number($scope.receipt.amount)){
			$scope.validate_error_msg = 'Please enter a valid amount';
			return false;
		} else if($scope.receipt.mode == '' || $scope.receipt.mode == undefined){
			$scope.validate_error_msg = 'Please choose the mode of payment';
			return false;
		} else if($scope.receipt.mode == 'card' && ($scope.receipt.card_no == '' || $scope.receipt.card_no == undefined)){
			$scope.validate_error_msg = 'Please enter the card number';
			return false;
		} else if($scope.receipt.mode == 'card' && ($scope.receipt.card_no !== '0' && !Number($scope.receipt.card_no))){
			$scope.validate_error_msg = 'Please enter a valid card number';
			return false;
		} else if($scope.receipt.mode == 'card' && ($scope.receipt.card_holder_name == '' || $scope.receipt.card_holder_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of card holder';
			return false;
		} else if(($scope.receipt.mode == 'card' || $scope.receipt.mode == 'cheque') && ($scope.receipt.bank_name == '' || $scope.receipt.bank_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the bank';
			return false;
		} else if($scope.receipt.mode == 'cheque' && ($scope.receipt.cheque_number == '' || $scope.receipt.cheque_number == undefined)){
			$scope.validate_error_msg = 'Please enter the cheque number';
			return false;
		} else if($scope.receipt.mode == 'cheque' && ($scope.receipt.cheque_number !== '0' && !Number($scope.receipt.cheque_number))){
			$scope.validate_error_msg = 'Please enter a valid cheque number';
			return false;
		} else if($scope.receipt.mode == 'cheque' && ($scope.receipt.cheque_date == '' || $scope.receipt.cheque_date == undefined)){
			$scope.validate_error_msg = 'Please select the cheque date';
			return false;
		} else if($scope.receipt.mode == 'cheque' && ($scope.receipt.branch == '' || $scope.receipt.branch == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the branch';
			return false;
		} else if(($scope.receipt.mode == 'cheque' || $scope.receipt.mode == 'card') && ($scope.receipt.bank_ledger == '' || $scope.receipt.bank_ledger == undefined)){
			$scope.validate_error_msg = 'Please choose the bank ledger';
			return false;
		} else if($scope.receipt.ledger == '' || $scope.receipt.ledger == undefined || $scope.ledger_name == '' || $scope.ledger_name == undefined){
			$scope.validate_error_msg = 'Please select an account';
			return false;
		}
		var start_date = new Date();
        var date_value = $scope.receipt.transaction_date.split('/');
        var end_date = new Date(date_value[2],date_value[1]-1, date_value[0]);
        if(start_date < end_date){
          $scope.validate_error_msg = 'Please check the date of receipt';
          return false;
        }
		return true;
	}
	$scope.save_receipt = function(){
		if($scope.validate_receipt()){
			show_loader();
			params = {
				'receipt': angular.toJson($scope.receipt),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method: 'post',
				url: '/accounting/create_receipt/',
				data: $.param(params),
				headers: {
					'Content-Type' : 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				$scope.validate_error_msg = "";
				if(data.result == 'error'){
					$scope.validate_error_msg = data.message;
				} else{
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Receipt ';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/accounting/create_receipt/';
	}
}
function TransactionController($scope, $http){
	$scope.transaction = {
		'transaction_date': '',
		'amount': '',
		'mode': '',
		'cheque_number': '',
		'cheque_date': '',
		'card_no': '',
		'card_holder_name': '',
		'bank_name': '',
		'branch': '',
		'narration': '',
		'debit_ledger': '',
		'credit_ledger': '',
	}
	$scope.ledger = {
		'parent': '',
		'name': '',
	}
	$scope.debit_ledger_name = "";
	$scope.credit_ledger_name = "";
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
	}
	$scope.get_ledgers = function(ledger){
		if($scope.debit_ledger_name.length == 0){
			$scope.debit_ledgers = "";
			$scope.no_debit_ledger_msg = "";
		}
		if($scope.credit_ledger_name.length == 0){
			$scope.credit_ledgers = "";
			$scope.no_credit_ledger_msg = "";
		}
		if(ledger == 'debit_ledger')
			$scope.transaction.debit_ledger = "";
		if(ledger == 'credit_ledger')
			$scope.transaction.credit_ledger = "";
		get_ledger_search_list($scope, $http, ledger);
	}
	$scope.get_debit_ledger_details = function(ledger){
		$scope.debit_ledger_name = ledger.name;
		$scope.transaction.debit_ledger = ledger.id;
		$scope.debit_ledgers = "";
		$scope.no_debit_ledger_msg = "";
	}
	$scope.get_credit_ledger_details = function(ledger){
		$scope.credit_ledger_name = ledger.name;
		$scope.transaction.credit_ledger = ledger.id;
		$scope.credit_ledgers = "";
		$scope.no_credit_ledger_msg = "";
	}
	$scope.validate_transaction = function(){
		$scope.validate_error_msg = "";
		if($scope.transaction.transaction_date == ''){
			$scope.validate_error_msg = 'Please select the date of transaction';
			return false;
		} else if($scope.transaction.amount == ''){
			$scope.validate_error_msg = 'Please enter the amount';
			return false;
		} else if($scope.transaction.amount !== '0' && !Number($scope.transaction.amount)){
			$scope.validate_error_msg = 'Please enter a valid amount';
			return false;
		} else if($scope.transaction.debit_ledger == '' || $scope.debit_ledger_name == ''){
			$scope.validate_error_msg = 'Please select the debit ledger from the list';
			return false;
		} else if($scope.transaction.credit_ledger == '' || $scope.credit_ledger_name == ''){
			$scope.validate_error_msg = 'Please select the credit ledger from the list';
			return false;
		} else if(($scope.transaction.credit_ledger == $scope.transaction.debit_ledger) || ($scope.credit_ledger_name == $scope.debit_ledger_name)){
			$scope.validate_error_msg = 'Credit and Debit ledgers cannot be the same';
			return false;
		} else if($scope.transaction.mode == ''){
			$scope.validate_error_msg = 'Please choose the mode of payment';
			return false;
		} else if($scope.transaction.mode == 'card' && ($scope.transaction.card_no == '' || $scope.transaction.card_no == undefined)){
			$scope.validate_error_msg = 'Please enter the card number';
			return false;
		} else if($scope.transaction.mode == 'card' && ($scope.transaction.card_no !== '0' && !Number($scope.transaction.card_no))){
			$scope.validate_error_msg = 'Please enter a valid card number';
			return false;
		} else if($scope.transaction.mode == 'card' && ($scope.transaction.card_holder_name == '' || $scope.transaction.card_holder_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of card holder';
			return false;
		}  else if(($scope.transaction.mode == 'card' || $scope.transaction.mode == 'cheque') && ($scope.transaction.bank_name == '' || $scope.transaction.bank_name == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the bank';
			return false;
		} else if($scope.transaction.mode == 'cheque' && ($scope.transaction.cheque_number == '' || $scope.transaction.cheque_number == undefined)){
			$scope.validate_error_msg = 'Please enter the cheque number';
			return false;
		} else if($scope.transaction.mode == 'cheque' && ($scope.transaction.cheque_number !== '0' && !Number($scope.transaction.cheque_number))){
			$scope.validate_error_msg = 'Please enter a valid cheque number';
			return false;
		} else if($scope.transaction.mode == 'cheque' && ($scope.transaction.cheque_date == '' || $scope.transaction.cheque_date == undefined)){
			$scope.validate_error_msg = 'Please select the cheque date';
			return false;
		} else if($scope.transaction.mode == 'cheque' && ($scope.transaction.branch == '' || $scope.transaction.branch == undefined)){
			$scope.validate_error_msg = 'Please enter the name of the branch';
			return false;
		} 
		var start_date = new Date();
        var date_value = $scope.transaction.transaction_date.split('/');
        var end_date = new Date(date_value[2],date_value[1]-1, date_value[0]);
        if(start_date < end_date){
          $scope.validate_error_msg = 'Please check the date of transaction';
          return false;
        }
		return true;
	}
	$scope.create_ledger = function() {
		$('#popup_overlay').css('display', 'block');
		$('#dialogue_popup_container').css('height', '100%');
		$('#dialogue_popup_container').css('display', 'block');
		$('#dialogue_popup').css('display', 'block');
		$('#transaction_reference_no_details').css('display', 'none');
	}
	$scope.save_ledger = function() {
		save_ledger($scope, $http, 'transaction');
	}
	$scope.get_ledger_list = function() {
		get_ledger_search_list($scope, $http);
	}
	$scope.hide_popup = function() {
		hide_ledger_popup($scope, $http);
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger.parent = ledger.id;
		$scope.ledger_name = ledger.name;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.save_transaction = function(){
		if($scope.validate_transaction()){
			show_loader();
			params = {
				'transaction': angular.toJson($scope.transaction),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method: 'post',
				url: '/accounting/other_transaction/',
				data: $.param(params),
				headers: {
					'Content-Type' : 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				$scope.validate_error_msg = "";
				if(data.result == 'error'){
					$scope.validate_error_msg = data.message;
				} else{
					$('#new_ledger').css('display', 'none');
					$scope.transaction_reference_no = data.transaction_reference_no;
					$scope.transaction_name = ' Payment ';
					$('#transaction_reference_no_details').css('display', 'block');
					create_popup();
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}
	$scope.hide_popup_transaction_details = function() {
		document.location.href = '/accounting/other_transaction/';
	}
}

function LedgerReportController($scope, $http){
	$scope.ledger_name = '';
	$scope.start_date = '';
	$scope.end_date = '';
	$scope.ledger_details = {
			'start_date': '',
			'end_date': '',
			'ledger_name': '',
		}
	$scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
    }
	$scope.get_ledger_list = function() {
		get_ledger_search_list($scope, $http);
	}

	$scope.get_ledger_details = function(ledger) {
		$scope.ledger_id = ledger.id;
		$scope.ledger_name = ledger.name;
		$scope.ledger_details.ledger = ledger.id;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.validate = function(){
		console.log($scope.ledger);
		if($scope.ledger_name == '' || $scope.ledger_name == undefined){
			$scope.validate_error_msg = 'Please select the ledger';
			return false;
		} else if($scope.start_date == ''){
			$scope.validate_error_msg = 'Please select the start date';
			return false;
		} else if($scope.end_date == ''){
			$scope.validate_error_msg = 'Please select the end date';
			return false;
		} return true;
	}
	$scope.view_ledger = function(){
		if($scope.validate()){
			if($scope.ledger_name.length > 0 && $scope.ledger_details.ledger == ''){
				$scope.validate_error_msg = "Please choose a valid ledger from the list or leave as blank";
				$scope.ledger_entries = "";
			} else {
				$scope.validate_error_msg = ""
				$scope.ledger_details.start_date = $scope.start_date;
				$scope.ledger_details.end_date = $scope.end_date;
				show_loader();
				$http.get('/accounting/ledger_report?ledger='+$scope.ledger_details.ledger+'&start_date='+$scope.ledger_details.start_date+'&end_date='+$scope.ledger_details.end_date).success(function(data){
			        hide_loader();
			        $scope.ledger_entries = data.ledger_entries;
			        console.log($scope.ledger_entries);
			        paginate($scope.ledger_entries, $scope, 10);
			        if($scope.ledger_entries.length == 0)
			        	$scope.validate_error_msg = "No ledger entries found";
			    }).error(function(data, status){
			        $scope.message = data.message;
			    })
			}
		}
	}	
	$scope.select_page = function(page){
        select_page(page, $scope.ledger_entries, $scope, 10);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
	$scope.get_ledger_report = function(){
		
        document.location.href = '/accounting/ledger_report?ledger='+$scope.ledger_details.ledger+'&start_date='+$scope.start_date+'&end_date='+$scope.end_date+'&report_type=pdf';
    }
}

function OpeningBalanceController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.opening_balance = {
			'amount': '',
			'ledger_name': '',
		}
	}

	$scope.validate_opening_balance = function(){
		$scope.validate_error_msg = "";
		if($scope.opening_balance.amount == '' || $scope.opening_balance.amount == undefined){
			$scope.validate_error_msg = 'Please enter the balance amount';
			return false;
		} else if($scope.opening_balance.amount !== '0' && !Number($scope.opening_balance.amount)){
			$scope.validate_error_msg = 'Please enter a valid amount';
			return false;
		} return true;

	}

	$scope.save_opening_balance = function(){
		if($scope.validate_opening_balance()){
			show_loader();
			params = {
				'opening_balance': angular.toJson($scope.opening_balance),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method: 'post',
				url: '/accounting/opening_balance/',
				data: $.param(params),
				headers: {
					'Content-Type' : 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				$scope.validate_error_msg = "";
				if(data.result == 'error'){
					$scope.validate_error_msg = data.message;
				} else{
					$scope.validate_error_msg = data.message;
					$scope.opening_balance = "";
				}
			}).error(function(data, status){
				console.log('Request failed' || data);
			});
		}
	}
	$scope.get_ledger_list = function(ledger) {
		$scope.ledgers = [];
		get_ledger_search_list($scope, $http,ledger);
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.opening_balance.ledger_name = ledger.name;
		$scope.opening_balance.ledger = ledger.id;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
}	


function DayBookController($scope, $http){
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		$scope.day_book = {
			'date': '',
			'ledger': '',
		}
		$scope.ledger_name = '';
	}
	$scope.get_ledger_list = function(ledger) {
		if($scope.ledger_name.length == 0){
			$scope.ledgers_list = "";
			$scope.day_book.ledger = "";
		}
		else{
			$scope.day_book.ledger = "";	
			get_ledger_search_list($scope, $http,ledger);
		}
	}
	$scope.get_ledger_details = function(ledger) {
		$scope.ledger_name = ledger.name;
		$scope.day_book.ledger = ledger.id;
		$scope.ledgers_list = [];
		$scope.no_ledger_msg = "";
	}
	$scope.view_day_book = function(){
		if($scope.ledger_name.length > 0 && $scope.day_book.ledger == ''){
			$scope.validate_error_msg = "Please choose a valid ledger from the list or leave as blank";
			$scope.ledger_entries = "";
		}
		else
		{
			$scope.validate_error_msg = ""
			$scope.day_book.date = document.getElementById("select_date").value;
			show_loader();
			$http.get('/accounting/day_book/?date='+$scope.day_book.date+'&ledger='+$scope.day_book.ledger).success(function(data){
	        hide_loader();
	        $scope.ledger_entries = data.transaction_entries;
	        if($scope.ledger_entries.length == 0)
	        	$scope.validate_error_msg = "No ledger entries found";
	        	console.log($scope.ledger_entries);
		    }).error(function(data, status){
		        $scope.message = data.message;
		    })
		}
	}
	$scope.generate_pdf = function(){
		if($scope.ledger_name.length > 0 && $scope.day_book.ledger == ''){
			$scope.validate_error_msg = "Please choose a valid ledger from the list or leave as blank";
			$scope.ledger_entries = "";
		}
		else{
			$scope.day_book.date = document.getElementById("select_date").value;
			document.location.href = '/accounting/day_book/?date='+$scope.day_book.date+'&ledger='+$scope.day_book.ledger+'&report_type=pdf';
		}
	}
}
function CashBookController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.start_date = "";
		$scope.end_date = "";
	}
	$scope.validate = function(){
		$scope.validate_error_msg = "";
		$scope.cash_entries = "";
		if($scope.start_date == ''){
			$scope.validate_error_msg = 'Please select the start date';
			return false;
		} else if($scope.end_date == ''){
			$scope.validate_error_msg = 'Please select the end date';
			return false;
		} 
		var date_value = $scope.start_date.split('/');
		var start_date = new Date(date_value[2],date_value[0]-1, date_value[1]);
		var date_value = $scope.end_date.split('/');
		var end_date = new Date(date_value[2],date_value[0]-1, date_value[1]);
		if(start_date > end_date){
          $scope.validate_error_msg = 'Please check the dates';
          return false;
        }
		return true;
	}
	$scope.view_cash_book = function(){
		if($scope.validate()){
			$scope.validate_error_msg = "";
			show_loader();
			$http.get('/accounting/cash_book/?start_date='+$scope.start_date+'&end_date='+$scope.end_date).success(function(data){
	        hide_loader();
	        $scope.cash_entries = data.cash_entries;
	        console.log(data);
	        if($scope.cash_entries.length == 0)
	        	$scope.validate_error_msg = "No ledger entries found";
		    }).error(function(data, status){
		        $scope.message = data.message;
		    })
		}
	}
	$scope.generate_pdf = function(ledger){
		if($scope.validate())
			document.location.href = '/accounting/cash_book/?start_date='+$scope.start_date+'&end_date='+$scope.end_date+'&report_type=pdf';
	}
}
function BankBookController($scope, $http){
	$scope.init = function(csrf_token){
		$scope.csrf_token = csrf_token;
		$scope.start_date = "";
		$scope.end_date = "";
	}
	$scope.validate = function(){
		$scope.validate_error_msg = "";
		$scope.bank_entries = "";
		if($scope.start_date == ''){
			$scope.validate_error_msg = 'Please select the start date';
			return false;
		} else if($scope.end_date == ''){
			$scope.validate_error_msg = 'Please select the end date';
			return false;
		} 
		var date_value = $scope.start_date.split('/');
		var start_date = new Date(date_value[2],date_value[0]-1, date_value[1]);
		var date_value = $scope.end_date.split('/');
		var end_date = new Date(date_value[2],date_value[0]-1, date_value[1]);
		if(start_date > end_date){
          $scope.validate_error_msg = 'Please check the dates';
          return false;
        }
		return true;
	}
	$scope.view_bank_book = function(){
		if($scope.validate()){
			$scope.validate_error_msg = "";
			show_loader();
			$http.get('/accounting/bank_book/?start_date='+$scope.start_date+'&end_date='+$scope.end_date).success(function(data){
	        hide_loader();
	        $scope.bank_entries = data.bank_entries;
	        if($scope.bank_entries.length == 0)
	        	$scope.validate_error_msg = "No ledger entries found";
		    }).error(function(data, status){
		        $scope.message = data.message;
		    })
		}
	}
	$scope.generate_pdf = function(ledger){
		if($scope.validate())
			document.location.href = '/accounting/bank_book/?start_date='+$scope.start_date+'&end_date='+$scope.end_date+'&report_type=pdf';
	}
}

function LedgerBalanceController($scope, $http) {
    $scope.init = function(csrf_token) {
        $scope.ledger_balance_visible = false;
        $scope.csrf_token = csrf_token;
    }
    $scope.get_ledger_balance = function() {
        var url = '';
        if($scope.ledger_name){
            url = '/accounting/ledger_balance/?'+'ledger_name'+'='+$scope.ledger_name;
            show_loader();
            $http.get(url).success(function(data)
            {
                $scope.no_ledger_msg = '';
                hide_loader();
                if (data.ledgers.length == 0) {
                    $scope.no_ledger_msg = 'No such ledger';
                    $scope.ledger_balances = [];
                } else {
                    $scope.ledger_balances = data.ledgers;                   
                    if($scope.ledger_balances.length == 0)
                        $scope.no_ledger_msg = "No such ledger";
                }
                paginate($scope.ledger_balances, $scope, 15);
            }).error(function(data, status)
            {
                console.log(data || "Request failed");
            });
        }
    }
    $scope.select_page = function(page){
        select_page(page, $scope.items, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.toggle_ledger_balance_search = function(selector, event){
        var element = $(selector);
        var target = $(event.currentTarget);
        if($scope.ledger_balance_visible){
            element.animate({'margin-top': '-100%'}, 1000);
            element.parent().css('z-index', 3);
            $scope.ledger_balance_visible = false;
            target.addClass('closed_search').removeClass('open_search');
            $scope.ledger_balances = [];
        } else {
            element.animate({'margin-top': '0%'}, 1000);
            $scope.ledger_balance_visible = true;
            element.parent().css('z-index', 4);
            target.removeClass('closed_search').addClass('open_search');
        }
    }
}