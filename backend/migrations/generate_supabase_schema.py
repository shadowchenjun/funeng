"""Generate the baseline Supabase migration from the live SQLAlchemy models.

Run from the repository root with PYTHONPATH=backend. Review the generated SQL
before applying it through Supabase's migration tool.
"""
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import Base
import app.models.smart_agriculture  # noqa: F401 - registers tables
import app.api.digital_marketing  # noqa: F401 - registers legacy columns


def main() -> None:
    dialect = postgresql.dialect()
    print("-- Generated baseline for funeng; all application tables require RLS.")
    emitted_indexes = set()
    for table in Base.metadata.sorted_tables:
        print(str(CreateTable(table, if_not_exists=True).compile(dialect=dialect)) + ";")
        for index in sorted(table.indexes, key=lambda item: item.name):
            if index.name in emitted_indexes:
                continue
            emitted_indexes.add(index.name)
            print(str(CreateIndex(index, if_not_exists=True).compile(dialect=dialect)) + ";")
        print(f'ALTER TABLE public."{table.name}" ENABLE ROW LEVEL SECURITY;')
    # Six tables already exist in the linked project. Their only observed
    # column drift is the missing categories.color field (all have zero rows).
    print("ALTER TABLE public.categories ADD COLUMN IF NOT EXISTS color VARCHAR(20);")
    print("INSERT INTO storage.buckets (id, name, public) VALUES")
    print("  ('funeng-images', 'funeng-images', false),")
    print("  ('funeng-exports', 'funeng-exports', false)")
    print("ON CONFLICT (id) DO NOTHING;")


if __name__ == "__main__":
    main()
