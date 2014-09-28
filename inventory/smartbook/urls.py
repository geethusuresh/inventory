from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'', include('web.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sales/', include('sales.urls')),
    url(r'^purchases/', include('purchases.urls')),
    url(r'^accounting/', include('accounting.urls')),
    url(r'^inventory/', include('inventory.urls')),
    url(r'^customers/', include('customers.urls')),
    url(r'^suppliers/', include('suppliers.urls')),
)
