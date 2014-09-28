
import simplejson
import ast
from datetime import datetime

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.admin.util import lookup_field

from web.models import Staff, Permission, Salesman, Shope
from sales.models import Sale

def get_user_permission(request, permission_module):
    if request.user.is_superuser:
        return True
    else:
        if request.user.staff_set.all()[0].permission:
            data = lookup_field(permission_module, request.user.staff_set.all()[0].permission)
            return data[-1]
        else:
            return False

class Home(View):
    def get(self, request, *args, **kwargs):
        shope_details = Shope.objects.all()
        try:
            stock_value = StockValue.objects.latest('id')
            stock_by_value = stock_value.stock_by_value
        except:
            stock_by_value = 0
        if shope_details.count() > 0:
            shope = shope_details[0]
            res = {
                'result': 'ok',
                'shop_exists': True,
                'shope_details': {
                    'name': shope.name,
                    'address': shope.address,
                    'email': shope.email,
                    'contact_no': shope.contact_no
                }
            }
        else:
            shope = None
            res = {
                'result': 'ok',
                'shope_details': [],
                'shope_exists': False,
            }
        if request.is_ajax():            
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'home.html', 
            {
                'shope': shope
            }
        )


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html', {})

    def post(self, request, *args, **kwargs):

        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            context = {
                'message' : 'Username or password is incorrect',
                'username': request.POST['username']
            }
            return render(request, 'login.html', context)     

class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))

class StaffList(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            if request.is_ajax():
                staffs = Staff.objects.all()
                ctx_staffs = []
                for staff in staffs:
                    ctx_staffs.append({
                        'id': staff.id,
                        'name': staff.user.first_name + ' ' +staff.user.last_name if staff.user else '',
                        'first_name': staff.user.first_name,
                        'last_name': staff.user.last_name,
                        'username': staff.user.username,
                        'address': staff.address,
                        'contact_no': staff.contact_no,
                        'designation': staff.designation,
                        'email': staff.user.email if staff.user else '',
                    })
                res = {
                    'result': 'ok',
                    'staffs': ctx_staffs,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')

            return render(request, 'staffs.html', {})
        else:
            return render(request, 'staffs.html', {'message': 'You have no permission to access this page'})

class AddStaff(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            staff_details = ast.literal_eval(request.POST['staff_details'])
            if staff_details.get('id', ''):
                staff = Staff.objects.get(id=staff_details['id'])
                user = staff.user
            else:
                try:
                    user = User.objects.get(username=staff_details['username'])
                    res = {
                        'result': 'error',
                        'message': 'Username already exists',
                    }
                except Exception as ex:
                    user = User.objects.create(username=staff_details['username'])
                    user.set_password(staff_details['password'])
                    user.save()
                    staff = Staff.objects.create(user=user)
            user.first_name = staff_details['first_name']
            user.last_name = staff_details['last_name']
            user.email = staff_details['email']
            user.save()
            staff.user = user
            staff.designation = staff_details['designation']
            staff.address = request.POST['address']
            staff.contact_no = staff_details['contact_no']
            staff.save()
            res = {
                'result': 'ok',
                'name': staff.user.first_name + '  ' + staff.user.last_name,
                'id': staff.id,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class DeleteStaff(View):

    def get(self, request, *args, **kwargs):
        staff_id = request.GET.get('staff_id', '')
        if staff_id:
            staff = Staff.objects.get(id=staff_id)
            staff.user.delete()
            staff.delete()
        return HttpResponseRedirect(reverse('staffs'))

class CheckStaffUserExists(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', '')
        if username:
            try:
                user = User.objects.get(username=username)
                res = {
                    'result': 'error',
                    'message': 'Username already exists',
                }
            except Exception as ex:
                res = {
                    'result': 'ok',
                }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class SearchStaff(View):

    def get(self, request, *args, **kwargs):

        staff_name = request.GET.get('staff_name', '')
        ctx_staffs = []
        if staff_name:
            staffs = Staff.objects.filter(user__first_name__istartswith=staff_name)
            for staff in staffs:
                ctx_staffs.append({
                    'id': staff.id,
                    'name': staff.user.first_name + '  ' + staff.user.last_name,
                    'accounts_permission': 'true' if staff.permission and staff.permission.accounts_permission else 'false',
                    'inventory_permission': 'true' if staff.permission and staff.permission.inventory_permission else 'false',
                    'purchase_permission': 'true' if staff.permission and staff.permission.purchase_permission else 'false',
                    'sales_permission': 'true' if staff.permission and staff.permission.sales_permission else 'false',
                    'suppliers': 'true' if staff.permission and staff.permission.suppliers else 'false',
                    'customers': 'true' if staff.permission and staff.permission.customers else 'false',
                    'first_name': staff.user.first_name,
                    'last_name': staff.user.last_name,
                    'username': staff.user.username,
                    'address': staff.address,
                    'contact_no': staff.contact_no,
                    'designation': staff.designation,
                    'email': staff.user.email if staff.user else '',
                })
        res = {
            'result': 'ok',
            'staffs': ctx_staffs,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class SetPermissions(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'permission.html', {})
    def post(self, request, *args, **kwargs):

        permission_details = ast.literal_eval(request.POST['staff_permission'])
        staff_id = permission_details['staff']
        staff = Staff.objects.get(id=staff_id)
        if staff.permission:
            permission = staff.permission
        else:
            permission = Permission()
        if permission_details['accounts_permission'] == 'true':
            permission.accounts_permission = True
        else:
            permission.accounts_permission = False
        if permission_details['inventory_permission'] == 'true':
            permission.inventory_permission = True
        else:
            permission.inventory_permission = False
        if permission_details['purchase_permission'] == 'true':
            permission.purchase_permission = True
        else:
            permission.purchase_permission = False
        if permission_details['sales_permission'] == 'true':
            permission.sales_permission = True
        else:
            permission.sales_permission = False
        if permission_details['suppliers'] == 'true':
            permission.suppliers = True
        else:
            permission.suppliers = False
        if permission_details['customers'] == 'true':
            permission.customers = True
        else:
            permission.customers = False
        permission.save()
        staff.permission = permission
        staff.save()
        res = {
            'result': 'ok'
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class Salesmen(View):

    def get(self, request, *args, **kwargs):

        if request.is_ajax():
            try:
                salesmen = Salesman.objects.all()
                ctx_salesmen= []
                for salesman in salesmen:
                    ctx_salesmen.append({
                        'id': salesman.id,
                        'name': salesman.first_name + " " + salesman.last_name,
                        'first_name': salesman.first_name,
                        'last_name': salesman.last_name,
                        'address': salesman.address,
                        'contact_no': salesman.contact_no,
                        'email': salesman.email if salesman.email else '',
                        })
                res = {
                    'result': 'ok',
                    'salesmen': ctx_salesmen,
                }
            except Exception as ex:
                print str(ex)
                res = {
                    'result': 'error',
                }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'salesmen.html', {})

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            salesman_details = ast.literal_eval(request.POST['salesman_details'])
            try:
                if salesman_details.get('id', ''):
                    salesman = Salesman.objects.get(id=salesman_details.get('id', ''))
                else:
                    salesman = Salesman()
                salesman.first_name = salesman_details['first_name']
                salesman.last_name = salesman_details['last_name']
                salesman.address = salesman_details['address']
                salesman.contact_no = salesman_details['contact_no']
                salesman.email = salesman_details['email']
                salesman.save()
                res = {
                    'result': 'ok',
                    'message': 'ok',
                    'salesman' : {
                        'id': salesman.id,
                        'name': salesman.first_name + " " + salesman.last_name,
                        'first_name': salesman.first_name,
                        'last_name': salesman.last_name,
                        'address': salesman.address,
                        'contact_no': salesman.contact_no,
                        'email': salesman.email if salesman.email else '',
                        }
                }
            except:
                res = {
                    'result': 'error',
                }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class DeleteSalesman(View):

    def get(self, request, *args, **kwargs):
        salesman_id = request.GET.get('id', '')
        salesman = Salesman.objects.get(id=salesman_id)
        salesman.delete()
        return HttpResponseRedirect(reverse('salesmen'))


class SearchSalesman(View):

    def get(self, request, *args, **kwargs):

        salesman_name = request.GET.get('salesman_name', '')
        ctx_salesmen = []
        salesmen = Salesman.objects.filter(first_name__istartswith=salesman_name)
        for salesman in salesmen:
            ctx_salesmen.append({
                'id': salesman.id,
                'name': salesman.first_name + " " + salesman.last_name,
                'first_name': salesman.first_name,
                'last_name': salesman.last_name,
                'address': salesman.address,
                'contact_no': salesman.contact_no,
                'email': salesman.email if salesman.email else '',
                })
        res = {
            'result': 'ok',
            'salesmen': ctx_salesmen,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')        

class ShopeDetails(View):
    def post(self, request, *args, **kwargs):
        shope = Shope()
        shope.name = request.POST['name']
        shope.address = request.POST['address']
        shope.email = request.POST['email']
        shope.contact_no = request.POST['contact_no']
        shope.save()
        return HttpResponse('Shop saved Successfully')

class Incentives(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'incentives.html', {})


class SalesmanSales(View):

    def get(self, request, *args, **kwargs):

        salesman_id = request.GET.get('salesman_id', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        salesman = Salesman.objects.get(id=salesman_id)
        sales = Sale.objects.filter(salesman=salesman, sales_invoice_date__gte=datetime.strptime(start_date, '%d/%m/%Y'), sales_invoice_date__lte=datetime.strptime(end_date, '%d/%m/%Y'))
        res = {
            'result': 'ok',
            'no_of_sales': sales.count(),
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')        
