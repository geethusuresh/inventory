import simplejson
import ast
from datetime import datetime
import calendar
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from inventory.models import Category, Product, Brand, VatType, Item, BatchItem, Batch, UOMConversion,\
 OpeningStock, OpeningStockItem, StockValue, OpeningStockValue
from accounting.models import Ledger, LedgerEntry, Transaction
from purchases.models import Purchase
from sales.models import Sale

style = [
    ('FONTSIZE', (0,0), (-1, -1), 10),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]
para_style = ParagraphStyle('fancy')
para_style.fontSize = 9
para_style.fontName = 'Helvetica'

from web.views import get_user_permission

def get_category_list():
    ctx_categories = []
    categories = Category.objects.filter(parent=None)
    for category in categories:
        ctx_categories.append({
            'subcategories': [],
            'id': category.id,
            'name': category.name,
        })
    res = {
        'categories': ctx_categories,
        'result': 'ok',
    }
    response = simplejson.dumps(res)
    return HttpResponse(response, status=200, mimetype='application/json')

class Categories(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                return get_category_list()        
            return render(request, 'categories.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class AddCategory(View):

    def post(self, request, *args, **kwargs):

        if request.is_ajax(): 
            category_details = ast.literal_eval(request.POST['category'])
            print category_details
            if category_details.get('id', ''):
                category = Category.objects.get(id=category_details.get('id', ''))
                try:
                    if category_details.get('parent', ''): 
                        print "in if"
                        parent = Category.objects.get(id=category_details['parent'])
                        try:
                            category_obj = Category.objects.filter(parent=parent,name=category_details['name']).exclude(id=category_details.get('id', ''))
                            if category_obj.count() > 0:
                                res = {
                                    'result': 'error',
                                    'message': 'Category name already exists',
                                }
                            else:
                                category.name = category_details['name']
                                category.parent = parent
                                res = {
                                    'result': 'ok',
                                    'message': 'ok',
                                }
                        except Exception as ex:
                            print str(ex)
                            category.name = category_details['name']
                            category.parent = parent
                            res = {
                                'result': 'ok',
                                'message': 'ok',
                            }
                    else:
                        category.name = category_details['name']
                        
                    category.save()
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                    }
                    
                except Exception as ex:
                    print str(ex)
                    res = {
                        'result': 'ok',
                        'message': 'Category name already exists',
                    }
            else:
                try:
                    if category_details['parent'] != '': 
                        parent = Category.objects.get(id=category_details['parent'])
                        category = Category.objects.get(name=category_details['name'], parent=parent)
                    else:
                        category = Category.objects.get(name=category_details['name'])
                    res = {
                        'result': 'error',
                        'message': 'Category name already exists',
                    }
                except Exception as ex:
                    if category_details['parent'] != '': 
                        parent = Category.objects.get(id=category_details['parent'])
                        category = Category.objects.create(name=category_details['name'], parent=parent)
                    else:
                        category = Category.objects.create(name=category_details['name'])
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                        'new_category': {
                            'parent': category.parent.id if category.parent else '',
                            'id': category.id,
                            'name': category.name,
                            'subcategories': [],
                            'temp_subcategories': [],
                        }
                    }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class DeleteCategory(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            category_id = request.GET.get('category_id', '')
            category = Category.objects.get(id=category_id)
            category.delete()
            return HttpResponseRedirect(reverse('categories'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class CategorySubcategoryList(View):

    def get(self, request, *args, **kwargs):

        category_id = kwargs['category_id']
        category = Category.objects.get(id=category_id)
        ctx_category_details = []
        ctx_subcategory = []
        subcategories = Category.objects.filter(parent=category)
        for subcatrgory in subcategories:
            ctx_subcategory.append({
                'id': subcatrgory.id,
                'name': subcatrgory.name,
                'subcategories': [],
                'temp_subcategories': [],
            })
        ctx_category_details.append({
            'id': category.id,
            'name': category.name,
            'subcategories': ctx_subcategory,
        })
        res = {
            'result': 'ok',
            'subcategories': ctx_subcategory,
            'category_details': ctx_category_details
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class CategoryTreeView(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                return get_category_list()
            return render(request, 'categories_tree_view.html', {})
        return HttpResponseRedirect(reverse('dashboard'))

class SearchCategory(View):

    def get(self, request, *args, **kwargs):

        category_name = request.GET.get('name', '')
        ctx_categories = []
        categories = Category.objects.filter(name__istartswith=category_name)
        for category in categories:
            ctx_categories.append({
                'id': category.id,
                'name': category.name,
                'parent_name': category.parent.name if category.parent else ''
            })
        res = {
            'result': 'ok',
            'categories': ctx_categories,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class Products(View):

    def get(self, request, *args, **kwargs):
        ctx_products = []
        products = Product.objects.all()
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                for product in products:
                    ctx_products.append({
                        'id': product.id,
                        'name': product.name,
                        'category': product.category.id,
                        'category_name': product.category.name,
                    })
                res = {
                    'result': 'ok',
                    'products': ctx_products,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'products.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class AddProduct(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            product_details = ast.literal_eval(request.POST['product'])
            if product_details.get('id', ''):
                product = Product.objects.get(id=product_details.get('id', ''))
                try:
                    product.name = product_details['name']
                    product.category = Category.objects.get(id=product_details.get('category', ''))
                    product.save()
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                    }
                except Exception as ex:
                    res = {
                        'result': 'ok',
                        'message': 'Product name already exists'+str(ex),
                    }
            else:
                category = Category.objects.get(id=product_details['category'])
                try:
                    product = Product.objects.get(name=product_details['name'], category=category)
                    res = {
                        'result': 'error',
                        'message': 'Product name already exists',
                    }
                except Exception as ex:
                    product = Product.objects.create(name=product_details['name'], category=category)
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                        'product': {
                            'id': product.id,
                            'name': product.name,
                        }
                    }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class DeleteProduct(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            product_id = request.GET.get('product_id', '')
            product = Product.objects.get(id=product_id)
            product.delete()
            return HttpResponseRedirect(reverse('products'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class SearchProduct(View):

    def get(self, request, *args, **kwargs):
        name = request.GET.get('product_name', '')
        ctx_product_list = []
        category_id = request.GET.get('category_id', '')
        
        try:
            category = Category.objects.get(id=category_id)
            products = Product.objects.filter(name__istartswith=name, category=category)
        except:
            products = Product.objects.filter(name__istartswith=name)
        for product in products:
            ctx_product_list.append({
                'id': product.id,
                'name': product.name,
                'category_name': product.category.name,
            })
        res = {
            'result': 'ok',
            'products': ctx_product_list,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class BrandList(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                ctx_brands = []
                brands = Brand.objects.all()
                for brand in brands:
                    ctx_brands.append({
                        'id': brand.id,
                        'name': brand.name,
                    })
                res = {
                    'result': 'ok',
                    'brands': ctx_brands,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'brand_list.html', {})  
        else:
            return HttpResponseRedirect(reverse('dashboard')) 

class AddBrand(View):
    
    def post(self, request, *args, **kwargs):
        brand_details = ast.literal_eval(request.POST['brand'])
        
        if brand_details.get('id', ''):
            brand = Brand.objects.get(id=brand_details['id'])
            try:
                brand.name = brand_details['name']
                brand.save()
                res = {
                    'result': 'ok',
                }
            except Exception as ex:
                res = {
                    'result': 'error',
                    'message': 'Brand name already exists',
                }
        else:
            try:
                brand = Brand.objects.get(name=brand_details['name'])
                res = {
                    'result': 'error',
                    'message': 'Brand name already exists',
                }   
            except Exception as ex:
                brand = Brand.objects.create(name=brand_details['name'])
                res = {
                    'result': 'ok',
                    'brand': {
                        'id': brand.id,
                        'name': brand.name,
                    }
                }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeleteBrand(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            brand_id = request.GET.get('brand_id', '')
            brand = Brand.objects.get(id=brand_id)
            brand.delete()
            return HttpResponseRedirect(reverse('brands'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class SearchBrand(View):

    def get(self, request, *args, **kwargs):
        name = request.GET.get('brand_name', '')
        ctx_brand_list = []
        brand_names = Brand.objects.filter(name__istartswith=name)
        for brand in brand_names:
            ctx_brand_list.append({
                'id': brand.id,
                'name': brand.name,
            })
        res = {
            'result': 'ok',
            'brand_list': ctx_brand_list,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class VatList(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                ctx_vats = []
                vats = VatType.objects.all()
                for vat in vats:
                    ctx_vats.append({
                        'id': vat.id,
                        'name': vat.vat_type,
                        'tax_percentage': vat.tax_percentage,
                    })
                res = {
                    'result': 'ok',
                    'vats': ctx_vats,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'vat_list.html', {}) 
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class AddVat(View):
    
    def post(self, request, *args, **kwargs):
        vat_details = ast.literal_eval(request.POST['vat'])
        
        if vat_details.get('id',''):
            vat = VatType.objects.get(id=vat_details['id'])
            try:
                vat.vat_type = vat_details['name']
                vat.tax_percentage = vat_details['tax_percentage']
                vat.save()
                res = {
                    'result': 'ok',
                }
            except Exception as ex:
                res = {
                    'result': 'error',
                    'message': 'vat type  already exists',
                }
        else:
            try:
                vat = VatType.objects.get(vat_type=vat_details['name'])
                res = {
                    'result': 'error',
                    'message': 'vat type  already exists',
                }   
            except Exception as ex:
                vat = VatType.objects.create(vat_type=vat_details['name'] ,tax_percentage=vat_details['tax_percentage'])
                res = {
                    'result': 'ok',
                    'vat': {
                        'id': vat.id,
                        'name': vat.vat_type,
                        'tax': vat.tax_percentage,
                    }
                }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeleteVat(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            vat_id = request.GET.get('vat_id', '')
            vat = VatType.objects.get(id=vat_id)
            vat.delete()
            return HttpResponseRedirect(reverse('vat'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class SearchVat(View):

    def get(self, request, *args, **kwargs):

        vat_type = request.GET.get('vat_type', '')
        vat_list = VatType.objects.filter(vat_type__istartswith=vat_type)
        ctx_vat_list = []
        for vat in vat_list:
            ctx_vat_list.append({
                'id': vat.id,
                'vat_type': vat.vat_type,
                'vat_percentage': vat.tax_percentage,
                'tax_percentage': vat.tax_percentage,
                'name': vat.vat_type,
                'vat_name': str(vat.vat_type)+ str(' - ') + str(vat.tax_percentage),
            })
        res = {
            'result': 'ok',
            'vat_list': ctx_vat_list,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class ItemList(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                ctx_items = []
                items = Item.objects.all()
                for item in items:
                    ctx_items.append({
                        'id': item.id,
                        'name': item.name,
                        'code': item.code,
                        'product_name': item.product.name,
                        'brand_name': item.brand.name,
                        'product': item.product.id,
                        'brand': item.brand.id,
                        'vat_name': item.vat_type.vat_type + str(' - ') + str(item.vat_type.tax_percentage) if item.vat_type else '',
                        'vat': item.vat_type.id if item.vat_type else '',
                        'barcode': item.barcode,
                        'description': item.description,
                        'cess': item.cess,
                        'size': item.size,
                        'offer_quantity': item.offer_quantity
                    })
                res = {
                    'result': 'ok',
                    'items': ctx_items,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'item_list.html', {})   
        else:
            return HttpResponseRedirect(reverse('dashboard')) 

class AddItem(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'add_inventory_item.html', {})

    def post(self, request, *args, **kwargs):
        item_details = ast.literal_eval(request.POST['item'])
        product = Product.objects.get(id=int(item_details['product']))
        brand = Brand.objects.get(id=int(item_details['brand']))
        try:
            vat_type = VatType.objects.get(id=item_details['vat']) 
        except Exception as ex:
            print str(ex)
            vat_type = None
        if item_details.get('id', ''):
            item = Item.objects.get(id=item_details['id'])
            item.product = product
            item.brand = brand
            item.name = item_details['name']
        else:
            item = Item.objects.create(name=item_details['name'] ,product=product,brand=brand)
        try:
            if vat_type != None:
                item.vat_type = vat_type
            if item_details.get('cess', ''):
                item.cess = item_details['cess']
            item.size = item_details['size']
            item.barcode = item_details['barcode']
            item.description = item_details['description']
            if item_details.get('offer_quantity', ''):
                item.offer_quantity = item_details['offer_quantity']
            item.save()
            res = {
                'result': 'ok',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'code': item.code,
                    'product_name': item.product.name,
                    'brand_name': item.brand.name,
                    'product': item.product.id,
                    'brand': item.brand.id,
                    'vat_name': item.vat_type.vat_type + str(' - ') + str(item.vat_type.tax_percentage) if item.vat_type else '',
                    'vat': item.vat_type.id if item.vat_type else '',
                    'barcode': item.barcode,
                    'description': item.description,
                    'cess': item.cess,
                    'size': item.size,
                    'offer_quantity': item.offer_quantity
                }
            }
        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'message': 'item  already exists',
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeleteItem(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            item_id = request.GET.get('item_id', '')
            item = Item.objects.get(id=item_id)
            item.delete()
            return HttpResponseRedirect(reverse('items'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class SearchItem(View):
    def get(self, request, *args, **kwargs):
        ctx_items = []
        try:
            item_code = request.GET.get('item_code', '')
            item_name = request.GET.get('item_name', '')
            brand = request.GET.get('brand', '')
            batch = request.GET.get('batch', '')
            product = request.GET.get('product', '')
            if brand == 'undefined':
                brand = ''
            if product == 'undefined':
                product = ''
            items = []
            if item_code:
                items = Item.objects.filter(code__istartswith=item_code, brand__id=brand, product__id=product)
            elif item_name:
                if brand and product:
                    items = Item.objects.filter(name__istartswith=item_name, brand__id=brand, product__id=product)
                else:
                    items = Item.objects.filter(name__istartswith=item_name)
            for item in items:
                try:
                    if batch and batch != 'undefined':
                        batch_item = BatchItem.objects.get(item=item, batch__id=batch)
                        purchase_price = batch_item.purchase_price
                        selling_price = batch_item.selling_price
                        stock = batch_item.quantity
                    else:
                        purchase_price = 0
                        selling_price = 0
                        stock = 0
                except Exception as ex:
                    purchase_price = 0
                    selling_price = 0
                    stock = 0
                ctx_items.append({
                    'id': item.id,
                    'name': item.name,
                    'item_name': item.product.category.name+ ' - ' + item.product.name + ' - ' + str(item.name) + (str(' - ') + str(item.size) if item.size else ''),
                    'code': item.code,
                    'product_name': item.product.name,
                    'brand_name': item.brand.name,
                    'product': item.product.id,
                    'brand': item.brand.id,
                    'vat_name': item.vat_type.vat_type + str(' - ') + str(item.vat_type.tax_percentage) if item.vat_type else '',
                    'vat': item.vat_type.id if item.vat_type else '',
                    'barcode': item.barcode if item.barcode else '',
                    'description': item.description if item.description else '',
                    'cess': item.cess,
                    'size': item.size,
                    'purchase_price': purchase_price,
                    'selling_price': selling_price,
                    'stock': stock,
                    'quantity': 0,
                })
            res = {
                'result': 'ok',
                'items': ctx_items,
            }
        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'error_message': str(ex),
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class BatchList(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            if request.is_ajax():
                ctx_batches = []
                batches = Batch.objects.all()
                for batch in batches:
                    ctx_batches.append({
                        'id': batch.id,
                        'name': batch.name,
                        'created_date': batch.created_date.strftime('%d/%m/%Y') if batch.created_date else '',
                        'expiry_date': batch.expiry_date.strftime('%d/%m/%Y') if batch.expiry_date else '',
                    })
                res = {
                    'result': 'ok',
                    'batches': ctx_batches,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'batch_list.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class AddBatch(View):

    def post(self, request, *args, **kwargs):
        batch = None
        if request.is_ajax():
            batch_details = ast.literal_eval(request.POST['batch_details'])
            if batch_details.get('id', ''):
                batch = Batch.objects.get(id=batch_details['id'])
            else:
                try:
                    batch = Batch.objects.get(name=batch_details['name'])  
                    res = {
                        'result': 'error',
                        'message': 'Batch with this name already exists',
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                except Exception as ex:
                    print str(ex)
                    batch = Batch.objects.create(name=batch_details['name'])  
            batch.created_date = datetime.strptime(batch_details['created_date'], '%d/%m/%Y')
            batch.expiry_date = datetime.strptime(batch_details['expiry_date'], '%d/%m/%Y')
            batch.save()
            res = {
                'result': 'ok',
                'id': batch.id,
                'name': batch.name,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class DeleteBatch(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            batch_id = request.GET.get('batch_id', '')
            batch = Batch.objects.get(id=batch_id)
            batch.delete()
            return HttpResponseRedirect(reverse('batches'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class SearchBatch(View):

    def get(self, request, *args, **kwargs):

        batch_name = request.GET.get('batch_name', '')
        batches = Batch.objects.filter(name__istartswith=batch_name)
        ctx_batches = []
        for batch in batches:
            ctx_batches.append({
                'id': batch.id,
                'name': batch.name,
                'created_date': batch.created_date.strftime('%d/%m/%Y') if batch.created_date else '',
                'expiry_date': batch.expiry_date.strftime('%d/%m/%Y') if batch.expiry_date else '',
            })
        res = {
            'result': 'ok',
            'batches': ctx_batches,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class OpeningStockView(View):

    def get(self, request, *args, **kwargs):

        if request.is_ajax():
            res = {
                'result': 'ok',
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'opening_stock.html', {})

class SaveOpeningStock(View):

    def post(self, request, *args, **kwargs):

        total_purchase_price = 0
        if request.is_ajax():
            opening_stock_items = ast.literal_eval(request.POST['opening_stock_items'])
            if opening_stock_items:
                cash_ledger = Ledger.objects.get(name='Cash')
                stock_ledger = Ledger.objects.get(name='Stock')
                transaction = Transaction()
                try:
                    transaction_ref = Transaction.objects.latest('id').id + 1
                except:
                    transaction_ref = '1'
              
                transaction.transaction_ref = 'OPSTK' + str(transaction_ref)
                
                try:
                    opening_stock = OpeningStock.objects.create(transaction_reference_no=transaction.transaction_ref, date=datetime.now() )
                    for item_detail in opening_stock_items:
                        item = Item.objects.get(id=item_detail['id'])
                        batch = Batch.objects.get(id=item_detail['batch'])
                        batch_item, batch_item_created = BatchItem.objects.get_or_create(item=item,batch=batch)
                        try:
                            opening_stock_item = OpeningStockItem.objects.get(opening_stock=opening_stock,batch_item=batch_item)
                        except:
                            opening_stock_item = OpeningStockItem.objects.create(opening_stock=opening_stock,batch_item=batch_item)
                        opening_stock_item.quantity = item_detail['quantity']
                        opening_stock_item.whole_sale_price = item_detail['whole_sale_price']
                        opening_stock_item.retail_price = item_detail['retail_price']
                        opening_stock_item.purchase_price = item_detail['purchase_price']
                        opening_stock_item.net_amount = item_detail['net_amount']
                        opening_stock_item.uom = item_detail['purchase_unit']
                        opening_stock_item.save()
                        conversion_type = UOMConversion.objects.get(id=item_detail['conversion_unit'])
                        quantity = 0
                        selling_price = 0
                        purchase_price = 0
                        if conversion_type.selling_unit == item_detail['purchase_unit']:
                            quantity = item_detail['quantity']
                            whole_sale_price = item_detail['whole_sale_price']
                            retail_price = item_detail['retail_price']
                            purchase_price = item_detail['purchase_price']
                        else:
                            quantity = float(item_detail['quantity']) * float(conversion_type.relation)
                            whole_sale_price = float(item_detail['whole_sale_price']) / float(conversion_type.relation)
                            retail_price = float(item_detail['retail_price']) / float(conversion_type.relation)
                            purchase_price = float(item_detail['purchase_price']) / float(conversion_type.relation)
                        batch_item.whole_sale_price = whole_sale_price
                        batch_item.retail_price = retail_price
                        batch_item.purchase_price = purchase_price
                        if batch_item_created:
                            batch_item.quantity = quantity
                            batch_item.uom_conversion = conversion_type
                        else:
                            batch_item.quantity = float(batch_item.quantity) + float(quantity)
                        batch_item.uom = conversion_type.selling_unit
                        total_purchase_price = float(total_purchase_price) + float(batch_item.purchase_price) * float(quantity)
                        batch_item.save()
                except Exception as ex:
                    print str(ex), 'Exception'
                    res = {
                        'result': 'error',
                        'error_message': str(ex),
                    }
                ledger_entry_cash_ledger = LedgerEntry()
                ledger_entry_cash_ledger.ledger = cash_ledger
                ledger_entry_cash_ledger.credit_amount = total_purchase_price
                ledger_entry_cash_ledger.date = datetime.now()
                ledger_entry_cash_ledger.save()
                ledger_entry_stock_ledger = LedgerEntry()
                ledger_entry_stock_ledger.ledger = stock_ledger
                ledger_entry_stock_ledger.debit_amount = total_purchase_price
                ledger_entry_stock_ledger.date = datetime.now()
                ledger_entry_stock_ledger.save()
                try:
                    stock_value = StockValue.objects.latest('id')
                except Exception as ex:
                    stock_value = StockValue()
                if stock_value.stock_by_value is not None:
                    stock_value.stock_by_value = float(stock_value.stock_by_value) + float(total_purchase_price)
                else:
                    stock_value.stock_by_value = float(total_purchase_price)
                stock_value.save()
                try:
                    opening_stock_value = OpeningStockValue.objects.latest('id')
                except Exception as ex:
                    opening_stock_value = OpeningStockValue()
                if opening_stock_value.stock_by_value is not None:
                    opening_stock_value.stock_by_value = float(opening_stock_value.stock_by_value) + float(total_purchase_price)
                else:
                    opening_stock_value.stock_by_value = float(total_purchase_price)
                opening_stock_value.save()


                transaction.credit_ledger = ledger_entry_cash_ledger
                transaction.debit_ledger = ledger_entry_stock_ledger
                transaction.transaction_date = datetime.now()
                transaction.amount = total_purchase_price
                cash_ledger.balance = float(cash_ledger.balance) - float(total_purchase_price)
                stock_ledger.balance = float(stock_ledger.balance) + float(total_purchase_price)
                cash_ledger.save()
                stock_ledger.save()
                transaction.save()
            res = {
                'result': 'ok',
                'transaction_reference_no': transaction.transaction_ref
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class StockReport(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'inventory_permission'):
            batch_id = request.GET.get('batch_id')
            if not batch_id:
                context = {
                    'message': 'Please enter a Batch',              
                }
                return render(request, 'stock_report.html', context)
            else:
                try:
                    batch = Batch.objects.get(id=batch_id)
                except:
                    context = {
                    'message': 'No such Batch',
                    }
                    return render(request, 'stock_report.html', context)
            if request.is_ajax():
                stock_entries_list = []
                count = 1
              
                stock_entries = BatchItem.objects.filter(batch=batch)
                whole_sale_price = 0
                purchase_price = 0
                retail_price = 0
                stock = 0

                for stock_entry in stock_entries:
                    stock = float(stock_entry.quantity) / float(stock_entry.uom_conversion.relation)
                    whole_sale_price = float(stock_entry.whole_sale_price) * float(stock_entry.uom_conversion.relation)
                    retail_price = float(stock_entry.retail_price) * float(stock_entry.uom_conversion.relation)
                    purcahse_price = float(stock_entry.purchase_price) * float(stock_entry.uom_conversion.relation)
                    stock_entries_list.append({
                        'count': count,
                        'id': stock_entry.id,
                        'name': stock_entry.batch.name,
                        'item_name':stock_entry.item.name,
                        'quantity':stock,
                        'purchase_price': purcahse_price,
                        'whole_sale_price': whole_sale_price,
                        'retail_price':retail_price,
                        })
                    count = count + 1
                res = {
                    'result': 'ok',
                    'stock_entries': stock_entries_list,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            response = HttpResponse(content_type='application/pdf')
            if request.GET.get('report_type',''):
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                status_code = 200
                
                context = {

                }
                p.setFontSize(16)

                p.drawString(400, y - 70, ' Stock Report - ' + batch.name)
                p.drawString(100, y-100, 'No')
                p.drawString(200, y - 100, 'Item name ' )
                p.drawString(330, y-100, 'Quantity')
                p.drawString(460, y-100, 'Whole Sale Price')
                p.drawString(650, y-100, 'Retail Price')
                p.drawString(790, y-100, 'Purchase Price')
                p.setFontSize(14)
                y = y - 120 
                count = 1 
                batch_items = BatchItem.objects.filter(batch=batch)
                for batch_item in batch_items:
                    stock = float(batch_item.quantity) / float(batch_item.uom_conversion.relation)
                    whole_sale_price = float(batch_item.whole_sale_price) * float(batch_item.uom_conversion.relation)
                    retail_price = float(batch_item.retail_price) * float(batch_item.uom_conversion.relation)
                    purcahse_price = float(batch_item.purchase_price) * float(batch_item.uom_conversion.relation)
                    p.drawString(100, y, str(count))
                    data=[[Paragraph(batch_item.item.name, para_style)]]
                    table = Table(data, colWidths=[100], rowHeights=100, style=style)      
                    table.wrapOn(p, 200, 400)
                    table.drawOn(p, 200, y)
                    # p.drawString(200, y, batch_item.item.name)
                    p.drawString(330, y, str(stock))
                    p.drawString(460, y, str(whole_sale_price))
                    p.drawString(650, y, str(retail_price))
                    p.drawString(790, y, str(purcahse_price))
                    count = count + 1
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)
                p.showPage()
                p.save()
                return response
            else:            
                return render(request, 'stock_report.html',{})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class BatchItemDetails(View):

    def get(self, request, *args, **kwargs):
        batch_id = request.GET.get('batch_id', '')
        item_id = request.GET.get('item_id', '')
        item = Item.objects.get(id=item_id)
        try:
            batch = Batch.objects.get(id=batch_id)
            batch_item = BatchItem.objects.get(batch=batch, item=item)
            selling_price = 0
            stock = 0 
            stock = float(batch_item.quantity) / float(batch_item.uom_conversion.relation)
            whole_sale_price = float(batch_item.whole_sale_price) * float(batch_item.uom_conversion.relation)
            retail_price = float(batch_item.retail_price) * float(batch_item.uom_conversion.relation)
            purchase_price = float(batch_item.purchase_price) * float(batch_item.uom_conversion.relation)
            res = {
                'stock': stock,
                'quantity': batch_item.quantity,
                'purchase_unit': batch_item.uom_conversion.purchase_unit if batch_item.quantity > 0 else '',
                'selling_unit': batch_item.uom_conversion.selling_unit if batch_item.quantity > 0 else '',
                'relation': batch_item.uom_conversion.relation if batch_item.quantity > 0 else '',
                'stock_unit': batch_item.uom,
                'whole_sale_price': whole_sale_price,
                'retail_price': retail_price,
                'whole_sale_price_sales': batch_item.whole_sale_price,
                'retail_price_sales': batch_item.retail_price,
                'result': 'ok',
                'conversion_unit': batch_item.uom_conversion.id if batch_item.quantity > 0 else '',
                'conversion_unit_name': '1 '+ batch_item.uom_conversion.purchase_unit + ' = ' + str(batch_item.uom_conversion.relation) + batch_item.uom_conversion.selling_unit if batch_item.quantity > 0 else '',
                'tax': item.vat_type.tax_percentage if item.vat_type else '',
                'offer_quantity': batch_item.item.offer_quantity,
                'purchase_price': purchase_price,
                'cost_price': batch_item.cost_price,
            }
        except Exception as ex:
            print str(ex)
            res = {
                'stock': 0,
                'uom_conversion': '',
                'purchase_unit': '',
                'selling_unit': '',
                'result': 'ok',
                'conversion_unit': '',
                'conversion_unit_name':'',
                'whole_sale_price': 0,
                'retail_price': 0,
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class SearchBatchItem(View):

    def get(self, request, *args, **kwargs):
        batch = request.GET.get('batch', '')
        item_id = request.GET.get('item', '')
        item = Item.objects.get(id=item_id)
        batch_items = BatchItem.objects.filter(item=item, batch__name__istartswith=batch)
        batch_items_list = []
        for batch_item in batch_items:
            batch_items_list.append({
                'batch_id': batch_item.batch.id,
                'batch_name': batch_item.batch.name,
                })
        res = {
            'result': 'ok',
            'batch_items': batch_items_list,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class UOMConversionView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            uom_list = settings.UOM
            conversions = UOMConversion.objects.all()
            conversion_list = []
            purchase_unit = request.GET.get('purchase_unit', '')
            if purchase_unit:
                conversions = UOMConversion.objects.filter(purchase_unit=purchase_unit)
            for conversion in conversions:
                conversion_list.append({
                    'purchase_unit': conversion.purchase_unit,
                    'sales_unit': conversion.selling_unit,
                    'relation': conversion.relation,
                    'id': conversion.id,
                    'status': conversion.status,
                    'name': '1 ' + conversion.purchase_unit + ' = ' + str(conversion.relation) + ' ' + conversion.selling_unit
                })
            res = {
                'result': 'ok',
                'uoms': uom_list,
                'conversions': conversion_list
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'uom_conversion.html',{})
    
    def post(self, request, *args, **kwargs):   
        uom_conversion = ast.literal_eval(request.POST['conversion'])  
        if uom_conversion.get('id',''):
            conversion = UOMConversion.objects.get(id=uom_conversion["id"])
        else:
            conversion = UOMConversion()
        conversion.purchase_unit = uom_conversion["purchase_unit"]
        conversion.selling_unit = uom_conversion["sales_unit"]
        conversion.relation = uom_conversion["relation"]
        conversion.save()    
        if request.is_ajax():
            res = {
                'result': 'ok',
                'conversion': {
                    'purchase_unit': conversion.purchase_unit,
                    'sales_unit': conversion.selling_unit,
                    'relation': conversion.relation,
                    'id': conversion.id
                },
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'uom_conversion.html',{})

class DeleteUOMConversion(View):
    def get(self, request, *args, **kwargs):
        conversion = UOMConversion.objects.get(id=kwargs['conversion_id'])
        conversion.delete()
        if request.is_ajax():
            res = {
                'result': 'ok',            
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'uom_conversion.html',{})


class SearchItemStock(View):
    def get(self, request, *args, **kwargs):
        ctx_items = []
        try:
            item_name = request.GET.get('item_name', '')
            items = []
            if item_name:
                items = Item.objects.filter(name__istartswith=item_name)
            for item in items:
                batch_items = item.batchitem_set.all()
                for batch_item in batch_items:
                    item_dict = {
                        'id': item.id,
                        'name': item.name,
                        'item_name': str(item.name),
                        'category': item.product.category.name,
                        'code': item.code,
                        'product_name': item.product.name,
                        'brand_name': item.brand.name,                  
                        'stock': batch_item.quantity, 
                        'batch': batch_item.batch.name,
                        'uom': batch_item.uom,
                        'size': batch_item.item.size
                    }                
                    ctx_items.append(item_dict)    
            res = {
                'result': 'ok',
                'items': ctx_items,
            }
        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'error_message': str(ex),
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class StockAgingReport(View):

    def get(self, request, *args, **kwargs):

        if request.GET.get('batch', ''):
            stock_items = []
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            ctx_months = []
            fields = ['Rcvd', 'Sold']
            for i in range(1,current_month + 1):
                ctx_months.append({
                    'name' : calendar.month_name[i][:3],
                    'fields': fields,
                })
            batch = Batch.objects.get(id=request.GET.get('batch', ''))
            for batch_item in batch.batchitem_set.all():
                ctx_month_details = []
                for i in range(1,current_month + 1):
                    month_name = calendar.month_name[i][:3]
                    month_details = []
                    opening_stock = OpeningStock.objects.filter(date__month=i, date__year=current_year)
                    purchases = Purchase.objects.filter(purchase_invoice_date__month=i, purchase_invoice_date__year=current_year)
                    sales = Sale.objects.filter(sales_invoice_date__month=i, sales_invoice_date__year=current_year)
                    p_quantity = 0
                    s_quantity = 0
                    opening_stock_quantity = 0
                    for stock in opening_stock:
                        for o_item in stock.openingstockitem_set.filter(batch_item=batch_item):
                            opening_stock_quantity = float(o_item.quantity) + float(opening_stock_quantity)
                    for purchase in purchases:
                        for p_item in purchase.purchaseitem_set.filter(batch_item=batch_item):
                            p_quantity = float(p_item.quantity) + float(p_quantity)
                    for sale in sales:
                        for s_item in sale.salesitem_set.filter(batch_item=batch_item):
                            quantity = float(s_item.quantity)/float(s_item.batch_item.uom_conversion.relation)
                            s_quantity = float(quantity) + float(s_quantity)
                    fields = [p_quantity + opening_stock_quantity, s_quantity]
                    ctx_month_details.append({
                        'name': month_name,
                        'fields' : fields
                    })
                stock_items.append({
                   'item_name' : batch_item.item.name,
                   'month_details': ctx_month_details,
                })
                ctx_month_details = []
            res = {
                'stock': stock_items,
                'months': ctx_months,
                'result': 'ok'
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        else:
            return render(request, 'stock_aging_report.html', {})

class AllStockReport(View):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/pdf')
        p = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        data = []
        d = [['Stock Report']]
        t = Table(d, colWidths=(450), rowHeights=25, style=style)
        t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('FONTSIZE', (0,0), (0,0), 15),
                    ])   
        elements.append(t)
        elements.append(Spacer(2,20 ))
        data = []
        data.append(['Item', 'Product', 'Brand', 'Category', 'Size', 'Batch', 'Stock', 'Uom' ])
        table = Table(data, colWidths=(120, 60, 60, 70, 50, 50, 100, 50), rowHeights=25, style=style)
        table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.white),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ('FONTNAME', (0, 0), (-1,-1), 'Helvetica-Bold')
                    ])
        elements.append(table)
        data = []
        items = Item.objects.all()
        for item in items:
            quantity = 0
            batch_items = BatchItem.objects.filter(item=item)
            for batch_item in batch_items:
                quantity = float(quantity) + float(batch_item.quantity)
                data.append([Paragraph(item.name, para_style), Paragraph(item.product.name, para_style), Paragraph(item.brand.name, para_style), Paragraph(item.product.category.name, para_style), Paragraph(item.size, para_style), Paragraph(batch_item.batch.name, para_style), round(batch_item.quantity, 2), Paragraph(batch_item.uom, para_style)])
        table = Table(data, colWidths=(120, 60, 60, 70, 50, 50, 100, 50), style=style)
        table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.white),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ('FONTSIZE', (0, 0), (-1,-1), 9)
                    ])   
        elements.append(table)
        p.build(elements)        
        return response