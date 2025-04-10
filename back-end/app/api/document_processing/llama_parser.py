from llama_parse import LlamaParse
from typing import Dict, Any, List
import re
from dotenv import load_dotenv
import os


class DocumentParser:
    def __init__(self, api_key: str):
        load_dotenv()
        print("Available environment variables:", [k for k in os.environ.keys()])

        api_key = os.getenv('LLAMA_CLOUD_API_KEY')
        if not api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY environment variable is not set")

        self.parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
            num_workers=4,
            verbose=True,
            language="en"
        )
    
    async def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document using LlamaParse's OCR and structured parsing
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing structured document data
        """
        try:
            documents = await self.parser.aload_data(file_path)
            return self._structure_output(documents)
        except Exception as e:
            raise Exception(f"Error parsing document: {str(e)}")
    
    def _structure_output(self, parsed_data: List) -> Dict[str, Any]:
        """
        Structure the parsed data from LlamaParse into sections and metadata.
        """
        structured_docs = []

        for doc in parsed_data:
            text = doc.text
            metadata = doc.metadata

            # Basic section splitting using markdown headers
            sections = self._split_into_sections(text)

            structured_docs.append({
                "content": text,
                "metadata": metadata,
                "sections": sections,
                "tables": []  # Tables not extracted by LlamaParse by default
            })

        return {"documents": structured_docs}

    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits markdown content into sections based on headers.
        """
        pattern = r"(#+ .+)"
        parts = re.split(pattern, text)
        sections = []

        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            content = parts[i+1].strip() if i + 1 < len(parts) else ""
            sections.append({
                "header": header,
                "content": content
            })

        return sections