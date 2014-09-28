
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from suppliers.views import Suppliers, AddSupplier, DeleteSupplier, SearchSupplier, AccountPayable

urlpatterns = patterns('',	
	url(r'^supplier_list/$', login_required(Suppliers.as_view(), login_url='/login/'),name='supplier_list'),
	url(r'^add_supplier/$', login_required(AddSupplier.as_view(), login_url='/login/'),name='add_supplier'),
	url(r'^delete_supplier/$', login_required(DeleteSupplier.as_view(), login_url='/login/'),name='delete_supplier'),
	url(r'^search_supplier/$', login_required(SearchSupplier.as_view(), login_url='/login/'), name='search_supplier'),

	url(r'^account_payable/$', login_required(AccountPayable.as_view(), login_url='/login/'), name='account_payable'),
)	