import requests
import boto3
import time
from dynamodb_json import json_util

# Regular expression pattern to find URLs
API_GATEWAY_URL = "https://kfkc3v9702.execute-api.us-east-1.amazonaws.com/prod/transaction"
ACCOUNTS_TABLE = "HW10-Account-List"
DEPOSIT = "dep"
WITHDRAWAL = "wtd"
INVALID_ACCOUNT_NUMBER = "263826278362382"
WAIT_PERIOD = 3 # seconds
MAX_ACCOUNTS = 3 # Only test the first X accounts present in the Accounts table
accounts = []
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(ACCOUNTS_TABLE)

def load_account_list():
    ddbresponse = table.scan()
    for a in ddbresponse["Items"]:
        converted = json_util.loads(a)
        accounts.append(converted)
    print("Accounts: ", accounts)

def get_account_balance(acct):
    response = table.get_item(
        Key={
            'account': acct
        }
    )
    if "Item" in response:
        return json_util.loads(response["Item"]["balance"])
    else:
        print("*** No account found:", acct)
        return 0

def http_post(url, acct, amt, type):
    data = {"account": acct, "amount": amt, "type": type, "desc": "Automated test" }
    result = requests.post(url, json=data)
    if result.status_code != 200:
        print("**** HTTP error %d" % result.status_code)
    # print(result)

def deposit_funds(acct, amt):
    initial_balance = get_account_balance(acct)
    http_post(API_GATEWAY_URL, acct, amt, DEPOSIT)
    time.sleep(WAIT_PERIOD)    
    final_balance = get_account_balance(acct)
    print(" TEST: DEP %d into %s..... %d --> %d" % (amt, acct, initial_balance, final_balance))
    return final_balance == initial_balance + amt

def withdraw_funds(acct, amt):
    initial_balance = get_account_balance(acct)
    http_post(API_GATEWAY_URL, acct, amt, WITHDRAWAL)
    time.sleep(WAIT_PERIOD)    
    final_balance = get_account_balance(acct)
    print(" TEST: WTD ", amt, "from", acct, ".....", initial_balance, "-->", final_balance)
    return final_balance == initial_balance - amt

def test_simple_deposit():
    print("--------------------- SIMPLE DEPOSIT TESTS ---------------------")
    for a in accounts:
        assert deposit_funds(a["account"], 100)

def test_simple_withdrawal():
    print("--------------------- SIMPLE WITHDRAWAL TESTS ---------------------")
    for a in accounts:
        assert withdraw_funds(a["account"], 50)

def test_invalid_account():
    print("--------------------- INVALID ACCOUNT TESTS ---------------------")
    assert not deposit_funds(INVALID_ACCOUNT_NUMBER, 100)
    assert not withdraw_funds(INVALID_ACCOUNT_NUMBER, 100)

def test_insufficient_funds():
    print("--------------------- INSUFFICIENT FUNDS TESTS ---------------------")
    # Attempt to withdraw $100 more than the current balance
    assert not withdraw_funds(accounts[0]["account"], accounts[0]["balance"] + 100)

if __name__ == "__main__":
    load_account_list()
    test_simple_deposit()
    test_simple_withdrawal()
    test_invalid_account()
    test_insufficient_funds()
