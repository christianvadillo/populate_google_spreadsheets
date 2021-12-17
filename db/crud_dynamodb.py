import boto3
import os

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()  # take environment variables from .env.

ERROR_HELP_STRINGS = {
    # Common Errors
    "InternalServerError": "Internal Server Error, generally safe to retry with exponential back-off",
    "ProvisionedThroughputExceededException": "Request rate is too high. If you're using a custom retry strategy make sure to retry with exponential back-off."
    + "Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index",
    "ResourceNotFoundException": "One of the tables was not found, verify table exists before retrying",
    "ServiceUnavailable": "Had trouble reaching DynamoDB. generally safe to retry with exponential back-off",
    "ThrottlingException": "Request denied due to throttling, generally safe to retry with exponential back-off",
    "UnrecognizedClientException": "The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying",
    "ValidationException": "The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying",
    "RequestLimitExceeded": "Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying",
}


def handle_error(error):
    error_code = error.response["Error"]["Code"]
    error_message = error.response["Error"]["Message"]
    error_help_string = ERROR_HELP_STRINGS[error_code]

    print(
        "[{error_code}] {help_string}. Error message: {error_message}".format(
            error_code=error_code,
            help_string=error_help_string,
            error_message=error_message,
        )
    )


def _squeeze_dicts(d: Dict) -> Dict:
    """
    Flatten a dictionary.
    """
    return {k: list(v.values())[0] for k, v in d.items()}


def get_trial_groups() -> List[Dict]:
    # dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
    dynamodb_client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION"))
    # table = dynamodb.Table(os.getenv('AWS_TABLE_NAME'))

    scan_inputs = {
        "TableName": os.getenv("AWS_TABLE_NAME"),
        "IndexName": os.getenv("AWS_INDEX_NAME"),
        "FilterExpression": "begins_with(#7cd00, :7cd00) And #7cd01 = :7cd01",
        "ExpressionAttributeNames": {"#7cd00": "Etiqueta", "#7cd01": "Vigente"},
        "ExpressionAttributeValues": {
            ":7cd00": {"S": "Prueba"},
            ":7cd01": {"BOOL": True},
        },
    }

    try:
        response = dynamodb_client.scan(**scan_inputs)
        print("Scan successful.")
        # Handle response
    except ClientError as error:
        handle_error(error)
    except BaseException as error:
        print("Unknown error while scanning: " + error.response["Error"]["Message"])

    return [_squeeze_dicts(record) for record in response["Items"]]


# if __name__ == "__main__":
#     items = query_trial_groups()
#     import pdb

#     pdb.set_trace()
