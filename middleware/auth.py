import boto3
client = boto3.client('cognito-identity','ap-east-2')

def Auth(accessToken):
    try:
        user = client.get_user(
            AccessToken=accessToken
        )
        return {
            success: True,
            data: user
        }
    except ClientError as err:
        return {
            "error": err.response['Error']['Code'],
            "errormessage" : err.response['Error']['Message']
        }
    except Exception as e:
        return {
            "error": "INTERNAL_ERROR"
        }

