from abc import ABC, abstractmethod
import boto3
import json
import logging

your_profile_name = "pkawsazurelogin"   # Replace with your AWS profile name
your_region_name = "us-east-1"  # Replace with your desired region

def create_conversation(user: str, user_message: str):
    """
    Creates a conversation dictionary with the user's message.
    """
    return [
        {
            "role": user,
            "content": [{"text": user_message}],
        }
    ]


class BedrockInvoker:
    """
    Utility class for invoking Bedrock models.
    """
    def __init__(self, profile_name, region_name, inference_profile_arn=None):
        self.session = boto3.Session(profile_name=profile_name)
        self.bedrock_runtime = self.session.client('bedrock-runtime', region_name=region_name)
        self.inference_profile_arn = inference_profile_arn

    def invoke_model(self, model_id, prompt, max_tokens=512, temperature=0.1, stop_sequences=None, user_message=None):
        if stop_sequences is None:
            stop_sequences = []
        
        # Prepare the request body
        body = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop_sequences": stop_sequences,
        }

        # Add user_message if provided
        if user_message:
            body["user_message"] = user_message

        response = self.bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body).encode('utf-8'),
            contentType="application/json"
        )
        return json.loads(response['body'].read().decode('utf-8'))['generations'][0]['text']
    


class ModelInvoker(ABC):
    """
    Abstract base class for model invocation strategies.
    """
    @abstractmethod
    def invoke(self, prompt: str, max_tokens: int, temperature: float, stop_sequences: list) -> str:
        pass


class CohereInvoker(ModelInvoker):
    def __init__(self):
        self.bedrock_invoker = BedrockInvoker(profile_name=your_profile_name, region_name=your_region_name)

    def invoke(self, prompt: str, max_tokens: int, temperature: float, stop_sequences: list) -> str:
        logging.info("Invoking Cohere model...")
        return self.bedrock_invoker.invoke_model(
            model_id="cohere.command-text-v14",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences
        )


class ClaudeInvoker(ModelInvoker):
    def __init__(self):
        self.bedrock_invoker = BedrockInvoker(
            profile_name=your_profile_name,
            region_name=your_region_name,
            # inference_profile_arn="arn:aws:bedrock:us-east-1:123456789012:inference-profile/your-inference-profile"
        )

    def invoke(self, prompt: str, max_tokens: int, temperature: float, stop_sequences: list) -> str:
        logging.info("Invoking Claude model...")

        # Create the conversation object
        conversation = create_conversation(user="user", user_message=prompt)

        # Prepare the inference configuration
        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.9
        }

        # Call the Claude model using the `converse` API
        try:
            response = self.bedrock_invoker.bedrock_runtime.converse(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                messages=conversation,
                inferenceConfig=inference_config
            )

            # Extract and return the response text
            response_text = response["output"]["message"]["content"][0]["text"]
            return response_text

        except Exception as e:
            logging.error(f"Claude model invocation failed: {e}")
            raise Exception(f"Claude model invocation failed: {e}")


class OpenAIInvoker(ModelInvoker):
    def __init__(self):
        self.bedrock_invoker = BedrockInvoker(profile_name="your-profile-name", region_name="your-region-name")

    def invoke(self, prompt: str, max_tokens: int, temperature: float, stop_sequences: list) -> str:
        logging.info("Invoking OpenAI model...")
        return self.bedrock_invoker.invoke_model(
            model_id="openai.gpt-4",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences
        )


def get_model_invoker(model_type: str) -> ModelInvoker:
    """
    Factory function to return the appropriate model invoker based on the model type.
    """
    if model_type == "cohere":
        return CohereInvoker()
    elif model_type == "claude":
        return ClaudeInvoker()
    elif model_type == "openai":
        return OpenAIInvoker()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")