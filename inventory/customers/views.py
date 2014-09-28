import simplejson
import ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY, TA_CENTER

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect

from customers.models import Customer
from accounting.models import Ledger, LedgerEntry

from web.views import get_user_permission

style = [
    ('FONTSIZE', (0,0), (-1, -1), 12),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]

para_style = ParagraphStyle('fancy')
para_style.fontSize = 12
para_style.fontName = 'Helvetica'


class Customers(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'customers'):
            customers = Customer.objects.all()
            ctx_customers= []
            if request.is_ajax():
                for customer in customers:
                    ctx_customers.append({
                        'id': customer.id,
                        'name': customer.name,
                        'address': customer.address,
                        'mobile': customer.mobile,
                        'telephone_number': customer.telephone_number,
                        'email': customer.email,
                        })
                res = {
                    'result': 'ok',
                    'customers': ctx_customers,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'customers.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))


class AddCustomer(View):

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            customer_details = ast.literal_eval(request.POST['customer'])
            try:
                parent = Ledger.objects.get(name='Sundry Debtors')
                if customer_details.get('id', ''):
                    customer = Customer.objects.get(id=customer_details.get('id', ''))
                else:
                    customer = Customer()
                try:
                    customer.name = customer_details['name']
                    customer.address = customer_details['address']
                    customer.mobile = customer_details['mobile']
                    customer.telephone_number = customer_details['telephone_number']
                    customer.email = customer_details['email']
                    customer.save()
                    if customer.ledger:
                        customer.ledger.name = customer_details['name']
                        customer.ledger.save()
                    else:
                        ledger = Ledger()
                        ledger.parent = parent
                        ledger.name = customer_details['name']
                        ledger.save()
                        customer.ledger = ledger
                    customer.save()
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                        'customer': {
                            'id': customer.id,
                            'name': customer.name,
                            'address': customer.address,
                            'mobile': customer.mobile,
                            'telephone_number': customer.telephone_number,
                            'email': customer.email,
                        }
                    }
                except Exception as ex:
                    print str(ex)
                    res = {
                        'result': 'error',
                        'message': 'Customer name already exists',
                    }
            except:
                res = {
                        'result': 'error',
                        'message': 'Ledger Sundry Debtors not found'
                    }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class DeleteCustomer(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'customers'):
            customer_id = request.GET.get('customer_id', '')
            customer = Customer.objects.get(id=customer_id)
            customer.ledger.delete()
            customer.delete()
            return HttpResponseRedirect(reverse('customer_list'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))   


class SearchCustomer(View):

    def get(self, request, *args, **kwargs):

        customer_name = request.GET.get('name', '')
        ctx_customers = []
        customers = Customer.objects.filter(name__istartswith=customer_name)
        for customer in customers:
            ctx_customers.append({
                'id': customer.id,
                'name': customer.name,
                'address': customer.address,
                'mobile': customer.mobile,
                'telephone_number': customer.telephone_number,
                'email': customer.email,
            })
        res = {
            'result': 'ok',
            'customers': ctx_customers,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class AccountsReceivable(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            if request.is_ajax():
                account_receivables_list = []
                count = 1
                account_receivables = Ledger.objects.filter(parent__name='Sundry Debtors')
                for account_receivable in account_receivables:
                    debit_balance = 0
                    credit_balance = 0
                    if account_receivable.balance >= 0:
                        debit_balance = account_receivable.balance
                    else:
                        credit_balance = account_receivable.balance
                    account_receivables_list.append({
                        'count': count,
                        'id': account_receivable.id,
                        'name': account_receivable.name,
                        'debit_balance': abs(debit_balance),
                        'credit_balance': abs(credit_balance),
                        })
                    count = count + 1
                res = {
                    'result': 'ok',
                    'account_receivables': account_receivables_list,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            if request.GET.get('report_type',''):
                response = HttpResponse(content_type='application/pdf')
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                status_code = 200
               
                p.setFontSize(20)
                p.drawString(350, y, 'Accounts Receivable Report')

                p.setFontSize(13)

                p.drawString(150, y - 30, "No")
                p.drawString(250, y-30, "Ledger Name")
                p.drawString(450, y-30, "Cr")
                p.drawString(550, y-30, "Dr")
                count = 0
               
                account_receivables = Ledger.objects.filter(parent__name='Sundry Debtors')
               
                if len(account_receivables) > 0:
                    for account_receivable in account_receivables:
                        
                        y = y - 50
                        if y <= 100:
                            y = 1100
                            p.showPage()
                        p.drawString(150,y,str(count+1))
                        data=[[Paragraph(account_receivable.name, para_style)]]

                        table = Table(data, colWidths=[100], rowHeights=100, style=style)      
                        table.wrapOn(p, 200, 400)
                        table.drawOn(p, 250, y)
                        debit_balance = 0
                        credit_balance = 0
                        if account_receivable.balance >= 0:
                            debit_balance = abs(account_receivable.balance)
                        else:
                            credit_balance = abs(account_receivable.balance)
                        p.drawString(450, y, str(debit_balance))
                        p.drawString(550, y, str(credit_balance))
                        count = count + 1

                p.showPage()
                p.save()
                return response
            else:            
                return render(request, 'accounts_receivable.html',{})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class ReceivedReport(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            if not start_date:            
                return render(request, 'received_report.html', {})
            elif not end_date:
                return render(request, 'received_report.html', {}) 
            else:
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
                end_date = datetime.strptime(end_date, '%d/%m/%Y')
            if request.is_ajax():
                ledger_entries_list = []
                count = 1
                # date = datetime.strptime(request.GET.get('date', ''), '%d/%m/%Y')
                customers = Customer.objects.all()
                for customer in customers:
                    if customer.ledger.balance <=0:
                        ledger_entries = LedgerEntry.objects.filter(ledger=customer.ledger,date__gte=start_date, date__lte=end_date).order_by('-date')

                        for ledger_entry in ledger_entries:
                            if not ledger_entry.debit_amount:
                                ledger_entries_list.append({
                                    'count': count,
                                    'customer_name': customer.name,
                                    'name': ledger_entry.ledger.name,
                                    'credit_amount': ledger_entry.credit_amount,
                                    'debit_amount': ledger_entry.debit_amount,
                                    'date': ledger_entry.date.strftime('%d/%m/%Y'),
                                    })
                                count = count + 1
                res = {
                    'result': 'ok',
                    'ledger_entries': ledger_entries_list,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            if request.GET.get('report_type',''):
                response = HttpResponse(content_type='application/pdf')
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                status_code = 200
               
                p.setFontSize(20)
                p.drawString(350, y, 'Date Wise Received Report')
                
                p.setFontSize(13)

                p.drawString(150, y - 30, "No")
                p.drawString(250, y-30, "Date")
                p.drawString(350, y-30, "Customer Name")
                p.drawString(550, y-30, "Cr")
                p.drawString(650, y-30, "Dr")
                count = 0
                customers = Customer.objects.all()
                for customer in customers:
                    
                    if customer.ledger.balance <= 0:
                        ledger_entries = LedgerEntry.objects.filter(ledger=customer.ledger, date__gte=start_date, date__lte=end_date).order_by('-date')
                        if len(ledger_entries) > 0:
                            for ledger_entry in ledger_entries:
                                if not ledger_entry.debit_amount:
                                    y = y - 50
                                    if y <= 100:
                                        y = 1100
                                        p.showPage()
                                    p.drawString(150,y,str(count+1))
                                    p.drawString(250, y, ledger_entry.date.strftime('%d/%m/%Y') if ledger_entry.date else '')
                                    data=[[Paragraph(customer.name, para_style)]]

                                    table = Table(data, colWidths=[100], rowHeights=100, style=style)      
                                    table.wrapOn(p, 200, 400)
                                    table.drawOn(p, 350, y)
                                    # p.drawString(350, y, ledger_entry.ledger.name)
                                    p.drawString(550, y, str(ledger_entry.credit_amount)if ledger_entry.credit_amount else '')
                                    p.drawString(650, y, str(ledger_entry.debit_amount)if ledger_entry.debit_amount else '')
                                    count = count + 1

                p.showPage()
                p.save()
                return response
            else:            
                return render(request, 'ledger_report.html',{})
        else:
            return HttpResponseRedirect(reverse('dashboard'))