from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AuthorityEntity(Base):
    __tablename__ = "authority"
    __table_args__ = {"schema": "authority"}

    authority_id: Mapped[int] = mapped_column(primary_key=True)
    authority_full_name: Mapped[str] = mapped_column(unique=True)
    authority_abbreviation: Mapped[str] = mapped_column(unique=True)


class UserEntity(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(length=256), unique=True)
    authority_abbreviation = mapped_column(
        ForeignKey("authority.authority.authority_abbreviation", name="user_authority_abbreviation_fkey"),
        nullable=False,
    )


class CapitalSchemeOverviewEntity(Base):
    __tablename__ = "capital_scheme_overview"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_overview_capital_scheme_id_fkey"
        ),
        nullable=False,
    )
    scheme_name: Mapped[str] = mapped_column(Text)
    bid_submitting_authority_id = mapped_column(
        ForeignKey("authority.authority.authority_id", name="capital_scheme_overview_bid_submitting_authority_id_fkey"),
        nullable=False,
    )
    bid_submitting_authority: Mapped[AuthorityEntity] = relationship()
    scheme_type_id: Mapped[int]
    funding_programme_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]


class CapitalSchemeBidStatusEntity(Base):
    __tablename__ = "capital_scheme_bid_status"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_bid_status_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_bid_status_capital_scheme_id_fkey"
        ),
        nullable=False,
    )
    bid_status_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]


class CapitalSchemeFinancialEntity(Base):
    __tablename__ = "capital_scheme_financial"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_financial_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_financial_capital_scheme_id_fkey"
        ),
        nullable=False,
    )
    financial_type_id: Mapped[int]
    amount: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    data_source_id: Mapped[int]


class CapitalSchemeMilestoneEntity(Base):
    __tablename__ = "capital_scheme_milestone"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_milestone_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_milestone_capital_scheme_id_fkey"
        ),
        nullable=False,
    )
    milestone_id: Mapped[int]
    status_date: Mapped[date]
    observation_type_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    data_source_id: Mapped[int]


class CapitalSchemeInterventionEntity(Base):
    __tablename__ = "capital_scheme_intervention"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_intervention_id: Mapped[int] = mapped_column(primary_key=True)
    intervention_type_measure_id: Mapped[int]
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id", name="capital_scheme_intervention_capital_scheme_id_fkey"
        ),
        nullable=False,
    )
    intervention_value: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=6))
    observation_type_id: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]


class CapitalSchemeAuthorityReviewEntity(Base):
    __tablename__ = "capital_scheme_authority_review"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_authority_review_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(
        ForeignKey(
            "capital_scheme.capital_scheme.capital_scheme_id",
            name="capital_scheme_authority_review_capital_scheme_id_fkey",
        ),
        nullable=False,
    )
    review_date: Mapped[datetime]
    data_source_id: Mapped[int]


class CapitalSchemeEntity(Base):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship()
    capital_scheme_bid_statuses: Mapped[list[CapitalSchemeBidStatusEntity]] = relationship()
    capital_scheme_financials: Mapped[list[CapitalSchemeFinancialEntity]] = relationship()
    capital_scheme_milestones: Mapped[list[CapitalSchemeMilestoneEntity]] = relationship()
    capital_scheme_interventions: Mapped[list[CapitalSchemeInterventionEntity]] = relationship()
    capital_scheme_authority_reviews: Mapped[list[CapitalSchemeAuthorityReviewEntity]] = relationship()
