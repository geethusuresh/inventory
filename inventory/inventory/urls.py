
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from inventory.views import (Categories, AddCategory, DeleteCategory, CategorySubcategoryList, \
 Products, CategoryTreeView, SearchCategory, DeleteProduct, AddProduct, BrandList, AddBrand, DeleteBrand , VatList, \
 DeleteVat, AddVat, SearchBrand, SearchProduct, SearchVat, ItemList, AddItem, DeleteItem, SearchItem, BatchList, \
 OpeningStockView, AddBatch, DeleteBatch, SearchBatch, SaveOpeningStock, StockReport, BatchItemDetails, \
 SearchBatchItem, UOMConversionView, DeleteUOMConversion, SearchItemStock, StockAgingReport, AllStockReport)

urlpatterns = patterns('',
	url(r'^categories/$', login_required(Categories.as_view(), login_url='/login/'),name='categories'),
	url(r'^add_category/$', login_required(AddCategory.as_view(), login_url='/login/'),name='add_category'),
	url(r'^delete_category/$', login_required(DeleteCategory.as_view(), login_url='/login/'),name='delete_category'),
	url(r'^subcategory_list/(?P<category_id>\d+)/$', login_required(CategorySubcategoryList.as_view(), login_url='/login/'), name='subcategory_list'),
	url(r'^categories_tree_view/$', login_required(CategoryTreeView.as_view(), login_url='/login/'),name='categories_tree_view'),
	url(r'^search_category/$', login_required(SearchCategory.as_view(), login_url='/login/'), name='search_category'),
	
	url(r'^products/$', login_required(Products.as_view(), login_url='/login/'),name='products'),
	url(r'^add_product/$', login_required(AddProduct.as_view(), login_url='/login/'),name='add_product'),
	url(r'^delete_product/$', login_required(DeleteProduct.as_view(), login_url='/login/'),name='delete_product'),
	url(r'^search_product/$', login_required(SearchProduct.as_view(), login_url='/login/'), name='search_product'),

	url(r'^brands/$', login_required(BrandList.as_view(), login_url='/login/'),name='brands'),
	url(r'^add_brand/$', login_required(AddBrand.as_view(), login_url='/login/'),name='add_brand'),
	url(r'^delete_brand/$', login_required(DeleteBrand.as_view(), login_url='/login/'),name='delete_brand'),
	url(r'^search_brand/$', login_required(SearchBrand.as_view(), login_url='/login/'), name='search_brand'),

	url(r'^vat/$', login_required(VatList.as_view(), login_url='/login/'),name='vat'),
	url(r'^add_vat/$', login_required(AddVat.as_view(), login_url='/login/'),name='add_vat'),
	url(r'^delete_vat/$', login_required(DeleteVat.as_view(), login_url='/login/'),name='delete_vat'),
	url(r'^search_vat/$', login_required(SearchVat.as_view(), login_url='/login/'), name='search_vat'),
	
	url(r'^items/$', login_required(ItemList.as_view(), login_url='/login/'),name='items'),
	url(r'^add_item/$', login_required(AddItem.as_view(), login_url='/login/'),name='add_item'),
	url(r'^delete_item/$', login_required(DeleteItem.as_view(), login_url='/login/'),name='delete_item'),
	url(r'^search_item/$', login_required(SearchItem.as_view(), login_url='/login/'), name='search_item'),
	url(r'^search_item_stock/$', login_required(SearchItemStock.as_view(), login_url='/login/'), name='search_item_stock'),

	url(r'^batches/$', login_required(BatchList.as_view(), login_url='/login/'),name='batches'),
	url(r'^add_batch/$', login_required(AddBatch.as_view(), login_url='/login/'), name='add_batch'),
	url(r'^delete_batch/$', login_required(DeleteBatch.as_view(), login_url='/login/'), name='delete_batch'),
	url(r'^search_batch/$', login_required(SearchBatch.as_view(), login_url='/login/'), name='search_batch'),
	url(r'^search_batch_item/$', login_required(SearchBatchItem.as_view(), login_url='/login/'), name='search_batch_item'),

	url(r'^opening_stock/$', login_required(OpeningStockView.as_view(), login_url='/login/'),name='opening_stock'),
	url(r'^save_opening_stock/$', login_required(SaveOpeningStock.as_view(), login_url='/login/'),name='save_opening_stock'),

	url(r'^batch_item_details/$', login_required(BatchItemDetails.as_view(), login_url='/login/'),name='batch_item_details'),
	url(r'^stock_report/$', login_required(StockReport.as_view(), login_url='/login/'),name='stock_report'),
	url(r'^uom_conversion/$', login_required(UOMConversionView.as_view(), login_url="login"), name='uom_conversion'),
	url(r'^delete_uom_conversion/(?P<conversion_id>\d+)/$', login_required(DeleteUOMConversion.as_view(), login_url='/login/'), name='delete_uom_conversion'),

	url(r'^stock_aging_report/$', login_required(StockAgingReport.as_view(), login_url='/login/'), name='stock_aging_report'),
	url(r'^all_stock_report/$', login_required(AllStockReport.as_view(), login_url='/login/'), name='all_stock_report'),
)
