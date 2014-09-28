
/************************************ Inventory - common js methods ****************************************/
function hide_inventory_item_popup_div($scope) {
	$('#add_brand').css('display', 'none');
    $('#add_product').css('display', 'none');
    $('#add_vat').css('display', 'none');
}
function hide_opening_stock_popup_divs() {
    $('#calculate_quantity_div').css('display', 'none');
    $('#search_items').css('display', 'none');
    $('#new_batch').css('display', 'none');
    $('#add_item').css('display', 'none');
    $('#transaction_reference_no_details').css('display', 'none');
}
function get_conversions($scope, $http, uom, unit) {
    var url = '/inventory/uom_conversion/';
    if (uom && unit) {
        url = '/inventory/uom_conversion/?'+unit+'='+uom;
    }
    $http.get(url).success(function(data){
        $scope.uoms = data.uoms;
        $scope.conversions = data.conversions;
        if (uom && unit) {
            if($scope.current_purchase_item){
            $scope.current_purchase_item.conversions = data.conversions;
            } else if($scope.current_item_details){
                $scope.current_item_details.conversions = data.conversions;
            }
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_product_search_list($scope, $http, category_wise) {
    $scope.products = [];
    $scope.no_product_msg = '';
    $scope.category_wise = '';
    $scope.category_wise = category_wise;
    var url = '';
    if ($scope.category_wise != undefined && $scope.category_wise != '' && $scope.product_name != '' && $scope.product_name != undefined && $scope.product_name.length > 0){
    	url = '/inventory/search_product/?product_name='+$scope.product_name+'&category_id='+$scope.category_wise;
    }else if ($scope.product_name != '' && $scope.product_name != undefined && $scope.product_name.length > 0) {
        var product_name = $scope.product_name;
    	url = '/inventory/search_product/?product_name='+product_name;
    }
    if (url != '') {
        show_loader();
        $http.get(url).success(function(data){
            hide_loader();
            $scope.no_product_msg = '';
            if (data.products.length == 0) {
                $scope.no_product_msg = 'No such product';
                $scope.products = [];
            } else {
                $scope.products = data.products;
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}

function get_item_search_list($scope, $http, item, batch, from) {
    var url = ''
    if($scope.item_name){
    	url = '/inventory/search_item/?'+'item_name'+'='+$scope.item_name;
    }
    else{
    	url = '/inventory/search_item/?'+'item_name'+'='+item+'&batch='+batch;
    }
    if (url) {
        show_loader();
        $http.get(url).success(function(data)
        {
            var item_name = $scope.item_name;
            $scope.no_item_msg = '';
            hide_loader();
            if (data.items.length == 0) {
                $scope.no_item_msg = 'No such item';
                $scope.items = [];
            } else {
                $scope.items = data.items;
                if (from == 'purchase') {
                    $scope.current_purchase_item.items = data.items; 
                }else if (from == 'opening_stock'){
                    $scope.current_item_details.items = data.items; 
                }
                if($scope.items.length == 0)
                    $scope.no_item_msg = "No such item";
            }
            paginate($scope.items, $scope, 15);
        }).error(function(data, status)
        {
            console.log(data || "Request failed");
        });
    }
}
function get_category_search_list($scope, $http) {
    $scope.categories_list = [];
    $scope.no_category_msg = '';
    if ($scope.category_name != '' && $scope.category_name != undefined && $scope.category_name.length > 0) {
        var category_name = $scope.category_name;
        show_loader();
        $http.get('/inventory/search_category/?name='+category_name).success(function(data){
            hide_loader();
            $scope.no_category_msg = '';
            if (data.categories.length == 0) {
                $scope.no_category_msg = 'No such category';
                $scope.categories_list = [];
            } else {
                $scope.categories_list = data.categories;
            }
            paginate($scope.categories_list, $scope, 15);
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}
function get_brand_search_list($scope, $http) {
    $scope.brands = [];
    $scope.no_brand_msg = '';
    if ($scope.brand_name != '' && $scope.brand_name != undefined && $scope.brand_name.length > 0) {
        var brand_name = $scope.brand_name;
        show_loader();
        $http.get('/inventory/search_brand/?brand_name='+brand_name).success(function(data){
            hide_loader();
            $scope.no_brand_msg = '';
            if (data.brand_list.length == 0) {
                $scope.no_brand_msg = 'No such brand';
                $scope.brands = [];
            } else {
                $scope.brands = data.brand_list;
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}
function get_vat_search_details($scope,$http) {
    $scope.vat_list = [];
    $scope.no_vat_msg = '';
    if ($scope.vat_type != '' && $scope.vat_type != undefined && $scope.vat_type.length > 0) {
        var vat_type = $scope.vat_type;
        show_loader();
        $http.get('/inventory/search_vat/?vat_type='+vat_type).success(function(data){
            hide_loader();
            $scope.no_vat_msg = '';
            $scope.vat_list = data.vat_list;
            $scope.vats = data.vat_list;
            if (data.vat_list.length == 0) {
                $scope.no_vat_msg = 'No such vat';
                $scope.vat_list = [];
            } 
            paginate($scope.vats, $scope, 10);
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}
function get_inventory_categories($scope, $http) {
    show_loader();
    $http.get('/inventory/categories/').success(function(data){
        hide_loader();
        if (data.result == 'ok') {
            if (data.categories.length > 0) {
                $scope.categories = data.categories;
                paginate($scope.categories, $scope, 5);
            } 
        } else {
            $scope.message = data.message;
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_brands($scope, $http) {
    show_loader();
    $http.get('/inventory/brands/').success(function(data){
        hide_loader();
        $scope.brands = data.brands;
        if ($scope.brands.length > 0) {
            paginate($scope.brands, $scope, 15);
        } 
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_vats($scope, $http){
    show_loader();
    $http.get('/inventory/vat/').success(function(data){
        hide_loader();
        $scope.vats = data.vats;
        if ($scope.vats.length > 0) {
            paginate($scope.vats, $scope, 10);
        } 
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_items($scope, $http){
    show_loader();
    $http.get('/inventory/items/').success(function(data){
        hide_loader();
        $scope.items = data.items;
        paginate($scope.items, $scope, 15);
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_batches($scope, $http){
    show_loader();
    $http.get('/inventory/batches/').success(function(data){
        hide_loader();
        $scope.batches = data.batches;
        if ($scope.batches.length > 0) {
            paginate($scope.batches, $scope, 15);
        } 
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_batch_items_list($scope, $http){
    $scope.batch_items_list = [];
    $scope.no_batch_item_msg = '';
    if ($scope.batch_name != '' && $scope.batch_name != undefined && $scope.batch_name.length > 0) {
        var batch_name = $scope.batch_name;
        var item = $scope.item;
        show_loader();
        $http.get('/inventory/search_batch_item/?item='+item+'&batch='+batch_name).success(function(data){
            hide_loader();
            $scope.no_batch_item_msg = '';
            if (data.batch_items.length == 0) {
                $scope.no_batch_item_msg = 'No such batch';
                $scope.batch_items_list = [];
            } else {
                $scope.batch_items_list = data.batch_items;
                if($('#sales').length > 0)
                    $scope.current_sales_item.batches = data.batch_items;
                else if($('#estimate').length > 0)
                    $scope.current_estimate_item.batches = data.batch_items;
            }
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}
function get_inventory_products($scope, $http) {
    show_loader();
    $http.get('/inventory/products/').success(function(data){
        hide_loader();
        if (data.result == 'ok') {
            $scope.products = data.products;
            if ($scope.products.length > 0){
                paginate($scope.products, $scope, 15);
            } 
        } else {
            $scope.message = data.message;
        }
    }).error(function(data, status){
        $scope.message = data.message;
    })
}
function get_category_subcategory_list($scope, $http) {
    $http.get('/inventory/categories_tree_view/').success(function(data){
        $scope.categories = data.categories;
        for (var i=0; i<$scope.categories.length; i++) {
            $scope.categories[i].is_closed = true;
        }
    }).error(function(data, status){
        console.log('Request failed' || data);
    })
}
function get_subcategory_list($scope, $http, category_id, view_type) {
    $http.get('/inventory/subcategory_list/'+category_id+'/').success(function(data){
        if (view_type == 'edit') {
            $scope.categories_details = data.category_details[0];
        } else {
            $scope.current_category.subcategories = data.subcategories;
            $scope.current_category.temp_subcategories = data.subcategories;
        }
    }).error(function(data, status){
        console.log('Request failed' || data);
    })
}
function validate_category($scope) {
    if ($scope.categry.name == '' || $scope.categry.name == undefined) {
        $scope.validate_category_error_msg = 'Please enter the name';
        return false;
    } else if($scope.no_category_msg != undefined && $scope.no_category_msg.length > 0) {
        $scope.validate_category_error_msg = "Parent doesn't exists";
        return false;
    } return true;
}
function save_category($scope, $http, view_type) {
    params = {
        'category': angular.toJson($scope.categry),
        "csrfmiddlewaretoken": $scope.csrf_token,
    }
    if (validate_category($scope)) {
        show_loader();
        $http({
            method: 'post',
            url: '/inventory/add_category/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            $scope.validate_category_error_msg = '';
            if (data.result == 'error') {
                $scope.validate_category_error_msg = data.message;
            } else {
                if (view_type == 'tree') {
                    // document.location.href = '/inventory/categories_tree_view/';
                    hide_popup();
                    if($scope.selected_parent_catergory){
                        if (data.new_category.parent != '')
                            $scope.selected_parent_catergory.subcategories.push(data.new_category);
                        else {
                            $scope.categories.push(data.new_category);
                        }
                    } else {
                        $scope.categories.push(data.new_category);
                    }
                } else {
                    document.location.href = '/inventory/categories/';
                }
            }
        }).error(function(data, status) {   
            console.log('Request failed' || data);
        });
    }
}
function validate_item($scope) {
    if ($scope.item.name == '' || $scope.item.name == undefined) {
        $scope.validate_item_error_msg = 'Please enter the name';
        return false;
    } else if($scope.item.product == '' || $scope.item.product == undefined){
        $scope.validate_item_error_msg = 'Please enter a product';
        return false;
    } else if($scope.item.brand == '' || $scope.item.brand == undefined){
        $scope.validate_item_error_msg = 'Please enter a brand';
        return false;
    } else if ($scope.item.cess && ($scope.item.cess != Number($scope.item.cess))) {
        $scope.validate_item_error_msg = 'Please enter valid cess';
        return false;
    } else if ($scope.item.offer_quantity != Number($scope.item.offer_quantity)) {
        $scope.validate_item_error_msg = 'Please enter valid Offer Quantity';
        return false;
    }return true;
}
function save_item($scope, $http, from){
    if ($scope.item.description == null) {
        $scope.item.description = '';
    }
    if ($scope.item.barcode == null) {
        $scope.item.barcode = '';
    }
    if ($scope.item.size == null) {
        $scope.item.size = '';
    }
    params = {
        'item': angular.toJson($scope.item),
        'csrfmiddlewaretoken': $scope.csrf_token,
    }
    if(validate_item($scope)){
        show_loader();
        $http({
            method: 'post',
            url: '/inventory/add_item/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            if (data.result == 'ok') {
                if (from == 'purchase') {
                    $scope.current_purchase_item.name = data.item.name;
                    $scope.current_purchase_item.id = data.item.id;
                    $scope.current_purchase_item.code = data.item.code;
                    hide_popup();
                    $scope.get_batch($scope.current_purchase_item);
                } else if(from == 'opening_stock'){
                    $scope.current_item_details.name = data.item.name;
                    $scope.current_item_details.id = data.item.id;
                    $scope.current_item_details.code = data.item.code;
                    hide_popup();
                }else
                    document.location.href = '/inventory/items/';
            } else {
                $scope.validate_item_error_msg = data.message;
            }
        }).error(function(data, status){
            console.log('Request failed'||data);
        });
    }
}
function validate_batch($scope) {
    if ($scope.batch.name == '' || $scope.batch.name == undefined) {
        $scope.validate_batch_error_msg = 'Please enter the batch name';
        return false;
    } else if ($scope.batch.created_date == '' || $scope.batch.created_date == undefined) {
        $scope.validate_batch_error_msg = 'Please enter the created date';
        return false;
    } else if ($scope.batch.expiry_date == '' || $scope.batch.expiry_date == undefined) {
        $scope.validate_batch_error_msg = 'Please enter the expiry date';
        return false;
    } return true;
}
function save_batch($scope, $http, from) {
    if (validate_batch($scope)) {
        show_loader();
        params = {
            'batch_details': angular.toJson($scope.batch),
            'csrfmiddlewaretoken': $scope.csrf_token,
        }
        $http({
            method:'post',
            url: '/inventory/add_batch/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            console.log(data.result);
            if (data.result == 'ok') {
                if (from == 'purchase') {
                    $scope.current_purchase_item.batch = data.id;
                    $scope.current_purchase_item.batch_name = data.name;
                    $scope.get_batch($scope.current_purchase_item);
                    hide_popup();
                } else if(from == 'opening_stock'){
                    console.log(data)
                    $scope.current_item_details.batch = data.id;
                    $scope.current_item_details.batch_name = data.name;
                    console.log($scope.current_item_details)
                    $scope.get_batch($scope.current_item_details);
                    hide_popup();
                }else
                    document.location.href = '/inventory/batches/';
            } else {
                $scope.validate_batch_error_msg = data.message;
            }   
        }).error(function(data, status){
            console.log('Request failed' || data);
        });
    }
}
function get_batch_search_details($scope, $http, from) {
    $scope.batches = [];
    $scope.no_batch_msg = '';
    
    if ($scope.batch_name != '' && $scope.batch_name != undefined && $scope.batch_name.length > 0) {
        var batch_name = $scope.batch_name;
        show_loader();
        $http.get('/inventory/search_batch/?batch_name='+batch_name).success(function(data){
            hide_loader();
            $scope.no_batch_msg = '';
            if (data.batches.length == 0) {
                $scope.no_batch_msg = 'No such batch';
                $scope.batches = [];
            } else {
                if (from == 'purchase')
                    $scope.current_purchase_item.batches = data.batches;
                else if($('#opening_stock').length > 0)
                    $scope.current_item_details.batches = data.batches;
                else {
                    $scope.batches = data.batches;
                }
            }
            paginate($scope.batches, $scope, 15);
        }).error(function(data, status){
            console.log('Request failed'|| data);
        });
    }
}

function save_brand($scope, $http, from) {
    $scope.validate_brand_error_msg = '';
    if ($scope.brand.name == '' || $scope.brand.name == undefined) {
        $scope.validate_brand_error_msg = 'Please enter brand name';
    } else {
        params = {
            'brand': angular.toJson($scope.brand),
            'csrfmiddlewaretoken': $scope.csrf_token,
        }
        $http({
            method: 'post',
            url: '/inventory/add_brand/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            if (data.result == 'ok') {
                if (from == 'item') {
                    $scope.item.brand = data.brand.id;
                    $scope.brand_name = data.brand.name;
                    $scope.select_brand_flag = false;
                    $scope.brands = [];
                    hide_popup();
                } else
                    document.location.href = '/inventory/brands/';
            } else {
                $scope.validate_brand_error_msg = data.message;
            }
        }).error(function(data, status){
            console.log('Request failed'||data);
        });
    }
}

function validate_product($scope) {
    if ($scope.product_details.name == '' || $scope.product_details.name == undefined) {
        $scope.validate_product_error_msg = 'Please enter the name';
        return false;
    }else if($scope.product_details.category == '' || $scope.product_details.category == undefined){
        $scope.validate_product_error_msg = 'Please enter the category';
        return false;
    } return true;
}

function save_product($scope, $http, from) {
    if (validate_product($scope)) {
        params = {
            'product': angular.toJson($scope.product_details),
            "csrfmiddlewaretoken": $scope.csrf_token,
        }
        show_loader();
        $http({
            method: 'post',
            url: '/inventory/add_product/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            $scope.validate_product_error_msg = '';
            if (data.result == 'error') {
                $scope.validate_product_error_msg = data.message;
            } else {
                if (from == 'item') {
                    $scope.selected_product_flag = false;
                    hide_popup();
                    $scope.item.product = data.product.id;
                    $scope.product_name = data.product.name;
                    $scope.products = [];
                } else  
                    document.location.href = '/inventory/products/';
            }
        }).error(function(data, status) {   
            console.log('Request failed' || data);
        });
    }
}
function validate_vat_type($scope) {
    if ($scope.vat.name == '' || $scope.vat.name == undefined) {
        $scope.validate_vat_error_msg = 'Please enter the vat type';
        return false;
    }else if($scope.vat.tax_percentage == '' || $scope.vat.tax_percentage == undefined || !Number($scope.vat.tax_percentage)){
        $scope.validate_vat_error_msg = 'Please enter the percentage';
        return false;
    } return true;
}

function save_vat($scope, $http, from) {
    if(validate_vat_type($scope)) {
        params = {
        'vat': angular.toJson($scope.vat),
        'csrfmiddlewaretoken': $scope.csrf_token,
        }
        show_loader();
        $http({
            method: 'post',
            url: '/inventory/add_vat/',
            data : $.param(params),
            headers : {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
        }).success(function(data){
            hide_loader();
            if (data.result == 'ok') {
                if (from == 'item') {
                    $scope.item.vat = data.vat.id;
                    $scope.vat_type = data.vat.name + ' - ' + data.vat.tax;
                    hide_popup();
                    $scope.selected_vat_flag = false;
                    $scope.vat_list = [];

                } else 
                    document.location.href = '/inventory/vat/';
            } else {
                $scope.validate_vat_error_msg = data.message;
            }
        }).error(function(data, status){
            console.log('Request failed'||data);
        });
    }
}

/************************************ Inventory - common js methods - end ************************************/
function CategoryController($scope, $http) {
	$scope.categry = {
		'parent': '',
		'name': '',
	}
	$scope.init = function(csrf_token, category_id) {
		$scope.category_id = category_id;
		$scope.csrf_token = csrf_token;
        $scope.visible_list = []; 
		get_inventory_categories($scope, $http);
		if (category_id) {
			get_subcategory_list($scope, $http, category_id, 'edit');
		}
	}
	$scope.get_category_list = function() {
		get_category_search_list($scope, $http);
	}
	$scope.create_category = function() {
        $scope.no_category_msg = '';
        $scope.category_name = '';
        $scope.categry = {
            'parent': '',
            'name': '',
        }
		create_popup();
	}
	$scope.save_category = function() {
		save_category($scope, $http, 'list');
	}
	$scope.view_category_details = function(category){
		document.location.href = '/inventory/subcategory_details/'+category.id+'/';
	}
	$scope.edit_category_details = function(category){
        console.log(category)
		$scope.categry = category;
        $scope.no_category_msg = '';
        $scope.category_name = '';
		create_popup();
	}
	$scope.delete_category = function(category) {
		document.location.href = '/inventory/delete_category/?category_id='+category.id;
	}
	$scope.edit_subcategory = function(subcategory, category) {
		$scope.categry.parent = category.id;
		$scope.categry.name = subcategory.name;
		$scope.categry.id = subcategory.id;
		$scope.create_category();
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.delete_subcategory = function(subcategory) {
		document.location.href = '/inventory/delete_category/?category_id='+subcategory.id;
	}
	$scope.get_category_details = function(category) {
		$scope.categry.parent = category.id;
		$scope.category_name = category.name;
		$scope.categories_list = [];
	}
    $scope.select_page = function(page){
        select_page(page, $scope.categories, $scope, 5);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}

function ProductController($scope, $http){
	$scope.product_details = {
		'name': '',
		'category': '',
		'id': '',
	}
	$scope.init = function(csrf_token, product_id) {
		$scope.product_id = product_id;
		$scope.csrf_token = csrf_token;
		get_inventory_products($scope,$http);
	}
	$scope.get_category_list = function() {
		get_category_search_list($scope, $http);
	}
    $scope.get_product_list = function() {
        get_product_search_list($scope, $http);
    }
	$scope.select_category_details = function(category) {
		$scope.product_details.category = category.id;
		$scope.category_name = category.name;
		$scope.categories_list = [];
	}
	$scope.create_product = function() {
		create_popup();
	}
	$scope.hide_popup = function() {
		hide_popup()
	}
	$scope.edit_product = function(product){
		$scope.product_details.name = product.name;
		$scope.category_name = product.category_name;
		$scope.product_details.category = product.category;
		$scope.product_details.id = product.id;
		$scope.create_product();
	}
	$scope.save_product = function() {
		save_product($scope, $http);
	}
	$scope.delete_product = function(product) {
		document.location.href = '/inventory/delete_product/?product_id='+product.id;
	}
    $scope.select_page = function(page){
        select_page(page, $scope.products, $scope, 5);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}

function CategoryTreeController($scope, $http) {
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_category_subcategory_list($scope, $http);
	}
	$scope.get_category_list = function() {
		get_category_search_list($scope, $http);
	}
	$scope.show_category_details = function(category) {
		$scope.current_category = category;
		get_subcategory_list($scope, $http, category.id,'subcategory');
	}
	$scope.get_category_details = function(category) {
		$scope.categry.parent = category.id;
		$scope.category_name = category.name;
		$scope.categories_list = [];
	}
	$scope.add_subcategory = function(category) {
		$scope.categry = {
			'parent': '',
			'name': '',
		}
		$scope.category_name = category.name;
		$scope.categry.parent = category.id;
        $scope.selected_parent_catergory = category;
		create_popup();
	}
	$scope.toggle_category_view = function(event, category) {
        var target = $(event.currentTarget);
        var element = target.parent().find('ul').first();
        var height_property = element.css('height');
        if(height_property == '0px') {
            element.animate({'height': '100%'}, 500);
            target.text('-');
            if(category.subcategories.length == 0){
                $scope.show_category_details(category);
            }
        } else {
            element.animate({'height': '0px'}, 500);
            target.text('+');
        }
    } 
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.create_category = function() {
		$scope.category_name = '';
		$scope.categry = {
			'parent': '',
			'name': '',
		}
		create_popup();
	}
	$scope.save_category = function() {
		save_category($scope, $http, 'tree');
	}
	$scope.edit_subcategory = function(category){
		$scope.categry = {
			'parent': '',
			'name': '',
		}
		$scope.category_name = category.parent_name;
		$scope.categry.parent = category.parent;
		$scope.categry.name = category.name;
		$scope.categry.id = category.id;
		create_popup();
	}
}

function BrandController($scope, $http) {
	$scope.brand = {
		'name': '',
		'id': '',
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_brands($scope, $http);
	}
	$scope.create_brand = function() {
		create_popup();
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.save_brand = function() {
		save_brand($scope, $http);
	}
	$scope.edit_brand_details = function(brand) {
		$scope.brand.name = brand.name;
		$scope.brand.id = brand.id;
		create_popup();
	}
	$scope.delete_brand = function(brand) {
		document.location.href = '/inventory/delete_brand/?brand_id='+brand.id;
	}
    $scope.select_page = function(page){
        select_page(page, $scope.brands, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.get_brands = function() {
        get_brand_search_list($scope, $http);
    }
}

function VatController($scope, $http){

	$scope.vat={
		'id': '',
		'name': '',
		'tax_percentage':0,
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_vats($scope, $http);
	}
	$scope.create_vat = function() {
        $scope.vat={
            'id': '',
            'name': '',
            'tax_percentage':0,
        }
		create_popup();
	}
    $scope.select_page = function(page){
        select_page(page, $scope.vats, $scope, 10);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
	$scope.hide_popup = function() {
		hide_popup();
	}
    $scope.get_vat_list = function() {
        get_vat_search_details($scope, $http);
    }
	$scope.save_vat = function(){
		save_vat($scope, $http);
	}
	$scope.edit_vat_details = function(vat) {
		$scope.vat.name = vat.name;
		$scope.vat.tax_percentage = vat.tax_percentage;
		$scope.vat.id = vat.id;
		create_popup();
	}
	$scope.delete_vat = function(vat) {
		document.location.href = '/inventory/delete_vat/?vat_id='+vat.id;
	}
}

function ItemController($scope, $http){

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
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_items($scope, $http);
	}
	$scope.create_item = function() {
		// create_popup();
        document.location.href = '/inventory/add_item/';
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.save_item = function() {
		save_item($scope, $http);
	}
	$scope.get_products = function() {
        $scope.selected_product_flag = true;
        if($scope.product_name){
            get_product_search_list($scope, $http);
        } else {
            $scope.products = [];
        }

	}
    $scope.get_category_list = function() {
        get_category_search_list($scope, $http);
    }
    $scope.select_category_details = function(category) {
        $scope.product_details.category = category.id;
        $scope.category_name = category.name;
        $scope.categories_list = [];
    }
	$scope.select_product_details = function(product) {
        $scope.selected_product_flag = false;
		$scope.item.product = product.id;
		$scope.product_name = product.name + '-' + product.category_name;
		$scope.products = [];
	}
	$scope.get_brands = function() {
        $scope.select_brand_flag = true;
		get_brand_search_list($scope, $http);
	}
	$scope.select_brand_details = function(brand) {
        $scope.select_brand_flag = false;
		$scope.item.brand = brand.id;
		$scope.brand_name = brand.name;
		$scope.brands = [];
	}
    $scope.new_brand = function() {
        $scope.brand = {
            'name': '',
            'id': '',
        }
        hide_inventory_item_popup_div();
        $('#add_brand').css('display', 'block');
        create_popup();
    }
    $scope.save_brand = function() {
        save_brand($scope, $http, 'item');
    }
    $scope.new_product = function() {
        $scope.product_details = {
            'name': '',
            'category': '',
            'id': '',
        }
        hide_inventory_item_popup_div();
        $('#add_product').css('display', 'block');
        create_popup();
    }
    $scope.save_product = function() {
        save_product($scope, $http, 'item');
    }
	$scope.get_vat_list = function() {
        $scope.selected_vat_flag = true;
		get_vat_search_details($scope, $http);
	}
	$scope.select_vat_details = function(vat) {
        $scope.selected_vat_flag = false;
		$scope.item.vat = vat.id;
		$scope.vat_type = vat.vat_name;
		$scope.vat_list = [];
	}
    $scope.new_vat = function() {
        $scope.vat={
            'id': '',
            'name': '',
            'tax_percentage':0,
        }
        hide_inventory_item_popup_div();
        $('#add_vat').css('display', 'block');
        create_popup();
    }
    $scope.save_vat = function() {
        save_vat($scope, $http, 'item');
    }
	$scope.edit_item_details = function(item) {
		$scope.item = item;
		$scope.product_name = item.product_name;
		$scope.brand_name = item.brand_name;
		$scope.vat_type = item.vat_name;
		create_popup();
	}
	$scope.delete_item = function(item) {
		document.location.href = '/inventory/delete_item/?item_id='+item.id;
	}
    $scope.get_items_list = function() {
        get_item_search_list($scope, $http,$scope.item_name);
    }
    $scope.select_page = function(page){
        select_page(page, $scope.items, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}
function BatchController($scope, $http){
	$scope.batch = {
		'id': '',
		'name': '',
		'created_date':'',
		'expiry_date': '',
	}
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		get_batches($scope, $http);
	}
	$scope.create_batch = function() {
		create_popup();
	}
	$scope.hide_popup = function() {
		hide_popup();
	}
	$scope.save_batch = function() {
		save_batch($scope, $http);
	}
	$scope.edit_batch_details = function(batch) {
		$scope.batch = batch;
		create_popup();
	}
	$scope.delete_batch = function(batch) {
		document.location.href = '/inventory/delete_batch/?batch_id='+batch.id;
	}
    $scope.select_page = function(page){
        select_page(page, $scope.batches, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
    $scope.get_batch_list = function() {
        get_batch_search_details($scope, $http);
    }
}
function OpeningStockController($scope, $http){
	
	// $scope.opening_stock = {
	// 	'id': '',
	// 	'product': '',
	// 	'category': '',
	// 	'brand': '',
	// 	'item_details': [],
	// 	'batch': '',
	// };
    $scope.product_name = "";
    $scope.opening_stock_items = [
        {
            'item_name': '',
            'code': '',
            'uom': '',
            'batch': '',
            'quantity': '',
            'purchase_price': '',
            'whole_sale_price': '',
            'retail_price': '',
            'net_amount': ''
        },
    ]
    $scope.current_item_details = [];
	$scope.init = function(csrf_token) {
		$scope.csrf_token = csrf_token;
		// $scope.opening_stock.item_details = [];
        get_conversions($scope, $http);
	}
    $scope.add_new_opening_stock_item = function() {
        $scope.opening_stock_items.push(
        {
            'item_name': '',
            'code': '',
            'uom': '',
            'batch': '',
            'quantity': '',
            'purchase_price': '',
            'whole_sale_price': '' ,
            'retail_price': '' ,
            'net_amount': ''
        });
    }
	
	
	$scope.hide_popup = function() {
		hide_popup();
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
    $scope.search_batch = function(item) {
        $scope.current_item_details = item;
        $scope.batch_name = item.batch_name;
        get_batch_search_details($scope, $http);
    }
    $scope.select_batch = function(batch) {
       $scope.batch_selected = true;
        $scope.current_item_details.batch_name = batch.name;
        $scope.current_item_details.batch = batch.id;
        if ($scope.current_item_details.id) {
            $scope.get_batch($scope.current_item_details);
        } 
        $scope.current_item_details.batches = [];
        $scope.current_item_details.batch_search = false;
       
    }
    $scope.get_batch = function(item){
        $http.get('/inventory/batch_item_details/?batch_id='+item.batch+'&item_id='+item.id).success(function(data){
            console.log(data)
            item.stock = data.stock;
            item.conversion_unit = data.conversion_unit;
            item.conversion_unit_name = data.conversion_unit_name;
            item.purchase_unit = data.purchase_unit;
            console.log(data.conversion_unit )
            if (data.purchase_unit.length > 0)
                $scope.current_item_details.uom_exists = true;
            else
                $scope.current_item_details.uom_exists = false;
           
            item.whole_sale_price  = data.whole_sale_price;
            item.retail_price  = data.retail_price;
        }).error(function(data, status) {
            console.log('Request failed' || data);
        });
    }
    $scope.new_batch = function(item) {
        $scope.batch = {
            'id': '',
            'name': '',
            'created_date':'',
            'expiry_date': '',
        }
        $scope.current_item_details = item;
        hide_opening_stock_popup_divs();
        $('#new_batch').css('display', 'block');
        create_popup();
    }
    $scope.save_batch = function() {
        save_batch($scope, $http, 'opening_stock');

    }
    $scope.add_new_item = function(item) {
        $scope.current_item_details = item;
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
        hide_opening_stock_popup_divs();
        $('#add_item').css('display', 'block');
        create_popup();
    }
    $scope.save_item = function() {
        save_item($scope, $http, 'opening_stock');
    }
    $scope.search_items = function(item) {  
        $scope.current_item_details = [];
        $scope.current_item_details = item;
        get_item_search_list($scope, $http, $scope.current_item_details.name, item.batch, 'opening_stock');
    }
	$scope.get_items = function() {
		
		get_item_search_list($scope, $http,$scope.item_name);
	}

	$scope.select_item_details = function(item) {
        $scope.current_item_details.name = item.name;
        $scope.current_item_details.code = item.code;
        $scope.current_item_details.id = item.id;
        $scope.current_item_details.items = [];
        if ($scope.current_item_details.batch) {
            $scope.select_batch($scope.current_item_details.batch);
        }
        $scope.current_item_details.item_search = false;
        
        hide_popup();
        $scope.current_item_details = []
        $scope.items = [];

	}
    $scope.get_conversion_units = function(item) {
        $scope.current_item_details = item;
        get_conversions($scope, $http, item.purchase_unit, 'purchase_unit');
    }
   
    
    $scope.save_quantity = function(item) {
        item.quantity_entered = item.quantity;
    }
    
    $scope.calculate_net_amount = function(item) {
        if (item.purchase_price != Number(item.purchase_price)) {
            item.purchase_price = 0.00;
        } 
        if (item.quantity != Number(item.quantity)) {
            item.quantity = 0.00;
        } 
        item.net_amount = item.quantity*item.purchase_price;
    }
   
    $scope.validate_opening_stock = function(){
        console.log($scope.opening_stock_items)
        console.log($scope.opening_stock_items.length)
        if ($scope.opening_stock_items.length == 0) {
            $scope.validate_opening_stock_msg = 'Please choose Items';
            return false;
        } else if ($scope.opening_stock_items.length > 0) {
            for (var i =0; i<$scope.opening_stock_items.length; i++) {
                if ($scope.opening_stock_items[i].code == '') {
                    $scope.validate_opening_stock_msg = 'Item  cannot be null in row'+ (i+1);
                    return false;
                } else if ($scope.opening_stock_items[i].batch == '') {
                    $scope.validate_opening_stock_msg = 'Please choose batch for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                } else if ($scope.opening_stock_items[i].quantity == '' || !Number($scope.opening_stock_items[i].quantity ) || $scope.opening_stock_items[i].quantity == 0){
                    $scope.validate_opening_stock_msg = 'Please enter quantity for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                } else if ($scope.opening_stock_items[i].purchase_unit == '') {
                    $scope.validate_opening_stock_msg = 'Please choose purchase unit for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                }else if ($scope.opening_stock_items[i].conversion_unit == '') {
                    $scope.validate_opening_stock_msg = 'Please choose Conversion unit for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                }else if ($scope.opening_stock_items[i].whole_sale_price == ''|| !Number($scope.opening_stock_items[i].whole_sale_price )) {
                    $scope.validate_opening_stock_msg = 'Please enter whole sale price for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                }else if ($scope.opening_stock_items[i].retail_price == ''|| !Number($scope.opening_stock_items[i].retail_price )) {
                    $scope.validate_opening_stock_msg = 'Please enter retail price for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                } else if ($scope.opening_stock_items[i].purchase_price == ''|| !Number($scope.opening_stock_items[i].purchase_price )) {
                    $scope.validate_opening_stock_msg = 'Please enter purchase price for the item '+ $scope.opening_stock_items[i].code;
                    return false;
                }
            }
        } return true;
    }
    $scope.remove_opening_stock_item = function(item) {
        var index = $scope.opening_stock_items.indexOf(item);
        $scope.opening_stock_items.splice(index, 1);
    }
    $scope.hide_popup_transaction_details = function() {
        document.location.href = '/inventory/opening_stock/';
    }
	$scope.save_opening_stock = function(){
        console.log($scope.opening_stock_items)
        if($scope.current_item_details.batch_search == false){
            $scope.current_item_details.batch_search = "false";
        }else{
            $scope.current_item_details.batch_search = "true";
        }
        if ($scope.current_item_details.item_search == false){
            $scope.current_item_details.item_search = 'false';
        }else{
            $scope.current_item_details.item_search = 'true';
        }
        if ($scope.current_item_details.uom_exists == true){
            $scope.current_item_details.uom_exists = 'true';
        }else{
            $scope.current_item_details.uom_exists = 'false';
        }
        if ($scope.validate_opening_stock()) {
    		params = {
    			'opening_stock_items': angular.toJson($scope.opening_stock_items),
    			'csrfmiddlewaretoken': $scope.csrf_token,
    			}
    		show_loader();
    		$http({
    			method: 'post',
    			url: '/inventory/save_opening_stock/',
    			data : $.param(params),
                headers : {
                    'Content-Type' : 'application/x-www-form-urlencoded'
                }
    		}).success(function(data){
    			hide_loader();
    			if (data.result == 'ok') {
    				hide_opening_stock_popup_divs()
                    $scope.transaction_reference_no = data.transaction_reference_no;
                    $scope.transaction_name = ' Opening Stock ';
                    $('#transaction_reference_no_details').css('display', 'block');
                    create_popup();
    			} 
    		}).error(function(data, status){
    			console.log('Request failed'||data);
    		});
    	}
    }
}

function StockReportController($scope, $http){
    $scope.batch =  {
        'id': '',
        'batch_name' : '',
    }
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
    }

    $scope.get_batches = function() {
        get_batch_search_details($scope, $http);
    }

    $scope.get_batch_details = function(batch) {
        $scope.batch.id = batch.id;
        
        $scope.batch_name = batch.name;
        $scope.batch.batch_name = batch.name;
        $scope.batches = [];
        
    }
    $scope.view_stock = function(){
        if($scope.batch_name.length > 0 && $scope.batch.batch_name == ''){
            $scope.validate_error_msg = "Please choose a valid batch from the list ";
            $scope.stock_entries = "";
        }
        else
        {
            $scope.validate_error_msg = ""
            show_loader();
            $http.get('/inventory/stock_report?batch_id='+$scope.batch.id).success(function(data){
                hide_loader();
                $scope.stock_entries = data.stock_entries;
                paginate($scope.stock_entries, $scope, 10);
                if($scope.stock_entries.length == 0)
                    $scope.validate_error_msg = "No stock entries found";
            }).error(function(data, status){
                $scope.message = data.message;
            })
        }
    }
    $scope.get_stock_report = function() {
    
        document.location.href = '/inventory/stock_report?batch_id='+$scope.batch.id+'&report_type=pdf';
    }  
    $scope.select_page = function(page){
        select_page(page, $scope.stock_entries, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}

function UOMConversionController($scope, $http) {
    $scope.conversion = {
        'purchase_unit': '',
        'sales_unit': '',
        'relation': '',
        'id': '',
        'status': ''
    }
    $scope.uoms = [];
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
        $scope.get_conversions();
    }
    $scope.get_conversions = function(){
        get_conversions($scope, $http);
    }
    $scope.save_conversion = function(){
        if($scope.conversion.purchase_unit != '' && $scope.conversion.sales_unit != '' && $scope.conversion.relation != ''){
            show_loader();
            params = {
                'conversion': angular.toJson($scope.conversion),
                'csrfmiddlewaretoken': $scope.csrf_token,
            }
            $http({
                method: 'post',
                url: '/inventory/uom_conversion/',
                data : $.param(params),
                headers : {
                    'Content-Type' : 'application/x-www-form-urlencoded'
                }
            }).success(function(data){
                hide_loader();
                $scope.conversion = {
                    'purchase_unit': '',
                    'sales_unit': '',
                    'relation': ''
                }
                $scope.get_conversions();
            }).error(function(data, status){
                console.log('Request failed'||data);
            });
        }        
    }
    $scope.edit_conversion = function(conversion){
        if(conversion.status == 'not used'){
            $scope.conversion = conversion;
        } else {
            $scope.msg = "Selected conversion is already used for stock conversion"
        }
    }
    $scope.delete_conversion = function(conversion){
        if(conversion.status == 'not used'){
            $http.get('/inventory/delete_uom_conversion/'+conversion.id+"/").success(function(data){
                $scope.get_conversions();
            }).error(function(data, status){
                $scope.message = data.message;
            })
        } else {
            $scope.msg = "Selected conversion is already used for stock conversion"
        }
    }
}

function StockViewController($scope, $http) {
    $scope.init = function(csrf_token) {
        $scope.stock_view_visible = false;
        $scope.csrf_token = csrf_token;
    }
    $scope.get_item_stock_list = function() {
        var url = '';
        if($scope.item_name){
            url = '/inventory/search_item_stock/?'+'item_name'+'='+$scope.item_name;
            show_loader();
            $http.get(url).success(function(data)
            {
                var item_name = $scope.item_name;
                $scope.no_item_msg = '';
                hide_loader();
                if (data.items.length == 0) {
                    $scope.no_item_msg = 'No such item';
                    $scope.stock_items = [];
                } else {
                    $scope.stock_items = data.items;                   
                    if($scope.stock_items.length == 0)
                        $scope.no_item_msg = "No such item";
                }
                paginate($scope.stock_items, $scope, 15);
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
    $scope.toggle_stock_search = function(selector, event){
        var element = $(selector);
        var target = $(event.currentTarget);
        if($scope.stock_view_visible){
            element.animate({'margin-top': '-100%'}, 1000);
            element.parent().css('z-index', 3);
            $scope.stock_view_visible = false;
            target.addClass('closed_search').removeClass('open_search');
            $scope.stock_items = [];
        } else {
            element.animate({'margin-top': '0%'}, 1000);
            $scope.stock_view_visible = true;
            element.parent().css('z-index', 4);
            target.removeClass('closed_search').addClass('open_search');
        }
    }
}

function StockAgingReportController($scope, $http) {
    $scope.batch_id =  '';
    $scope.init = function(csrf_token) {
        $scope.csrf_token = csrf_token;
    }
    $scope.get_batches = function() {
        get_batch_search_details($scope, $http);
    }
    $scope.select_batch_details = function(batch) {
        $scope.batch_id = batch.id;
        $scope.batch_name = batch.name;
        $scope.batches = [];
        $scope.get_stock_report();
    }
    $scope.get_stock_report = function() {
        $scope.validate_error_msg = '';
        if ($scope.batch_id == '' || $scope.batch_id == undefined || $scope.batch_id.length == 0) {
            $scope.validate_error_msg = 'Please choose the batch';
        } else {
            $http.get('/inventory/stock_aging_report?batch='+$scope.batch_id).success(function(data) {
                $scope.item_stock = data.stock;
                $scope.months = data.months;
                paginate($scope.item_stock, $scope, 15);
            });
        }
    }  
    $scope.select_page = function(page){
        select_page(page, $scope.item_stock, $scope, 15);
    }
    $scope.range = function(n) {
        return new Array(n);
    }
}