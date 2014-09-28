
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from purchases.views import PurchaseEntry, PurchaseReport, PurchaseReturnEntry, PurchaseItemsList, \
PurchaseReturnReport, PurchaseView, PurchaseReturnView


urlpatterns = patterns('',
	url(r'^purchase_entry/$', login_required(PurchaseEntry.as_view(), login_url='/login/'), name='purchase_entry'),
	url(r'^purchase_report/$', login_required(PurchaseReport.as_view(), login_url='/login/'), name='purchase_report'),
	url(r'^purchase_view/$', login_required(PurchaseView.as_view(), login_url='/login/'), name='purchase_view'),

	url(r'^purchase_return_entry/$', login_required(PurchaseReturnEntry.as_view(), login_url='/login/'), name='purchase_return_entry'),
	url(r'^purchase_items/$', login_required(PurchaseItemsList.as_view(), login_url='/login/'), name='purchase_items'),
	url(r'^purchase_return_report/$', login_required(PurchaseReturnReport.as_view(), login_url='/login/'), name='purchase_return_report'),
	url(r'^purchase_return_view/$', login_required(PurchaseReturnView.as_view(), login_url='/login/'), name='purchase_return_view'),
)