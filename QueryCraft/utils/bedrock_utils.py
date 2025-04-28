import boto3
import json

class BedrockInvoker:
    def __init__(self, profile_name, region_name):
        self.session = boto3.Session(profile_name=profile_name)
        self.bedrock_runtime = self.session.client('bedrock-runtime', region_name=region_name)

    def invoke_model(self, model_id, prompt, max_tokens=512, temperature=0.1, stop_sequences=None):
        if stop_sequences is None:
            stop_sequences = []
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