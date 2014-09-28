
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from accounting.views import Ledgers, AddLedger, DeleteLedger, SubledgerDetails, \
	LedgerSubledgerList, DeleteSubLedger, SearchLedger, LedgerTreeView,  \
	CreatePayment, CreateReceipt, OtherTransaction, OpeningBalance, LedgerReport, \
	DayBook, CashBook, BankBook, BankAccountDetails, LedgerBalance, TrialBalance, \
	ProfitAndLossStatement, BalanceSheet


urlpatterns = patterns('',
	url(r'^ledgers/$', login_required(Ledgers.as_view(), login_url='/login/'),name='ledgers'),
	url(r'^add_ledger/$', login_required(AddLedger.as_view(), login_url='/login/'),name='add_ledger'),
	url(r'^delete_ledger/$', login_required(DeleteLedger.as_view(), login_url='/login/'),name='delete_ledger'),
	url(r'^subledger_details/(?P<ledger_id>\d+)/$', login_required(SubledgerDetails.as_view(), login_url='/login/'), name='subledger_details'),
	url(r'^subledger_list/(?P<ledger_id>\d+)/$', login_required(LedgerSubledgerList.as_view(), login_url='/login/'), name='subledger_list'),
	url(r'^delete_subledger/$', login_required(DeleteSubLedger.as_view(), login_url='/login/'),name='delete_subledger'),
	url(r'^search_ledger/$', login_required(SearchLedger.as_view(), login_url='/login/'), name='search_ledger'),
	url(r'^ledgers_tree_view/$', login_required(LedgerTreeView.as_view(), login_url='/login/'),name='ledgers_tree_view'),

	url(r'^create_payment/$', login_required(CreatePayment.as_view(), login_url='/login/'),name='create_payment'),
	url(r'^create_receipt/$', login_required(CreateReceipt.as_view(), login_url='/login/'),name='create_receipt'),
	url(r'^other_transaction/$', login_required(OtherTransaction.as_view(), login_url='/login/'),name='other_transaction'),
	url(r'^opening_balance/$', login_required(OpeningBalance.as_view(), login_url='/login/'),name='opening_balance'),
	url(r'^ledger_balance/$', login_required(LedgerBalance.as_view(), login_url='/login/'),name='ledger_balance'),


	url(r'^ledger_report/$', login_required(LedgerReport.as_view(), login_url='/login/'),name='ledger_report'),


	url(r'^opening_balance/$', login_required(OpeningBalance.as_view(), login_url='/login/'),name='opening_balance'),
	url(r'^day_book/$', login_required(DayBook.as_view(), login_url='/login/'),name='day_book'),
	url(r'^cash_book/$', login_required(CashBook.as_view(), login_url='/login/'),name='cash_book'),
	url(r'^bank_book/$', login_required(BankBook.as_view(), login_url='/login/'),name='bank_book'),

	url(r'^bank_accounts/$', login_required(BankAccountDetails.as_view(), login_url='/login/'), name='bank_accounts'),
	url(r'^trial_balance/$', login_required(TrialBalance.as_view(), login_url='/login/'), name='trial_balance'),
	url(r'^profit_and_loss_statement/$', login_required(ProfitAndLossStatement.as_view(), login_url='/login/'), name='profit_and_loss_statement'),
	url(r'^balance_sheet/$', login_required(BalanceSheet.as_view(), login_url='/login/'), name='balance_sheet'),
) 