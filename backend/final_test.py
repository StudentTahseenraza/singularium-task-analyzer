import os
import django
import requests
import json
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')
django.setup()

def test_complete_workflow():
    """Test the complete application workflow with fixed data"""
    print("🧪 Testing PRODUCTION Backend on Render\n")
    
    # Use your actual Render backend URL
    BACKEND_URL = "https://singularium-task-analyzer.onrender.com"
    
    # FIXED test data - no circular dependencies
    today = date.today()
    test_tasks = [
        {
            "id": 1,
            "title": "Critical production fix - URGENT",
            "due_date": (today - timedelta(days=1)).strftime('%Y-%m-%d'),  # Past due
            "estimated_hours": 6,
            "importance": 10,
            "dependencies": []  # No dependencies to avoid circles
        },
        {
            "id": 2,
            "title": "Write unit tests for production fix",
            "due_date": (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            "estimated_hours": 4,
            "importance": 8,
            "dependencies": [1]  # Depends on task 1 (valid dependency)
        },
        {
            "id": 3,
            "title": "Quick documentation update",
            "due_date": None,
            "estimated_hours": 1,
            "importance": 5,
            "dependencies": []
        }
    ]
    
    # Test all strategies
    strategies = ["smart_balance", "fastest_wins", "high_impact", "deadline_driven"]
    
    for strategy in strategies:
        print(f"\n📊 Testing {strategy.replace('_', ' ').title()} Strategy")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/tasks/analyze/",
                json={
                    "tasks": test_tasks,
                    "strategy": strategy
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Analysis successful: {data['message']}")
                
                # Show top tasks
                for i, task in enumerate(data['data']['sorted_tasks'][:3], 1):
                    print(f"   {i}. {task['title']}")
                    print(f"      Score: {task['priority_score']:.3f}")
                    print(f"      Due: {task.get('due_date', 'None')}")
                    print(f"      Effort: {task['estimated_hours']}h")
                    print(f"      Importance: {task['importance']}/10")
                    print(f"      Reason: {task['explanation']}")
                    print()
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Message: {error_data.get('message', 'No message')}")
                    if error_data.get('errors'):
                        print(f"   Errors: {error_data['errors']}")
                except:
                    print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

def test_backend_health():
    """Test if backend is accessible"""
    print("\n🏥 Backend Health Check")
    print("-" * 50)
    
    BACKEND_URL = "https://singularium-task-analyzer.onrender.com"
    
    try:
        # Test if backend is reachable
        response = requests.get(f"{BACKEND_URL}/api/tasks/analyze/", timeout=10)
        print(f"✅ Backend is reachable")
        print(f"   Status: {response.status_code}")
        print(f"   Expected: 405 (Method Not Allowed for GET - this is normal)")
        
    except Exception as e:
        print(f"❌ Backend is not reachable: {e}")

if __name__ == "__main__":
    print("🚀 PRODUCTION BACKEND TEST SUITE")
    print("=" * 60)
    
    test_backend_health()
    test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 PRODUCTION TESTS COMPLETED!")