#!/usr/bin/env python3
"""
Integration test to verify SQLite database works with the application routes.
Tests the key operations: insert, find, and delete for reports.
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_collection, close_db

def test_reports_workflow():
    """Test the complete workflow for health reports."""
    print("🧪 Testing Reports Workflow with SQLite...\n")
    
    try:
        # Initialize database
        db = init_db()
        print(f"✅ Database initialized: {db.name}")
        
        # Get reports collection
        reports = get_collection('REPORTS')
        print(f"✅ Reports collection accessible: {reports.name}")
        
        # Insert a test report
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "reporter": "Integration Test",
            "location_name": "Test Village",
            "lat": 26.1234,
            "lng": 91.5678,
            "symptoms": "fever, diarrhea",
            "cases": 5,
            "turbidity": 15.5,
            "ph": 7.2,
            "chlorine": 0.3,
            "tds": 400.0,
            "fluoride": 0.5,
            "nitrate": 10.0,
            "chloride": 45.0,
            "ec": 650.0,
            "ai_prediction": "Medium Risk",
            "ai_confidence": 0.85,
        }
        
        result = reports.insert_one(test_report)
        print(f"✅ Report inserted successfully: ID={result.inserted_id}")
        
        # Find all reports
        all_reports = list(reports.find().limit(5))
        print(f"✅ Found {len(all_reports)} report(s)")
        
        if all_reports:
            report = all_reports[0]
            print(f"   Sample report: {report.get('location_name')} - {report.get('ai_prediction')}")
        
        # Test sorting
        sorted_reports = list(reports.find().sort('timestamp', -1).limit(3))
        print(f"✅ Sorted reports: {len(sorted_reports)} report(s)")
        
        # Clean up - delete test report
        reports.delete_one({"_id": result.inserted_id})
        print("✅ Test report deleted")
        
        # Test other collections
        collections_to_test = ['USERS', 'DATASETS', 'PREDICTIONS', 'ALERTS']
        for collection_name in collections_to_test:
            collection = get_collection(collection_name)
            print(f"✅ {collection_name} collection accessible: {collection.name}")
        
        print("\n🎉 All integration tests passed!")
        print("   The SQLite database is working correctly with the application.")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        close_db()


if __name__ == "__main__":
    print("🚀 Starting SQLite Integration Tests\n")
    success = test_reports_workflow()
    
    if success:
        print("\n✅ SUCCESS: Application is ready to use with SQLite database")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Please check the errors above")
        sys.exit(1)
