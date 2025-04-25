import boto3
import json
from botocore.exceptions import ClientError

class BedrockInvoker:
    def __init__(self, profile_name, region_name):
        """
        Initializes the BedrockInvoker with the specified AWS profile and region.
        """
        self.session = boto3.Session(profile_name=profile_name)
        self.bedrock_runtime = self.session.client('bedrock-runtime', region_name=region_name)

    def invoke_model(self, model_id, prompt, max_tokens=512, temperature=0.1, stop_sequences=None):
        """
        Invokes the specified Bedrock model with the given prompt and parameters.
        """
        if stop_sequences is None:
            stop_sequences = []

        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stop_sequences": stop_sequences
                }).encode('utf-8'),
                contentType="application/json"
            )
            return json.loads(response['body'].read().decode('utf-8'))['generations'][0]['text']
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            return None