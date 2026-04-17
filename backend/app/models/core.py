from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Repository(Base):
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pull_requests = relationship("PullRequest" , back_populates="repository")

class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True, index=True)
    github_pr_id = Column(BigInteger, unique=True, index=True, nullable=False)
    number = Column(Integer, nullable=False)
    state = Column(String(255), nullable=False) # e.g., "open", "closed"
    title = Column(String(255), nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.id'))

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    vulnerabilities = relationship("Vulnerability", back_populates="pull_request")

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey('pull_requests.id'))

    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    severity = Column(String(255), nullable=False) # "High", "Medium", "Low"
    description = Column(Text, nullable=False)
    status = Column(String(255), nullable=False, default="open") # "open", "resolved", "ignored"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    pull_request = relationship("PullRequest", back_populates="vulnerabilities")
    

class CustomRule(Base):
    __tablename__ = "custom_rules"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    rule_text = Column(Text, nullable=False) # e.g., "Never use MD5 hashing, enforce SHA-256."
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    repository = relationship("Repository", back_populates="custom_rules")