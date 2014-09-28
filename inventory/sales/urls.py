
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required


from sales.views import SalesEntry, SalesReceipts, SaleReturn, SalesReport, EstimateEntry, EstimatePdf,\
	EstimateView, SalesView, ChangeSalesDiscount, SalesReturnView

urlpatterns = patterns('',
	url(r'^sales_entry/$', login_required(SalesEntry.as_view(), login_url='/login/'), name='sales_entry'),
	url(r'^sales_receipts/$', login_required(SalesReceipts.as_view(), login_url='/login/'), name='sales_receipts'),
	url(r'^sales_return_entry/$', login_required(SaleReturn.as_view(), login_url='/login/'), name='sales_return_entry'),

	url(r'^sales_report/$', login_required(SalesReport.as_view(), login_url='/login/'), name='sales_report'),
	url(r'^estimate_entry/$', login_required(EstimateEntry.as_view(), login_url='/login/'), name='estimate_entry'),
	url(r'^estimate_pdf/(?P<estimate_id>\d+)/$', login_required(EstimatePdf.as_view(), login_url='/login/'), name='estimate_pdf'),
	url(r'^estimate_view/$', login_required(EstimateView.as_view(), login_url='/login/'), name='estimate_view'),

	url(r'^sales_view/$', login_required(SalesView.as_view(), login_url='/login/'), name='sales_view'),
	url(r'^sales_return_view/$', login_required(SalesReturnView.as_view(), login_url='/login/'), name='sales_return_view'),

	url(r'^change_sales_discount/$', login_required(ChangeSalesDiscount.as_view(), login_url='/login/'), name='change_sales_discount')

)