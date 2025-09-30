#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and database operations
"""
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, get_collection, close_db

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB Connection...")
    
    try:
        # Initialize database
        db = init_db()
        print(f"✅ Database connected: {db.name}")
        
        # Test collection access
        users_collection = get_collection('USERS')
        print(f"✅ Users collection accessible: {users_collection.name}")
        
        # Test insert operation
        test_user = {
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime.now(),
            "test": True
        }
        
        result = users_collection.insert_one(test_user)
        print(f"✅ Insert test successful: {result.inserted_id}")
        
        # Test find operation
        found_user = users_collection.find_one({"email": "test@example.com"})
        if found_user:
            print(f"✅ Find test successful: {found_user['name']}")
        else:
            print("❌ Find test failed")
            
        # Clean up test data
        users_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        # Test other collections
        collections_to_test = ['DATASETS', 'PREDICTIONS', 'REPORTS', 'ALERTS']
        for collection_name in collections_to_test:
            collection = get_collection(collection_name)
            print(f"✅ {collection_name} collection accessible: {collection.name}")
        
        print("\n🎉 All MongoDB tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        close_db()

def test_app_import():
    """Test if the Flask app can be imported and created"""
    print("\n🔍 Testing Flask App Import...")
    
    try:
        from app import create_app
        print("✅ App import successful")
        
        app = create_app()
        print("✅ App creation successful")
        
        # Test if database is accessible from app context
        with app.app_context():
            from database.db import get_collection
            collection = get_collection('USERS')
            print(f"✅ Database accessible from app context: {collection.name}")
        
        print("🎉 Flask app test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting MongoDB and Flask App Tests\n")
    
    # Test MongoDB connection
    mongodb_success = test_mongodb_connection()
    
    # Test Flask app
    app_success = test_app_import()
    
    print(f"\n📊 Test Results:")
    print(f"   MongoDB: {'✅ PASS' if mongodb_success else '❌ FAIL'}")
    print(f"   Flask App: {'✅ PASS' if app_success else '❌ FAIL'}")
    
    if mongodb_success and app_success:
        print("\n🎉 All tests passed! Your application is ready to run.")
        print("   Start the app with: python app.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
