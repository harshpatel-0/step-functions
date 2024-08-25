import boto3
from decimal import Decimal

def lambda_handler(event, context):
    print(f"Event received by Lambda: {event}")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('HW10-Account-List')
    account_number = event.get('account')
    withdrawal_amount = event.get('amount')

    if not withdrawal_amount:
        print("The withdrawal amount is missing from the event.")
        raise ValueError("Account number or withdrawal amount is missing from the event.")
    
    try:
        withdrawal_amount = Decimal(str(withdrawal_amount))
    except (TypeError, ValueError):
        print("Invalid withdrawal amount format.")
        raise ValueError("Invalid withdrawal amount format. Amount must be a number.")

    response = table.get_item(Key={'account': account_number})
    item = response.get('Item')
    if not item:
        print(f"Account {account_number} not found.")
        raise ValueError(f"Account {account_number} not found.")

    current_balance = item.get('balance')
    if current_balance is None:
        print("Current balance not available.")
        raise ValueError("Current balance not available.")

    current_balance = Decimal(current_balance)
    has_funds = current_balance >= withdrawal_amount
    print(f"Transaction status: {'approved' if has_funds else 'rejected due to insufficient funds'} for Account {account_number}")

    return {
        'has_funds': has_funds,
        'account': account_number,
        'current_balance': str(current_balance),
        'withdrawal_amount': str(withdrawal_amount)
    }
