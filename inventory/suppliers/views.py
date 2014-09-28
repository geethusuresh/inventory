import simplejson
import ast
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect

from suppliers.models import Supplier
from accounting.models import Ledger

from web.views import get_user_permission

style = [
    ('FONTSIZE', (0,0), (-1, -1), 14),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]

para_style = ParagraphStyle('fancy')
para_style.fontSize = 14
para_style.fontName = 'Helvetica'

class Suppliers(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'suppliers'):
            suppliers = Supplier.objects.all()
            ctx_supplier= []
            if request.is_ajax():
                for supplier in suppliers:
                    ctx_supplier.append({
                        'id': supplier.id,
                        'name': supplier.name,
                        'address': supplier.address,
                        'mobile': supplier.mobile,
                        'telephone_number': supplier.telephone_number,
                        'email': supplier.email,
                    })
                res = {
                    'result': 'ok',
                    'suppliers': ctx_supplier,
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'suppliers.html', {})    
        else:
            return HttpResponseRedirect(reverse('dashboard'))   


class AddSupplier(View):

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            supplier_details = ast.literal_eval(request.POST['supplier'])
            try:
                parent = Ledger.objects.get(name='Sundry Creditors')
                if supplier_details.get('id', ''):
                    supplier = Supplier.objects.get(id=supplier_details.get('id', ''))
                else:
                    supplier = Supplier()
                try:
                    supplier.name = supplier_details['name']
                    supplier.address = supplier_details['address']
                    supplier.mobile = supplier_details['mobile']
                    supplier.telephone_number = supplier_details['telephone_number']
                    supplier.email = supplier_details['email']
                    supplier.save()
                    if supplier.ledger:
                        supplier.ledger.name = supplier_details['name']
                        supplier.ledger.save()
                    else:
                        ledger = Ledger()
                        ledger.parent = parent
                        ledger.name = supplier_details['name']
                        ledger.save()
                        supplier.ledger = ledger
                    supplier.save()
                    res = {
                        'result': 'ok',
                        'message': 'ok',
                        'supplier' : {
                            'id': supplier.id,
                            'name': supplier.name,
                            'address': supplier.address,
                            'mobile': supplier.mobile,
                            'telephone_number': supplier.telephone_number,
                            'email': supplier.email,
                        }
                    }
                except Exception as ex:
                    print str(ex)
                    res = {
                        'result': 'error',
                        'message': 'Supplier name already exists',
                    }
            except:
                res = {
                        'result': 'error',
                        'message': 'Ledger Sundry Creditors not found'
                    }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class SearchSupplier(View):

    def get(self, request, *args, **kwargs):

        supplier_name = request.GET.get('name', '')
        ctx_suppliers = []
        suppliers = Supplier.objects.filter(name__istartswith=supplier_name)
        for supplier in suppliers:
            ctx_suppliers.append({
                'id': supplier.id,
                'name': supplier.name,
                'address': supplier.address,
                'mobile': supplier.mobile,
                'telephone_number': supplier.telephone_number,
                'email': supplier.email,
            })
        res = {
            'result': 'ok',
            'suppliers': ctx_suppliers,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

        
class DeleteSupplier(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'suppliers'):
            supplier_id = request.GET.get('supplier_id', '')
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.ledger.delete()
            supplier.delete()
            return HttpResponseRedirect(reverse('supplier_list'))
        else:
            return HttpResponseRedirect(reverse('dashboard'))   

class AccountPayable(View):

    def get(self, request, *args, **kwargs):

        if get_user_permission(request, 'suppliers'):
            suppliers = Supplier.objects.all()
            ctx_suppliers = []
            if request.is_ajax():
                for supplier in suppliers:
                    debit_balance = ''
                    credit_balance = ''
                    if supplier.ledger.balance >= 0:
                        debit_balance = supplier.ledger.balance
                    else:
                        credit_balance = supplier.ledger.balance
                    ctx_suppliers.append({
                        'name': supplier.name,
                        'debit_balance': abs(debit_balance) if debit_balance != '' else '',
                        'credit_balance': abs(credit_balance) if credit_balance != '' else '',
                    })
                res = {
                    'supplier_details': ctx_suppliers,
                    'result': 'ok',
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            else:
                if request.GET.get('pdf', ''):
                    response = HttpResponse(content_type='application/pdf')
                    canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
                    y = 1150
                    status_code = 200
                    canvas_paper.setFontSize(20)
                    canvas_paper.drawCentredString(500, y, 'Account Payable')
                    y1 = y - 100
                    canvas_paper.setFontSize(16)
                    canvas_paper.drawString(50, y1, 'Sl No')
                    canvas_paper.drawString(150, y1, 'Supplier Name')
                    canvas_paper.drawString(400, y1, 'Dr')
                    canvas_paper.drawString(600, y1, 'Cr')
                    y1 = y1 - 30
                    i = 1
                    for supplier in suppliers:
                        debit_balance = 0
                        credit_balance = 0
                        if supplier.ledger.balance >= 0:
                            debit_balance = abs(supplier.ledger.balance)
                        else:
                            credit_balance = abs(supplier.ledger.balance)
                        canvas_paper.setFontSize(14)
                        canvas_paper.drawString(50, y1, str(i))
                        data=[[Paragraph(supplier.name, para_style)]]
                        # canvas_paper.drawString(150, y1, 'Supplier Name')
                        table = Table(data, colWidths=[200], rowHeights=100, style=style)      
                        table.wrapOn(canvas_paper, 200, 400)
                        table.drawOn(canvas_paper, 150, y1-10)
                        canvas_paper.drawString(400, y1, str(debit_balance))
                        canvas_paper.drawString(600, y1, str(credit_balance))
                        i = i + 1
                        y1 = y1 - 30
                        if y1 < 270:
                            y1 = y - 50
                            canvas_paper.showPage()
                    canvas_paper.showPage()
                    canvas_paper.save()

                    return response
                else:
                    return render(request, 'account_payable.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))