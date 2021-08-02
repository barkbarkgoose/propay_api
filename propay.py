import url_credentials as settings
import requests # for json to use Propay API
import json

# ------------------------------ PROPAY_API -------------------------------
def propay_api(request, return_url, account, plan):
    # this will work with the normal api url and credentials, but not the testing one?
    """
    calls the propay processes needed to create a propay session, process/store card

    account.ccard1
    account.transid
    account.price_code
    account.accttype
    account.authcode
    account.areacode1

    """

    if account.payer_account_id is None:
        r2 = requests.put(
            settings.PROTECTPAY_PAYER_API,
            auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
            # json={"Name":account.first_name +" "+ account.last_name,"Email":account.email,"ExternalID1":account.token},
            json={"Name":account.first_name +" "+ account.last_name,"ExternalID1":account.token},
            )

        if r2.json()['RequestResult']['ResultCode'] != '00':
            # --- couldn't authenticate, send to error page saying so ---
            pass

        # --- authenification passed, now redirect user to payment page ---
        PayerAccountId =  r2.json()['ExternalAccountID']
        account.payer_account_id = r2.json()['ExternalAccountID']
        account.save()


    transaction_data = {
        # "BillerAccountID" => env('BILLER_ID'),
        # "AuthorizationToken" : env('AUTH_TOKEN'),
        "PayerAccountId" : account.payer_account_id,
        # "MerchantProfileId" : '2305383',
        "MerchantProfileId" : settings.MERCHANT_PROFILE_ID, # ? faxpipe profile id ?
        "Amount" : plan['propay'],
        "CurrencyCode" : "USD",
        "InvoiceNumber" : "Account Signup",
        # "InvoiceNumber" : $decoded['HostedTransactionIdentifier'];
        "Comment1" : plan['description'],
        "CardHolderNameRequirementType" : 1,
        "SecurityCodeRequirementType" : 1,
        "AvsRequirementType" : 1,
        # "AuthOnly" : False,
        # "ProcessCard" : True,
        "StoreCard" : True,
        "OnlyStoreCardOnSuccessfulProcess" : False,
        "CssUrl" : settings.CSS_URL,
        "Address1" : account.address,
        "Address2" : '',
        "City" : account.city,
        "Country" : 'USA',
        "Description" : '',
        "Name" : account.first_name + ' ' + account.last_name,
        "State" : account.state,
        "ZipCode" : account.zip,
        "BillerIdentityId" : None,
        "CreationDate" : None,
        "HostedTransactionIdentifier" : None,
        # ?? key ??
        "ReturnURL" : return_url,
        "PaymentTypeId" : "0",
        "Protected" : False
    }

    if plan['type'] == 0:
        # --- plan zero, don't charge but take card ---
        transaction_data["AuthOnly"] = True
        transaction_data["ProcessCard"] = False
        transaction_data["InvoiceNumber"] = "Card Authorization"
    else:
        # --- regular signup ---
        transaction_data["AuthOnly"] = False
        transaction_data["ProcessCard"] = True
        transaction_data["OnlyStoreCardOnSuccessfulProcess"] = True

    # ---- create hosted transaction identifier ----
    r3 = requests.put(
        settings.PROTECTPAY_TRANSACTION_API,
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        json=transaction_data,
        )

    if r3.json()['Result']['ResultCode'] != '00':
        # --- couldn't authenticate, send to error page saying so ---
        message = "we were unable to authorize a transaction at this time, please notify support"
        return json.dumps({"errormessage":message})
        # pass

    account.hostedtransactionidentifier = r3.json()['HostedTransactionIdentifier']
    account.save()

    # ---- go to hosted payment page (hpp) ----
    # return redirect(env('API_URL') . $decoded['HostedTransactionIdentifier']);
    api_url = settings.PROTECTPAY_PAYMENT_URL + account.hostedtransactionidentifier

    return requests.get(api_url)

# ---------------------------- GET_TRANSACTION_DATA ----------------------------
def get_transaction_info(account):
    """
    connect to propay api to get info on specified transaction.
    first parameter is url: 'https://api.propay.com/protectpay/HostedTransactionResults/'
        + the transaction identifier saved in the account model.

    only other thing needed is verification info
    """
    resp = requests.get(
                settings.PROTECTPAY_TRANSACTION_INFO + account.hostedtransactionidentifier,
                auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
            )
    return resp.json()

# ------------------------------ VOID_TRANSACTION ------------------------------
def void_transaction(account):
    """
    connect to propay api and void a transaction that was placed for the given account
    """
    json_data = {
        "OriginalTransactionId":account.transid,
        "MerchantProfileId":settings.MERCHANT_PROFILE_ID,
        "Comment1":"voiding transaction for account " + str(account.id),
    }
    resp = requests.put(
        settings.PROTECTPAY_VOID_API,
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        json=json_data,
        )
    return resp.json()

# -------------------------------- UPDATE_PAYER --------------------------------
def update_payer_extID(account, newid):
    """
    connect to propay api and update what was used for the ExternalID
    """
    resp = requests.post(
        settings.PROTECTPAY_PAYER_API + account.payer_account_id,
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        json = {"ExternalID1": str(newid)},
    )
    return resp.json()

# ------------------------------- GET PAYER INFO -------------------------------
def get_payerId_details(identifier):
    """
    REQUEST PAYERID DETAILS FROM PROPAY
        - checks against externalId1 first, if that doesn't return anything then
          will check externalId2
        - if neither externalIds check out then will compare against name
        - returns a list of matching Payers

    EXAMPLE RESPONSE:
    {
        'RequestResult': {
            'ResultValue': 'SUCCESS', 'ResultCode': '00', 'ResultMessage': ''
        },
        'Payers': [{
            'payerAccountId': '################',
            'Name': 'Test Name',
            'ExternalId1': '65306',
            'ExternalId2': '################'
        }]
    }
    """
    url = settings.PROTECTPAY_PAYER_API
    query = f"?externalId1={identifier}"
    resp = requests.get(
        url + query,
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
    )
    # --- identifier didnt' match externalId1, check externalId2 ---
    if 'Payers' in resp.json() and len(resp.json()['Payers']) == 0:
        query = f"?externalId2={identifier}"
        resp = requests.get(
            url + query,
            auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        )
    # --- identifier didnt' match externalId2, check name ---
    if 'Payers' in resp.json() and len(resp.json()['Payers']) == 0:
        query = f"?name={identifier}"
        resp = requests.get(
            url + query,
            auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        )
    #
    return resp.json()

# ------------------------- GET PAYMENT METHOD DETIALS -------------------------
def get_paymentMethod_details(payerID):
    """
    """
    url = settings.PROTECTPAY_PAYER_API
    url += f"{payerID}/PaymentMethods"
    resp = requests.get(
        url,
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
    )
    return resp.json()

# -------------------------------- DELETE PAYER --------------------------------
def delete_payerID(payerID):
    """
    connect to propay api and delete payer with given payerID
    """
    resp = requests.delete(
        settings.PROTECTPAY_PAYER_API + str(payerID),
        auth=(settings.BILLER_ID, settings.AUTH_TOKEN),
        # json = {"ExternalID1": str(newid)},
    )
    return resp.json()

# -------------------------------------------------------------------------------
