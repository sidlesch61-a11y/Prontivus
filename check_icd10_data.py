#!/usr/bin/env python3
"""
Check ICD-10 data directly from database
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import get_async_session
from app.models.icd10 import ICD10Chapter, ICD10Group, ICD10Category, ICD10Subcategory, ICD10SearchIndex
from sqlalchemy import select, func

async def check_icd10_data():
    """Check ICD-10 data in database"""
    print("🔍 Checking ICD-10 data in database...")
    
    async for db in get_async_session():
        # Count records
        chapters_count = (await db.execute(select(func.count(ICD10Chapter.id)))).scalar()
        groups_count = (await db.execute(select(func.count(ICD10Group.id)))).scalar()
        categories_count = (await db.execute(select(func.count(ICD10Category.id)))).scalar()
        subcategories_count = (await db.execute(select(func.count(ICD10Subcategory.id)))).scalar()
        search_count = (await db.execute(select(func.count(ICD10SearchIndex.id)))).scalar()
        
        print(f"\n📊 Database Records:")
        print(f"   Chapters: {chapters_count}")
        print(f"   Groups: {groups_count}")
        print(f"   Categories: {categories_count}")
        print(f"   Subcategories: {subcategories_count}")
        print(f"   Search Index: {search_count}")
        
        # Show sample chapters
        print(f"\n📖 Sample Chapters:")
        chapters = (await db.execute(select(ICD10Chapter).limit(5))).scalars().all()
        for chapter in chapters:
            print(f"   {chapter.code} - {chapter.description}")
        
        # Search for diabetes
        print(f"\n🔍 Searching for 'diabetes' in search index:")
        search_results = (await db.execute(
            select(ICD10SearchIndex)
            .where(ICD10SearchIndex.search_text.ilike('%diabetes%'))
            .limit(5)
        )).scalars().all()
        
        for result in search_results:
            print(f"   {result.code} - {result.description} ({result.level})")
        
        # Search for cancer
        print(f"\n🔍 Searching for 'cancer' in search index:")
        search_results = (await db.execute(
            select(ICD10SearchIndex)
            .where(ICD10SearchIndex.search_text.ilike('%cancer%'))
            .limit(5)
        )).scalars().all()
        
        for result in search_results:
            print(f"   {result.code} - {result.description} ({result.level})")
        
        break

if __name__ == "__main__":
    asyncio.run(check_icd10_data())
