from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any

class Column(BaseModel):
    name: str
    data_type: str
    nullable: bool
    default: Optional[str] = None

class ForeignKey(BaseModel):
    table: str
    column: str
    ref_table: str
    ref_column: str

class Table(BaseModel):
    name: str
    columns: List[Column]
    primary_key: List[str]
    foreign_keys: List[ForeignKey]
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list)

class SchemaSnapshot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_name: str = Field(alias="schema")
    tables: Dict[str, "Table"]

class RephraseOutput(BaseModel):
    rephrased_query: str
    reasoning: str

class PlanSQLOutput(BaseModel):
    sql_draft: str
    target_tables: List[str]
    assumptions: str

class ValidateFixOutput(BaseModel):
    validated_sql: Optional[str]
    attempts: int
    last_error: Optional[str]

class ExecutionResult(BaseModel):
    final_sql: str
    rows: List[Dict[str, Any]]
    rowcount: int

class ConversationTurn(BaseModel):
    original_question: str
    rephrased_question: str
    final_sql: str
    result_preview: List[Dict[str, Any]] = Field(default_factory=list)  # top-N rows only
    rowcount: int
    timestamp_iso: str

class ResponseOutput(BaseModel):
    reply_text: str

class QueryContext(BaseModel):
    user_query: str
    now_iso: str
    timezone: str
    previous_turns: List[ConversationTurn] = Field(default_factory=list)