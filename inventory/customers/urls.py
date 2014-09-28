
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from customers.views import Customers, AddCustomer, DeleteCustomer, SearchCustomer, AccountsReceivable, ReceivedReport

urlpatterns = patterns('',	
	url(r'^customer_list/$', login_required(Customers.as_view(), login_url='/login/'),name='customer_list'),
	url(r'^add_customer/$', login_required(AddCustomer.as_view(), login_url='/login/'),name='add_customer'),
	url(r'^delete_customer/$', login_required(DeleteCustomer.as_view(), login_url='/login/'),name='delete_customer'),
	url(r'^search_customer/$', login_required(SearchCustomer.as_view(), login_url='/login/'), name='search_customer'),
	url(r'^accounts_receivable/$', login_required(AccountsReceivable.as_view(), login_url='/login/'),name='accounts_receivable'),
	url(r'^received_report/$', login_required(ReceivedReport.as_view(), login_url='/login/'),name='received_report'),
)	