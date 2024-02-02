from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AuthorityEntity(Base):
    __tablename__ = "authority"

    authority_id: Mapped[int] = mapped_column(primary_key=True)
    authority_name: Mapped[str] = mapped_column(Text, unique=True)


class UserEntity(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(length=256), unique=True)
    authority_id = mapped_column(ForeignKey("authority.authority_id", name="user_authority_id_fkey"), nullable=False)


class CapitalSchemeEntity(Base):
    __tablename__ = "capital_scheme"

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_name: Mapped[str] = mapped_column(Text)
    bid_submitting_authority_id = mapped_column(
        ForeignKey("authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey")
    )
    scheme_type_id: Mapped[int | None]
    funding_programme_id: Mapped[int | None]
    capital_scheme_financials: Mapped[list[CapitalSchemeFinancialEntity]] = relationship()
    scheme_milestones: Mapped[list[SchemeMilestoneEntity]] = relationship()
    scheme_interventions: Mapped[list[SchemeInterventionEntity]] = relationship()


class CapitalSchemeFinancialEntity(Base):
    __tablename__ = "capital_scheme_financial"

    capital_scheme_financial_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey("capital_scheme.capital_scheme_id", name="capital_scheme_financial_capital_scheme_id_fkey"),
        nullable=False,
    )
    financial_type_id: Mapped[int]
    amount: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    data_source_id: Mapped[int]


class SchemeMilestoneEntity(Base):
    __tablename__ = "scheme_milestone"

    scheme_milestone_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey("capital_scheme.capital_scheme_id", name="scheme_milestone_capital_scheme_id_fkey"), nullable=False
    )
    milestone_id: Mapped[int]
    status_date: Mapped[date]
    observation_type_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    data_source_id: Mapped[int]


class SchemeInterventionEntity(Base):
    __tablename__ = "scheme_intervention"

    scheme_intervention_id: Mapped[int] = mapped_column(primary_key=True)
    intervention_type_measure_id: Mapped[int]
    capital_scheme_id = mapped_column(
        ForeignKey("capital_scheme.capital_scheme_id", name="scheme_intervention_capital_scheme_id_fkey"),
        nullable=False,
    )
    intervention_value: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=6))
    observation_type_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
