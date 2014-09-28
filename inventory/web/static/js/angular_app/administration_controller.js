function get_staff_list($scope, $http) {
	$http.get('/staffs/').success(function(data){
		$scope.staffs = [];
		$scope.staffs = data.staffs;
		paginate($scope.staffs, $scope, 10);
	}).error(function(data, status){
		console.log('Request failed' || data)
	});
}
function get_salesmen_list($scope, $http) {
	$http.get('/salesmen/').success(function(data){
		$scope.salesmen = [];
		$scope.salesmen = data.salesmen;
	}).error(function(data, status){
		console.log('Request failed' || data)
	});
}
function search_staff($scope, $http) {
	$http.get('/search_staff/?staff_name='+$scope.staff_name).success(function(data){
		$scope.no_staff_message = '';
		$scope.staffs = []
		if (data.staffs.length == 0) {
			$scope.no_staff_message = 'No such staff';
			$scope.no_staff_error = true;
		} else {
			$scope.staffs = data.staffs;
			$scope.no_staff_error = false;
		}
		paginate($scope.staffs, $scope, 10);
	}).error(function(data, status){
		console.log('Request failed' || data)
	});
}
function search_salesmen($scope, $http) {
	$http.get('/search_salesmen/?salesman_name='+$scope.salesman_name).success(function(data){
		$scope.no_salesman_message = '';
		$scope.salesmen = []
		if (data.salesmen.length == 0) {
			$scope.no_salesman_message = 'No such salesman';
		} else {
			$scope.salesmen = data.salesmen;
			$scope.no_salesman_message = "";
		}
	}).error(function(data, status){
		console.log('Request failed' || data)
	});
}
function reset_staff_details($scope) {
	$scope.address = '';
	$scope.staff_details = {
		'first_name': '',
		'last_name': '',
		'username': '',
		'password': '',
		'confirm_password': '',
		'email': '',
		'designation': '',
		'contact_no': '',
	}
	$scope.user_exists = false;
}
function validate_staff($scope) {
	$scope.validation_staff_message = '';
	if ($scope.staff_details.first_name == '' || $scope.staff_details.first_name == undefined) {
		$scope.validation_staff_message = 'Please enter first name';
		return false;
	} else if ($scope.staff_details.last_name == '' || $scope.staff_details.last_name == undefined) {
		$scope.validation_staff_message = 'Please enter last name';
		return false;
	} else if ($scope.staff_details.username == '' || $scope.staff_details.username == undefined) {
		$scope.validation_staff_message = 'Please enter username';
		return false;
	} else if ($scope.user_exists) { 
		$scope.validation_staff_message = 'Username already exists';
		return false;
	} else if (!$scope.is_edit && ($scope.staff_details.password == '' || $scope.staff_details.password == undefined)) {
		$scope.validation_staff_message = 'Please enter password';
		return false;
	} else if (!$scope.is_edit && ($scope.staff_details.confirm_password == '' || $scope.staff_details.confirm_password == undefined)) {
		$scope.validation_staff_message = 'Please enter confirm password';
		return false;
	} else if (!$scope.is_edit && ($scope.staff_details.password != $scope.staff_details.confirm_password)) {
		$scope.validation_staff_message = 'Password and Confirm password is not matching';
		return false;
	} else if (!validateEmail($scope.staff_details.email)) {
		$scope.validation_staff_message = 'Please enter a valid email';
		return false;
	} else if ($scope.staff_details.contact_no == '' || $scope.staff_details.contact_no == undefined) {
		$scope.validation_staff_message = 'Please enter contact no';
		return false;
	} else if ($scope.staff_details.contact_no.length > 15 || $scope.staff_details.contact_no.length < 9) {
		$scope.validation_staff_message = 'Please enter a valid contact no';
		return false;
	} return true;
}
function validate_salesman($scope, $http){
	$scope.validate_salesman_error_msg = "";
	if ($scope.salesman.first_name == '') {
		$scope.validate_salesman_error_msg = 'Please enter first name';
		return false;
	} else if ($scope.salesman.last_name == '') {
		$scope.validate_salesman_error_msg = 'Please enter last name';
		return false;
	} else if ($scope.salesman.address == '') {
		$scope.validate_salesman_error_msg = 'Please enter address';
		return false;
	} else if ($scope.salesman.contact_no == '') {
		$scope.validate_salesman_error_msg = 'Please enter contact number';
		return false;
	} else if ($scope.salesman.email != '' && !validateEmail($scope.salesman.email)) {
		$scope.validate_salesman_error_msg = 'Please enter a valid email';
		return false;
	} return true;
}
function save_staff($scope, $http, from) {
	if(validate_staff($scope)) {
		show_loader();
		params = {
			'staff_details': angular.toJson($scope.staff_details),
			'address': $scope.address,
			'csrfmiddlewaretoken': $scope.csrf_token,
		}
		$http({
			method: 'post',
			url: '/add_staff/',
			data: $.param(params),
			headers: {
				'Content-Type' : 'application/x-www-form-urlencoded'
			}
		}).success(function(data){
			hide_loader();
			if (data.result == 'ok') {
				if (from == 'staff')
					document.location.href = '/staffs/';
				else {
					hide_popup();
					$scope.staff_name = data.name;
					$scope.permission.staff = data.id;
				}
			} else {
				$scope.validation_staff_message = data.message;
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		});
	}
}
function save_salesman($scope, $http, from) {
	if(validate_salesman($scope)) {
		show_loader();
		params = {
			'salesman_details': angular.toJson($scope.salesman),
			'csrfmiddlewaretoken': $scope.csrf_token,
		}
		$http({
			method: 'post',
			url: '/salesmen/',
			data: $.param(params),
			headers: {
				'Content-Type' : 'application/x-www-form-urlencoded'
			}
		}).success(function(data){
			hide_loader();
			if (data.result == 'ok') {
				if (from == 'sales') {
                    $scope.current_sales.salesman = data.salesman.id;
                    $scope.salesman_name = data.salesman.name;
                    hide_popup();
                } else
					document.location.href = '/salesmen/';
			} else {
				$scope.validate_salesman_error_msg = data.message;
			}
		}).error(function(data, status){
			console.log('Request failed' || data);
		});
	}
}
function check_username_exists($scope, $http) {
	$scope.username_exists_msg = '';
	if ($scope.staff_details.username!= undefined && $scope.staff_details.username.length > 0) {
		show_loader();
		$http.get('/check_staff_user_exists/?username='+$scope.staff_details.username).success(function(data) {
			hide_loader();
			if (data.result == 'error') {
				$scope.username_exists_msg = data.message;
				$scope.user_exists = true;
		} else {
			$scope.user_exists = false;
		}
		}).error(function(data, status) {
			console.log('Request failed' || data)
		});
	}
}

function StaffController($scope, $http) {
	
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_staff_list($scope, $http);
		reset_staff_details($scope);
	}
	$scope.create_staff = function(){
		$('#view_staff').css('display', 'none');
		$('#add_staff').css('display', 'block');
		$scope.is_edit = false;
		reset_staff_details($scope);
		create_popup()
	}
	$scope.save_staff = function() {
		save_staff($scope, $http, 'staff');
	}
	$scope.edit_staff = function(staff) {
		$('#view_staff').css('display', 'none');
		$('#add_staff').css('display', 'block');
		$scope.is_edit = true;
		$scope.address = staff.address;
		$scope.staff_details.first_name = staff.first_name;
		$scope.staff_details.last_name = staff.last_name;
		$scope.staff_details.username = staff.username;
		$scope.staff_details.email = staff.email;
		$scope.staff_details.designation = staff.designation;
		$scope.staff_details.contact_no = staff.contact_no;
		$scope.staff_details.id = staff.id;
		create_popup();
	}
	$scope.hide_popup = function(){
		hide_popup();
	}
	$scope.view_staff_details = function(staff) {
		$scope.staff_details = staff;
		$('#view_staff').css('display', 'block');
		$('#add_staff').css('display', 'none');
		create_popup();
	}
	$scope.delete_staff = function(staff) {
		document.location.href = '/delete_staff/?staff_id='+staff.id;
	}
	$scope.check_username_exists = function() {
		check_username_exists($scope, $http);
	}
	$scope.select_page = function(page) {
		select_page(page, $scope.staffs, $scope, 10)
	}
	$scope.range = function(n) {
        return new Array(n);
    }
    $scope.get_staffs_list = function() {
    	search_staff($scope, $http);
    }
}

function PermissionController($scope, $http) {
	$scope.no_staff_error = false;
	$scope.permission = {
		'staff': '',
		'accounts_permission': false,
		'inventory_permission': false,
		'purchase_permission': false,
		'sales_permission': false,
		'suppliers': false,
		'customers': false,
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		reset_staff_details($scope);
	}
	$scope.search_staff = function() {
		$scope.select_staff_flag = true;
		search_staff($scope, $http);
	}
	$scope.save_staff = function() {
		save_staff($scope, $http, 'permission');
	}
	$scope.get_staff_details = function(staff) {
		$scope.select_staff_flag = false;
		$scope.staff_name = staff.name;
		$scope.permission.staff = staff.id;
		$scope.staffs = [];
		if (staff.accounts_permission == 'true') {
			$scope.permission.accounts_permission = true;
		} else {
			$scope.permission.accounts_permission = false;
		}
		if (staff.inventory_permission == 'true') {
			$scope.permission.inventory_permission = true;
		} else {
			$scope.permission.inventory_permission = false;
		}
		if (staff.purchase_permission == 'true') {
			$scope.permission.purchase_permission = true;
		} else {
			$scope.permission.purchase_permission = false;
		}
		if (staff.sales_permission == 'true') {
			$scope.permission.sales_permission = true;
		} else {
			$scope.permission.sales_permission = false;
		}
		if (staff.customers == 'true') {
			$scope.permission.customers = true;
		} else {
			$scope.permission.customers = false;
		}
		if (staff.suppliers == 'true') {
			$scope.permission.suppliers = true;
		} else {
			$scope.permission.suppliers = false;
		}
	}
	$scope.save_permissions = function() {

		$scope.validate_staff_permission = '';
		if ($scope.permission.staff == '' || $scope.permission.staff == undefined) {
			$scope.validate_staff_permission = 'Please choose the Staff';
		} else if ($scope.no_staff_error) {
			$scope.validate_staff_permission = 'No such staff';
		} else {
			show_loader();
			if ($scope.permission.accounts_permission == true) {
				$scope.permission.accounts_permission = 'true';
			} else {
				$scope.permission.accounts_permission = 'false';
			}
			if ($scope.permission.inventory_permission == true) {
				$scope.permission.inventory_permission = 'true';
			} else {
				$scope.permission.inventory_permission = 'false';
			}
			if ($scope.permission.purchase_permission == true) {
				$scope.permission.purchase_permission = 'true';
			} else {
				$scope.permission.purchase_permission = 'false';
			}
			if ($scope.permission.sales_permission == true) {
				$scope.permission.sales_permission = 'true';
			} else {
				$scope.permission.sales_permission = 'false';
			}
			if ($scope.permission.customers == true) {
				$scope.permission.customers = 'true';
			} else {
				$scope.permission.customers = 'false';
			}
			if ($scope.permission.suppliers == true) {
				$scope.permission.suppliers = 'true';
			} else {
				$scope.permission.suppliers = 'false';
			}
			params = {
				'staff_permission': angular.toJson($scope.permission),
				'csrfmiddlewaretoken': $scope.csrf_token,
			}
			$http({
				method:'post',
				url: '/permissions/',
				data: $.param(params),
				headers: {
					'Content-Type' : 'application/x-www-form-urlencoded'
				}
			}).success(function(data){
				hide_loader();
				document.location.href = '/permissions/';
			}).error(function(data, status) {
				console.log('Request failed' || data);
			})
		}
	}
	$scope.new_staff = function() {
		$scope.select_staff_flag = false;
		create_popup();
	}
	$scope.check_username_exists = function() {
		check_username_exists($scope, $http);
	}
}

function SalesmenController($scope, $http){
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		$scope.salesman = {
			'first_name': '',
			'last_name': '',
			'address': '',
			'contact_no': '',
			'email': '',
		}
		get_salesmen_list($scope, $http);
	}
    $scope.create_salesman = function(){
        $('#popup_overlay').css('display', 'block');
        $('#dialogue_popup_container').css('height', '100%')
        $('#dialogue_popup_container').css('display', 'block')
        $('#dialogue_popup').css('display', 'block');
    }
    $scope.hide_popup = function() {
        $scope.salesman= {
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
    $scope.save_salesman = function() {
		save_salesman($scope, $http);
	}
	$scope.edit_salesman_details = function(salesman){
        $scope.salesman = salesman;
        $scope.create_salesman();
	}
	$scope.delete_salesman = function(salesman) {
		document.location.href = '/delete_salesman/?id='+salesman.id;
	}
	$scope.get_salesmen_list = function(){
		search_salesmen($scope, $http);
	}
}

function IncentivesController($scope, $http){
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		$scope.salesman_name = '';
		$scope.start_date = '';
		$scope.end_date = '';
		$scope.no_of_sales = '';
		$scope.incentive_per_sale = '';
		$scope.total_incentive = ''
	}
    $scope.search_salesman = function(){
		if($scope.salesman_name.length == 0){
			$scope.salesmen = "";
			$scope.no_salesman_message = "";
		}
		else{
			search_salesmen($scope,$http);
		}	
	}
	$scope.select_salesman = function(salesman){
		$scope.salesman_name = salesman.name;
		$scope.salesman = salesman.id;
		$scope.salesmen = [];
	}
	$scope.get_sales = function () {
		$scope.error_msg = '';
		$scope.start_date = $('#start_date').val();
		$scope.end_date = $('#end_date').val();
		if($scope.start_date !='' && $scope.end_date !='' && $scope.salesman != ''){
			$http.get('/salesman/sales/?salesman_id='+$scope.salesman+'&start_date='+$scope.start_date+'&end_date='+$scope.end_date).success(function(data){
				$scope.no_of_sales = parseInt(data.no_of_sales);	
				if(data.no_of_sales<=0)		{
					$scope.error_msg = 'No sales';
				}
			}).error(function(data, status){
				console.log('Request failed' || data)
			});
		} else {
			$scope.error_msg = "Please fill all fields";
		}	
	}
	$scope.calculate_total_incentive = function(){
		$scope.total_incentive = $scope.no_of_sales * $scope.incentive_per_sale;
	}
}