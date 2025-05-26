import os
import jwt
import boto3
from typing import Dict, Optional

dynamodb = boto3.resource('dynamodb')
api_keys_table = dynamodb.Table(os.environ['API_KEYS_TABLE'])


class AuthContext:
    def __init__(self, api_key: str, user_id: Optional[str] = None,
                 organization_id: Optional[str] = None, rate_limit_quota=100):
        self.api_key = api_key
        self.user_id = user_id
        self.organization_id = organization_id
        self.rate_limit_quota = rate_limit_quota


def authenticate(event: Dict) -> AuthContext:
    headers = event.get('headers', {})
    api_key = headers.get('x-api_key')

    if not api_key:
        raise ValueError('Missing API key')
    response = api_keys_table.get_item(Key={'api_key': api_key})
    key_data = response.get('Item')

    if not key_data or not key_data.get('active'):
        raise ValueError('Invalid API key')

    auth_context = AuthContext(
        api_key=api_key,
        organization_id=key_data.get('organization_id'),
        rate_limit_quota=key_data.get('rate_limit_quota', 100)
    )

    auth_header = headers.get('authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        try:
            decoded = jwt.decode(
                token, os.environ['JWT_SECRET'], algorithms=['HS256'])
            auth_context.user_id = decoded.get('user_id')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid JWT token')
    return auth_context
