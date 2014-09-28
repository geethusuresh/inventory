function paginate(list, $scope, page_interval) {
    if(!page_interval)
        $scope.page_interval = 20;
    else 
        $scope.page_interval = page_interval;
    $scope.current_page = 1;
    $scope.pages = list.length / $scope.page_interval;
    if($scope.pages > parseInt($scope.pages))
        $scope.pages = parseInt($scope.pages) + 1;
    $scope.visible_list = list.slice(0, $scope.page_interval);
}
    
function select_page(page, list, $scope, page_interval) {
    if(!page_interval)
        $scope.page_interval = 20;
    var last_page = page - 1;
    var start = (last_page * $scope.page_interval);
    var end = $scope.page_interval * page;
    $scope.visible_list = list.slice(start, end);
    $scope.current_page = page;
}

function validateEmail(email) { 
    var re = /\S+@\S+\.\S+/;
    return re.test(email);
}
function create_popup() {
    $('#popup_overlay').css('display', 'block');
    $('#dialogue_popup_container').css('height', '100%');
    $('#dialogue_popup_container').css('display', 'block');
    $('#dialogue_popup').css('display', 'block');
}
function hide_popup() {
    $('#dialogue_popup_container').css('display', 'none');
    $('#popup_overlay').css('display', 'none');
}
function show_loader(){
    $('#overlay').css('display', 'block');
    $('.spinner').css('display', 'block');
}
function hide_loader(){
    $('#overlay').css('display', 'none');
    $('.spinner').css('display', 'none');
}
function show_dropdow(){
    $('#dropdown_menu').css('display', 'block');
}
function hide_dropdown(){
    $('#dropdown_menu').css('display', 'none');
}
function MenuController($scope, $element, $http, $timeout, $location)
{
    $scope.init = function(user){
        $scope.menu_visible = true;
    }
    $scope.show_submenu = function(event) {
        var target = $(event.currentTarget);
        var element = target.parent().find('ul').first();
        var height_property = element.css('height');
        if(height_property == '0px') {
            element.animate({'height': '100%'}, 500);
            target.addClass('submenu_open').removeClass('submenu_closed');

        } else {
            element.animate({'height': '0px'}, 500);
            target.addClass('submenu_closed').removeClass('submenu_open');
        }
    } 
    $scope.toggle_menu = function(selector) {
        var element = $(selector);
        if($scope.menu_visible){
            element.animate({'right': '-18%'}, 500);
            $('.menu_toggler').removeClass('open').addClass('closed');
            $scope.menu_visible = false;
        } else {
            element.animate({'right': '0%'}, 500);
            $('.menu_toggler').removeClass('closed').addClass('open');
            $scope.menu_visible = true;
        }
    }
}
function HomeController($scope, $element, $http, $timeout, $location)
{
    $scope.init = function(csrf_token){
        $scope.csrf_token = csrf_token;
        $scope.reset_shope_details();
        show_loader();
        $http.get('/').success(function(data){
            hide_loader();
            if (data.result == 'ok') {
                console.log(data.shope_details.length);
                if (data.shop_exists) {
                    $scope.shope = data.shope_details;
                } else {
                    $scope.show_shope_details();
                }
            } else{
                $scope.message = data.message;
            }
        }).error(function(data, status){
            $scope.message = data.message;
        })
    }
    $scope.show_shope_details = function() {
        create_popup();
    }    
    $scope.save_shope = function() {
        if($scope.validate_shop()){
            show_loader();
            params = {
                'name': $scope.name,
                'address': $scope.address,
                'email': $scope.email,
                'contact_no': $scope.contact_no,
                'csrfmiddlewaretoken': $scope.csrf_token,
            }
            $http({
                method: 'post',
                url: '/shope/',
                data: $.param(params),
                headers: {
                    'Content-Type' : 'application/x-www-form-urlencoded'
                }
            }).success(function(data){
                hide_loader();
                hide_popup();    
                $scope.reset_shope_details();      
                document.location.href = "/";
            }).error(function(data, status){
                console.log('Request failed' || data);
            });
        }
    }
    $scope.reset_shope_details = function() {
        $scope.address = '';
        $scope.email = '';
        $scope.address = '';
        $scope.contact_no = '';
    }
    $scope.validate_shop = function () {
        $scope.validation_message = '';
        if ($scope.name == '') {
            $scope.validation_message = 'Please enter name';
            return false;
        } else if ($scope.email!='' && !validateEmail($scope.email)) {
            $scope.validation_message = 'Please enter a valid email';
            return false;
        } else if ($scope.contact_no == '') {
            $scope.validation_message = 'Please enter contact no';
            return false;
        } else if ($scope.contact_no.length > 15 || $scope.contact_no.length < 9) {
            $scope.validation_message = 'Please enter a valid contact no';
            return false;
        } else if ($scope.address == '') {
            $scope.validation_message = 'Please enter address';
            return false;
        }
        return true;
    }
}

