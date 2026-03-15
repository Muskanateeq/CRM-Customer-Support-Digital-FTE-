import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT conname, conrelid::regclass, confrelid::regclass "
        "FROM pg_constraint "
        "WHERE conrelid IN ('tasks'::regclass, 'tags'::regclass) AND contype = 'f'"
    ))
    for row in result:
        print(f"{row[0]}: {row[1]} -> {row[2]}")
