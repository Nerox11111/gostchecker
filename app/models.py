from pydantic import BaseModel, Field


class Issue(BaseModel):
    rule_id: str
    paragraph_index: int | None = None
    description: str
    severity: str = Field(pattern="^(info|warning|error)$")
    current_value: str | None = None
    expected_value: str | None = None
    auto_fixable: bool = False


class CheckResponse(BaseModel):
    score: float
    doc_type: str
    mode: str
    session_id: str
    issues: list[Issue]


class FixRequest(BaseModel):
    session_id: str
    apply_rules: list[str] = Field(default_factory=list)


class FixResponse(BaseModel):
    session_id: str
    score_after: float
    download_url: str
    patches: list[dict]


class ClassificationResponse(BaseModel):
    doc_type: str
    mode: str
    confidence: float
    needs_confirmation: bool


class HistorySession(BaseModel):
    id: str
    doc_type: str
    mode: str
    score_before: float
    score_after: float | None = None
    created_at: str


class HistoryResponse(BaseModel):
    sessions: list[HistorySession]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

