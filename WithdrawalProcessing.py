import boto3
from decimal import Decimal
from datetime import datetime
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
account_table = dynamodb.Table('HW10-Account-List')
transaction_log_table = dynamodb.Table('HW10-Transaction-Log')

def lambda_handler(event, context):
    print(f"Event received by Lambda: {event}")

    account_number = event.get('account')
    withdrawal_amount = event.get('withdrawal_amount')
    has_funds = event.get('has_funds', False)

    if not account_number or withdrawal_amount is None:
        error_message = "Account number or withdrawal amount is missing from the event."
        print(error_message)
        return {'errorMessage': error_message}

    try:
        withdrawal_amount = Decimal(str(withdrawal_amount))
    except (TypeError, ValueError):
        error_message = "Invalid withdrawal amount format. Amount must be a number."
        print(error_message)
        return {'errorMessage': error_message}

    if not has_funds:
        error_message = "Insufficient funds for the withdrawal."
        print(error_message)
        return {'errorMessage': error_message}

    # Attempt to update the account balance if sufficient funds are available
    try:
        response = account_table.update_item(
            Key={'account': account_number},
            UpdateExpression='SET balance = balance - :val',
            ExpressionAttributeValues={':val': withdrawal_amount},
            ReturnValues="UPDATED_NEW"
        )
        print(f"Updated balance: {response['Attributes']}")

        log_transaction(account_number, 'wtd', withdrawal_amount, "Withdrawal processed successfully")
        
        return response['Attributes']
    except ClientError as e:
        error_message = f"Error updating balance: {e.response['Error']['Message']}"
        print(error_message)
        return {'errorMessage': error_message}

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
