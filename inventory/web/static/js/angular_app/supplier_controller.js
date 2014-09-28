/************************************ Supplier - common js methods ****************************************/

function get_accounting_suppliers($scope, $http) {
    show_loader();
    $http.get('/suppliers/supplier_list/').success(function(data){
        hide_loader();
        if (data.result == 'ok') {
            if (data.suppliers.length > 0) {
                $scope.suppliers = data.suppliers;
                paginate($scope.suppliers, $scope, 15);
            }
        } else{
            $scope.message = data.message;
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_supplier_search_list($scope, $http) {
    $scope.no_supplier_msg = '';
    if ($scope.supplier_name != '' && $scope.supplier_name != undefined && $scope.supplier_name.length > 0) {
        var supplier_name = $scope.supplier_name;
        show_loader();
        $http.get('/suppliers/search_supplier/?name='+supplier_name).success(function(data){
            hide_loader();
            $scope.no_supplier_msg = '';
            if (data.suppliers.length == 0) {
                $scope.no_supplier_msg = 'No such supplier';
                $scope.suppliers = [];
            } else {
                $scope.suppliers = data.suppliers;
                paginate($scope.suppliers, $scope, 15);
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
} 

function validate_supplier($scope) {
    if ($scope.supplier.name == '' || $scope.supplier.name == undefined) {
        $scope.validate_supplier_error_msg = 'Please enter the name';
        return false;
    } else if ($scope.supplier.address == '' || $scope.supplier.address == undefined) {
        $scope.validate_supplier_error_msg = 'Please enter the address';
        return false;
    } else if ($scope.supplier.mobile == '' || $scope.supplier.mobile == undefined) {
        $scope.validate_supplier_error_msg = 'Please enter the mobile';
        return false;
    } else if (!Number($scope.supplier.mobile) || $scope.supplier.mobile.length != 10) {
        $scope.validate_supplier_error_msg = 'Please enter a valid mobile number';
        return false;
    } else if ($scope.supplier.telephone_number && !Number($scope.supplier.telephone_number)) {
        $scope.validate_supplier_error_msg = 'Please enter a valid telephone number';
        return false;
    } 
    // else if ($scope.supplier.email == '' || $scope.supplier.email == undefined) {
    //     $scope.validate_supplier_error_msg = 'Please enter the email';
    //     return false;
    // } else if (!validateEmail($scope.supplier.email)) {
    //     $scope.validate_supplier_error_msg = 'Please enter a valid email';
    //     return false;
    // } 
    return true;
}

function save_supplier($scope, $http, from) {
    params = {
        'supplier': angular.toJson($scope.supplier),
        "csrfmiddlewaretoken": $scope.csrf_token,
    }
    if (validate_supplier($scope)) {
        show_loader();
        $http({
            method: 'post',
            url: '/suppliers/add_supplier/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            $scope.validate_supplier_error_msg = '';
            $scope.no_supplier_msg = '';
            if (data.result == 'error') {
                $scope.validate_supplier_error_msg = data.message;
            } else {
                if (from == 'purchase') {
                    $scope.current_purchase.supplier = data.supplier.id;
                    $scope.supplier_name = data.supplier.name;
                    hide_popup();
                } else 
                    document.location.href = '/suppliers/supplier_list/';
            }
        }).error(function(data, status) {   
            console.log('Request failed' || data);
        });
    }
}

/************************************ Supplier - common js methods - end ************************************/

function SupplierController($scope, $http){
    $scope.supplier= {
        'name': '',
        'address': '',
        'mobile': '',
        'telephone_number': '',
        'email': '',
    }
    $scope.select_page = function(page){
        select_page(page, $scope.suppliers, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.init = function(csrf_token, supplier_id){
        $scope.csrf_token = csrf_token;
        get_accounting_suppliers($scope, $http);
    }
    $scope.create_supplier = function(){
        $('#popup_overlay').css('display', 'block');
        $('#dialogue_popup_container').css('height', '100%')
        $('#dialogue_popup_container').css('display', 'block')
        $('#dialogue_popup').css('display', 'block');
    }
    $scope.save_supplier = function() {
        save_supplier($scope, $http);
    }
    $scope.get_supplier_list = function(){
        if($scope.supplier_name.length == 0)
            get_accounting_suppliers($scope, $http);
        else
            get_supplier_search_list($scope, $http);
    }
    $scope.edit_supplier_details = function(supplier){
        $scope.supplier = supplier;
        $scope.create_supplier();
    }
    $scope.delete_supplier = function(supplier) {
        document.location.href = '/suppliers/delete_supplier/?supplier_id='+supplier.id;
    }
    $scope.hide_popup = function() {
        $scope.supplier= {
            'name': '',
            'address': '',
            'mobile': '',
            'telephone_number': '',
            'email': '',
        }
        $scope.validate_supplier_error_msg = "";
        $('#dialogue_popup_container').css('display', 'none');
        $('#popup_overlay').css('display', 'none');
    }
}
function AccountPayableController($scope, $http) {
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
        $http.get('/suppliers/account_payable/').success(function(data){
            $scope.supplier_details = data.supplier_details;
            paginate($scope.supplier_details, $scope, 15);
        }).error(function(data, status){
            console.log('Request failed' || data);
        });
    }
    $scope.generate_report = function() {
        document.location.href = '/suppliers/account_payable/?pdf=true';
    }
    $scope.select_page = function(page){
        select_page(page, $scope.suppliers, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}