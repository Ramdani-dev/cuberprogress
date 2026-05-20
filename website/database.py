"""
Database models and setup for Cuber Progress.
Uses SQLAlchemy with SQLite.
"""
import os
import json
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(BASE_DIR, "data", "seed_data.json")

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # SQLAlchemy requires postgresql+pg8000:// (using pg8000 driver) or postgresql:// (using psycopg2)
    # We use pg8000 because it is pure-python and works reliably on Vercel without requiring libpq.so
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
    
    # Remove pgbouncer query parameter because pg8000 connect() does not accept it
    from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
    parsed = urlparse(DATABASE_URL)
    query_params = parse_qsl(parsed.query)
    filtered_params = [(k, v) for k, v in query_params if k.lower() != 'pgbouncer']
    new_query = urlencode(filtered_params)
    parsed = parsed._replace(query=new_query)
    DATABASE_URL = urlunparse(parsed)
    
    # We also configure pool pre-ping to verify connections and prevent drops
    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,
        pool_recycle=300
    )

else:
    # Use SQLite
    if os.environ.get("VERCEL"):
        DB_PATH = "/tmp/cuber_progress.db"
    else:
        DB_PATH = os.path.join(BASE_DIR, "data", "cuber_progress.db")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Case(Base):
    """A single algorithm case (F2L / ZBLS / ZBLL)."""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(10), nullable=False, index=True)      # F2L, ZBLS, ZBLL
    case_name = Column(String(100), nullable=False)                 # e.g. "Case 1"
    sub_group = Column(String(100), nullable=True)                  # e.g. "T-Shape", "Basic Insert"
    image_url = Column(String(255), nullable=False)                 # /static/images/f2l/...
    status = Column(Boolean, default=False, nullable=False)         # True = memorized
    date_learned = Column(DateTime, nullable=True)                  # When memorized

    # One case can have multiple algorithm variations
    algorithms = relationship(
        "Algorithm", back_populates="case",
        cascade="all, delete-orphan",
        order_by="Algorithm.order"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "case_name": self.case_name,
            "sub_group": self.sub_group,
            "image_url": self.image_url,
            "status": self.status,
            "date_learned": self.date_learned.isoformat() if self.date_learned else None,
            "algorithms": [a.to_dict() for a in self.algorithms],
            "selected_algorithm_id": next(
                (a.id for a in self.algorithms if a.is_selected), None
            ),
        }


class Algorithm(Base):
    """An algorithm variation for a specific case."""
    __tablename__ = "algorithms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    notation = Column(Text, nullable=False)                         # e.g. "R U R' U'"
    label = Column(String(50), nullable=True)                       # e.g. "Alt 1", "Main"
    order = Column(Integer, default=0)                              # Display order
    is_selected = Column(Boolean, default=False)                    # Which alg user chose to learn

    case = relationship("Case", back_populates="algorithms")

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "notation": self.notation,
            "label": self.label or f"Alg {self.order + 1}",
            "order": self.order,
            "is_selected": self.is_selected,
        }


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)


def seed_db():
    """Seed the database from seed_data.json if the DB is empty."""
    session = SessionLocal()
    try:
        count = session.query(Case).count()
        if count > 0:
            print(f"Database already has {count} cases. Skipping seed.")
            return

        if not os.path.exists(SEED_PATH):
            print(f"No seed file found at {SEED_PATH}. Skipping seed.")
            return

        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            case = Case(
                category=item["category"],
                case_name=item["case_name"],
                sub_group=item.get("sub_group"),
                image_url=item["image_url"],
                status=False,
                date_learned=None,
            )
            # Add algorithm variations
            algs = item.get("algorithms", [])
            if not algs and item.get("algorithm"):
                # Backward compat: single algorithm string
                algs = [{"notation": item["algorithm"], "label": "Main"}]

            for idx, alg in enumerate(algs):
                case.algorithms.append(Algorithm(
                    notation=alg["notation"],
                    label=alg.get("label", f"Alg {idx + 1}"),
                    order=idx,
                    is_selected=(idx == 0),  # First algorithm selected by default
                ))

            session.add(case)

        session.commit()
        print(f"Seeded {len(data)} cases into the database.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
    seed_db()
