"""Gemini extractor implementation using image data for the example pipeline."""

import os

import mlflow
from document_extraction_tools.base import BaseExtractor
from document_extraction_tools.config import (
    EvaluationPipelineConfig,
    ExtractionPipelineConfig,
)
from document_extraction_tools.types import (
    Document,
    ExtractionResult,
    ExtractionSchema,
    ImageData,
    PipelineContext,
)
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from document_extraction_examples.simple_lease_extraction.config.gemini_image_extractor_config import (
    GeminiImageExtractorConfig,
)


class GeminiImageExtractor(BaseExtractor):
    """Extracts lease data from images using the Gemini API."""

    def __init__(
        self,
        config: (
            GeminiImageExtractorConfig
            | ExtractionPipelineConfig
            | EvaluationPipelineConfig
        ),
    ) -> None:
        """Initialize the extractor and client."""
        super().__init__(config)

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Set GEMINI_API_KEY in the environment.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = self.config.model_name

        self.prompt = mlflow.genai.load_prompt(
            f"prompts:/{self.config.mlflow_prompt_name}/{self.config.mlflow_prompt_version}"
        ).format()

    @retry(
        retry=retry_if_exception_type(ServerError),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        stop=stop_after_attempt(10),
    )
    @mlflow.trace(name="extract_from_images", span_type="LLM")
    async def extract(
        self,
        document: Document,
        schema: type[ExtractionSchema],
        context: PipelineContext | None = None,
    ) -> ExtractionResult[ExtractionSchema]:
        """Run extraction against the Gemini API."""
        _ = context  # Required by BaseExtractor; reserved for future metadata.
        span = mlflow.get_current_active_span()
        if span:
            span.set_inputs(
                {
                    "document_id": document.id,
                    "prompt": self.prompt,
                    "model_name": self.model_name,
                }
            )

        contents = []

        contents.append(self.prompt)

        for page in document.pages:
            if isinstance(page.data, ImageData):
                contents.append(
                    types.Part.from_bytes(
                        data=page.data.content, mime_type="image/jpeg"
                    )
                )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        return ExtractionResult(data=response.parsed)
