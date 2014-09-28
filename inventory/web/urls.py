
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import (Home, Login, Logout, StaffList, AddStaff, DeleteStaff, CheckStaffUserExists, \
	SearchStaff, SetPermissions, Salesmen, DeleteSalesman, SearchSalesman, ShopeDetails, Incentives, \
    SalesmanSales)

urlpatterns = patterns('',
    url(r'^$', login_required(Home.as_view(), login_url="login"), name="dashboard"),
    url(r'^login/$', Login.as_view(), name="login"),
    url(r'^logout/$', Logout.as_view(), name="logout"),
    url(r'^staffs/$', login_required(StaffList.as_view(), login_url="login"), name="staffs"),
    url(r'^add_staff/$', login_required(AddStaff.as_view(), login_url="login"), name="add_staff"),
    url(r'^delete_staff/$', login_required(DeleteStaff.as_view(), login_url="login"), name="delete_staff"),
    url(r'^check_staff_user_exists/$', login_required(CheckStaffUserExists.as_view()), name='check_staff_user_exists'),
    url(r'^search_staff/$', login_required(SearchStaff.as_view(), login_url="login"), name='search_staff'),
    
    url(r'^salesmen/$', login_required(Salesmen.as_view(), login_url="login"), name="salesmen"),
    url(r'^delete_salesman/$', login_required(DeleteSalesman.as_view(), login_url="login"), name="delete_salesman"),
    url(r'^search_salesmen/$', login_required(SearchSalesman.as_view(), login_url="login"), name='search_salesmen'),
    url(r'^permissions/$', login_required(SetPermissions.as_view(), login_url="login"), name='permissions'),
    url(r'^shope/$', login_required(ShopeDetails.as_view(), login_url="login"), name='shope'),
    url(r'^incentives/$', login_required(Incentives.as_view(), login_url="login"), name='incentives'),
    url(r'^salesman/sales/$', login_required(SalesmanSales.as_view(), login_url="login"), name='salesman_sales'),

)