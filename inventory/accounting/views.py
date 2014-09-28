
import simplejson
import ast
from datetime import datetime
import decimal
import itertools

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.enums import TA_CENTER


from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from accounting.models import Ledger, Transaction, LedgerEntry
from inventory.models import OpeningStockValue, StockValue
from purchases.models import FreightValue

from web.views import get_user_permission
from web.models import Shope

style = [
    ('FONTSIZE', (0,0), (-1, -1), 12),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]

para_style = ParagraphStyle('fancy')
para_style.fontSize = 12
para_style.fontName = 'Helvetica'


def get_ledger_list():
    ctx_ledgers = []
    ledgers = Ledger.objects.filter(parent=None)
    for ledger in ledgers:
        ctx_ledgers.append({
            'subledgers': [],
            'id': ledger.id,
            'name': ledger.name,
        })
    res = {
        'ledgers': ctx_ledgers,
        'result': 'ok',
    }
    response = simplejson.dumps(res)
    return HttpResponse(response, status=200, mimetype='application/json')

class Ledgers(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            if request.is_ajax():
                return get_ledger_list()
            return render(request, 'ledgers.html', {})   
        else:
            return HttpResponseRedirect(reverse('dashboard'))       


class AddLedger(View):

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            ledger_details = ast.literal_eval(request.POST['ledger'])
            if ledger_details.get('id', ''):
                ledger = Ledger.objects.get(id=ledger_details.get('id', ''))
                try:
                    if ledger_details['parent'] != '': 
                        parent = Ledger.objects.get(id=ledger_details['parent'])
                        ledgers = Ledger.objects.filter(parent=parent, name=ledger_details['name'])
                        if ledgers.count() > 0:
                            res = {
                                'result': 'error',
                                'message': 'Ledger name already exists',
                            }
                        else:
                            ledger.name = ledger_details['name']
                            ledger.parent = parent
                    else:
                        ledger.name = ledger_details['name']
                    ledger.save()
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                    }
                except Exception as ex:
                    res = {
                        'result': 'error',
                        'message': 'Ledger name already exists',
                    }
            else:
                try:
                    if ledger_details['parent'] != '': 
                        parent = Ledger.objects.get(id=ledger_details['parent'])
                        ledger = Ledger.objects.get(name=ledger_details['name'], parent=parent)
                    else:
                        ledger = Ledger.objects.get(name=ledger_details['name'])
                    res = {
                        'result': 'error',
                        'message': 'Ledger name already exists',
                    }
                except Exception as ex:
                    if ledger_details['parent'] != '': 
                        parent = Ledger.objects.get(id=ledger_details['parent'])
                        ledger = Ledger.objects.create(name=ledger_details['name'], parent=parent)
                    else:
                        ledger = Ledger.objects.create(name=ledger_details['name'])
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                        'new_ledger': {
                            'id': ledger.id,
                            'name': ledger.name,
                        }
                    }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')


class LedgerTreeView(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            if request.is_ajax():
                return get_ledger_list()
            return render(request, 'ledgers_tree_view.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))


class SearchLedger(View):

    def get(self, request, *args, **kwargs):
        ledger_name = request.GET.get('name', '')
        filtr = request.GET.get('filter', '')
        ctx_ledgers = []
        ledgers = Ledger.objects.filter(name__istartswith=ledger_name)
        for ledger in ledgers:
            if filtr == 'true':
                if ledger.ledger_set.all().count() == 0:
                    ctx_ledgers.append({
                        'id': ledger.id,
                        'name': ledger.name,
                    })
                else:
                    pass
            else:
                ctx_ledgers.append({
                    'id': ledger.id,
                    'name': ledger.name,
                })
        res = {
            'result': 'ok',
            'ledgers': ctx_ledgers,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class LedgerBalance(View):
    def get(self, request, *args, **kwargs):
        ledger_name = request.GET.get('ledger_name', '')
        ctx_ledgers = []
        ledgers = Ledger.objects.filter(name__istartswith=ledger_name)
        for ledger in ledgers:            
            ctx_ledgers.append({
                'id': ledger.id,
                'name': ledger.name,
                'balance': ledger.balance
            })            
        res = {
            'result': 'ok',
            'ledgers': ctx_ledgers,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeleteLedger(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            ledger_id = request.GET.get('ledger_id', '')
            ledger = Ledger.objects.get(id=ledger_id)
            ledger.delete()
            return HttpResponseRedirect(reverse('ledgers'))  
        else:
            return HttpResponseRedirect(reverse('dashboard'))       


class SubledgerDetails(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            ledger_id = kwargs['ledger_id']
            context = {
                'ledger_id': ledger_id,
            }
            return render(request, 'sub_ledgers.html', context)     
        else:
            return HttpResponseRedirect(reverse('dashboard'))


class LedgerSubledgerList(View):

    def get(self, request, *args, **kwargs):

        ledger_id = kwargs['ledger_id']
        ledger = Ledger.objects.get(id=ledger_id)
        ctx_ledger_details = []
        ctx_subledger = []
        sub_ledgers = Ledger.objects.filter(parent=ledger)
        for sub_ledger in sub_ledgers:
            ctx_subledger.append({
                'id': sub_ledger.id,
                'name': sub_ledger.name,
                'subledgers': [],
                'temp_subledgers': [],
            })
        ctx_ledger_details.append({
            'id': ledger.id,
            'name': ledger.name,
            'sub_ledgers': ctx_subledger,
        })
        res = {
            'result': 'ok',
            'subledgers': ctx_subledger,
            'ledger_details': ctx_ledger_details,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')      


class DeleteSubLedger(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            ledger_id = request.GET.get('ledger_id', '')
            ledger = Ledger.objects.get(id=ledger_id)
            ledger.delete()
            return HttpResponseRedirect(reverse('ledgers')) 
        else:
            return HttpResponseRedirect(reverse('dashboard'))    


class CreatePayment(View):

    def get(self, request, *args, **kwargs):   
        if get_user_permission(request, 'accounts_permission'):     
            return render(request, 'create_payment.html', {}) 
        else:
            return HttpResponseRedirect(reverse('dashboard'))  

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            payment_details = ast.literal_eval(request.POST['payment'])
            transaction = Transaction()            
            if payment_details['mode'] == 'cash':
                credit_ledger = Ledger.objects.get(name="Cash")
                ledger_entry = LedgerEntry()
                ledger_entry.ledger = credit_ledger
                ledger_entry.credit_amount = payment_details['amount']
                ledger_entry.date = datetime.strptime(payment_details['transaction_date'], '%d/%m/%Y')
            else:
                credit_ledger = Ledger.objects.get(id=payment_details['bank_account'])
                ledger_entry = LedgerEntry()
                ledger_entry.ledger = credit_ledger
                ledger_entry.credit_amount = payment_details['amount']
                ledger_entry.date = datetime.strptime(payment_details['transaction_date'], '%d/%m/%Y')
            ledger_entry.save()
            credit_ledger.balance = float(credit_ledger.balance) - float(payment_details['amount'])
            credit_ledger.save()
            try:
                transaction_ref = Transaction.objects.latest('id').id
                transaction.transaction_ref = 'PY'+str(transaction_ref+1)
            except:
                transaction_ref = '1'
                transaction.transaction_ref = 'PY'+str(transaction_ref)
            ledger_entry.transaction_reference_number = transaction.transaction_ref 
            ledger_entry.save()
            transaction.credit_ledger = ledger_entry
            ledger_id = payment_details['ledger']
            ledger = Ledger.objects.get(id=ledger_id)
            debit_ledger_entry = LedgerEntry()
            debit_ledger_entry.ledger = ledger
            debit_ledger_entry.debit_amount = payment_details['amount']
            debit_ledger_entry.date = datetime.strptime(payment_details['transaction_date'], '%d/%m/%Y')
            debit_ledger_entry.save()
            ledger.balance = float(ledger.balance) + float(debit_ledger_entry.debit_amount)
            ledger.save()
            transaction.debit_ledger = debit_ledger_entry
            transaction.transaction_date = datetime.strptime(payment_details['transaction_date'], '%d/%m/%Y')
            transaction.debit_amount = payment_details['amount']
            transaction.credit_amount = payment_details['amount']
            if payment_details.get('narration', ''):
                transaction.narration = payment_details['narration']
            transaction.payment_mode = payment_details['mode']
            if payment_details['mode'] == 'card':
                transaction.bank_name = payment_details['bank_name']
                transaction.card_holder_name = payment_details['card_holder_name']
                transaction.card_no = payment_details['card_no']
            elif payment_details['mode'] == 'cheque':
                transaction.bank_name = payment_details['bank_name']
                transaction.cheque_date = datetime.strptime(payment_details['cheque_date'], '%d/%m/%Y')
                transaction.cheque_number = payment_details['cheque_number']
                transaction.branch = payment_details['branch']
            transaction.save()
            res = {
                'result': 'ok',
                'message': 'Payment saved successfully',
                'transaction_reference_no': transaction.transaction_ref,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')      


class CreateReceipt(View):

    def get(self, request, *args, **kwargs):  
        if get_user_permission(request, 'accounts_permission'):      
            return render(request, 'create_receipt.html', {}) 
        else:
            return HttpResponseRedirect(reverse('dashboard'))  

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            receipt_details = ast.literal_eval(request.POST['receipt'])
            transaction = Transaction()            
            if receipt_details['mode'] == 'cash':
                debit_ledger = Ledger.objects.get(name="Cash")
                ledger_entry = LedgerEntry()
                ledger_entry.ledger = debit_ledger
                ledger_entry.debit_amount = receipt_details['amount']
                ledger_entry.date = datetime.strptime(receipt_details['transaction_date'], '%d/%m/%Y')
            else:
                debit_ledger = Ledger.objects.get(id=receipt_details['bank_ledger'])
                ledger_entry = LedgerEntry()
                ledger_entry.ledger = debit_ledger
                ledger_entry.debit_amount = receipt_details['amount']
                ledger_entry.date = datetime.strptime(receipt_details['transaction_date'], '%d/%m/%Y')
            ledger_entry.save()
            debit_ledger.balance = float(debit_ledger.balance) + float(receipt_details['amount'])
            debit_ledger.save()
            try:
                transaction_ref = Transaction.objects.latest('id').id
                transaction.transaction_ref = 'RCPT'+str(transaction_ref+1)
            except:
                transaction_ref = '1'
                transaction.transaction_ref = 'RCPT'+str(transaction_ref)
            transaction.save()
            ledger_entry.transaction_reference_number = transaction.transaction_ref
            ledger_entry.save()
            transaction.debit_ledger = ledger_entry
            ledger_id = receipt_details['ledger']
            ledger = Ledger.objects.get(id=ledger_id)
            credit_ledger_entry = LedgerEntry()
            credit_ledger_entry.ledger = ledger
            credit_ledger_entry.credit_amount = receipt_details['amount']
            credit_ledger_entry.date = datetime.strptime(receipt_details['transaction_date'], '%d/%m/%Y')
            credit_ledger_entry.transaction_reference_number = transaction.transaction_ref
            credit_ledger_entry.save()
            ledger.balance = float(ledger.balance) - float(credit_ledger_entry.credit_amount)
            ledger.save()
            transaction.credit_ledger = credit_ledger_entry
            transaction.transaction_date = datetime.strptime(receipt_details['transaction_date'], '%d/%m/%Y')
            transaction.credit_amount = receipt_details['amount']
            transaction.debit_amount = receipt_details['amount']
            if receipt_details.get('narration', ''):
                transaction.narration = receipt_details['narration']
            transaction.payment_mode = receipt_details['mode']
            if receipt_details['mode'] == 'card':
                transaction.bank_name = receipt_details['bank_name']
                transaction.card_holder_name = receipt_details['card_holder_name']
                transaction.card_no = receipt_details['card_no']
            elif receipt_details['mode'] == 'cheque':
                transaction.bank_name = receipt_details['bank_name']
                transaction.cheque_date = datetime.strptime(receipt_details['cheque_date'], '%d/%m/%Y')
                transaction.cheque_number = receipt_details['cheque_number']
                transaction.branch = receipt_details['branch']
            transaction.save()
            res = {
                'result': 'ok',
                'message': 'Receipt saved successfully',
                'transaction_reference_no': transaction.transaction_ref,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')  


class OtherTransaction(View):

    def get(self, request, *args, **kwargs):   
        if get_user_permission(request, 'accounts_permission'):     
            return render(request, 'other_transaction.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))            

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            transaction_details = ast.literal_eval(request.POST['transaction'])
            transaction = Transaction()
            debit_ledger = Ledger.objects.get(id=transaction_details['debit_ledger'])
            credit_ledger = Ledger.objects.get(id=transaction_details['credit_ledger'])
            transaction.transaction_date = datetime.strptime(transaction_details['transaction_date'], '%d/%m/%Y')
            transaction.debit_amount = transaction_details['amount']
            transaction.credit_amount = transaction_details['amount']
            if transaction_details.get('narration', ''):
                transaction.narration = transaction_details['narration']
            transaction.payment_mode = transaction_details['mode']
            if transaction_details['mode'] == 'card':
                transaction.bank_name = transaction_details['bank_name']
                transaction.card_holder_name = transaction_details['card_holder_name']
                transaction.card_no = transaction_details['card_no']
            elif transaction_details['mode'] == 'cheque':
                transaction.bank_name = transaction_details['bank_name']
                transaction.cheque_date = datetime.strptime(transaction_details['cheque_date'], '%d/%m/%Y')
                transaction.cheque_number = transaction_details['cheque_number']
                transaction.branch = transaction_details['branch']
            debit_ledger_entry = LedgerEntry()
            debit_ledger_entry.ledger = debit_ledger
            debit_ledger_entry.debit_amount = transaction_details['amount']
            debit_ledger_entry.date = datetime.strptime(transaction_details['transaction_date'], '%d/%m/%Y')
            debit_ledger_entry.save()
            credit_ledger_entry = LedgerEntry()
            credit_ledger_entry.ledger = credit_ledger
            credit_ledger_entry.credit_amount = transaction_details['amount']
            credit_ledger_entry.date = datetime.strptime(transaction_details['transaction_date'], '%d/%m/%Y')
            credit_ledger_entry.save()
            debit_ledger.balance = float(debit_ledger.balance) + float(transaction_details['amount'])
            debit_ledger.save()
            credit_ledger.balance = float(credit_ledger.balance) - float(transaction_details['amount'])
            credit_ledger.save()
            try:
                transaction_ref = Transaction.objects.latest('id').id
                transaction.transaction_ref = 'OT'+str(transaction_ref+1)
            except:
                transaction_ref = '1'
                transaction.transaction_ref = 'OT'+str(transaction_ref)
            debit_ledger_entry.transaction_reference_number = transaction.transaction_ref
            debit_ledger_entry.save()
            credit_ledger_entry.transaction_reference_number = transaction.transaction_ref
            credit_ledger_entry.save()
            transaction.debit_ledger = debit_ledger_entry
            transaction.credit_ledger = credit_ledger_entry
            transaction.save()
            res = {
                'result': 'ok',
                'message': 'Transaction saved successfully',
                'transaction_reference_no': transaction.transaction_ref,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')          
         

class LedgerReport(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            ledger = request.GET.get('ledger')
            if not start_date:            
                return render(request, 'ledger_report.html', {})
            elif not end_date:
                return render(request, 'ledger_report.html', {}) 
            else:
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
                end_date = datetime.strptime(end_date, '%d/%m/%Y')
            if request.is_ajax():
                ledger_entries_list = []
                if request.GET.get('ledger',''):
                    ledger_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                    print ledger_entries
                for ledger_entry in ledger_entries:
                    ledger_entries_list.append({
                        'id': ledger_entry.id,
                        'transaction_ref': ledger_entry.transaction_ref,
                        'debit_ledger': ledger_entry.debit_ledger.ledger.name,
                        'debit_ledger_debit': ledger_entry.debit_ledger.debit_amount if ledger_entry.debit_ledger.debit_amount else '',
                        'debit_ledger_credit': ledger_entry.debit_ledger.credit_amount if ledger_entry.debit_ledger.credit_amount else '',
                        'credit_ledger': ledger_entry.credit_ledger.ledger.name,
                        'credit_ledger_debit': ledger_entry.credit_ledger.debit_amount if ledger_entry.credit_ledger.debit_amount else '',
                        'credit_ledger_credit': ledger_entry.credit_ledger.credit_amount if ledger_entry.credit_ledger.credit_amount else '',
                        'debit_amount': ledger_entry.debit_amount,
                        'credit_amount': ledger_entry.credit_amount,
                        'date': ledger_entry.transaction_date.strftime('%d/%m/%Y'),
                    })
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
                p.setFontSize(20)
                p.drawString(350, y, 'Date Wise Ledger Report')
                p.setFontSize(13)
                p.drawString(100, y - 50, "From")
                p.drawString(150, y - 50, ":")
                p.drawString(180, y - 50, str(start_date.strftime('%d/%m/%Y')))
                p.drawString(100, y - 80, "To")
                p.drawString(150, y - 80, ":")
                p.drawString(180, y - 80, str(end_date.strftime('%d/%m/%Y')))
                y = y - 80
                p.drawString(100, y - 50, "No")
                p.drawString(180, y - 50, "Date")
                p.drawString(300, y - 50, "Ref No")
                p.drawString(400, y - 50, "Ledger Entry")
                p.drawString(600, y - 50, "Debit Amount")
                p.drawString(800, y - 50, "Credit Amount")
                count = 1
                if ledger:
                    ledger_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                y = y - 90
                ledger_name = Ledger.objects.get(id=request.GET.get('ledger'))
                print ledger_name.name
                if len(ledger_entries) > 0:
                    for ledger_entry in ledger_entries:     
                        p.drawString(100, y - 30, str(count))
                        p.drawString(180, y - 30, str(ledger_entry.transaction_date.strftime('%d/%m/%Y')))
                        p.drawString(300, y - 30, str(ledger_entry.transaction_ref))
                        print ledger
                        if ledger_entry.debit_ledger.ledger.name != ledger_name.name:
                            #table is used for wrapping text within column
                            data=[[Paragraph(ledger_entry.debit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 200, 400)
                            table.drawOn(p, 400, y-30)
                            p.drawString(600, y - 30, str(ledger_entry.credit_amount))
                            count = count + 1
                            y = y - 30
                        else:
                            #table is used for wrapping text within column
                            data=[[Paragraph(ledger_entry.credit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 200, 400)
                            table.drawOn(p, 400, y-30)
                            p.drawString(800, y - 30, str(ledger_entry.debit_amount))
                            count = count + 1
                            y = y - 30
                        if y <= 100:
                            y = 1200
                            p.showPage()
                p.save()
                return response
            else:            
                return render(request, 'ledger_report.html',{})
        else:
            return HttpResponseRedirect(reverse('dashboard'))


class OpeningBalance(View):

    def get(self, request, *args, **kwargs):        
        if get_user_permission(request, 'accounts_permission'):
            return render(request, 'opening_balance.html', {})  
        else:
            return HttpResponseRedirect(reverse('dashboard'))

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            opening_balance_details = ast.literal_eval(request.POST['opening_balance'])
            ledger =  Ledger.objects.get(id=opening_balance_details['ledger'])
            opening_balance = LedgerEntry()
            opening_balance.ledger = ledger
            if float(opening_balance_details['amount']) < 0:
                opening_balance.credit_amount = abs(float(opening_balance_details['amount']))
            else:
                opening_balance.debit_amount = opening_balance_details['amount']
            opening_balance.date = datetime.now()
            opening_balance.save()
            opening_balance.ledger.balance = float(opening_balance.ledger.balance) + float(opening_balance_details['amount'])
            opening_balance.ledger.save()

            transaction = Transaction()
            transaction.debit_ledger = opening_balance
            transaction.debit_amount = opening_balance.debit_amount
            transaction.date = opening_balance.date
            transaction.save()
            transaction.transaction_ref = 'OPBL' + str(transaction.id)
            transaction.save()
            opening_balance.transaction_reference_number = transaction.transaction_ref
            opening_balance.save()
            res = {
                'result': 'ok',
                'message': 'Transaction saved successfully'
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')          


class DayBook(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            current_date = datetime.now().date()
            if request.GET.get('date', ''):
                date = datetime.strptime(request.GET.get('date', ''), '%d/%m/%Y')
                stock_ledger = Ledger.objects.get(name="Stock")
                if request.GET.get('ledger',''):
                    ledger = Ledger.objects.get(id=request.GET.get('ledger',''))
                    transactions = Transaction.objects.filter(Q(transaction_date=date), Q(debit_ledger__ledger=ledger) | Q(credit_ledger__ledger=ledger)).order_by('transaction_date')
                else:
                    print date
                    transactions = Transaction.objects.filter(Q(transaction_date=date)).order_by('transaction_date')
                print transactions
            if request.is_ajax():
                transaction_entries_list = []
                for transaction in transactions:
                    stock_transaction = False
                    if transaction.debit_ledger:
                        if transaction.debit_ledger.ledger == stock_ledger:
                            stock_transaction = True
                            continue
                    if transaction.credit_ledger:
                        if transaction.credit_ledger.ledger == stock_ledger:
                            stock_transaction = True
                            continue
                    if not stock_transaction: 
                        if transaction.debit_ledger:
                            transaction_entries_list.append({
                                'id': transaction.id,
                                'transaction_ref': transaction.transaction_ref,
                                'debit_ledger': transaction.debit_ledger.ledger.name if transaction.debit_ledger else '',
                                'debit_amount': transaction.debit_amount,
                                'date': transaction.transaction_date.strftime('%d/%m/%Y'),
                            })
                        if transaction.credit_ledger:
                            transaction_entries_list.append({
                                'id': transaction.id,
                                'transaction_ref': transaction.transaction_ref,
                                'credit_ledger': transaction.credit_ledger.ledger.name if transaction.credit_ledger else '',
                                'credit_amount': transaction.credit_amount,
                                'date': transaction.transaction_date.strftime('%d/%m/%Y'),
                            })
                res = {
                    'result': 'ok',
                    'transaction_entries': transaction_entries_list,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
                
            if request.GET.get('report_type',''):
                response = HttpResponse(content_type='application/pdf')
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                status_code = 200
                p.setFontSize(20)
                p.drawCentredString(500, y, 'Day Book on '+str(date.strftime('%d/%m/%Y')))
                p.setFontSize(13)
                p.drawString(50, y - 50, "No")
                p.drawString(100, y - 50, "Ref No")
                p.drawString(255, y - 50, "Ledger Entry")
                p.drawString(600, y - 50, "Debit Amount")
                p.drawString(750, y - 50, "Credit Amount")
                count = 1
                y = y - 50
                for transaction in transactions:
                    stock_transaction = False
                    if transaction.debit_ledger:
                        if transaction.debit_ledger.ledger == stock_ledger:
                            stock_transaction = True
                            continue
                    if transaction.credit_ledger:
                         if transaction.credit_ledger.ledger == stock_ledger:
                            stock_transaction = True
                            continue
                    if not stock_transaction:  
                        if transaction.debit_ledger:
                            p.drawString(50, y-30, str(count))
                            p.drawString(100, y - 30, str(transaction.transaction_ref))
                            #table is used for wrapping text within column
                            data=[[Paragraph(transaction.debit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 255, 400)
                            table.drawOn(p, 255, y-30)
                            
                            p.drawString(600, y - 30, str(transaction.debit_amount))
                            y = y - 30
                            count = count + 1
                        if transaction.credit_ledger:
                            p.drawString(50, y-30, str(count))
                            p.drawString(100, y - 30, str(transaction.transaction_ref))
                            #table is used for wrapping text within column
                            data=[[Paragraph(transaction.credit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 255, 400)
                            table.drawOn(p, 255, y-30)
                            p.drawString(750, y - 30, str(transaction.credit_amount))
                            count = count + 1                        
                            y = y - 30
                    if y <= 100:
                        y = 1200
                        p.showPage()
                p.save()
                return response

            else:            
                return render(request, 'day_book.html',{'current_date': current_date.strftime('%d/%m/%Y')})
        else:
            return HttpResponseRedirect(reverse('dashboard'))
                         

class CashBook(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            if request.is_ajax():
                cash_entries_list = []
                count = 1
                start_date = datetime.strptime(request.GET.get('start_date', ''), '%d/%m/%Y')
                end_date = datetime.strptime(request.GET.get('end_date', ''), '%d/%m/%Y')
                try:
                    ledger = Ledger.objects.get(name='Cash')
                    cash_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                    for cash_entry in cash_entries:
                        cash_entries_list.append({
                            'count': count,
                            'id': cash_entry.id,
                            'transaction_ref': cash_entry.transaction_ref,
                            'debit_ledger': cash_entry.debit_ledger.ledger.name,
                            'debit_ledger_debit': cash_entry.debit_ledger.debit_amount if cash_entry.debit_ledger.debit_amount else '',
                            'debit_ledger_credit': cash_entry.debit_ledger.credit_amount if cash_entry.debit_ledger.credit_amount else '',
                            'credit_ledger': cash_entry.credit_ledger.ledger.name,
                            'credit_ledger_debit': cash_entry.credit_ledger.debit_amount if cash_entry.credit_ledger.debit_amount else '',
                            'credit_ledger_credit': cash_entry.credit_ledger.credit_amount if cash_entry.credit_ledger.credit_amount else '',
                            'debit_amount': cash_entry.debit_amount,
                            'credits': cash_entry.credit_amount,
                            'date': cash_entry.transaction_date.strftime('%d/%m/%Y'),
                        })
                        count = count + 1
                    res = {
                        'result': 'ok',
                        'cash_entries': cash_entries_list,
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                except:
                    res = {
                        'result': 'error',
                        'message': 'Cash Account Ledger not found',
                    }
            if request.GET.get('report_type',''):
                start_date = datetime.strptime(request.GET.get('start_date', ''), '%d/%m/%Y')
                end_date = datetime.strptime(request.GET.get('end_date', ''), '%d/%m/%Y')
                response = HttpResponse(content_type='application/pdf')
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                p.setFontSize(20)
                p.drawCentredString(500, y, 'Cash Book')
                p.setFontSize(13)
                p.drawString(100, y - 50, "From")
                p.drawString(150, y - 50, ":")
                p.drawString(180, y - 50, str(start_date.strftime('%d/%m/%Y')))
                p.drawString(100, y - 80, "To")
                p.drawString(150, y - 80, ":")
                p.drawString(180, y - 80, str(end_date.strftime('%d/%m/%Y')))
                y = y - 80
                p.drawString(100, y - 50, "No")
                p.drawString(180, y - 50, "Date")
                p.drawString(300, y - 50, "Ref No")
                p.drawString(400, y - 50, "Ledger Entry")
                p.drawString(600, y - 50, "Debit Amount")
                p.drawString(800, y - 50, "Credit Amount")
                count = 1
                try:
                    ledger = Ledger.objects.get(name='Cash')
                    cash_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                    y = y - 50
                    for cash_entry in cash_entries:
                        p.drawString(100, y - 30, str(count))
                        p.drawString(180, y - 30, str(cash_entry.transaction_date.strftime('%d/%m/%Y')))
                        p.drawString(300, y - 30, str(cash_entry.transaction_ref))
                        if cash_entry.debit_ledger.ledger.name != 'Cash':
                            #table is used for wrapping text within column
                            data=[[Paragraph(cash_entry.debit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 200, 400)
                            table.drawOn(p, 400, y-30)
                            p.drawString(800, y - 30, str(cash_entry.credit_amount))
                            count = count + 1
                            y = y - 30
                        else:
                            #table is used for wrapping text within column
                            data=[[Paragraph(cash_entry.credit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 200, 400)
                            table.drawOn(p, 400, y-30)
                            p.drawString(600, y - 30, str(cash_entry.debit_amount))
                            count = count + 1
                            y = y - 30
                        if y <= 100:
                            y = 1200
                            p.showPage()
                    p.save()
                    return response
                except Exception as ex:
                    print str(ex)
                    res = {
                        'result': 'error',
                        'message': 'Cash Account Ledger not found',
                    }
            else:            
                return render(request, 'cash_book.html',{})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class BankBook(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'accounts_permission'):
            if request.is_ajax():
                bank_entries_list = []
                count = 1
                start_date = datetime.strptime(request.GET.get('start_date', ''), '%d/%m/%Y')
                end_date = datetime.strptime(request.GET.get('end_date', ''), '%d/%m/%Y')
                try:
                    ledgers = Ledger.objects.get(name='Bank').ledger_set.all()
                    for ledger in ledgers:
                        bank_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                        for bank_entry in bank_entries:
                            bank_entries_list.append({
                                'count': count,
                                'id': bank_entry.id,
                                'transaction_ref': bank_entry.transaction_ref,
                                'debit_ledger': bank_entry.debit_ledger.ledger.name,
                                'debit_ledger_debit': bank_entry.debit_ledger.debit_amount if bank_entry.debit_ledger.debit_amount else '',
                                'debit_ledger_credit': bank_entry.debit_ledger.credit_amount if bank_entry.debit_ledger.credit_amount else '',
                                'credit_ledger': bank_entry.credit_ledger.ledger.name,
                                'credit_ledger_debit': bank_entry.credit_ledger.debit_amount if bank_entry.credit_ledger.debit_amount else '',
                                'credit_ledger_credit': bank_entry.credit_ledger.credit_amount if bank_entry.credit_ledger.credit_amount else '',
                                'debit_amount': bank_entry.debit_amount,
                                'credit_amount': bank_entry.credit_amount,
                                'date': bank_entry.transaction_date.strftime('%d/%m/%Y'),
                            })
                            count = count + 1
                    res = {
                        'result': 'ok',
                        'bank_entries': bank_entries_list,
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                except Exception as e:
                    print e
                    res = {
                        'result': 'error',
                        'message': 'Bank Account Ledger not found',
                    }
            if request.GET.get('report_type',''):
                start_date = datetime.strptime(request.GET.get('start_date', ''), '%d/%m/%Y')
                end_date = datetime.strptime(request.GET.get('end_date', ''), '%d/%m/%Y')
                response = HttpResponse(content_type='application/pdf')
                p = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                p.setFontSize(20)
                p.drawCentredString(500, y, 'Bank Book')
                p.setFontSize(13)
                p.drawString(100, y - 50, "From")
                p.drawString(150, y - 50, ":")
                p.drawString(180, y - 50, str(start_date.strftime('%d/%m/%Y')))
                p.drawString(100, y - 80, "To")
                p.drawString(150, y - 80, ":")
                p.drawString(180, y - 80, str(end_date.strftime('%d/%m/%Y')))
                y = y - 80
                p.drawString(100, y - 50, "No")
                p.drawString(180, y - 50, "Date")
                p.drawString(300, y - 50, "Ref No")
                p.drawString(400, y - 50, "Debit Ledger")
                p.drawString(550, y - 50, "Credit Ledger")
                p.drawString(750, y - 50, "Debit Amount")
                p.drawString(900, y - 50, "Credit Amount")
                count = 1
                try:
                    ledgers = Ledger.objects.get(name='Bank').ledger_set.all()
                    for ledger in ledgers:
                        bank_entries = Transaction.objects.filter(Q(debit_ledger__ledger=ledger)| Q(credit_ledger__ledger=ledger), Q(transaction_date__gte=start_date), Q(transaction_date__lte=end_date)).order_by('transaction_date')
                        y = y - 50
                        for bank_entry in bank_entries:
                            p.drawString(100, y - 30, str(count))
                            p.drawString(180, y - 30, str(bank_entry.transaction_date.strftime('%d/%m/%Y')))
                            p.drawString(300, y - 30, str(bank_entry.transaction_ref))
                            #table is used for wrapping text withoin column                            
                            data=[[Paragraph(bank_entry.debit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 200, 400)
                            table.drawOn(p, 400, y-30)
                            p.drawString(750, y - 30, str(bank_entry.debit_amount))                            
                            #table is used for wrapping text withoin column                            
                            data=[[Paragraph(bank_entry.credit_ledger.ledger.name, para_style)]]
                            table = Table(data, colWidths=[200], rowHeights=200, style=style)      
                            table.wrapOn(p, 400, 400)
                            table.drawOn(p, 550, y-30)
                            p.drawString(900, y - 30, str(bank_entry.credit_amount))
                        count = count + 1
                        y = y - 30
                        if y <= 100:
                            y = 1200
                            p.showPage()
                    p.save()
                    return response
                except:
                    res = {
                        'result': 'error',
                        'message': 'Bank Account Ledger not found',
                    }
                    return response
            else:            
                return render(request, 'bank_book.html',{})   
        else:
            return HttpResponseRedirect(reverse('dashboard'))     

class BankAccountDetails(View):

    def get(self, request, *args, **kwargs):

        bank_accounts = Ledger.objects.filter(parent__name='Bank')
        ctx_bank_accounts = []
        for bank_account in bank_accounts:
            ctx_bank_accounts.append({
                'id': bank_account.id,
                'name': bank_account.name,
            })
        res = {
            'result': 'ok',
            'bank_accounts': ctx_bank_accounts,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

    def post(self, request, *args, **kwargs):

        bank_account = Ledger.objects.get(name='Bank')
        try:
            new_bank_account = Ledger.objects.get(parent=bank_account, name=request.POST['bank_account'])
            res = {
                'result': 'error',
                'message': 'Bank Account with this name already exists',
            }
        except:
            new_bank_account = Ledger.objects.create(parent=bank_account, name=request.POST['bank_account'])
            res = {
                'result': 'ok',
                'bank_account': {
                    'id': new_bank_account.id
                },
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class TrialBalance(View):

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()
        shop = Shope.objects.all()[0]
        response = HttpResponse(content_type='application/pdf')
        p = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        data = []
        d = [[shop.name], ['Trial Balance as at '+date.strftime('%d %B %Y')]]
        t = Table(d, colWidths=(450), rowHeights=25, style=style)
        t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    ('FONTSIZE', (0,0), (0,0), 20),
                    ('FONTSIZE', (1,0), (-1,-1), 17),
                    ])   
        elements.append(t)
        
        elements.append(Spacer(2, 5))
        
        data.append(['Account Title', 'Debit', 'Credit'])
        ledgers = Ledger.objects.all()
        total_debit = 0
        total_credit = 0
        for ledger in ledgers:
            balance = ledger.balance
            if balance > 0:
                data.append([ledger.name, balance, ''])
                total_debit = total_debit + balance
            elif balance < 0:
                data.append([ledger.name, '', abs(balance)])
                total_credit = total_credit + abs(balance)
        data.append(['Total', total_debit, total_credit])
        table = Table(data, colWidths=(250,100,100), rowHeights=25, style=style)
        table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.white),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.white),
                    ('FONTNAME', (0, -1), (-1,-1), 'Helvetica-Bold')
                    ])   
        elements.append(table)
        p.build(elements)        
        return response
        


class ProfitAndLossStatement(View):

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()
        shop = Shope.objects.all()[0]
        response = HttpResponse(content_type='application/pdf')
        p = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        data = []
        d = [[shop.name], ['Profit And Loss Statement '], ['For the Period Ended ' + date.strftime('%d %B %Y')]]
        t = Table(d, colWidths=(450), rowHeights=25, style=style)
        t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    ('FONTSIZE', (0,0), (0,0), 20),
                    ('FONTSIZE', (1,0), (-1,-1), 17),
                    ])   
        elements.append(t)
        elements.append(Spacer(2, 5))
        sales = Ledger.objects.get(name = 'Sales')
        net_sales = sales.balance
        data.append(['NET SALES', '', abs(net_sales)])
        data.append(['Cost Of Goods Sold:', '', ''])
        try:
            opening_stock = OpeningStockValue.objects.latest('id')
            opening_stock_by_value = opening_stock.stock_by_value
        except:
            opening_stock_by_value = decimal.Decimal('0.00')
        data.append(['Begining Inventory', '-'+str(opening_stock_by_value), ''])
        purchases = Ledger.objects.get(name='Purchase').balance
        data.append(['Merchandise Purchases', '-'+str(purchases), ''])
        try:
            freight = FreightValue.objects.latest('id')
            freight = freight.freight_value
            if freight is None:
                freight = decimal.Decimal('0.00')
        except:
            freight = decimal.Decimal('0.00')
        data.append(['Freight', '-'+str(freight), ''])
        goods_available = opening_stock_by_value + purchases + freight
        data.append(['Cost Of Goods Available for Sale', '', goods_available])
        try:
            stock_value = StockValue.objects.latest('id')
            stock_value = stock_value.stock_by_value
        except:
            stock_value = decimal.Decimal('0.00')
        data.append(['Less ending Inventory', '-' + str(stock_value), ''])
        cost_of_good_sold = goods_available - stock_value
        data.append(['COST OF GOODS SOLD', '', '-' + str(cost_of_good_sold)])
        gross_margin = net_sales - cost_of_good_sold
        data.append(['GROSS MARGIN', '', gross_margin])
        data.append(['Selling, Administrative and general expenses:', '', ''])
        data.append(['Income From Operations:', '', ''])
        data.append(['NET PROFIT', '', ''])
        
        table = Table(data, colWidths=(250,100,100), rowHeights=25, style=style)
        table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.white),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.white),
                    ('FONTNAME', (0, -1), (0,-1), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 0), (0,0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (0,1), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 5), (0,5), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 7), (0,7), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 8), (0,8), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 9), (0,9), 'Helvetica-Bold'),
                    ])   
        elements.append(table)
        p.build(elements)        
        return response
        
class BalanceSheet(View):

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()
        shop = Shope.objects.all()[0]
        response = HttpResponse(content_type='application/pdf')
        p = SimpleDocTemplate(response, pagesize=A4)
        elements = []        
        d = [[shop.name], ['Balance Sheet as at '+date.strftime('%d %B %Y')]]
        t = Table(d, colWidths=(450), rowHeights=25, style=style)
        t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    ('FONTSIZE', (0,0), (0,0), 20),
                    ('FONTSIZE', (1,0), (-1,-1), 17),
                    ])   
        elements.append(t)
        
        elements.append(Spacer(2, 5))
        data = []
        data.append(['Assets','','Liabilities'])
        asset_ledgers = Ledger.objects.filter(parent__name='Assets')
        a_total = 0
        l_total = 0
        liablity_ledgers = Ledger.objects.filter(parent__name='Liabilities')

        for (ast_ledger, lib_ledger) in itertools.izip_longest(asset_ledgers, liablity_ledgers) :
            data.append([ast_ledger.name,  '', lib_ledger.name, ''])
            ast_ledgers = Ledger.objects.filter(parent=ast_ledger)
            lib_ledgers = Ledger.objects.filter(parent=lib_ledger)

            for (a_ledger, l_ledger) in itertools.izip_longest(ast_ledgers, lib_ledgers):
                
                data_list = []
                if a_ledger is None:
                    data_list = ['', '']                    
                else:
                    
                    if a_ledger.name == 'Stock':
                        stock_value = StockValue.objects.latest('id')
                        data_list = [Paragraph(a_ledger.name,para_style),  abs(stock_value.stock_by_value)]
                        a_total = a_total + abs(stock_value.stock_by_value)
                    else:
                        data_list = [Paragraph(a_ledger.name, para_style), abs(a_ledger.balance)]                    
                        a_total = a_total + abs(a_ledger.balance)
                if l_ledger is None:                   
                    data_list.append('')
                    data_list.append('')
                else:    
                    l_total = l_total + abs(l_ledger.balance) 
                    data_list.append(Paragraph(l_ledger.name,para_style))
                    data_list.append(abs(l_ledger.balance))
                data.append(data_list)                
        data.append(['Total', a_total, 'Total',l_total])
        table = Table(data, colWidths=(130),  style=style)
        table.setStyle([('ALIGN',(0,-1),(0,-1),'LEFT'),
                    ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('BACKGROUND',(0, 0),(-1,-1),colors.white),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ('FONTNAME', (0, -1), (-1,-1), 'Helvetica-Bold'),
                    ('SPAN',(0,0),(1,0)),
                    ('SPAN',(2,0),(3,0)),
                    # ('SPAN',(0,1),(1,1)),
                    # ('SPAN',(2,1),(3,1)),
                    # ('SPAN',(0,6),(1,6)),
                    # ('SPAN',(2,6),(3,6)),
                    ])   
        elements.append(table)

        
        p.build(elements)        
        return response