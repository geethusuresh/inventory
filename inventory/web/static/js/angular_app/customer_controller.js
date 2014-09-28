/************************************ Customer - common js methods ****************************************/
function get_accounting_customers($scope, $http) {
    show_loader();
    $http.get('/customers/customer_list/').success(function(data){
        hide_loader();
        if (data.result == 'ok') {
            if (data.customers.length > 0) {
                $scope.customers = data.customers;
                paginate($scope.customers, $scope, 15);
            }
        } else{
            $scope.message = data.message;
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_customer_search_list($scope, $http) {
    $scope.no_customer_msg = '';
    if ($scope.customer_name != '' && $scope.customer_name != undefined && $scope.customer_name.length > 0) {
        var customer_name = $scope.customer_name;
        show_loader();
        $http.get('/customers/search_customer/?name='+customer_name).success(function(data){
            hide_loader();
            $scope.no_customer_msg = '';
            if (data.customers.length == 0) {
                $scope.no_customer_msg = 'No such customer';
                $scope.customers = [];
            } else {
                $scope.customers = data.customers;
                paginate($scope.customers, $scope, 15);
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
} 
function validate_customer($scope) {
        if ($scope.customer.name == '' || $scope.customer.name == undefined) {
            $scope.validate_customer_error_msg = 'Please enter the name';
            return false;
        } else if ($scope.customer.address == '' || $scope.customer.address == undefined) {
            $scope.validate_customer_error_msg = 'Please enter the address';
            return false;
        } else if ($scope.customer.mobile == '' || $scope.customer.mobile == undefined) {
            $scope.validate_customer_error_msg = 'Please enter the mobile';
            return false;
        } else if (!Number($scope.customer.mobile) || $scope.customer.mobile.length != 10) {
            $scope.validate_customer_error_msg = 'Please enter a valid mobile number';
            return false;
        } else if ($scope.customer.telephone_number && !Number($scope.customer.telephone_number)) {
            $scope.validate_customer_error_msg = 'Please enter a valid telephone number';
            return false;
        } else if ($scope.customer.email && !validateEmail($scope.customer.email)) {
            $scope.validate_customer_error_msg = 'Please enter a valid email';
            return false;
        } 
        return true;
    }
function save_customer($scope, $http, from){
    params = {
        'customer': angular.toJson($scope.customer),
        "csrfmiddlewaretoken": $scope.csrf_token,
    }
    if (validate_customer($scope)) {
        show_loader();
        $http({
            method: 'post',
            url: '/customers/add_customer/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            $scope.validate_customer_error_msg = '';
            if (data.result == 'error') {
                $scope.validate_customer_error_msg = data.message;
            } else {
                if (from == 'sales') {
                    $scope.current_sales.customer = data.customer.id;
                    $scope.customer_name = data.customer.name;
                    hide_popup();
                } else
                    document.location.href = '/customers/customer_list/';
            }
        }).error(function(data, status) {   
            console.log('Request failed' || data);
        });
    }
}
/************************************ Customer - common js methods - end ************************************/
function CustomerController($scope, $http){
    $scope.customer= {
        'name': '',
        'address': '',
        'mobile': '',
        'telephone_number': '',
        'email': '',
    }
    $scope.init = function(csrf_token, customer_id){
        $scope.csrf_token = csrf_token;
        get_accounting_customers($scope, $http);
    }
    $scope.select_page = function(page){
        select_page(page, $scope.customers, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.create_customer = function(){
        $('#popup_overlay').css('display', 'block');
        $('#dialogue_popup_container').css('height', '100%')
        $('#dialogue_popup_container').css('display', 'block')
        $('#dialogue_popup').css('display', 'block');
    }
    $scope.get_customer_list = function(){
        if($scope.customer_name.length == 0)
            get_accounting_customers($scope, $http);
        else
            get_customer_search_list($scope, $http);
    }
    $scope.save_customer = function() {
        save_customer($scope, $http);
    }
    $scope.edit_customer_details = function(customer){
        $scope.customer = customer;
        $scope.create_customer();
    }
    $scope.delete_customer = function(customer) {
        document.location.href = '/customers/delete_customer/?customer_id='+customer.id;
    }
    $scope.hide_popup = function() {
        $scope.customer= {
            'name': '',
            'address': '',
            'mobile': '',
            'telephone_number': '',
            'email': '',
        }
        $scope.validate_customer_error_msg = "";
        $('#dialogue_popup_container').css('display', 'none');
        $('#popup_overlay').css('display', 'none');
    }
}
function AccountsReceivableController($scope, $http){
    
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
        $http.get('/customers/accounts_receivable').success(function(data)
        {
            $scope.account_receivables = data.account_receivables;
            paginate($scope.account_receivables, $scope, 10);
        }).error(function(data, status)
        {
            console.log(data || "Request failed");
        });
    }
    
    $scope.select_page = function(page){
        select_page(page, $scope.account_receivables, $scope, 10);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.get_account_receivable_report = function(){
        
        document.location.href = '/customers/accounts_receivable?report_type=pdf';
    }
}
function ReceivedReportController($scope, $http){
    $scope.start_date = '';
    $scope.end_date = '';
    $scope.report_details = {
            'start_date': '',
            'end_date': '',
        }
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
    }
    $scope.validate = function(){
        if($scope.start_date == ''){
            $scope.validate_error_msg = 'Please select the start date';
            return false;
        } else if($scope.end_date == ''){
            $scope.validate_error_msg = 'Please select the end date';
            return false;
        } return true;
    }
    $scope.view_ledger = function(){
        if($scope.validate()){
            $scope.validate_error_msg = ""
            $scope.report_details.start_date = $scope.start_date;
            $scope.report_details.end_date = $scope.end_date;
            show_loader();
            $http.get('/customers/received_report?start_date='+$scope.report_details.start_date+'&end_date='+$scope.report_details.end_date).success(function(data){
            hide_loader();
            $scope.ledger_entries = data.ledger_entries;
            paginate($scope.ledger_entries, $scope, 10);
            if($scope.ledger_entries.length == 0)
                $scope.validate_error_msg = "No ledger entries found";
            }).error(function(data, status){
                $scope.message = data.message;
            })
            
        }
    }   
    $scope.select_page = function(page){
        select_page(page, $scope.ledger_entries, $scope, 10);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.get_received_report = function(){
        
       document.location.href = '/customers/received_report?start_date='+$scope.start_date+'&end_date='+$scope.end_date+'&report_type=pdf';
    }
}