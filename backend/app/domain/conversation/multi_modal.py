from pydantic import BaseModel, Field
from typing import List, Optional

class MultiModalAttachment(BaseModel):
    """
    Represents an image, document, or OCR text sent by the caller during a conversation.
    """
    attachment_id: str
    content_type: str # e.g., 'image/png', 'application/pdf', 'text/ocr'
    url: Optional[str] = None
    extracted_text: Optional[str] = None
    base64_data: Optional[str] = None

class MultiModalContextExtension:
    """
    Mixin/Extension for ConversationContext to track multi-modal inputs.
    """
    def __init__(self):
        self.attachments: List[MultiModalAttachment] = []
        
    def add_attachment(self, attachment: MultiModalAttachment):
        self.attachments.append(attachment)
        
    def get_latest_ocr_text(self) -> str:
        texts = [a.extracted_text for a in self.attachments if a.extracted_text]
        return "\n".join(texts)
