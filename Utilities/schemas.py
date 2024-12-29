from pydantic import BaseModel, field_validator, Field
from typing import Dict, Any

class Source(BaseModel):
    """Source information schema."""

    blob: str = Field(
        description="The blob, or filename of the PDF document containing the source information."
    )
    page: int = Field(
        description="The page number in the PDF where the relevant information is found."
    )
    chapter: str = Field(
        description="The chapter and subchapters (if applicable) of the relevant retrieved page."
    )

    class Config:
        schema_extra = {
            "example": {
                "blob": "general_company_information.pdf",
                "page": 42,
                "chapter": "Chapter 3: Methodology, Section 3.2: Data Collection"
            }
        }

class ChatResponse(BaseModel):
    """Chat response schema."""

    sender: str
    message: str
    type: str

    @field_validator("sender")
    def sender_must_be_bot_or_you(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("sender must be bot or you")
        return v

    @field_validator("type")
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info", "source"]:
            raise ValueError("type must be start, stream, end, error, source, or info")
        return v
    
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class SourceResponse(BaseModel):
    sender: str
    message: Dict[str, Any]  # Changed to Dict to accommodate the entire JSON object
    type: str