"""
TaskNest Knowledge Base Populator
Reads context files and populates the knowledge_base table
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not set in .env file")
    sys.exit(1)


async def populate_knowledge_base():
    """Populate knowledge base with context files."""

    print("=" * 60)
    print("TaskNest Knowledge Base Populator")
    print("=" * 60)
    print()

    # Connect to database
    print("🔌 Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)

    # Context files to load
    context_dir = Path(__file__).parent.parent.parent / 'context'

    knowledge_entries = []

    # 1. Company Profile (Custora AI)
    company_profile_path = context_dir / 'custora-company-profile.md'
    if company_profile_path.exists():
        print(f"📄 Reading {company_profile_path.name}...")
        content = company_profile_path.read_text(encoding='utf-8')

        # Split into sections
        sections = content.split('\n## ')
        for i, section in enumerate(sections):
            if i == 0:
                title = "Custora AI Company Overview"
                text = section
            else:
                lines = section.split('\n', 1)
                title = f"Custora AI - {lines[0].strip()}"
                text = lines[1] if len(lines) > 1 else ""

            if text.strip():
                knowledge_entries.append({
                    'title': title,
                    'content': text.strip(),
                    'category': 'company_profile',
                    'source': 'custora-company-profile.md'
                })

        print(f"  ✅ Extracted {len([e for e in knowledge_entries if e['category'] == 'company_profile'])} sections")

    # 2. Product Documentation (Custora AI)
    product_docs_path = context_dir / 'custora-product-docs.md'
    if product_docs_path.exists():
        print(f"📄 Reading {product_docs_path.name}...")
        content = product_docs_path.read_text(encoding='utf-8')

        sections = content.split('\n## ')
        for i, section in enumerate(sections):
            if i == 0:
                continue

            lines = section.split('\n', 1)
            title = f"Custora AI - {lines[0].strip()}"
            text = lines[1] if len(lines) > 1 else ""

            if text.strip() and len(text) > 100:
                knowledge_entries.append({
                    'title': title,
                    'content': text.strip()[:5000],
                    'category': 'product_documentation',
                    'source': 'custora-product-docs.md'
                })

        print(f"  ✅ Extracted {len([e for e in knowledge_entries if e['category'] == 'product_documentation'])} sections")

    # 3. Escalation Rules (Custora AI)
    escalation_path = context_dir / 'custora-escalation-rules.md'
    if escalation_path.exists():
        print(f"📄 Reading {escalation_path.name}...")
        content = escalation_path.read_text(encoding='utf-8')

        knowledge_entries.append({
            'title': 'Custora AI Escalation Rules and Guidelines',
            'content': content.strip(),
            'category': 'escalation_rules',
            'source': 'custora-escalation-rules.md'
        })

        print(f"  ✅ Added escalation rules")

    # 4. Brand Voice (Custora AI)
    brand_voice_path = context_dir / 'custora-brand-voice.md'
    if brand_voice_path.exists():
        print(f"📄 Reading {brand_voice_path.name}...")
        content = brand_voice_path.read_text(encoding='utf-8')

        knowledge_entries.append({
            'title': 'Custora AI Brand Voice and Communication Guidelines',
            'content': content.strip(),
            'category': 'brand_voice',
            'source': 'custora-brand-voice.md'
        })

        print(f"  ✅ Added brand voice guidelines")

    print()
    print(f"📊 Total knowledge entries to insert: {len(knowledge_entries)}")
    print()

    # Clear existing knowledge base
    print("🗑️  Clearing existing knowledge base...")
    await conn.execute("DELETE FROM knowledge_base")
    print("✅ Cleared")
    print()

    # Insert entries
    print("💾 Inserting knowledge entries...")
    inserted = 0

    for entry in knowledge_entries:
        try:
            await conn.execute("""
                INSERT INTO knowledge_base (title, content, category)
                VALUES ($1, $2, $3)
            """,
            entry['title'],
            entry['content'],
            entry['category']
            )
            inserted += 1
            print(f"  ✅ Inserted: {entry['title'][:60]}...")
        except Exception as e:
            print(f"  ❌ Failed to insert {entry['title'][:60]}: {e}")

    print()
    print(f"✅ Successfully inserted {inserted}/{len(knowledge_entries)} entries")

    # Verify
    count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")
    print(f"📊 Total entries in knowledge_base: {count}")

    # Show categories
    categories = await conn.fetch("""
        SELECT category, COUNT(*) as count
        FROM knowledge_base
        GROUP BY category
        ORDER BY count DESC
    """)

    print()
    print("📂 Entries by category:")
    for row in categories:
        print(f"  - {row['category']}: {row['count']} entries")

    await conn.close()

    print()
    print("=" * 60)
    print("🎉 Knowledge Base Population Complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(populate_knowledge_base())
