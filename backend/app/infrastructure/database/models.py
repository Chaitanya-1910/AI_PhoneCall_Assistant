from sqlalchemy import String, Integer, Float, Boolean, JSON, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Dict, Any, List

class Base(DeclarativeBase):
    pass

class SQLAlchemyCallerProfile(Base):
    __tablename__ = "caller_profiles"
    
    caller_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    phone_numbers: Mapped[List[str]] = mapped_column(JSON)
    organizations: Mapped[List[str]] = mapped_column(JSON)
    relationship: Mapped[str] = mapped_column(String, default="NEW")
    preferred_language: Mapped[str] = mapped_column(String, default="en")
    preferred_callback_time: Mapped[str] = mapped_column(String, nullable=True)
    communication_style: Mapped[str] = mapped_column(String, default="NEUTRAL")
    previous_topics: Mapped[List[str]] = mapped_column(JSON)
    
    histories: Mapped[List["SQLAlchemyConversationHistory"]] = relationship(back_populates="profile")

class SQLAlchemyConversationHistory(Base):
    __tablename__ = "conversation_histories"
    
    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    caller_id: Mapped[str] = mapped_column(ForeignKey("caller_profiles.caller_id"))
    timestamp: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(String)
    outcome: Mapped[str] = mapped_column(String)
    
    # Store the Knowledge Graph snapshot as JSONB for efficient querying
    knowledge_graph_dump: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    profile: Mapped["SQLAlchemyCallerProfile"] = relationship(back_populates="histories")

class SQLAlchemyDomainEvent(Base):
    __tablename__ = "domain_events"
    
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    conversation_id: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    correlation_id: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    aggregate_id: Mapped[str] = mapped_column(String, index=True)
    aggregate_version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    metadata_dump: Mapped[Dict[str, Any]] = mapped_column(JSON)
    source_component: Mapped[str] = mapped_column(String)
    trace_id: Mapped[str] = mapped_column(String, nullable=True)

class SQLAlchemyAgentProfile(Base):
    __tablename__ = "agent_profiles"
    
    agent_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    system_prompt: Mapped[str] = mapped_column(String)
    allowed_tools: Mapped[List[str]] = mapped_column(JSON)
    preferred_model: Mapped[str] = mapped_column(String)

class SQLAlchemyToolExecution(Base):
    __tablename__ = "tool_executions"
    
    execution_id: Mapped[str] = mapped_column(String, primary_key=True)
    tool_name: Mapped[str] = mapped_column(String, index=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    success: Mapped[bool] = mapped_column(Boolean)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON)
    result_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    error_message: Mapped[str] = mapped_column(String, nullable=True)
    requested_at: Mapped[float] = mapped_column(Float)
    completed_at: Mapped[float] = mapped_column(Float)
