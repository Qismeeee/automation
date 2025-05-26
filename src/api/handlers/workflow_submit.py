import json
import uuid
import os
import boto3
from datetime import datetime

from ..middleware.auth import authenticate
from ..middleware.rate_limiter import check_rate_limit
from ..schemas.workflow import validate_workflow
from ..utils.response import create_response

stepfunctions = boto3.client('stepfunctions')
STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']


def handler(event, context):
    try:
        auth_context = authenticate(event)

        rate_limit_result = check_rate_limit(
            f"rate-limit:{auth_context.api_key}",
            auth_context.rate_limit_quota
        )

        if not rate_limit_result['allowed']:
            return create_response(429, {
                'error': 'Rate limit exceeded',
                'remaining': rate_limit_result['remaining'],
                'reset_at': rate_limit_result['reset_at']
            })

        body = json.loads(event.get('body', '{}'))

        is_valid, error_message = validate_workflow(body)
        if not is_valid:
            return create_response(400, {
                'error': 'Invalid workflow format',
                'details': error_message
            })

        execution_id = str(uuid.uuid4())
        execution_name = f"{body['workflow_id']}-{execution_id}"

        stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=execution_name,
            input=json.dumps({
                'execution_id': execution_id,
                'workflow': body,
                'context': {
                    'api_key': auth_context.api_key,
                    'user_id': auth_context.user_id,
                    'organization_id': auth_context.organization_id,
                    'started_at': datetime.utcnow().isoformat()
                }
            })
        )

        return create_response(202, {
            'execution_id': execution_id,
            'status': 'accepted',
            'estimated_duration': estimate_execution_time(body),
            'message': 'Workflow submitted successfully'
        }, headers={
            'X-RateLimit-Remaining': str(rate_limit_result['remaining']),
            'X-RateLimit-Reset': rate_limit_result['reset_at']
        })

    except ValueError as e:
        if 'API key' in str(e) or 'JWT' in str(e):
            return create_response(401, {'error': 'Unauthorized'})
        return create_response(400, {'error': str(e)})
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


def estimate_execution_time(workflow):
    base_time = 5
    per_step_time = 2
    ai_multiplier = 1.5 if workflow.get(
        'config', {}).get('ai_assisted', True) else 1

    return int((base_time + len(workflow['steps']) * per_step_time) * ai_multiplier)
