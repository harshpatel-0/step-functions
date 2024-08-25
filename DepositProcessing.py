import boto3
from decimal import Decimal
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb')
account_table = dynamodb.Table('HW10-Account-List')
transaction_log_table = dynamodb.Table('HW10-Transaction-Log')

def lambda_handler(event, context):
    print(f"Event received by Lambda: {event}")

    account_number = event.get('account')
    deposit_amount = event.get('amount')
    description = event.get('desc', 'Deposit without description')  # Optional description

    # Convert to Decimal
    try:
        deposit_amount = Decimal(str(deposit_amount))
    except (TypeError, ValueError):
        print("Invalid amount format. Amount must be a number.")
        return {
            'errorMessage': "Invalid amount format. Amount must be a number."
        }

    if account_number is None or deposit_amount is None:
        print("Account number or amount is missing from the event.")
        return {
            'errorMessage': "Account number or amount is missing from the event."
        }

    # Fetch the current account item to check if it exists and has a balance attribute
    current_account = account_table.get_item(Key={'account': account_number})
    if 'Item' not in current_account or 'balance' not in current_account['Item']:
        print(f"Account {account_number} does not exist or has no balance attribute.")
        return {
            'errorMessage': f"Account {account_number} does not exist or has no balance attribute."
        }

    try:
        response = account_table.update_item(
            Key={'account': account_number},
            UpdateExpression='SET balance = balance + :val',
            ExpressionAttributeValues={':val': deposit_amount},
            ReturnValues="UPDATED_NEW"
        )
        print(f"DynamoDB update response: {response}")
        
        log_transaction(account_number, 'dep', deposit_amount, description)
        
        return response['Attributes']
    except Exception as e:
        print(f"Error updating DynamoDB: {str(e)}")
        return {'errorMessage': str(e)}

def log_transaction(account_number, transaction_type, amount, description):
    transaction_log_table.put_item(
        Item={
            'transactionId': str(uuid.uuid4()),
            'account': account_number,
            'type': transaction_type,
            'amount': str(amount),  
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'description': description
        }
    )
    print(f"Logged {transaction_type} transaction for account {account_number}")
