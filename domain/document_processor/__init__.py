import os
from typing import Optional

from llama_parse import LlamaParse

LAMA_PARSE_API_KEY = os.getenv('LAMA_PARSE_API_KEY')

parser = LlamaParse(
    api_key=LAMA_PARSE_API_KEY,  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown",  # "markdown" and "text" are available
    num_workers=1,  # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="en",  # Optionally you can define a language, default=en
)


def extract_from_document(document_file_path: str) -> Optional[str]:
    """
    Extracts text from document provided.
    :param document_file_path:
    :return:
    """
    documents = parser.load_data(document_file_path)
    if documents:
        return documents[0].text
    else:
        return None