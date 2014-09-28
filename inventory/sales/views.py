import simplejson
import ast
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q

from customers.models import Customer
from sales.models import SalesItem, Sale, Invoice, Estimate, EstimateItem,  Receipt, SalesReturn, SalesReturnItem
from inventory.models import Item, BatchItem, Batch, StockValue
from accounting.models import Ledger, LedgerEntry, Transaction
from web.models import Salesman
from purchases.models import FreightValue

from web.views import get_user_permission

style = [
    ('FONTSIZE', (0,0), (-1, -1), 14),
    ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
]

para_style = ParagraphStyle('fancy')
para_style.fontSize = 11
para_style.fontName = 'Helvetica'

class SalesEntry(View):
    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'sales_permission'):
            if request.GET.get('transaction_ref_no'):
                transaction_ref = request.GET.get('transaction_ref_no')
                sale = Sale.objects.get(transaction_reference_no=transaction_ref)
                response = HttpResponse(content_type='application/pdf')
                canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
                y = 1150
                status_code = 200
                canvas_paper.setFontSize(15)
                canvas_paper.drawCentredString(500, y, 'SALES RECEIPT')
                canvas_paper.drawString(770,  y - 120, 'Date:')
                canvas_paper.drawString(100,  y - 120, 'Invoice No...............................')

                canvas_paper.drawString(100, y - 140, 'Sold To.......................................................................................')
                # Table
                if sale.bill_type == 'Invoice':
                    width = 875
                else: 
                    width = 780
                canvas_paper.line(150, y - 200, width, y - 200)
                canvas_paper.line(150, y - 200, 150, y - 850) 
                canvas_paper.line(150, y - 250, width, y - 250) 
                canvas_paper.line(250, y - 200, 250, y - 850)
                canvas_paper.line(450, y - 200, 450, y - 850)  
                canvas_paper.line(550, y - 200, 550, y - 850)
                canvas_paper.line(650, y - 200, 650, y - 850)
                canvas_paper.line(width, y - 200, width, y - 850) 
                if sale.bill_type == 'Invoice':
                    canvas_paper.line(750, y - 200, 750, y - 850) 
                canvas_paper.line(150, y - 850, width, y - 850)
                # end table
                canvas_paper.drawString(180, y - 230, 'SL. No.')
                # canvas_paper.drawString(290, y-230, 'Sch.')
                canvas_paper.drawString(320, y - 230, 'Item Name ')
                canvas_paper.drawString(460, y-230, 'Quantity')
                canvas_paper.drawString(570, y - 230, 'MRP')
                x = 570
                if sale.bill_type == 'Invoice':
                    canvas_paper.drawString(670, y - 230, 'Tax')
                    x = 670
                canvas_paper.drawString(x+100, y - 230, 'Amount')

                if sale.sales_invoice_number != '':
                    invoice_no = str(sale.sales_invoice_number)
                elif sale.bill_type == 'Receipt':
                    receipt = Receipt.objects.get(sales=sale)
                    invoice_no = receipt.receipt_no
                elif sale.bill_type == 'Invoice':
                    invoice = Invoice.objects.get(sales=sale)
                    invoice_no = invoice.invoice_no
                canvas_paper.drawString(820,  y - 120, sale.sales_invoice_date.strftime('%d-%b-%Y'))
                canvas_paper.drawString(200,  y - 117, invoice_no)

                if sale.customer:
                    customer = sale.customer.name
                else:
                    customer = ''
                canvas_paper.drawString(180, y - 137, customer)
                sales_items = sale.salesitem_set.all()
                i=0
                y1 = y - 280
                total_amount = 0
                for sales_item in sales_items:         
                    if y1 <= 270:
                        y1 = y - 280
                        canvas_paper.showPage()
                        canvas_paper = invoice_body_layout(canvas_paper, y, sales)
                        
                        canvas_paper.setFont('Helvetica', 10)
                    i = i +1
                    canvas_paper.drawString(160, y1, str(i))
                    data=[[Paragraph(sales_item.batch_item.item.name, para_style)]]

                    table = Table(data, colWidths=[100], rowHeights=100, style=style)      
                    table.wrapOn(canvas_paper, 200, 400)
                    table.drawOn(canvas_paper, 280, y1-10)
                    canvas_paper.drawString(460,y1, str(round(sales_item.quantity, 2))+" "+str(sales_item.uom))
                    canvas_paper.drawString(570,y1, str(round(sales_item.mrp, 2)))
                    if sale.bill_type == 'Invoice':
                        if sales_item.batch_item.item.vat_type:
                            tax_percentage = sales_item.batch_item.item.vat_type.tax_percentage
                            canvas_paper.drawString(670,y1, str(tax_percentage)+" %")
                        else:
                            canvas_paper.drawString(670,y1, '')
                                                
                    
                    canvas_paper.drawString(x+100, y1, str(round(sales_item.net_amount,2)))

                    #total_amount = total_amount + s_item.net_amount

                    y1 = y1 - 30
                # total box
                canvas_paper.line(150, y - 1000, width, y - 1000)

                
                canvas_paper.line(650, y - 850, 652, y - 1000)
                canvas_paper.line(150, y - 850, 150, y - 1000)
                canvas_paper.line(width, y - 850, width, y - 1000)

                # total box end
                canvas_paper.drawString(x+100, y - 882, 'Rs '+str(sale.grant_total))
                canvas_paper.line(150, y - 827, width, y - 827)
                # p.setFont("Helvetica-Bold", 30)  
                canvas_paper.drawString(165, y - 882, 'Total')
                canvas_paper.showPage()
                canvas_paper.save()
                return response

            else:
                current_date = datetime.now().date()
                return render(request, 'sales.html', {'current_date': current_date.strftime('%d/%m/%Y'),})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

    def post(self, request, *args, **kwargs):
        sales_details = ast.literal_eval(request.POST['sales_details']) 
        try:
            sale = Sale()           
            sale.sales_invoice_number = sales_details['invoice_no']
            sale.sales_invoice_date = datetime.strptime(sales_details['invoice_date'], '%d/%m/%Y')
            sale.do_number = sales_details['do_no']
            sale.bill_type  = sales_details['bill_type']
            try:
                transaction_reference_no = Sale.objects.latest('id').id
                if sales_details['bill_type'] == 'Receipt':
                    sale.transaction_reference_no = 'SREC'+str(transaction_reference_no+1)
                else:
                    sale.transaction_reference_no = 'SINV'+str(transaction_reference_no+1)
            except:
                transaction_reference_no = '1'
                if sales_details['bill_type'] == 'Receipt':
                    sale.transaction_reference_no = 'SREC'+str(transaction_reference_no)
                else:
                    sale.transaction_reference_no = 'SINV'+str(transaction_reference_no)
            sale.payment_mode = sales_details['payment_mode']
            if sales_details['payment_mode'] == 'cheque':
                sale.bank_name = sales_details['bank_name']
                sale.branch = sales_details['branch']
                sale.cheque_number = sales_details['cheque_no']
                sale.cheque_date = datetime.strptime(sales_details['cheque_date'], '%d/%m/%Y')
            elif sales_details['payment_mode'] == 'card':
                sale.bank_name = sales_details['bank_name']
                sale.card_holder_name = sales_details['card_holder_name']
                sale.card_number = sales_details['card_no']
            salesman = Salesman.objects.get(id=sales_details['salesman'])
            sale.salesman = salesman
            if sales_details['customer']:
                customer = Customer.objects.get(id=sales_details['customer'])
                sale.customer = customer
            sale.discount = sales_details['discount']
            if sales_details['round_off'] != '':
                sale.round_off = sales_details['round_off']
            sale.grant_total = sales_details['grant_total']
            sales_items = sales_details['items']
            sale.save()
            if sales_details['bill_type'] == 'Receipt':
                receipt = Receipt()
                receipt.sales = sale
                try:
                    receipt_no  = Receipt.objects.latest('id').receipt_no
                    receipt.receipt_no = "RCPT-" + str(int(receipt_no.split('-')[1]) + 1)
                except Exception as ex:
                    print str(ex)
                    receipt_no = 1
                    receipt.receipt_no = "RCPT-" + str(receipt_no)
                receipt.save()
            elif sales_details['bill_type'] == 'Invoice':
                invoice = Invoice()
                invoice.sales = sale
                try:
                    invoice_no  = Invoice.objects.latest('id').invoice_no
                    invoice.invoice_no = "INVC-" + str(int(invoice_no.split('-')[1]) + 1)
                except:
                    invoice_no = 1
                    invoice.invoice_no = "INVC-" + str(invoice_no)
                invoice.invoice_type = "Tax Inclusive"
                invoice.save()

            transaction_1 = Transaction()
            ledger_entry_debit_customer = LedgerEntry()
            if sales_details['customer']:
                customer = Customer.objects.get(id=sales_details['customer'])
                ledger_entry_debit_customer.ledger = customer.ledger
            else:
                parent = Ledger.objects.get(name='Sundry Debtors')
                counter_sales_ledger, created = Ledger.objects.get_or_create(name="Counter Sales", parent=parent)
                ledger_entry_debit_customer.ledger = counter_sales_ledger
            ledger_entry_debit_customer.debit_amount = sale.grant_total
            ledger_entry_debit_customer.date = sale.sales_invoice_date
            ledger_entry_debit_customer.transaction_reference_number = sale.transaction_reference_no
            ledger_entry_debit_customer.save()
            ledger_entry_credit_sales = LedgerEntry()
            sales_ledger = Ledger.objects.get(name='Sales')
            ledger_entry_credit_sales.ledger = sales_ledger
            ledger_entry_credit_sales.credit_amount = sales_details['tax_exclusive_total']
            ledger_entry_credit_sales.date = sale.sales_invoice_date
            ledger_entry_credit_sales.transaction_reference_number = sale.transaction_reference_no
            ledger_entry_credit_sales.save()
            transaction_1.credit_ledger = ledger_entry_credit_sales
            transaction_1.debit_ledger = ledger_entry_debit_customer
            transaction_1.transaction_ref = sale.transaction_reference_no
            transaction_1.debit_amount = ledger_entry_debit_customer.debit_amount
            transaction_1.credit_amount = ledger_entry_credit_sales.credit_amount
            sales_ledger.balance = float(sales_ledger.balance) - float(ledger_entry_credit_sales.credit_amount)
            sales_ledger.save()
            if sales_details['customer']:
                customer.ledger.balance = float(customer.ledger.balance) + float(ledger_entry_debit_customer.debit_amount)
                customer.ledger.save()
            else:
                counter_sales_ledger.balance = float(counter_sales_ledger.balance) + float(ledger_entry_debit_customer.debit_amount)
                counter_sales_ledger.save()
            if sale.payment_mode != 'credit':
                if sale.payment_mode == 'cash':
                    debit_ledger = Ledger.objects.get(name="Cash")
                elif sale.payment_mode == 'card' or sale.payment_mode == 'cheque':
                    debit_ledger = Ledger.objects.get(id=sales_details['bank_account_ledger'])
                ledger_entry_debit_accounts = LedgerEntry()
                ledger_entry_debit_accounts.ledger = debit_ledger
                ledger_entry_debit_accounts.debit_amount = sale.grant_total
                ledger_entry_debit_accounts.date = sale.sales_invoice_date
                ledger_entry_debit_accounts.transaction_reference_number = sale.transaction_reference_no
                ledger_entry_debit_accounts.save()

                ledger_entry_credit_customer = LedgerEntry()
                if sales_details['customer']:
                    customer = Customer.objects.get(id=sales_details['customer'])
                    ledger_entry_credit_customer.ledger = customer.ledger
                else:
                    counter_sales_ledger = Ledger.objects.get(name="Counter Sales")
                    ledger_entry_credit_customer.ledger = counter_sales_ledger
                ledger_entry_credit_customer.credit_amount = sale.grant_total
                ledger_entry_credit_customer.date = sale.sales_invoice_date
                ledger_entry_credit_customer.transaction_reference_number = sale.transaction_reference_no
                ledger_entry_credit_customer.save()
                debit_ledger.balance = float(debit_ledger.balance) + ledger_entry_debit_accounts.debit_amount
                debit_ledger.save()
                if sales_details['customer']:
                    customer.ledger.balance = float(customer.ledger.balance) - float(ledger_entry_credit_customer.credit_amount)
                    customer.ledger.save()
                else:
                    counter_sales_ledger.balance = float(counter_sales_ledger.balance) - float(ledger_entry_credit_customer.credit_amount)
                    counter_sales_ledger.save()
                transaction_2 = Transaction()
                transaction_2.credit_ledger = ledger_entry_credit_customer
                transaction_2.debit_ledger = ledger_entry_debit_accounts
                transaction_2.transaction_ref = sale.transaction_reference_no
                transaction_2.debit_amount = sale.grant_total
                transaction_2.credit_amount = sale.grant_total
            transaction_3 = Transaction()
            credit_stock_ledger = Ledger.objects.get(name="Stock")
            ledger_entry_credit_stock = LedgerEntry()
            ledger_entry_credit_stock.ledger = credit_stock_ledger
            ledger_entry_credit_stock.credit_amount = sales_details['tax_exclusive_total']
            ledger_entry_credit_stock.date = sale.sales_invoice_date
            ledger_entry_credit_stock.transaction_reference_number = sale.transaction_reference_no
            ledger_entry_credit_stock.save()
            credit_stock_ledger.balance = float(credit_stock_ledger.balance) - float(ledger_entry_credit_stock.credit_amount)
            credit_stock_ledger.save()
            transaction_3.credit_ledger = ledger_entry_credit_stock
            transaction_3.transaction_ref = sale.transaction_reference_no
            transaction_3.credit_amount = ledger_entry_credit_stock.credit_amount
            
            if sales_details['bill_type'] == 'Invoice':
                transaction_4 = Transaction()
                credit_tax_ledger = Ledger.objects.get(name="Output Vat (sales)")
                ledger_entry_credit_tax_account = LedgerEntry()
                ledger_entry_credit_tax_account.ledger = credit_tax_ledger
                ledger_entry_credit_tax_account.date = sale.sales_invoice_date
                ledger_entry_credit_tax_account.credit_amount = float(sale.grant_total) - float(sales_details['tax_exclusive_total'])
                ledger_entry_credit_tax_account.transaction_reference_number = sale.transaction_reference_no
                ledger_entry_credit_tax_account.save()
                credit_tax_ledger.balance = float(credit_tax_ledger.balance) - float(ledger_entry_credit_tax_account.credit_amount)
                credit_tax_ledger.save()
                transaction_4.credit_ledger = ledger_entry_credit_tax_account
                transaction_4.credit_amount = ledger_entry_credit_tax_account.credit_amount
                transaction_4.transaction_ref = sale.transaction_reference_no
                transaction_4.transaction_date = sale.sales_invoice_date
                transaction_4.narration = 'By Sales - '+ str(sale.sales_invoice_number)
                transaction_4.payment_mode = sale.payment_mode
                if sale.payment_mode != 'credit':
                    if sale.payment_mode == 'cheque':
                         transaction_4.bank_name = sale.bank_name
                         transaction_4.branch = sale.branch
                    elif sale.payment_mode == 'card':
                        transaction_4.bank_name = sale.bank_name
                        transaction_4.card_no = sale.card_number
                        transaction_4.card_holder_name = sale.card_holder_name
                transaction_4.save()
            transaction_1.transaction_date = sale.sales_invoice_date
            transaction_1.narration = 'By Sales - '+ str(sale.sales_invoice_number)
            transaction_1.payment_mode = sale.payment_mode
            if sale.payment_mode != 'credit':
                transaction_2.transaction_date = sale.sales_invoice_date
                transaction_2.narration = 'By Sales - '+ str(sale.sales_invoice_number)
                transaction_2.payment_mode = sale.payment_mode
            transaction_3.transaction_date = sale.sales_invoice_date
            transaction_3.narration = 'By Sales - '+ str(sale.sales_invoice_number)
            transaction_3.payment_mode = sale.payment_mode

            if sale.payment_mode != 'credit':
                if sale.payment_mode == 'cheque':
                    transaction_1.bank_name = sale.bank_name
                    transaction_2.bank_name = sale.bank_name
                    transaction_3.bank_name = sale.bank_name
                    transaction_1.cheque_number = sale.cheque_number
                    transaction_1.cheque_date = sale.cheque_date
                    transaction_1.branch = sale.branch
                    transaction_2.cheque_number = sale.cheque_number
                    transaction_2.cheque_date = sale.cheque_date
                    transaction_2.branch = sale.branch
                    transaction_3.cheque_number = sale.cheque_number
                    transaction_3.cheque_date = sale.cheque_date
                    transaction_3.branch = sale.branch
                elif sale.payment_mode == 'card':
                    transaction_1.bank_name = sale.bank_name
                    transaction_2.bank_name = sale.bank_name
                    transaction_3.bank_name = sale.bank_name
                    transaction_1.card_holder_name = sale.card_holder_name
                    transaction_1.card_no = sale.card_number
                    transaction_2.card_holder_name = sale.card_holder_name
                    transaction_2.card_no = sale.card_number
                    transaction_3.card_holder_name = sale.card_holder_name
                    transaction_3.card_no = sale.card_number
                transaction_2.save()
            transaction_1.save()
            transaction_3.save()
            total_cost_price = 0
            total_freight_value = 0
            total_purchase_price = 0
            for item in sales_items:
                sales_item = SalesItem()
                sales_item.sales = sale
                item_obj = BatchItem.objects.get(batch__id=item['batch_id'],item__id=item['id'])
                sales_item.batch_item = item_obj
                sales_item.quantity = item['quantity']
                sales_item.uom = item['uom']
                sales_item.mrp = item['current_item_price']
                sales_item.net_amount = item['net_amount']
                sales_item.save()
                batch_item = BatchItem.objects.get(batch__id=item['batch_id'], item__id=item['id'])
                if item['stock_unit'] == item['uom']:
                    net_quantity = float(item['quantity']) / float(item['relation'])
                    purchase_price = float(item_obj.purchase_price) * float(item['relation'])
                    batch_item.quantity = float(batch_item.quantity) - float(item['quantity'])
                    total_cost_price = float(total_cost_price) + (float(net_quantity) * float(item_obj.cost_price))
                    total_purchase_price = float(total_purchase_price) + (float(net_quantity) * float(purchase_price))
                    total_freight_value = float(total_freight_value) + (float(net_quantity) * float(item_obj.freight_charge))
                else:   
                    net_quantity = float(item['quantity']) * float(item['relation'])
                    purchase_price = float(item_obj.purchase_price) * float(item['relation'])
                    batch_item.quantity = float(batch_item.quantity) - float(net_quantity)
                    total_cost_price = float(total_cost_price) + (float(item['quantity']) * float(item_obj.cost_price))
                    total_freight_value = float(total_freight_value) + (float(item['quantity']) * float(item_obj.freight_charge))
                    total_purchase_price = float(total_purchase_price) + (float(item['quantity']) * float(purchase_price))
                sales_item.save()
                batch_item.save()
            try:
                stock_value = StockValue.objects.latest('id')
            except Exception as ex:
                stock_value = StockValue()
            if stock_value.stock_by_value is not None:
                stock_value.stock_by_value = float(stock_value.stock_by_value) - float(total_cost_price)
            else:
                stock_value.stock_by_value = 0 - float(total_cost_price)
            stock_value.save()
            try:
                freight = FreightValue.objects.latest('id')
            except:
                freight = FreightValue()
            if freight.freight_value is not None:
                freight.freight_value = float(freight.freight_value) - float(total_freight_value)
            else:
                freight.freight_value = 0 - float(total_freight_value)
            freight.save()
            res = {
                'result': 'ok',
                'message': 'Transaction saved',
                'transaction_reference_no': sale.transaction_reference_no,
            }
        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'message': 'Transaction failed'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class SalesReceipts(View):

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        if request.is_ajax():
            startdate = datetime.strptime(start_date, '%d/%m/%Y')
            enddate = datetime.strptime(end_date, '%d/%m/%Y')
            sales_receipts = Sale.objects.filter(sales_invoice_date__gte=startdate,sales_invoice_date__lte=enddate,bill_type='Receipt').order_by('sales_invoice_date')
            sales_receipts_list = []
            for sales_receipt in sales_receipts:
                try:
                    Invoice.objects.get(sales=sales_receipt)
                except:
                    receipt = Receipt.objects.get(sales=sales_receipt)
                    sales_receipts_list.append({
                        'id': sales_receipt.id,
                        'sales_invoice_number': sales_receipt.sales_invoice_number,
                        'sales_invoice_date': sales_receipt.sales_invoice_date.strftime('%d/%m/%Y'),
                        'auto_invoice_no': receipt.receipt_no,
                        'transaction_reference_no': sales_receipt.transaction_reference_no,
                        'amount': sales_receipt.grant_total,
                    })
            res = {
                'result': 'ok',
                'sales_receipts': sales_receipts_list,
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'sales_receipts.html', {})
        
    
    def post(self, request, *args, **kwargs):
        sales_receipts = ast.literal_eval(request.POST['sales_receipts'])  
        try:
            for sales_receipt in sales_receipts:
                if sales_receipt['invoice'] == 'true':
                    amount = 0;
                    tax = 0;
                    net_amount = 0
                    net_tax = 0
                    sales_items = SalesItem.objects.filter(sales__id=sales_receipt['id'])       
                    for sales_item in sales_items:
                        if sales_item.batch_item.item.vat_type:
                            tax = float(sales_item.net_amount) * float(sales_item.batch_item.item.vat_type.tax_percentage/100) 
                        else:
                            tax = 0
                        amount = float(sales_item.net_amount) - float(tax)
                        net_amount = float(net_amount) + float(amount) 
                        net_tax = float(net_tax) + float(tax) 
                    sales_ledger = Ledger.objects.get(name='Sales')  
                    sales_ledger_entry = LedgerEntry.objects.get(transaction_reference_number=sales_receipt['transaction_reference_no'], ledger=sales_ledger)
                    sales_ledger_entry.credit_amount = net_amount
                    sales_ledger_entry.save()
                    sales_ledger.balance = float(sales_ledger.balance) - float(sales_ledger_entry.credit_amount)
                    sales_ledger.save()
                    credit_tax_ledger = Ledger.objects.get(name="Output Vat (sales)")
                    ledger_entry_credit_tax_account = LedgerEntry()
                    ledger_entry_credit_tax_account.ledger = credit_tax_ledger
                    ledger_entry_credit_tax_account.date = datetime.strptime(sales_receipt['sales_invoice_date'], '%d/%m/%Y')
                    ledger_entry_credit_tax_account.credit_amount = float(net_tax)
                    ledger_entry_credit_tax_account.transaction_reference_number = sales_receipt['transaction_reference_no']
                    ledger_entry_credit_tax_account.save()
                    credit_tax_ledger.balance = float(credit_tax_ledger.balance) - float(net_tax)
                    credit_tax_ledger.save()
                    invoice = Invoice()
                    sale = Sale.objects.get(id=sales_receipt['id'])
                    invoice.sales = sale
                    try:
                        invoice_no  = Invoice.objects.latest('id').invoice_no
                        invoice.invoice_no = "INVC-" + str(int(invoice_no) + 1)
                    except:
                        invoice_no = 1
                        invoice.invoice_no = "INVC-" + str(invoice_no)
                    invoice.invoice_type = 'Tax Inclusive'
                    invoice.save() 
                    res = {
                        'result': 'ok',
                        'message': 'Success'
                    }
        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'message': 'Failed'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class SaleReturn(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            sales_invoice = request.GET.get('sales_invoice_no', '')
            sale = []
            ctx_sales = []
            ctx_sales_items = []
            if sales_invoice:
                sales = Sale.objects.filter(Q(sales_invoice_number=sales_invoice)|Q(transaction_reference_no=sales_invoice))
                if len(sales) > 0:
                    for sale in sales:
                        sale = sale
            if len(sales) == 0:
                receipts = Receipt.objects.filter(Q(receipt_no=sales_invoice))
                if len(receipts) > 0:
                    for receipt in receipts:
                        sale = receipt.sales
            if len(sales) == 0 and len(receipts) == 0:
                invoices = Invoice.objects.filter(Q(invoice_no=sales_invoice))
                if len(invoices) > 0:
                    for invoice in invoices:
                        sale = invoice.sales
            if sale:
                sales_items = SalesItem.objects.filter(sales__id=sale.id)
                for sales_item in sales_items:
                    returned_qty = 0.0
                    return_items = SalesReturnItem.objects.filter(sales_item=sales_item)
                    for r_item in return_items:
                        returned_qty = returned_qty + float(r_item.quantity)
                    ctx_sales_items.append({
                        'id': sales_item.id,
                        'item_code': sales_item.batch_item.item.code,
                        'item_name': sales_item.batch_item.item.name,
                        'item_quantity': sales_item.quantity,
                        'uom': sales_item.uom,
                        'net_amount': sales_item.net_amount,
                        'tax': sales_item.batch_item.item.vat_type.tax_percentage if sales_item.batch_item.item.vat_type else '',
                        'mrp': sales_item.mrp,
                        'returned_qty': returned_qty,
                    })               
                ctx_sales.append({
                    'id': sale.id,
                    'sales_invoice': sale.sales_invoice_number,
                    'customer': sale.customer.name if sale.customer else '',
                    'salesman': sale.salesman.first_name + " " + sale.salesman.last_name,
                    'discount': sale.discount,
                    'grant_total': sale.grant_total,
                    'sales_items': ctx_sales_items,
                    'bill_type': sale.bill_type,
                })
                ctx_sales_items = []
            res = {
                'sales_details': ctx_sales,
                'result': 'ok',
            }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'sales_return.html', {})

    def post(self, request, *args, **kwargs):
        sales_return_details = ast.literal_eval(request.POST['sales_return'])
        try:
            sales = Sale.objects.get(id=sales_return_details['sales_id'])
            sales_return = SalesReturn()
            sales_return.sales = sales
            sales_return.return_invoice_number = sales_return_details['return_invoice']
            sales_return.invoice_date = datetime.strptime(sales_return_details['return_invoice_date'], '%d/%m/%Y')
            sales_return.grant_total = sales_return_details['return_balance'] 
            try:
                transaction_reference_no = SalesReturn.objects.latest('id').id
                if sales.bill_type == 'Receipt':
                    sales_return.transaction_reference_no = 'SRREC'+str(transaction_reference_no+1)
                else:
                    sales_return.transaction_reference_no = 'SRINV'+str(transaction_reference_no+1)
            except:
                transaction_reference_no = '1'
                if sales.bill_type == 'Receipt':
                    sales_return.transaction_reference_no = 'SRREC'+str(transaction_reference_no)
                else:
                    sales_return.transaction_reference_no = 'SINV'+str(transaction_reference_no)
            sales_return.save()
            sales_return_items = sales_return_details['items']
            total_cost_price = 0
            total_freight_value = 0
            for item in sales_return_items:
                if item['returned_qty'] != '' and float(item['returned_qty']) != 0:
                    sales_item = SalesItem.objects.get(id=item['id'])
                    return_item = SalesReturnItem()
                    return_item.sales_return = sales_return
                    return_item.sales_item = sales_item
                    return_item.quantity = item['returned_qty']
                    return_item.net_amount = item['balance']
                    return_item.uom = item['uom']
                    return_item.save()
                    
                    batch_item = sales_item.batch_item
                    if batch_item.uom_conversion.purchase_unit == item['uom']:
                        quantity = float(return_item.quantity) * float(batch_item.uom_conversion.relation)
                        total_cost_price = float(total_cost_price) + (float(batch_item.cost_price) * float(return_item.quantity))
                        total_freight_value = float(total_freight_value) + (float(batch_item.freight_charge) * float(return_item.quantity))
                    else:
                        quantity = return_item.quantity
                        stock_quantity = float(return_item.quantity) / float(batch_item.uom_conversion.relation)
                        total_cost_price = float(total_cost_price) + (float(batch_item.cost_price) * float(stock_quantity))
                        total_freight_value = float(total_freight_value) + (float(batch_item.freight_charge) * float(stock_quantity))
                    batch_item.quantity = float(batch_item.quantity) + float(quantity)
                    batch_item.save()
            debit_sales_return_entry = LedgerEntry()
            sales_return_ledger = Ledger.objects.get(name='Sales Return')
            debit_sales_return_entry.ledger = sales_return_ledger
            debit_sales_return_entry.debit_amount = float(sales_return.grant_total) - float(sales_return_details['total_tax'])
            debit_sales_return_entry.date = sales_return.invoice_date
            debit_sales_return_entry.transaction_reference_number = sales_return.transaction_reference_no
            debit_sales_return_entry.save()
            sales_return_ledger.balance = float(sales_return_ledger.balance) + float(debit_sales_return_entry.debit_amount)
            sales_return_ledger.save()
            credit_customer_entry = LedgerEntry()
            if sales_return_details['customer']:
                customer = Customer.objects.get(name=sales_return_details['customer'])
                credit_customer_entry.ledger = customer.ledger
                customer.ledger.balance = float(customer.ledger.balance) - float(sales_return.grant_total)
                customer.ledger.save()
            else:
                counter_sales_ledger = Ledger.objects.get(name="Counter Sales")
                credit_customer_entry.ledger = counter_sales_ledger
                counter_sales_ledger.balance = float(counter_sales_ledger.balance) - float(sales_return.grant_total)
                counter_sales_ledger.save()
            credit_customer_entry.credit_amount = sales_return.grant_total
            credit_customer_entry.date = sales_return.invoice_date
            credit_customer_entry.transaction_reference_number = sales_return.transaction_reference_no
            credit_customer_entry.save()
            transaction_1 = Transaction()
            transaction_1.debit_ledger = debit_sales_return_entry
            transaction_1.credit_ledger = credit_customer_entry
            transaction_1.transaction_ref = sales_return.transaction_reference_no
            transaction_1.transaction_date = sales_return.invoice_date
            transaction_1.debit_amount = debit_sales_return_entry.debit_amount
            transaction_1.credit_amount = credit_customer_entry.credit_amount
            transaction_1.narration = 'By Sales Return- '+ str(sales_return.return_invoice_number)
            transaction_1.save()

            debit_stock_entry = LedgerEntry()
            stock_ledger = Ledger.objects.get(name='Stock')
            debit_stock_entry.ledger = stock_ledger
            debit_stock_entry.debit_amount = sales_return.grant_total
            debit_stock_entry.date = sales_return.invoice_date
            debit_stock_entry.transaction_reference_number = sales_return.transaction_reference_no
            debit_stock_entry.save()
            stock_ledger.balance = float(stock_ledger.balance) + sales_return.grant_total
            stock_ledger.save()

            transaction_2 = Transaction()
            transaction_2.transaction_ref = sales_return.transaction_reference_no
            transaction_2.debit_ledger = debit_stock_entry
            transaction_2.transaction_date = sales_return.invoice_date
            transaction_2.credit_amount = sales_return.grant_total
            transaction_2.narration = 'By Sales Return- '+ str(sales_return.return_invoice_number)
            transaction_2.save()

            if sales_return_details['bill_type'] == 'Invoice':
                debit_tax_account_entry = LedgerEntry()
                debit_tax_ledger = Ledger.objects.get(name="Output Vat (sales)")
                debit_tax_account_entry.ledger = debit_tax_ledger
                debit_tax_account_entry.debit_amount = sales_return_details['total_tax']
                debit_tax_account_entry.date = sales_return.invoice_date
                debit_tax_account_entry.transaction_reference_number = sales_return.transaction_reference_no
                debit_tax_account_entry.save()
                debit_tax_ledger.balance = float(debit_tax_ledger.balance) + sales_return_details['total_tax']
                debit_tax_ledger.save()

                credit_cash_ledger_entry = LedgerEntry()
                credit_cash_ledger = Ledger.objects.get(name="Cash")
                credit_cash_ledger_entry.ledger = credit_cash_ledger
                credit_cash_ledger_entry.credit_amount = float(sales_return.grant_total) - float(sales_return_details['total_tax'])
                credit_cash_ledger_entry.date = sales_return.invoice_date
                credit_cash_ledger_entry.transaction_reference_number = sales_return.transaction_reference_no
                credit_cash_ledger_entry.save()
                credit_cash_ledger.balance = float(credit_cash_ledger.balance) - float(credit_cash_ledger_entry.credit_amount)
                credit_cash_ledger.save()

                transaction_3 = Transaction()
                transaction_3.transaction_ref = sales_return.transaction_reference_no
                transaction_3.credit_ledger = credit_cash_ledger_entry
                transaction_3.debit_ledger = debit_tax_account_entry
                transaction_3.transaction_date = sales_return.invoice_date
                transaction_3.narration = 'By Sales Return- '+ str(sales_return.return_invoice_number)
                transaction_3.save()
            try:
                stock_value = StockValue.objects.latest('id')
            except Exception as ex:
                stock_value = StockValue()
            if stock_value.stock_by_value is not None:
                stock_value.stock_by_value = float(stock_value.stock_by_value) + float(total_cost_price)
            else:
                stock_value.stock_by_value = float(total_cost_price)
            stock_value.save()
            try:
                freight = FreightValue.objects.latest('id')
            except:
                freight = FreightValue()
            if freight.freight_value is not None:
                freight.freight_value = float(freight.freight_value) + float(total_freight_value)
            else:
                freight.freight_value = float(total_freight_value)
            freight.save()
            res = {
                'result': 'ok',
                'transaction_reference_no': sales_return.transaction_reference_no,
            }

        except Exception as ex:
            print str(ex)
            res = {
                'result': 'error',
                'message': 'Return Invoice no already exists',
                'error_message': str(ex),
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class SalesReport(View):

    def get(self, request, *args, **kwargs):

        if get_user_permission(request, 'sales_permission'):
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            if not start_date and not end_date:
                return render(request, 'sales_report.html', {})
            else:
                startdate = datetime.strptime(start_date, '%d/%m/%Y')
                enddate = datetime.strptime(end_date, '%d/%m/%Y')
                if request.user.is_superuser:
                    sales = Sale.objects.filter(sales_invoice_date__gte=startdate,sales_invoice_date__lte=enddate ).order_by('sales_invoice_date')
                else:
                    sales = Sale.objects.filter(sales_invoice_date__gte=startdate,sales_invoice_date__lte=enddate ).exclude(bill_type='Receipt').order_by('sales_invoice_date')
                ctx_sales = []
                if request.is_ajax():
                    for sale in sales:
                        if sale.invoice_set.all().count() > 0:
                            invoice_no = sale.invoice_set.all()[0].invoice_no
                        else:
                            invoice_no = sale.receipt_set.all()[0].receipt_no if sale.receipt_set.all().count() > 0 else sale.sales_invoice_number
                        total_tax = 0
                        for s_item in sale.salesitem_set.all():
                            total_tax = float(total_tax) + ( (float(s_item.net_amount)) - (float(s_item.mrp)*float(s_item.quantity)))
                        ctx_sales.append({
                            'date': sale.sales_invoice_date.strftime('%d/%m/%Y'),
                            'invoice': invoice_no,
                            'transaction_ref': sale.transaction_reference_no,
                            'payment_mode': sale.payment_mode,
                            'grant_total': sale.grant_total,
                            'discount': sale.discount,
                            'salesman': sale.salesman.first_name + ' ' + sale.salesman.last_name,
                            'customer': sale.customer.name if sale.customer else '',
                            'tax': str(total_tax),
                            'round_off':str(sale.round_off)
                        })
                    res = {
                        'sales_details': ctx_sales,
                        'result': 'ok',
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
                else:
                    response = HttpResponse(content_type='application/pdf')
                    canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
                    y = 1150
                    status_code = 200
                    canvas_paper.setFontSize(20)
                    canvas_paper.drawCentredString(500, y, 'Sales Report - ' + start_date + ' - ' +end_date )
                    y1 = y - 100
                    canvas_paper.setFontSize(12)
                    # if request.user.is_superuser:
                    canvas_paper.drawString(50, y - 100, 'Date')
                    canvas_paper.drawString(120, y - 100, 'Invoice')
                    canvas_paper.drawString(170, y - 100, 'Transaction')
                    canvas_paper.drawString(250, y - 100, 'Salesman')
                    canvas_paper.drawString(400, y - 100, 'Customer')
                    canvas_paper.drawString(570, y - 100, 'Payment')
                    canvas_paper.drawString(650, y - 100, 'Total')
                    canvas_paper.drawString(730, y - 100, 'Discount')
                    canvas_paper.drawString(800, y - 100, 'Tax')
                    canvas_paper.drawString(860, y - 100, 'Round off')
                    y1 = y1 - 30
                    total = 0
                    total_discount = 0
                    for sale in sales:
                        total_tax = 0
                        for s_item in sale.salesitem_set.all():
                            total_tax = float(total_tax) + ( (float(s_item.net_amount)) - (float(s_item.mrp)*float(s_item.quantity)))
                        if sale.invoice_set.all().count() > 0:
                            invoice_no = sale.invoice_set.all()[0].invoice_no
                        else:
                            invoice_no = sale.receipt_set.all()[0].receipt_no if sale.receipt_set.all().count() > 0 else sale.sales_invoice_number
                        canvas_paper.setFontSize(11)
                        canvas_paper.drawString(50, y1, sale.sales_invoice_date.strftime('%d/%m/%Y'))
                        canvas_paper.drawString(120, y1, str(invoice_no))
                        canvas_paper.drawString(170, y1, sale.transaction_reference_no)
                        data=[[Paragraph(sale.salesman.first_name + str(' ') + sale.salesman.last_name, para_style)]]
                        table = Table(data, colWidths=[150], rowHeights=100, style=style)      
                        table.wrapOn(canvas_paper, 200, 400)
                        table.drawOn(canvas_paper, 250, y1 - 10)
                        # canvas_paper.drawString(350, y1, sale.salesman.first_name + str(' ') + sale.salesman.last_name)
                        if sale.customer:
                            data=[[Paragraph(sale.customer.name, para_style)]]
                            table = Table(data, colWidths=[170], rowHeights=100, style=style)      
                            table.wrapOn(canvas_paper, 200, 400)
                            table.drawOn(canvas_paper, 400, y1 - 10)
                        else:
                            canvas_paper.drawString(400, y1, ' ')
                        canvas_paper.drawString(570, y1, sale.payment_mode)
                        canvas_paper.drawString(650, y1, str(sale.grant_total))
                        canvas_paper.drawString(730, y1, str(sale.discount))
                        canvas_paper.drawString(800, y1, str(total_tax))
                        canvas_paper.drawString(860, y1, str(sale.round_off))
                 
                        total_discount = float(total_discount) + float(sale.discount)
                        total = float(total) + float(sale.grant_total)
                        y1 = y1 - 30
                        if y1 < 270:
                            y1 = y - 50
                            canvas_paper.showPage()
                    canvas_paper.drawString(50, y1, 'Total Amount: ')
                    canvas_paper.drawString(140, y1, str(total))
                    canvas_paper.drawString(435, y1, str(total_discount))
                    canvas_paper.drawString(350, y1, 'Total Discount : ')
                    canvas_paper.showPage()
                    canvas_paper.save()
                    # response = HttpResponse(content_type='application/pdf')
                    # p = SimpleDocTemplate(response, pagesize=A4)
                    # elements = []
                    # data = []
                    # d = [['Sales Report - ' + start_date + ' - ' +end_date ]]
                    # t = Table(d, colWidths=(450), rowHeights=25, style=style)
                    # t.setStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    #             ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    #             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    #             ('FONTSIZE', (0,0), (-1,-1), 17),
                    #             ])   
                    # elements.append(t)
                    
                    # elements.append(Spacer(2, 5))
                    
                    # data.append(['Date', 'Invoice', 'Reference', 'Salesman', 'Customer', 'Payment', 'Total', 'Discount', 'Round off'])
                    # total_debit = 0
                    # total_credit = 0
                    # for sale in sales:
                    #     if sale.invoice_set.all().count() > 0:
                    #         invoice_no = sale.invoice_set.all()[0].invoice_no
                    #     else:
                    #         invoice_no = sale.receipt_set.all()[0].receipt_no if sale.receipt_set.all().count() > 0 else sale.sales_invoice_number
                    #     salesman = sale.salesman.first_name + ' ' + sale.salesman.last_name
                    #     data.append([sale.sales_invoice_date.strftime('%d/%m/%Y'), invoice_no, sale.transaction_reference_no, salesman, sale.customer.name, sale.payment_mode, sale.grant_total, sale.discount, sale.round_off])
                    # table = Table(data, colWidths=(60,50,55, 100, 100, 50, 50, 50, 60), rowHeights=25, style=style)
                    # table.setStyle([('ALIGN',(0,0),(-1,-1),'LEFT'),
                    #             ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                    #             ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    #             # ('BACKGROUND',(0, 0),(-1,-1),colors.HexColor('#EEEEEE')),
                    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    #             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    #             ('FONTNAME', (0, -1), (-1,-1), 'Helvetica'),
                    #             ('FONTSIZE', (0,0), (-1,-1), 10),
                    #             ])   
                    # elements.append(table)
                    # p.build(elements)     
                    return response
        else:
            return HttpResponseRedirect(reverse('dashboard'))

class EstimateEntry(View):

    def get(self, request, *args, **kwargs):
        if get_user_permission(request, 'sales_permission'):
            current_date = datetime.now().date()
            return render(request, 'estimate.html', {'current_date': current_date.strftime('%d/%m/%Y'),})
        else:
            return HttpResponseRedirect(reverse('dashboard'))

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            estimate_details = ast.literal_eval(request.POST['estimate_details'])
            
            try:
                estimate_no_already_exists = Estimate.objects.get(estimate_invoice_number=estimate_details['estimate_no']) 
                res = {
                    'result': 'error',
                    'message': 'estimate no already exists',
                }
            except:
                estimate = Estimate()           
                if estimate_details['bill_type'] == 'NonTaxable':
                    estimate.bill_type = 'Tax Exclusive'
                else:
                    estimate.bill_type = 'Tax Inclusive'
                if estimate_details['estimate_no']:
                    estimate.estimate_invoice_number = estimate_details['estimate_no']
                else:
                    invoice_no  = Estimate.objects.latest('id').id + 1
                    estimate.auto_invoice_number = "EST" + str(invoice_no)
                    estimate.estimate_invoice_number = estimate.auto_invoice_number
                estimate.estimate_invoice_date = datetime.strptime(estimate_details['estimate_date'], '%d/%m/%Y')
                estimate.do_number = estimate_details['do_no']
                # estimate.payment_mode = estimate_details['payment_mode']
                # if estimate_details['payment_mode'] == 'cheque':
                #     estimate.bank_name = estimate_details['bank_name']
                #     estimate.branch = estimate_details['branch']
                #     estimate.cheque_number = estimate_details['cheque_no']
                #     estimate.cheque_date = datetime.strptime(estimate_details['cheque_date'], '%d/%m/%Y')
                # elif estimate_details['payment_mode'] == 'card':
                #     estimate.bank_name = estimate_details['bank_name']
                #     estimate.card_holder_name = estimate_details['card_holder_name']
                #     estimate.card_number = estimate_details['card_no']
                salesman = Salesman.objects.get(id=estimate_details['salesman'])
                estimate.salesman = salesman
                if estimate_details['customer']:
                    customer = Customer.objects.get(id=estimate_details['customer'])
                    estimate.customer = customer
                estimate.discount = estimate_details['discount']
                estimate.grant_total = estimate_details['grant_total']
                estimate_items = estimate_details['items']
            
                estimate.save()
                for item in estimate_items:
                    estimate_item = EstimateItem()
                    estimate_item.estimate = estimate
                    item_obj = Item.objects.get(id=item['id'])
                    estimate_item.item = item_obj
                    batch_item = BatchItem.objects.get(batch__id=item['batch_id'], item__id=item['id'])
                    estimate_item.batch_item = batch_item
                    estimate_item.quantity = item['quantity']
                    estimate_item.uom = item['uom']
                    estimate_item.mrp = item['current_item_price']
                    estimate_item.net_amount = item['net_amount']
                    estimate_item.save()
                estimate.save()
                res = {
                    'estimate_details': estimate_details,
                    'result': 'ok',
                    'id': estimate.id,
                    }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')

class EstimatePdf(View):

    def get(self, request, *args, **kwargs):

        estimate_id = kwargs['estimate_id']
        estimate = Estimate.objects.get(id=estimate_id)
        response = HttpResponse(content_type='application/pdf')
        canvas_paper = canvas.Canvas(response, pagesize=(1000, 1250))
        y = 1150
        status_code = 200
        canvas_paper.setFontSize(15)
        canvas_paper.drawCentredString(500, y, 'Estimate - ' + estimate.estimate_invoice_number  )
        canvas_paper.drawString(770,  y - 120, 'Date:')
        canvas_paper.drawString(100,  y - 120, 'Estimate No...............................')

        canvas_paper.drawString(100, y - 140, 'Sold To.......................................................................................')
        # Table
        canvas_paper.line(150, y - 200, 875, y - 200)
        canvas_paper.line(150, y - 200, 150, y - 850) 
        canvas_paper.line(150, y - 250, 875, y - 250) 
        canvas_paper.line(250, y - 200, 250, y - 850)
        canvas_paper.line(450, y - 200, 450, y - 850)  
        canvas_paper.line(550, y - 200, 550, y - 850)
        canvas_paper.line(650, y - 200, 650, y - 850)
        canvas_paper.line(740, y - 200, 740, y - 850) 
        canvas_paper.line(875, y - 200, 875, y - 850) 
        canvas_paper.line(150, y - 850, 875, y - 850)
        # end table
        canvas_paper.drawString(180, y - 230, 'SL. No.')
        # canvas_paper.drawString(290, y-230, 'Sch.')
        canvas_paper.drawString(320, y - 230, 'Item Name ')
        canvas_paper.drawString(460, y-230, 'Rate of Tax')
        canvas_paper.drawString(570, y - 230, 'Quantity')
        canvas_paper.drawString(670, y - 230, 'Rate')
        canvas_paper.drawString(760, y - 230, 'Amount')

        canvas_paper.drawString(820,  y - 120, estimate.estimate_invoice_date.strftime('%d-%b-%Y'))
        canvas_paper.drawString(200,  y - 117, estimate.estimate_invoice_number)

        canvas_paper.drawString(180, y - 137, estimate.customer.name)
        i=0
        y1 = y - 280
        total_amount = 0
        for s_item in estimate.estimateitem_set.all():         
            if y1 <= 270:
                y1 = y - 280
                canvas_paper.showPage()
                canvas_paper = invoice_body_layout(canvas_paper, y, sales)
                
                canvas_paper.setFont('Helvetica', 10)
            i = i +1
            canvas_paper.drawString(160, y1, str(i))
            data=[[Paragraph(s_item.item.name, para_style)]]

            table = Table(data, colWidths=[100], rowHeights=100, style=style)      
            table.wrapOn(canvas_paper, 200, 400)
            table.drawOn(canvas_paper, 280, y1-10)

            if s_item.item.vat_type:
                tax_percentage = s_item.item.vat_type.tax_percentage
            else:
                tax_percentage = ''
            canvas_paper.drawString(480,y1, str(tax_percentage))
            canvas_paper.drawString(520, y1, '%')
            canvas_paper.drawString(570, y1, str(round(s_item.quantity,2)))
            canvas_paper.drawString(670, y1, str(round(s_item.mrp,2)))
            canvas_paper.drawString(760, y1, str(round(s_item.net_amount,2)))

            total_amount = total_amount + s_item.net_amount

            y1 = y1 - 30
        # total box
        canvas_paper.line(150, y - 1000, 875, y - 1000)

        
        canvas_paper.line(650, y - 850, 652, y - 1000)
        canvas_paper.line(150, y - 850, 150, y - 1000)
        canvas_paper.line(875, y - 850, 875, y - 1000)

        # total box end
        canvas_paper.drawString(660, y - 882, 'Rs')
        canvas_paper.drawString(680, y - 882, str(total_amount))
        canvas_paper.line(150, y - 827, 875, y - 827)
        # p.setFont("Helvetica-Bold", 30)  
        canvas_paper.drawString(165, y - 882, 'Total')
        canvas_paper.showPage()
        canvas_paper.save()
        return response

class EstimateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            estimate_invoice_number  = request.GET.get('estimate_no', '')
            ctx_estimate = {}
            if estimate_invoice_number:
                try:
                    estimate = Estimate.objects.get(estimate_invoice_number=estimate_invoice_number)
                    ctx_items = []
                    for e_item in estimate.estimateitem_set.all():
                        stock = float(e_item.quantity) 
                        
                        ctx_items.append({
                            'name': e_item.item.name,
                            'code': e_item.item.code,
                            'batch_name': e_item.batch_item.batch.name,
                            'stock': stock,
                            'tax_percentage': e_item.item.vat_type.tax_percentage if e_item.item.vat_type else '',
                            'mrp': e_item.mrp,
                            'stock_unit': e_item.uom,
                            'net_amount': e_item.net_amount,
                            'quantity': e_item.quantity,
                            
                        })
                    ctx_estimate.update({
                        'items': ctx_items,
                        'estimate_no': estimate.estimate_invoice_number,
                        'estimate_date': estimate.estimate_invoice_date.strftime('%d/%m/%Y'),
                        'payment_mode': estimate.payment_mode,
                        'discount': estimate.discount,
                        'grant_total': estimate.grant_total,
                        'do_no': estimate.do_number,
                        'bill_type': estimate.bill_type,
                        'salesman': estimate.salesman.first_name,
                        'customer':estimate.customer.name,
                    })
                    res = {
                        'estimate':ctx_estimate,
                        'result': 'ok',
                    }
                except Exception as ex:
                    print str(ex)
                    res = {
                        'result': 'error',
                        'message': 'No Estimate with this Invoice No',
                        'estimate':ctx_estimate,
                    }
                response = simplejson.dumps(res)
                return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'estimate_view.html', {})

class SalesView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            sales_invoice = request.GET.get('ref_no', '')
            sale = []
            ctx_sales = {}
            ctx_sales_items = []
            if sales_invoice:
                sales = Sale.objects.filter(Q(sales_invoice_number=sales_invoice)|Q(transaction_reference_no=sales_invoice))
                if len(sales) > 0:
                    for sale in sales:
                        sale = sale
            if len(sales) == 0:
                receipts = Receipt.objects.filter(Q(receipt_no=sales_invoice))
                if len(receipts) > 0:
                    for receipt in receipts:
                        sale = receipt.sales
            if len(sales) == 0 and len(receipts) == 0:
                invoices = Invoice.objects.filter(Q(invoice_no=sales_invoice))
                if len(invoices) > 0:
                    for invoice in invoices:
                        sale = invoice.sales
            if sale:
                sales_items = SalesItem.objects.filter(sales__id=sale.id)
                for sales_item in sales_items:
                    ctx_sales_items.append({
                        'id': sales_item.id,
                        'code': sales_item.batch_item.item.code,
                        'name': sales_item.batch_item.item.name,
                        'batch': sales_item.batch_item.batch.name,
                        'item_quantity': sales_item.quantity,
                        'uom': sales_item.uom,
                        'net_amount': sales_item.net_amount,
                        'tax': sales_item.batch_item.item.vat_type.tax_percentage if sales_item.batch_item.item.vat_type else '',
                        'mrp': sales_item.mrp,
                    }) 
                    if sale.bill_type == 'Invoice':
                        invoice = Invoice.objects.get(sales__id=sale.id)
                        ref_no = invoice.invoice_no
                    else:
                        receipt = Receipt.objects.get(sales__id=sale.id)
                        ref_no = receipt.receipt_no
                ctx_sales.update({
                    'id': sale.id,
                    'sales_invoice': sale.sales_invoice_number if sale.sales_invoice_number else ref_no,
                    'invoice_date': sale.sales_invoice_date.strftime('%d/%m/%Y'),
                    'customer': sale.customer.name if sale.customer else '',
                    'salesman': sale.salesman.first_name + " " + sale.salesman.last_name,
                    'discount': sale.discount,
                    'grant_total': sale.grant_total,
                    'items': ctx_sales_items,
                    'bill_type': sale.bill_type,
                    'do_no': sale.do_number,
                    'payment_mode': sale.payment_mode,
                    'bank_name': sale.bank_name if sale.bank_name else '',
                    'cheque_date': sale.cheque_date.strftime('%d/%m/%Y') if sale.cheque_date else '',
                    'cheque_number': sale.cheque_number if sale.cheque_number else '',
                    'branch': sale.branch if sale.branch else '',
                    'card_number': sale.card_number if sale.card_number else '',
                    'card_holder_name': sale.card_holder_name if sale.card_holder_name else '',
                    'round_off': sale.round_off,
                    'roundoff': sale.round_off,
                })
                ctx_sales_items = []
                res = {
                    'sales_view': ctx_sales,
                    'result': 'ok',
                }
            else:
                res = {
                    'message': 'No Sales found',
                    'result': 'error',
                }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'sales_view.html', {})


class SalesReturnView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            invoice_no = request.GET.get('ref_no', '')
            sale = []
            ctx_sales = {}
            ctx_sales_items = []
            try:    
                sales_return = SalesReturn.objects.get(return_invoice_number=invoice_no)
            except Exception as ex:
                try:
                    sales_return = SalesReturn.objects.get(transaction_reference_no=invoice_no)
                except:
                    res = {
                    'message': 'No Sales found',
                    'result': 'error',
                    }
                    response = simplejson.dumps(res)
                    return HttpResponse(response, status=200, mimetype='application/json')
            if sales_return:
                sales_items = sales_return.salesreturnitem_set.all()
                for item in sales_items:
                    ctx_sales_items.append({
                        'id': item.id,
                        'code': item.sales_item.batch_item.item.code,
                        'name': item.sales_item.batch_item.item.name,
                        'batch': item.sales_item.batch_item.batch.name,
                        'item_quantity': item.quantity,
                        'uom': item.uom,
                        'net_amount': item.net_amount,
                        'tax': item.sales_item.batch_item.item.vat_type.tax_percentage if item.sales_item.batch_item.item.vat_type else '',
                        'mrp': item.sales_item.mrp,
                    }) 
                ctx_sales.update({
                    'id': sales_return.id,
                    'sales_invoice': sales_return.return_invoice_number,
                    'invoice_date': sales_return.invoice_date.strftime('%d/%m/%Y'),
                    'customer': sales_return.sales.customer.name if sales_return.sales.customer else '',
                    'salesman': sales_return.sales.salesman.first_name + " " + sales_return.sales.salesman.last_name,
                    'grant_total': sales_return.grant_total,
                    'items': ctx_sales_items,
                    'bill_type': sales_return.sales.bill_type,
                    'do_no': sales_return.sales.do_number,
                    'payment_mode': sales_return.sales.payment_mode,
                    'bank_name': sales_return.sales.bank_name if sales_return.sales.bank_name else '',
                    'cheque_date': sales_return.sales.cheque_date.strftime('%d/%m/%Y') if sales_return.sales.cheque_date else '',
                    'cheque_number': sales_return.sales.cheque_number if sales_return.sales.cheque_number else '',
                    'branch': sales_return.sales.branch if sales_return.sales.branch else '',
                    'card_number': sales_return.sales.card_number if sales_return.sales.card_number else '',
                    'card_holder_name': sales_return.sales.card_holder_name if sales_return.sales.card_holder_name else '',
                    'round_off': sales_return.sales.round_off,
                    'roundoff': sales_return.sales.round_off,
                })
                ctx_sales_items = []
                res = {
                    'sales_view': ctx_sales,
                    'result': 'ok',
                }
            else:
                res = {
                    'message': 'No Sales found',
                    'result': 'error',
                }
            response = simplejson.dumps(res)
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'sales_return_view.html', {})


class ChangeSalesDiscount(View):

    def post(self, request, *args, **kwargs):

        sales = Sale.objects.get(id=request.POST['sales_id'])
        round_off = request.POST['round_off']
        old_grant_total = sales.grant_total
        sales.grant_total = (float(sales.grant_total) + float(sales.round_off)) - float(round_off)
        transactions = Transaction.objects.filter(transaction_ref=sales.transaction_reference_no)
        stock = Ledger.objects.get(name="Stock")
        tax = Ledger.objects.get(name="Output Vat (sales)")
        sales.save()
        for transaction in transactions:
            stock_tax_transaction = False
            if transaction.debit_ledger:
                if transaction.debit_ledger.ledger == stock or transaction.debit_ledger.ledger == tax:
                    stock_tax_transaction = True
            if transaction.credit_ledger:
                if transaction.credit_ledger.ledger == stock or transaction.credit_ledger.ledger == tax:
                    stock_tax_transaction = True
            if not stock_tax_transaction:
                transaction.debit_amount = (float(transaction.debit_amount) + float(sales.round_off)) - float(round_off)
                transaction.credit_amount = (float(transaction.credit_amount) + float(sales.round_off)) - float(round_off)
                if transaction.debit_ledger:
                    transaction.debit_ledger.debit_amount = transaction.debit_amount
                    transaction.debit_ledger.ledger.balance = (float(transaction.debit_ledger.ledger.balance) + float(sales.round_off)) - float(round_off)
                    transaction.debit_ledger.ledger.save()
                    transaction.debit_ledger.save()
                else:
                    transaction.credit_ledger.credit_amount = transaction.credit_amount
                    transaction.credit_ledger.ledger.balance = (float(transaction.credit_ledger.ledger.balance) + float(sales.round_off)) - float(round_off)
                    transaction.credit_ledger.ledger.save()
                    transaction.credit_ledger.save()
                transaction.save()
        sales.round_off = float(round_off)
        sales.save()
        res = {
            'result': 'ok',
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')