# src/core/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(Text, nullable=False)
    brand = Column(Text, nullable=False)
    objective = Column(Text)
    inputs = Column(JSON)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

class AgentRun(Base):
    __tablename__ = "agent_runs"

    agent_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    agent_name = Column(String(50))
    input_summary = Column(Text)
    output_summary = Column(Text)
    duration_ms = Column(Integer)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    status = Column(String(20))

class ImageContent(Base):
    __tablename__ = "image_contents"

    image_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    generated_image_url = Column(Text)
    prompt_used = Column(Text)
    agent_name = Column(String(50))
    validation_status = Column(String(20))
    created_at = Column(DateTime(timezone=False), server_default=func.now())

class TextContent(Base):
    __tablename__ = "text_contents"

    text_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    generated_text = Column(Text)
    prompt_used = Column(Text)
    agent_name = Column(String(50))
    validation_status = Column(String(20))
    created_at = Column(DateTime(timezone=False), server_default=func.now())

class RagDocument(Base):
    __tablename__ = "rag_documents"

    rag_id = Column(Integer, primary_key=True, index=True)
    doc_name = Column(String(50))
    source = Column(String(50))
    content = Column(Text)
    embedding_id = Column(String(100))

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    content_type = Column(String(50))
    content_id = Column(Integer)
    status = Column(String(20))
    issues_found = Column(Text)
    validated_at = Column(DateTime(timezone=False), server_default=func.now())
