import boto3
import json

def lambda_handler(event, context):
    print(f"Event received by Lambda: {event}")
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('HW10-Account-List')

    account_number = event.get('account')
    if not account_number:
        print("Account number is missing from the event.")
        raise Exception("Account number is missing from the event.")

    response = table.get_item(Key={'account': account_number})
    if 'Item' not in response:
        print("Account does not exist.")
        raise Exception("AccountNotFoundException")  
    # Get the transaction type from the event
    transaction_type = event.get('type', 'unknown')
    
    # Check the type of transaction and set the appropriate amount
    if transaction_type == "dep":
        amount = event.get('amount', 0)  # Default to 0 if no amount provided
        transaction_detail = "Deposit Amount"
    elif transaction_type == "wtd":
        amount = event.get('amount', 0)  # Default to 0 if no amount provided
        transaction_detail = "Withdrawal Amount"
    else:
        print("Unknown transaction type.")
        raise Exception("InvalidTransactionType")  # Handle unknown transaction types

    # Log the transaction details
    print(f"Account Number: {account_number}, Transaction Type: {transaction_type}, {transaction_detail}: {amount}")

    return {
        'account_exists': True,
        'account': account_number,
        'type': transaction_type,
        'amount': amount
    }
