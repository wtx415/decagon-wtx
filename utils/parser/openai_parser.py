from typing import List, Optional
import json


# Third-party packages
from openai import OpenAI, Completion

# custom packages
from utils.schema import Chunk


class OpenAIParser:
    DEFAULT_PROMPT_TEMPLATE = """
        Please parse the given HTML content to extract the text content and return a list of chunks.
        As you do this, please following the following rules:
            - As you create chunks, ensure that the similar text content in the same area is grouped together.
            - Ignore any non-text content such as images, videos, and other media.
            - Remove any extra html tags and attributes.
            - Ensure that the text content is properly formatted and does not contain any extra spaces or newlines.
            - Each chunk should not exceed chunk size of {chunk_size_limit} characters.
            - However, if list items are present, they should be grouped into a single chunk and they can ignore the
             chunk size limit. Remember, this is a very important rule and must be followed.
            - Output the chunks in JSON format with the key of `results` and value being a list of strings.
    """

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = "gpt-4o-mini",
        prompt: Optional[str] = None,
        chunk_size: Optional[int] = 750,
        chunk_size_buffer: Optional[int] = 30,
    ):
        if prompt is None:
            prompt = self._get_default_prompt(chunk_size, chunk_size_buffer)

        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.chunk_size = chunk_size
        self.chunk_size_buffer = chunk_size_buffer
        self.prompt = prompt

    def _get_default_prompt(self, chunk_size: int, chunk_size_buffer: int):
        return self.DEFAULT_PROMPT_TEMPLATE.format(
            chunk_size_limit=chunk_size + chunk_size_buffer
        )

    def _make_request(self, text: str) -> Completion:
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"{self.prompt}"},
                {"role": "user", "content": text},
            ],
        )
        return response

    def _convert_response_to_chunks(
        self, response: Completion, url: str
    ) -> List[Chunk]:
        content_raw = response.choices[0].message.content
        content_json = json.loads(content_raw)
        results = content_json["results"]

        chunks = []
        for result in results:
            chunk = Chunk(result, metadata={"url": url})
            chunks.append(chunk)

        return chunks

    def parse(self, text: str, url: str):
        """Parse the given HTML content to extract the text content and return a list of chunks using OpenAI API."""
        response = self._make_request(text)
        return self._convert_response_to_chunks(response, url)
