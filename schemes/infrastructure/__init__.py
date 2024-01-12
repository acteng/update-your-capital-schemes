from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)

metadata = MetaData()

authority_table = Table(
    "authority",
    metadata,
    Column("authority_id", Integer, primary_key=True),
    Column("authority_name", Text, nullable=False, unique=True),
)

user_table = Table(
    "user",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("email", String(length=256), nullable=False, unique=True),
    Column(
        "authority_id", Integer, ForeignKey("authority.authority_id", name="user_authority_id_fkey"), nullable=False
    ),
)

capital_scheme_table = Table(
    "capital_scheme",
    metadata,
    Column("capital_scheme_id", Integer, primary_key=True),
    Column("scheme_name", Text, nullable=False),
    Column(
        "bid_submitting_authority_id",
        Integer,
        ForeignKey("authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"),
    ),
    Column("scheme_type_id", Integer),
    Column("funding_programme_id", Integer),
)

capital_scheme_financial_table = Table(
    "capital_scheme_financial",
    metadata,
    Column("capital_scheme_financial_id", Integer, primary_key=True),
    Column(
        "capital_scheme_id",
        Integer,
        ForeignKey("capital_scheme.capital_scheme_id", name="capital_scheme_financial_capital_scheme_id_fkey"),
        nullable=False,
    ),
    Column("financial_type_id", Integer, nullable=False),
    Column("amount", Integer, nullable=False),
    Column("effective_date_from", Date, nullable=False),
    Column("effective_date_to", Date),
    Column("data_source_id", Integer, nullable=False),
)

scheme_milestone_table = Table(
    "scheme_milestone",
    metadata,
    Column("scheme_milestone_id", Integer, primary_key=True),
    Column(
        "capital_scheme_id",
        Integer,
        ForeignKey("capital_scheme.capital_scheme_id", name="scheme_milestone_capital_scheme_id_fkey"),
        nullable=False,
    ),
    Column("milestone_id", Integer, nullable=False),
    Column("status_date", Date, nullable=False),
    Column("observation_type_id", Integer, nullable=False),
    Column("effective_date_from", Date, nullable=False),
    Column("effective_date_to", Date),
)

scheme_intervention_table = Table(
    "scheme_intervention",
    metadata,
    Column("scheme_intervention_id", Integer, primary_key=True),
    Column("intervention_type_measure_id", Integer, nullable=False),
    Column(
        "capital_scheme_id",
        Integer,
        ForeignKey("capital_scheme.capital_scheme_id", name="scheme_intervention_capital_scheme_id_fkey"),
        nullable=False,
    ),
    Column("intervention_value", Numeric(precision=15, scale=6), nullable=False),
    Column("observation_type_id", Integer, nullable=False),
    Column("effective_date_from", Date, nullable=False),
    Column("effective_date_to", Date),
)
