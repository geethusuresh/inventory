
from datetime import datetime

from django.contrib.sites.models import Site
from django.db import models
from accounting.models import *
from inventory.models import StockValue

def site_variables(request):
    today = datetime.now()
    if request.user.is_authenticated():     
        ledger, created = Ledger.objects.get_or_create(name='Stock')
        try:
            stock_value = StockValue.objects.latest('id')
            stock_by_value = stock_value.stock_by_value
        except:
            stock_by_value = ''
        return {
            # 'stock': ledger.balance,
            'stock': stock_by_value,
            'today': today
        }       
    else:
        return {
            'stock': '',
            'today': today
        }