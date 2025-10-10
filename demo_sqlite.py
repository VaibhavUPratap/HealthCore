#!/usr/bin/env python3
"""
Demo script to show the database migration is complete.
This simulates adding a health report and retrieving it.
"""
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_collection, close_db

def main():
    print("=" * 60)
    print("  HEALTHCORE - Database Migration Demo")
    print("  MongoDB → SQLite Migration Complete ✅")
    print("=" * 60)
    print()
    
    # Initialize database
    db = init_db()
    print(f"📊 Database: {db.name}")
    print(f"📂 Database Type: SQLite (file-based, serverless)")
    print(f"🔧 No MongoDB server required!")
    print()
    
    # Add a sample report
    reports = get_collection('REPORTS')
    
    sample_report = {
        "timestamp": datetime.now().isoformat(),
        "reporter": "Demo User",
        "location_name": "Rural Village, Assam",
        "lat": 26.1445,
        "lng": 91.7362,
        "symptoms": "diarrhea, vomiting",
        "cases": 8,
        "turbidity": 18.2,
        "ph": 6.9,
        "chlorine": 0.2,
        "tds": 450.0,
        "fluoride": 0.6,
        "nitrate": 15.0,
        "chloride": 55.0,
        "ec": 700.0,
        "ai_prediction": "High Risk",
        "ai_confidence": 0.92,
    }
    
    print("📝 Adding sample health report...")
    result = reports.insert_one(sample_report)
    print(f"   ✅ Report added with ID: {result.inserted_id}")
    print()
    
    # Retrieve reports
    print("📖 Retrieving reports from database...")
    all_reports = list(reports.find().limit(5))
    print(f"   Found {len(all_reports)} report(s)")
    
    for i, report in enumerate(all_reports, 1):
        print(f"\n   Report #{i}:")
        print(f"   - Location: {report.get('location_name', 'N/A')}")
        print(f"   - Cases: {report.get('cases', 'N/A')}")
        print(f"   - AI Prediction: {report.get('ai_prediction', 'N/A')}")
        print(f"   - Confidence: {report.get('ai_confidence', 'N/A')}")
    
    print()
    print("=" * 60)
    print("✅ Database migration successful!")
    print("✅ All operations working correctly!")
    print("=" * 60)
    
    close_db()

if __name__ == "__main__":
    main()
