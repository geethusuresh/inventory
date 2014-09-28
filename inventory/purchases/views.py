import simplejson
import ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from suppliers.models import Supplier
from purchases.models import PurchaseItem, Purchase, PurchaseReturn, PurchaseReturnItem, FreightValue
from inventory.models import Item, BatchItem, Batch, UOMConversion, StockValue
from accounting.models import Ledger, LedgerEntry, Transaction

from web.views import get_user_permission

style = [
    ('FONTSIZE', (0,0), (-1, -1), 14),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]

para_style = ParagraphStyle('fancy')
para_style.fontSize = 12
para_style.fontName = 'Helvetica'


class PurchaseEntry(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'purchase_permission'):
            return render(request, 'purchase.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))
        
    def post(self, request, *args, **kwargs):
        purchase_details = ast.literal_eval(request.POST['purchase_details'])
        try:
            purchase = Purchase.objects.create(purchase_invoice_number=purchase_details['invoice_no'])
            purchase.do_number = purchase_details['do_no']
            supplier = Supplier.objects.get(id=purchase_details['supplier'])
            purchase.supplier = supplier
            purchase.purchase_invoice_date = datetime.strptime(purchase_details['invoice_date'], '%d/%m/%Y')
            purchase.payment_mode = purchase_details['payment_mode']
            purchase.discount = purchase_details['discount']
            purchase.grant_total = purchase_details['grant_total']
            purchase.purchase_tax = float(purchase_details['purchase_tax'])
            if purchase.payment_mode == 'cheque':
                purchase.bank_name = purchase_details['bank_name']
                purchase.branch = purchase_details['branch']
                purchase.cheque_date = datetime.strptime(purchase_details['cheque_date'], '%d/%m/%Y')
                purchase.cheque_number = purchase_details['cheque_no']
            elif purchase.payment_mode == 'card':
                purchase.bank_name = purchase_details['bank_name']
                purchase.card_number = purchase_details['card_no']  
                purchase.card_holder_name = purchase_details['card_holder_name'] 
            transaction_ref = 'PRINV' + str(purchase.id)
            purchase.transaction_reference_no = transaction_ref
            purchase.save()
            
            # Transaction 1 - Credit entry for Supplier and Debit entry for purchase
            transaction_1 = Transaction()
            ledger_entry_credit_supplier = LedgerEntry()
            ledger_entry_credit_supplier.ledger = supplier.ledger
            ledger_entry_credit_supplier.credit_amount = purchase.grant_total + purchase.purchase_tax
            ledger_entry_credit_supplier.date = purchase.purchase_invoice_date
            ledger_entry_credit_supplier.transaction_reference_number = transaction_ref
            ledger_entry_credit_supplier.save()
            ledger_entry_debit_purchase = LedgerEntry()
            purchase_ledger = Ledger.objects.get(name='Purchase')
            ledger_entry_debit_purchase.ledger = purchase_ledger
            ledger_entry_debit_purchase.debit_amount = purchase.grant_total
            ledger_entry_debit_purchase.date = purchase.purchase_invoice_date
            ledger_entry_debit_purchase.transaction_reference_number = transaction_ref
            ledger_entry_debit_purchase.save()
            transaction_1.credit_ledger = ledger_entry_credit_supplier
            transaction_1.debit_ledger = ledger_entry_debit_purchase
            transaction_1.transaction_ref = transaction_ref
            transaction_1.debit_amount = purchase.grant_total
            transaction_1.credit_amount = purchase.grant_total + purchase.purchase_tax
            total_amount = purchase.grant_total + purchase.purchase_tax
            supplier.ledger.balance = float(supplier.ledger.balance) - total_amount
            supplier.ledger.save()
            purchase_ledger.balance = float(purchase_ledger.balance) + float(purchase.grant_total)
            purchase_ledger.save()
            # transaction_1.save()
            
            # Transaction 2 - Credit entry for Cash or Bank account and Debit entry for Supplier 
            if purchase.payment_mode != 'credit':
                credit_ledger = None
                if purchase.payment_mode == 'cash':
                    credit_ledger = Ledger.objects.get(name="Cash")
                elif purchase.payment_mode == 'card' or purchase.payment_mode == 'cheque':
                    credit_ledger = Ledger.objects.get(id=purchase_details['bank_account_ledger'])
                ledger_entry_credit_accounts = LedgerEntry()
                ledger_entry_credit_accounts.ledger = credit_ledger
                ledger_entry_credit_accounts.credit_amount = purchase.grant_total + purchase.purchase_tax 
                ledger_entry_credit_accounts.date = purchase.purchase_invoice_date
                ledger_entry_credit_accounts.transaction_reference_number = transaction_ref
                ledger_entry_credit_accounts.save()

                ledger_entry_debit_supplier = LedgerEntry()
                ledger_entry_debit_supplier.ledger = supplier.ledger
                ledger_entry_debit_supplier.debit_amount = purchase.grant_total + purchase.purchase_tax 
                ledger_entry_debit_supplier.date = purchase.purchase_invoice_date
                ledger_entry_debit_supplier.transaction_reference_number = transaction_ref
                ledger_entry_debit_supplier.save()
                if credit_ledger:
                    credit_ledger.balance = float(credit_ledger.balance) - float(total_amount)
                    credit_ledger.save()
                if supplier.ledger:
                    supplier.ledger.balance = float(supplier.ledger.balance) + float(total_amount)
                    supplier.ledger.save()

                transaction_2 = Transaction()
                transaction_2.credit_ledger = ledger_entry_credit_accounts
                transaction_2.debit_ledger = ledger_entry_debit_supplier
                transaction_2.transaction_ref = transaction_ref
                transaction_2.debit_amount = purchase.grant_total + purchase.purchase_tax 
                transaction_2.credit_amount = purchase.grant_total + purchase.purchase_tax 

            # Transaction 3 - Debit entry for Stock
            debit_stock_ledger = Ledger.objects.get(name="Stock")
            ledger_entry_debit_stock = LedgerEntry()
            ledger_entry_debit_stock.ledger = debit_stock_ledger
            ledger_entry_debit_stock.debit_amount = purchase.grant_total
            ledger_entry_debit_stock.date = purchase.purchase_invoice_date
            ledger_entry_debit_stock.transaction_reference_number = transaction_ref
            debit_stock_ledger.balance = float(debit_stock_ledger.balance) + float(purchase.grant_total)
            debit_stock_ledger.save()
            ledger_entry_debit_stock.save()
            transaction_3 = Transaction()
            transaction_3.debit_ledger = ledger_entry_debit_stock
            transaction_3.transaction_ref = transaction_ref
            transaction_3.debit_amount = purchase.grant_total

            # Transaction 4 - Debit Entry for Tax account
            
            debit_tax_ledger = Ledger.objects.get(name="Input Vat (Purchases)")
            ledger_entry_debit_tax_account = LedgerEntry()
            ledger_entry_debit_tax_account.date = purchase.purchase_invoice_date
            ledger_entry_debit_tax_account.transaction_reference_number = transaction_ref
            ledger_entry_debit_tax_account.ledger = debit_tax_ledger
            ledger_entry_debit_tax_account.debit_amount = purchase.purchase_tax
            debit_tax_ledger.balance = float(debit_tax_ledger.balance) + float(purchase.purchase_tax)
            debit_tax_ledger.save()
            ledger_entry_debit_tax_account.save()
            transaction_4 = Transaction()
            transaction_4.debit_ledger = ledger_entry_debit_tax_account
            transaction_4.transaction_ref = transaction_ref
            transaction_4.debit_amount = purchase.purchase_tax 


            transaction_1.transaction_date = purchase.purchase_invoice_date
            transaction_1.narration = 'By Purchase - '+ str(purchase.purchase_invoice_number)
            transaction_1.payment_mode = purchase.payment_mode
            if purchase.payment_mode != 'credit':
                transaction_2.transaction_date = purchase.purchase_invoice_date
                transaction_2.narration = 'By Purchase - '+ str(purchase.purchase_invoice_number)
                transaction_2.payment_mode = purchase.payment_mode
                transaction_4.transaction_date = purchase.purchase_invoice_date
                transaction_4.narration = 'By Purchase - '+ str(purchase.purchase_invoice_number)
                transaction_4.payment_mode = purchase.payment_mode

            transaction_3.transaction_date = purchase.purchase_invoice_date
            transaction_3.narration = 'By Purchase - '+ str(purchase.purchase_invoice_number)
            transaction_3.payment_mode = purchase.payment_mode

            if purchase.payment_mode != 'credit':
                if purchase.payment_mode == 'cheque':
                    transaction_1.bank_name = purchase.bank_name
                    transaction_2.bank_name = purchase.bank_name
                    transaction_3.bank_name = purchase.bank_name
                    transaction_4.bank_name = purchase.bank_name
                    transaction_1.cheque_number = purchase.cheque_number
                    transaction_1.cheque_date = purchase.cheque_date
                    transaction_1.branch = purchase.branch
                    transaction_2.cheque_number = purchase.cheque_number
                    transaction_2.cheque_date = purchase.cheque_date
                    transaction_2.branch = purchase.branch
                    transaction_3.cheque_number = purchase.cheque_number
                    transaction_3.cheque_date = purchase.cheque_date
                    transaction_3.branch = purchase.branch
                    transaction_4.branch = purchase.branch
                elif purchase.payment_mode == 'card':
                    transaction_1.bank_name = purchase.bank_name
                    transaction_2.bank_name = purchase.bank_name
                    transaction_3.bank_name = purchase.bank_name
                    transaction_4.bank_name = purchase.bank_name
                    transaction_1.card_holder_name = purchase.card_holder_name
                    transaction_1.card_no = purchase.card_number
                    transaction_2.card_holder_name = purchase.card_holder_name
                    transaction_2.card_no = purchase.card_number
                    transaction_3.card_holder_name = purchase.card_holder_name
                    transaction_3.card_no = purchase.card_number
                    transaction_4.card_no = purchase.card_number
                    transaction_4.card_holder_name = purchase.card_holder_name
                transaction_2.save()
                transaction_4.save()
            transaction_1.save()
            transaction_3.save()
            purchase_item_details = purchase_details['items']
            total_cost_price = 0
            total_quantity = 0
            total_freight = 0
            for purchase_item_data in purchase_item_details:
                total_quantity = float(total_quantity) + float(purchase_item_data['quantity'])
            unit_item_discount = float(purchase.discount)/float(total_quantity)
            for purchase_item_data in purchase_item_details:
                batch = Batch.objects.get(id=purchase_item_data['batch'])
                item = Item.objects.get(id=purchase_item_data['id'])
                batch_item, batch_item_created = BatchItem.objects.get_or_create(batch=batch, item=item)

                conversion_type = UOMConversion.objects.get(id=purchase_item_data['conversion_unit'])
                purchase_item, created = PurchaseItem.objects.get_or_create(purchase=purchase, batch_item=batch_item)
                purchase_item.quantity = purchase_item_data['quantity']
                purchase_item.uom = purchase_item_data['uom']
                purchase_item.purchase_price = purchase_item_data['purchase_price']

                if float(purchase_item_data['cost_price']) == 0:
                    purchase_item.unit_freight = 0
                    purchase_item.cost_price = float(purchase_item_data['purchase_price']) - float(unit_item_discount)
                else:
                    purchase_item.unit_freight = float(purchase_item_data['cost_price']) - float(purchase_item_data['purchase_price'])
                    purchase_item.cost_price = float(purchase_item_data['cost_price']) - float(unit_item_discount)
                purchase_item.net_amount = purchase_item_data['net_amount']
                purchase_item.uom_conversion = conversion_type
                purchase_item.uom = purchase_item_data['purchase_unit']
                purchase_item.whole_sale_price = purchase_item_data['whole_sale_price']
                purchase_item.retail_price = purchase_item_data['retail_price']
                purchase_item.unit_discount = unit_item_discount
                purchase_item.save()
                total_cost_price = float(total_cost_price) + (float(purchase_item.cost_price) * float(purchase_item.quantity))
                total_freight = float(total_freight) + (float(purchase_item.unit_freight) * float(purchase_item.quantity))
                quantity = 0
                selling_price = 0
                purchase_price = 0
                if conversion_type.selling_unit == purchase_item_data['purchase_unit']:
                    quantity = purchase_item_data['quantity']
                    whole_sale_price = purchase_item_data['whole_sale_price']
                    retail_price = purchase_item_data['retail_price']
                    purchase_price = purchase_item_data['purchase_price']
                else:
                    quantity = float(purchase_item_data['quantity']) * float(conversion_type.relation)
                    whole_sale_price = float(purchase_item_data['whole_sale_price']) / float(conversion_type.relation)
                    retail_price = float(purchase_item_data['retail_price']) / float(conversion_type.relation)
                    purchase_price = float(purchase_item_data['purchase_price']) / float(conversion_type.relation)
                if batch_item_created:
                    batch_item.quantity = quantity
                    batch_item.uom_conversion = conversion_type
                    batch_item.freight_charge = purchase_item.unit_freight
                    batch_item.cost_price = purchase_item.cost_price
                    batch_item.whole_sale_price = whole_sale_price
                    batch_item.retail_price = retail_price
                    batch_item.purchase_price = purchase_price
                    batch_item.uom = conversion_type.selling_unit
                else:
                    batch_item.quantity = float(batch_item.quantity) + float(quantity)
                batch_item.save()
            try:
                freight = FreightValue.objects.latest('id')
            except:
                freight = FreightValue()
            if freight.freight_value is not None:
                freight.freight_value = float(freight.freight_value) + float(total_freight)
            else:
                freight.freight_value = float(total_freight)
            freight.save()
            try:
                stock_value = StockValue.objects.latest('id')
            except Exception as ex:
                stock_value = StockValue()
            print total_cost_price,"Total Cost Price ==" 
            if stock_value.stock_by_value is not None:
                stock_value.stock_by_value = float(total_cost_price) + float(stock_value.stock_by_value)
            else:
                stock_value.stock_by_value = float(total_cost_price)

            stock_value.save()
            res = {
                'result': 'ok',
                'transaction_reference_no': transaction_1.transaction_ref,
            }
        except Exception as ex:
            print str(ex), 'Exception'

            res = {
                'result': 'error',
                'error_message': str(ex),
                'message': 'Purchase Invoice number already exists',
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype="application/json")


class PurchaseReport(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'purchase_permission'):
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            if not start_date and not end_date:
                return render(request, 'purchase_report.html', {})
            else:
                startdate = datetime.strptime(start_date, '%d/%m/%Y')
                enddate = datetime.strptime(end_date, '%d/%m/%Y')
                purchases = Purchase.objects.filter(purchase_invoice_date__gte=startdate,purchase_invoice_date__lte=enddate ).order_by('purchase_invoice_date')
                ctx_purchases = []
                if request.is_ajax():
                    for purchase in purchases:
                        ctx_purchases.append({
                            'date': purchase.purchase_invoice_date.strftime('%d/%m/%Y'),
                            'invoice': purchase.purchase_invoice_number,
                            'payment_mode': purchase.payment_mode,
                            'grant_total': purchase.grant_total,
                            'discount': purchase.discount,
                            'tax': purchase.purchase_tax,
                            'supplier': purchase.supplier.name,
                            'transaction_ref': purchase.transaction_reference_no,
                        })
                    res = {
                        'purchase_details': ctx_purchases,
                        'result': 'ok',
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                else:
                    response = HttpResponse(content_type='application/pdf')
                    canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
                    y = 1150
                    canvas_paper.setFontSize(20)
                    canvas_paper.drawCentredString(500, y, 'Purchase Report - ' + start_date + ' - ' +end_date )
                    y1 = y - 100
                    canvas_paper.setFontSize(16)
                    canvas_paper.drawString(50, y1, 'Date')
                    canvas_paper.drawString(150, y1, 'Invoice no.')
                    canvas_paper.drawString(240, y1, 'Payment Mode')
                    canvas_paper.drawString(360, y1, 'Grant Total')
                    canvas_paper.drawString(460, y1, 'Discount')
                    canvas_paper.drawString(550, y1, 'Tax')
                    canvas_paper.drawString(650, y1, 'Supplier')
                    canvas_paper.drawString(810, y1, 'Transaction Ref.no')
                    y1 = y1 - 30
                    total = 0
                    total_tax = 0
                    total_discount = 0
                    for purchase in purchases:
                        canvas_paper.setFontSize(12)
                        canvas_paper.drawString(50, y1,purchase.purchase_invoice_date.strftime('%d/%m/%Y'))
                        canvas_paper.drawString(150, y1,purchase.purchase_invoice_number )
                        canvas_paper.drawString(240, y1, purchase.payment_mode)
                        canvas_paper.drawString(360, y1, str(purchase.grant_total))
                        canvas_paper.drawString(460, y1, str(purchase.discount))
                        canvas_paper.drawString(550, y1, str(purchase.purchase_tax))
                        canvas_paper.drawString(840, y1, str(purchase.transaction_reference_no))
                        data=[[Paragraph(purchase.supplier.name, para_style)]]
                        table = Table(data, colWidths=[200], rowHeights=100, style=style)      
                        table.wrapOn(canvas_paper, 200, 400)
                        table.drawOn(canvas_paper, 650, y1-10)
                        total_tax = float(total_tax) + float(purchase.purchase_tax)
                        total_discount = float(total_discount) + float(purchase.discount)
                        # canvas_paper.drawString(700, y1, str(purchase.supplier.name))
                        total = float(total) + float(purchase.grant_total)
                        y1 = y1 - 30
                        if y1 < 270:
                            y1 = y - 50
                            canvas_paper.showPage()

                    canvas_paper.drawString(50, y1, 'Total Amount: ')
                    canvas_paper.drawString(140, y1, str(total))
                    canvas_paper.drawString(515, y1, str(total_discount))
                    canvas_paper.drawString(780, y1, str(total_tax))
                    canvas_paper.drawString(350, y1, 'Total Purchase Discount : ')
                    canvas_paper.drawString(650, y1, 'Total Purchase Tax : ')
                    canvas_paper.showPage()
                    canvas_paper.save()

                    return response
                    # response = HttpResponse(content_type='application/pdf')
                    # p = SimpleDocTemplate(response, pagesize=A4)
                    # heading = 'Purchase Report - ' + start_date + ' - ' +end_date
                    # d = [[heading]]
                    # elements = []
                    # data = []
                    # t = Table(d, colWidths=(450), rowHeights=50, style=style)
                    # t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    #             ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    #             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    #             # ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    #             ('FONTSIZE', (0,0), (0,0), 20),
                    #             ('FONTSIZE', (1,0), (-1,-1), 17),
                    #             ])   
                    # elements.append(t)
                    
                    # elements.append(Spacer(2, 5))
                    
                    # data.append(['Account Title', 'Debit', 'Credit'])
                    # ledgers = Ledger.objects.all()
                    # total_debit = 0
                    # total_credit = 0
                    # for ledger in ledgers:
                    #     balance = ledger.balance
                    #     if balance > 0:
                    #         data.append([ledger.name, balance, ''])
                    #         total_debit = total_debit + balance
                    #     elif balance < 0:
                    #         data.append([ledger.name, '', abs(balance)])
                    #         total_credit = total_credit + abs(balance)
                    # data.append(['Total', total_debit, total_credit])
                    # table = Table(data, colWidths=(250,100,100), rowHeights=25, style=style)
                    # table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    #             ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#699AB7')),
                    #             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    #             ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.white),
                    #             ('BOX', (0,0), (-1,-1), 0.25, colors.white),
                    #             ('FONTSIZE', (0,-1), (-1,-1), 15),
                    #             ])   
                    # elements.append(table)
                    # p.build(elements)        
                    # return response
        
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class PurchaseReturnEntry(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'purchase_permission'):
            if request.is_ajax():
                purchase_invoice = request.GET.get('purchase_invoice_no', '')
                purchases = []
                ctx_purchases = []
                if purchase_invoice:
                    purchases = Purchase.objects.filter(purchase_invoice_number=purchase_invoice)
                for purchase in purchases:
                    ctx_purchases.append({
                        'id': purchase.id,
                        'purchase_invoice': purchase.purchase_invoice_number,
                        'supplier': purchase.supplier.name if purchase.supplier else '',
                        'discount': purchase.discount,
                    })
                res = {
                    'purchase_deatails': ctx_purchases,
                    'result': 'ok',
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
            return render(request, 'purchase_return.html', {})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

    def post(self, request, *args, **kwargs):

        purchase_return_details = ast.literal_eval(request.POST['purchase_return_details'])
        try:
            purchase = Purchase.objects.get(id=purchase_return_details['purchase_id'])
            purchase_return = PurchaseReturn.objects.create(return_invoice_number=purchase_return_details['return_invoice'])
            purchase_return.invoice_date = datetime.strptime(purchase_return_details['return_invoice_date'], '%d/%m/%Y')
            purchase_return.purchase = purchase
            
            purchase_return.grant_total = purchase_return_details['grant_total']
            purchase_return.save()

            purchase_return_items = purchase_return_details['items']
            total_cost_price = 0
            for pr_item in purchase_return_items:
                purchase_item = PurchaseItem.objects.get(id=pr_item['id'])
                return_item, created = PurchaseReturnItem.objects.get_or_create(purchase_return=purchase_return, purchase_item=purchase_item)
                if created:
                    return_item.quantity = pr_item['quantity']
                    return_item.net_amount = pr_item['net_amount']
                return_item.save()
                total_cost_price = float(total_cost_price) + float(float(return_item.quantity) * float(purchase_item.cost_price))
                batch_item = purchase_item.batch_item
                quantity = float(return_item.quantity) * float(purchase_item.uom_conversion.relation)
                batch_item.quantity = float(batch_item.quantity) - quantity
                batch_item.save()

            purchased_quantity = 0
            unit_item_discount = 0
            unit_item_purchase_tax = 0
            returned_quantity = 0
            return_discount = 0
            return_purchase_tax = 0
            for item in purchase.purchaseitem_set.all():
                purchased_quantity = float(purchased_quantity) + float(item.quantity)
                unit_discount = item.unit_discount
            if float(purchase.discount) > 0:
                unit_item_discount = float(purchase.discount) / float(purchased_quantity)
            print unit_discount, unit_item_discount
            if float(purchase.purchase_tax) > 0:
                unit_item_purchase_tax = float(purchase.purchase_tax) / float(purchased_quantity)

            for item in purchase_return.purchasereturnitem_set.all():
                returned_quantity = float(returned_quantity) + float(item.quantity)
            purchase_return.discount = returned_quantity * unit_item_discount
            purchase_return.purchase_tax = returned_quantity * unit_item_purchase_tax
            transaction_ref = 'PRRINV' + str(purchase_return.id)
            purchase_return.transaction_reference_no = transaction_ref
            purchase_return.save()
            # Transaction 1 - Debit entry for Supplier and credit entry for Purchase Return
            debit_supplier_entry = LedgerEntry()
            debit_supplier_entry.ledger = purchase.supplier.ledger
            debit_supplier_entry.debit_amount = purchase_return.purchase_tax + purchase_return.grant_total
            debit_supplier_entry.date = purchase_return.invoice_date
            debit_supplier_entry.transaction_reference_number = transaction_ref
            debit_supplier_entry.save()
            purchase.supplier.ledger.balance = float(purchase.supplier.ledger.balance) + purchase_return.purchase_tax + purchase_return.grant_total
            purchase.supplier.ledger.save()
            credit_purchase_return_entry = LedgerEntry()
            purchase_return_ledger = Ledger.objects.get(name='Purchase Return')
            credit_purchase_return_entry.ledger = purchase_return_ledger
            credit_purchase_return_entry.credit_amount = purchase_return.grant_total
            credit_purchase_return_entry.date = purchase_return.invoice_date
            credit_purchase_return_entry.transaction_reference_number = transaction_ref
            credit_purchase_return_entry.save()
            purchase_return_ledger.balance = purchase_return_ledger.balance - purchase_return.grant_total
            purchase_return_ledger.save()

            transaction_1 = Transaction()
            transaction_1.transaction_ref = transaction_ref
            transaction_1.debit_ledger = debit_supplier_entry
            transaction_1.credit_ledger = credit_purchase_return_entry
            transaction_1.transaction_date = purchase_return.invoice_date
            transaction_1.debit_amount = purchase_return.purchase_tax + purchase_return.grant_total
            transaction_1.credit_amount = purchase_return.grant_total
            transaction_1.narration = 'By Purchase Return- '+ str(purchase_return.return_invoice_number)
            transaction_1.save()

            # Transaction 2 - Credit Entry for Stock

            credit_stock_entry = LedgerEntry()
            stock_ledger = Ledger.objects.get(name='Stock')
            credit_stock_entry.ledger = stock_ledger
            credit_stock_entry.credit_amount = purchase_return.grant_total
            credit_stock_entry.date = purchase_return.invoice_date
            credit_stock_entry.transaction_reference_number = transaction_ref
            credit_stock_entry.save()
            stock_ledger.balance = float(stock_ledger.balance) - purchase_return.grant_total
            stock_ledger.save()

            transaction_2 = Transaction()
            transaction_2.transaction_ref = transaction_ref
            transaction_2.credit_ledger = credit_stock_entry
            transaction_2.transaction_date = purchase_return.invoice_date
            transaction_2.credit_amount = purchase_return.grant_total
            transaction_2.narration = 'By Purchase Return- '+ str(purchase_return.return_invoice_number)
            transaction_2.save()

            try:
                stock_value = StockValue.objects.latest('id')
            except Exception as ex:
                stock_value = StockValue()
            if stock_value.stock_by_value is not None:
                stock_value.stock_by_value = float(stock_value.stock_by_value) - float(total_cost_price)
            else:
                stock_value.stock_by_value = 0 - float(total_cost_price)
            stock_value.save()
            
            # Transaction 3 - Credit Entry for Tax Account

            credit_tax_account_entry = LedgerEntry()
            credit_tax_ledger = Ledger.objects.get(name="Input Vat (Purchases)")
            credit_tax_account_entry.ledger = credit_tax_ledger
            credit_tax_account_entry.credit_amount = purchase_return.purchase_tax
            credit_tax_account_entry.date = purchase_return.invoice_date
            credit_tax_account_entry.transaction_reference_number = transaction_ref
            credit_tax_account_entry.save()
            credit_tax_ledger.balance = float(credit_tax_ledger.balance) - purchase_return.purchase_tax
            credit_tax_ledger.save()

            transaction_3 = Transaction()
            transaction_3.transaction_ref = transaction_ref
            transaction_3.credit_ledger = credit_tax_account_entry
            transaction_3.transaction_date = purchase_return.invoice_date
            transaction_3.credit_amount = purchase_return.purchase_tax
            transaction_3.narration = 'By Purchase Return- '+ str(purchase_return.return_invoice_number)
            transaction_3.save()

            res = {
                'result': 'ok',
                'transaction_reference_no': transaction_ref,
            }

        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'message': 'Retrun Invoice no already exists',
                'error_message': str(ex),
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class PurchaseItemsList(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'purchase_permission'):
            item_name = request.GET.get('item_name', '')
            purchase_inveoice_no = request.GET.get('purchase_id', '')
            ctx_items = []
            purchase = Purchase.objects.get(purchase_invoice_number=purchase_inveoice_no)
            if item_name:
                purchase_items = PurchaseItem.objects.filter(purchase=purchase, batch_item__item__name__istartswith=item_name)
                for p_item in purchase_items:
                    returned_qty = 0.0
                    return_items = PurchaseReturnItem.objects.filter(purchase_item=p_item)
                    for r_item in return_items:
                        returned_qty = returned_qty + float(r_item.quantity)
                    stock = p_item.batch_item.quantity / p_item.uom_conversion.relation
                    ctx_items.append({
                        'id': p_item.id,
                        'purchased_quantity': p_item.quantity,
                        'purchase_price': p_item.purchase_price,
                        'cost_price': p_item.cost_price,
                        'purchase_unit': p_item.uom,
                        'conversion_unit': p_item.uom_conversion.id,
                        'conversion_unit_name': str('1') + p_item.uom_conversion.purchase_unit + ' - ' + str(p_item.uom_conversion.relation) + p_item.uom_conversion.selling_unit,
                        'batch': p_item.batch_item.batch.id,
                        'batch_item': p_item.batch_item.id,
                        'batch_name': p_item.batch_item.batch.name,
                        'item_name': p_item.batch_item.item.product.category.name+ ' - ' + p_item.batch_item.item.product.name + ' - ' + str(p_item.batch_item.item.name) + str(' - ') + str(p_item.batch_item.item.code),
                        'code': p_item.batch_item.item.code,
                        'name': p_item.batch_item.item.name,
                        'returned_qty': returned_qty,
                        'stock': stock,
                    })
            else:
                purchase_items = PurchaseItem.objects.filter(purchase=purchase)
                for p_item in purchase_items:
                    returned_qty = 0.0
                    return_items = PurchaseReturnItem.objects.filter(purchase_item=p_item)
                    for r_item in return_items:
                        returned_qty = returned_qty + float(r_item.quantity)
                    stock = p_item.batch_item.quantity / p_item.uom_conversion.relation
                    ctx_items.append({
                        'id': p_item.id,
                        'purchased_quantity': p_item.quantity,
                        'purchase_price': p_item.purchase_price,
                        'cost_price': p_item.cost_price,
                        'purchase_unit': p_item.uom,
                        'conversion_unit': p_item.uom_conversion.id,
                        'conversion_unit_name': str('1') + p_item.uom_conversion.purchase_unit + ' - ' + str(p_item.uom_conversion.relation) + p_item.uom_conversion.selling_unit,
                        'batch': p_item.batch_item.batch.id,
                        'batch_item': p_item.batch_item.id,
                        'batch_name': p_item.batch_item.batch.name,
                        'item_name': p_item.batch_item.item.product.category.name+ ' - ' + p_item.batch_item.item.product.name + ' - ' + str(p_item.batch_item.item.name) + str(' - ') + str(p_item.batch_item.item.code),
                        'code': p_item.batch_item.item.code,
                        'name': p_item.batch_item.item.name,
                        'returned_qty': returned_qty,
                        'stock': stock,
                    })
            res = {
                'result': 'ok',
                'items': ctx_items
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class PurchaseReturnReport(View):

    def get(self, request, *args, **kwargs):

        if get_user_permission(request, 'purchase_permission'):
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            if not start_date and not end_date:
                return render(request, 'purchase_return_report.html', {})
            else:
                startdate = datetime.strptime(start_date, '%d/%m/%Y')
                enddate = datetime.strptime(end_date, '%d/%m/%Y')
                purchase_returns = PurchaseReturn.objects.filter(invoice_date__gte=startdate,invoice_date__lte=enddate ).order_by('invoice_date')
                ctx_purchase_returns = []
                if request.is_ajax():
                    for purchase_return in purchase_returns:
                        ctx_purchase_returns.append({
                            'date': purchase_return.invoice_date.strftime('%d/%m/%Y'),
                            'purchase_invoice': purchase_return.return_invoice_number,
                            'invoice': purchase_return.purchase.purchase_invoice_number,
                            'grant_total': purchase_return.grant_total,
                            'discount': purchase_return.discount,
                            'tax': purchase_return.purchase_tax,
                            'supplier': purchase_return.purchase.supplier.name,
                            'transaction_ref': purchase_return.transaction_reference_no,
                        })
                    res = {
                        'purchase_return_details': ctx_purchase_returns,
                        'result': 'ok',
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                else:
                    response = HttpResponse(content_type='application/pdf')
                    canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
                    canvas_paper.setFont("Helvetica", 11)  
                    y = 1150
                    canvas_paper.setFontSize(20)
                    canvas_paper.drawCentredString(500, y, 'Purchase Return Report - ' + start_date + ' - ' +end_date )
                    y1 = y - 100
                    canvas_paper.setFontSize(16)
                    canvas_paper.drawString(50, y1, 'Date')
                    canvas_paper.drawString(130, y1, 'Invoice no.')
                    canvas_paper.drawString(220, y1, 'Purchase')
                    canvas_paper.drawString(300, y1, 'Grant Total')
                    canvas_paper.drawString(450, y1, 'Discount')
                    canvas_paper.drawString(550, y1, 'Tax')
                    canvas_paper.drawString(650, y1, 'Supplier')
                    canvas_paper.drawString(850, y1, 'Transaction Ref')

                    y1 = y1 - 30
                    total = 0
                    total_tax = 0
                    total_discount = 0
                    canvas_paper.setFontSize(12)
                    for purchase_return in purchase_returns:
                        canvas_paper.drawString(50, y1,purchase_return.invoice_date.strftime('%d/%m/%Y'))
                        canvas_paper.drawString(150, y1,purchase_return.return_invoice_number )
                        canvas_paper.drawString(260, y1, purchase_return.purchase.purchase_invoice_number)
                        canvas_paper.drawString(300, y1, str(purchase_return.grant_total))
                        canvas_paper.drawString(450, y1, str(purchase_return.discount))
                        canvas_paper.drawString(550, y1, str(purchase_return.purchase_tax))
                        canvas_paper.drawString(850, y1, str(purchase_return.transaction_reference_no))
                        data=[[Paragraph(purchase_return.purchase.supplier.name, para_style)]]
                        table = Table(data, colWidths=[250], rowHeights=100, style=style)      
                        table.wrapOn(canvas_paper, 200, 400)
                        table.drawOn(canvas_paper, 650, y1-10)
                        # canvas_paper.drawString(700, y1, str(purchase_return.purchase.supplier.name))
                        total = float(total) + float(purchase_return.grant_total)
                        total_tax = float(total_tax) + float(purchase_return.purchase_tax)
                        total_discount = float(total_discount) + float(purchase_return.discount)
                        y1 = y1 - 30
                        if y1 < 270:
                            y1 = y - 50
                            canvas_paper.showPage()

                    canvas_paper.drawString(200, y1, str(total))
                    canvas_paper.drawString(500, y1, str(total_discount))
                    canvas_paper.drawString(765, y1, str(total_tax))
                    canvas_paper.drawString(50, y1, 'Total Return Amount : ')
                    canvas_paper.drawString(350, y1, 'Total Return Discount : ')
                    canvas_paper.drawString(650, y1, 'Total Return Tax : ')

                    canvas_paper.showPage()
                    canvas_paper.save()

                    return response
        else:
            return HttpResponseRedirect(reverse('dashboard'))


class PurchaseView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            invoice_no = request.GET.get('invoice_no', '')
            ctx_purchase = {}
            if invoice_no:
                try:
                    purchase = None
                    try:    
                        purchase = Purchase.objects.get(purchase_invoice_number=invoice_no)
                    except Exception as ex:
                        purchase = Purchase.objects.get(transaction_reference_no=invoice_no)
                    if purchase:
                        ctx_items = []
                        for p_item in purchase.purchaseitem_set.all():
                            stock = float(p_item.batch_item.quantity) / float(p_item.batch_item.uom_conversion.relation)
                            whole_sale_profit = float(p_item.whole_sale_price) - float(float(p_item.purchase_price) + float(p_item.cost_price))
                            retail_profit = float(p_item.retail_price) - float(float(p_item.purchase_price) + float(p_item.cost_price))
                            ctx_items.append({
                                'name': p_item.batch_item.item.name,
                                'code': p_item.batch_item.item.code,
                                'batch_name': p_item.batch_item.batch.name,
                                'stock': stock,
                                'purchase_unit': p_item.uom,
                                'purchase_price': p_item.purchase_price,
                                'cost_price': p_item.cost_price,
                                'whole_sale_profit': whole_sale_profit,
                                'retail_profit': retail_profit,
                                'retail_price': p_item.retail_price,
                                'whole_sale_price': p_item.whole_sale_price,
                                'net_amount': p_item.net_amount,
                                'quantity': p_item.quantity,
                                'conversion_unit_name':  '1 ' + p_item.uom_conversion.purchase_unit + str(' - ') + str(p_item.uom_conversion.relation) + str('  ') + str(p_item.uom_conversion.selling_unit)
                            })
                        ctx_purchase.update({
                            'items': ctx_items,
                            'invoice_no': purchase.purchase_invoice_number,
                            'invoice_date': purchase.purchase_invoice_date.strftime('%d/%m/%Y'),
                            'payment_mode': purchase.payment_mode,
                            'discount': purchase.discount,
                            'purchase_tax': purchase.purchase_tax,
                            'grant_total': purchase.grant_total,
                            'do_no': purchase.do_number,
                            'supplier': purchase.supplier.name,
                            'transaction_ref': purchase.transaction_reference_no,
                            'bank_name': purchase.bank_name,
                            'card_number': purchase.card_number,
                            'cheque_date': purchase.cheque_date.strftime('%d/%m/%Y') if purchase.cheque_date else '',
                            'cheque_number': purchase.cheque_number,
                            'branch': purchase.branch,
                            'card_holder_name': purchase.card_holder_name,
                        })
                        res = {
                            'purchase':ctx_purchase,
                            'result': 'ok',
                        }
                    else:
                        res = {
                            'result': 'error',
                            'message': 'No Purchase with this Invoice No',
                            'purchase':ctx_purchase,
                        }
                except Exception as ex:
                    res = {
                        'result': 'error',
                        'message': 'No Purchase with this Invoice No',
                        'purchase':ctx_purchase,
                    }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'view_purchase.html', {})

class PurchaseReturnView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            invoice_no = request.GET.get('invoice_no', '')
            ctx_purchase_return = {}
            if invoice_no:
                try:
                    purchase_return = None
                    try:    
                        purchase_return = PurchaseReturn.objects.get(return_invoice_number=invoice_no)
                    except Exception as ex:
                        purchase_return = PurchaseReturn.objects.get(transaction_reference_no=invoice_no)
                    if purchase_return:
                        ctx_items = []
                        for p_item in purchase_return.purchasereturnitem_set.all():
                            returned_qty = 0.0
                            return_items = PurchaseReturnItem.objects.filter(purchase_item=p_item)
                            for r_item in return_items:
                                returned_qty = returned_qty + float(r_item.quantity)
                            stock = float(p_item.purchase_item.batch_item.quantity) / float(p_item.purchase_item.batch_item.uom_conversion.relation)
                            ctx_items.append({
                                'name': p_item.purchase_item.batch_item.item.name,
                                'code': p_item.purchase_item.batch_item.item.code,
                                'batch_name': p_item.purchase_item.batch_item.batch.name,
                                'stock': stock,
                                'purchased_qty': p_item.purchase_item.quantity,
                                'returned_qty': returned_qty,
                                'purchase_unit': p_item.purchase_item.uom,
                                'purchase_price': p_item.purchase_item.purchase_price,
                                'net_amount': p_item.net_amount,
                                'quantity': p_item.quantity,
                            })
                        ctx_purchase_return.update({
                            'items': ctx_items,
                            'invoice_no': purchase_return.return_invoice_number,
                            'invoice_date': purchase_return.invoice_date.strftime('%d/%m/%Y'),
                            'discount': purchase_return.discount,
                            'purchase_tax': purchase_return.purchase_tax,
                            'grant_total': purchase_return.grant_total,
                            'supplier': purchase_return.purchase.supplier.name,
                            'transaction_ref': purchase_return.transaction_reference_no,
                            'purchase_invoice': purchase_return.purchase.purchase_invoice_number,
                        })
                        res = {
                            'purchase_return':ctx_purchase_return,
                            'result': 'ok',
                        }
                    else:
                        res = {
                            'result': 'error',
                            'message': 'No Purchase Return with this Invoice No',
                            'purchase_return':ctx_purchase_return,
                        }
                except Exception as ex:
                    res = {
                        'result': 'error',
                        'message': 'No Purchase Return with this Invoice No',
                        'purchase_return':ctx_purchase_return,
                    }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'view_purchase_return.html', {})
