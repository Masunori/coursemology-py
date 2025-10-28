from pydantic import BaseModel

class ProgrammingFilePayload(BaseModel):
    """Represents a single file in a programming answer payload."""
    id: int | None = None  # Needed for existing files
    filename: str
    content: str

class ProgrammingAnswerPayload(BaseModel):
    """Payload for saving or submitting a programming answer."""
    id: int  # The ID of the answer object being updated
    files_attributes: list[ProgrammingFilePayload]

class McqMrqAnswerPayload(BaseModel):
    """Payload for saving MCQ/MRQ answers."""
    id: int
    option_ids: list[int]

class TextResponseAnswerPayload(BaseModel):
    """Payload for saving text response answers."""
    id: int
    answer_text: str
    files: list[dict[str, str]] | None = None

class VoiceResponseAnswerPayload(BaseModel):
    """Payload for saving voice response answers."""
    id: int
    file: dict[str, str] | None = None

class ForumPostResponseAnswerPayload(BaseModel):
    """Payload for saving forum post response answers."""
    id: int
    answer_text: str
    selected_post_packs: list[dict[str, str | int | bool]] | None = None

class RubricBasedResponseAnswerPayload(BaseModel):
    """Payload for saving rubric-based response answers."""
    id: int
    answer_text: str

class ScribingAnswerPayload(BaseModel):
    """Payload for saving scribing answers."""
    id: int
    scribbles: list[dict[str, str]] | None = None

class FileUploadAnswerPayload(BaseModel):
    """Payload for saving file upload answers."""
    id: int
    files: list[dict[str, str]] | None = None