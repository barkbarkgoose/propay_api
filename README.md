# propay_api
python REST API functions for the Propay payment sphere

# required global variables
put the following code into a settings file and adjust the import at the top of propay.py to match accordingly
```
# ----------------------------------- PROPAY -----------------------------------
PROTECTPAY_PAYER_API = 'https://api.propay.com/ProtectPay/Payers/'
PROTECTPAY_TRANSACTION_API = 'https://api.propay.com/ProtectPay/HostedTransactions/'
PROTECTPAY_TRANSACTION_INFO = 'https://api.propay.com/protectpay/HostedTransactionResults/'
PROTECTPAY_PAYMENT_URL = 'https://protectpay.propay.com/hpp/v2/'
PROTECTPAY_VOID_API = 'https://api.propay.com/protectpay/VoidedTransactions/'

BILLER_ID = '<biller_id>'   # propay assigns
AUTH_TOKEN = '<auth_token'  # propay assigns

CSS_URL = 'https://protectpaytest.propay.com/hpp/css/pmi.css'
RETURN_URL = '<url_to_return_to_after_card_process>'
MERCHANT_PROFILE_ID = '<your_id_here>'


#  ------------------------ TEST URL's AND CREDENTIALS --------------------------
TEST_PROTECTPAY_PAYER_API = 'https://xmltestapi.propay.com/ProtectPay/Payers/'
TEST_PROTECTPAY_TRANSACTION_API = 'https://xmltestapi.propay.com/ProtectPay/HostedTransactions/'
TEST_PROTECTPAY_PAYMENT_URL = 'https://protectpaytest.propay.com/hpp/v2/'

TEST_BILLER_ID = '7310599495234916'
TEST_AUTH_TOKEN = '2a44f9bd-d3c6-40e0-8988-7c1853e13396'

TEST_BILLER_ID2 = '9999986379225246'
TEST_AUTH_TOKEN2 = '16dfe8d7-889b-4380-925f-9c2c6ea4d930'
```
**propay has not been helpful in trying to set up proper tests, support for developers is basically non-existent. If you have the misfortune of working with them you'll likely need to use the same credentials that you will in production.**

# notes
this is not an exact copy of the code used in production.  Make sure you test all the urls and have your own biller ID and auth token handy when setting this up.

most of the functions in propay.py take an _account_ instance as a parameter, that is used to store the first_name, last_name, payer_account_id, address, city, state, zip, card, hostedtransactionidentifier and transid.  You can replace that object with a dictionary or your own model/class as needed.

