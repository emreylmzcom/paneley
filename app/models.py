from sqlalchemy import Column, Integer, String, ForeignKey  # ForeignKey burada eklenmeli
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class DNSRecord(Base):
    __tablename__ = "dns_records"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, nullable=False)
    ip_address = Column(String, nullable=False)

class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String, unique=True, index=True)
    root_path = Column(String)

    # Subdomain ilişkisi
    subdomains = relationship("Subdomain", back_populates="domain")

class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(Integer, primary_key=True, index=True)
    subdomain_name = Column(String, unique=True, index=True)
    root_path = Column(String)

    # Domain ile ilişki
    domain_id = Column(Integer, ForeignKey("domains.id"))
    domain = relationship("Domain", back_populates="subdomains")