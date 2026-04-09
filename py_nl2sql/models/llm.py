"""
Author: pillar
Date: 2024-08-30
Description: prompts
Note: Different languages should use prompts that are appropriate for that language.
"""

import json

from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv
from py_nl2sql.constants.type import LLMModel
from py_nl2sql.utilities.tools import batch_image_to_base64

# 确保加载 .env 文件（覆盖系统环境变量）
load_dotenv(find_dotenv(), override=True)


class LLM:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        # OpenRouter 需要的额外 headers（可选，但有助于使用分析）
        default_headers = {
            "HTTP-Referer": "https://github.com/pillarliang/py-nl2sql",
            "X-Title": "py-nl2sql"
        }
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers=default_headers
        )

    def get_response(self, query: str):
        completion = self.client.chat.completions.create(
            model=LLMModel.Default,
            messages=[
                {"role": "user", "content": query},
            ],
        )
        return completion.choices[0].message.content

    def get_structured_response(self, query: str, response_format):
        """
        Get structured response from LLM.
        For OpenRouter compatibility, tries beta API first, falls back to JSON mode.
        """
        try:
            # Try beta API first (works with OpenAI, may not work with OpenRouter)
            completion = self.client.beta.chat.completions.parse(
                model=LLMModel.Default.value,
                messages=[{"role": "user", "content": query}],
                response_format=response_format,
            )
            print(completion)
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            # Fallback to JSON mode if beta API is not supported
            # This is common with OpenRouter and other OpenAI-compatible APIs
            import inspect
            from pydantic import BaseModel
            
            # Get the schema from the response_format (Pydantic model)
            if inspect.isclass(response_format) and issubclass(response_format, BaseModel):
                schema = response_format.model_json_schema()
            else:
                schema = response_format
            
            # Create a prompt that requests JSON output
            json_prompt = f"""{query}

Please respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Respond only with the JSON object, no other text."""
            
            completion = self.client.chat.completions.create(
                model=LLMModel.Default.value,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that responds only with valid JSON matching the requested schema."
                    },
                    {"role": "user", "content": json_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            content = completion.choices[0].message.content
            # Parse the JSON response
            parsed = json.loads(content)
            
            # If response_format is a Pydantic model, validate it
            if inspect.isclass(response_format) and issubclass(response_format, BaseModel):
                return response_format(**parsed).model_dump()
            return parsed

    def get_multimodal_response(self, query: str, contexts):
        texts = contexts.get("texts", "")
        images = contexts.get("images", "")
        encoded_images = batch_image_to_base64(images)

        prompts = f"""
        Please answer the following query based on the provided context and image information, rather than prior knowledge. 
        If the context cannot answer the question, please return: 暂找不到相关问题，请重新提供问题。
        
        Question: {query}
        
        Context: {texts}
        """

        messages = [{"type": "text", "text": prompts}]
        for item in encoded_images:
            messages.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{item}"}})

        completion = self.client.chat.completions.create(
            model=LLMModel.GPT_4o_mini,
            messages=[
                {"role": "user", "content": messages},
            ],
        )
        return completion.choices[0].message.content

    @property
    def embedding_model(self):
        """
        Get embedding model instance.
        Uses OpenRouter-compatible model name format: openai/text-embedding-ada-002
        """
        return OpenAIEmbeddings(
            api_key=self.api_key,
            base_url=self.base_url,
            model="openai/text-embedding-ada-002"  # OpenRouter format
        )
