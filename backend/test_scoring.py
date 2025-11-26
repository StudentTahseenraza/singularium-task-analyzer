import os
import django
import json
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')
django.setup()

from tasks.scoring import analyze_and_sort_tasks

# Test data
today = date.today()
test_tasks = [
    {
        "id": 1,
        "title": "Fix critical bug - past due",
        "due_date": (today - timedelta(days=2)).strftime('%Y-%m-%d'),
        "estimated_hours": 4,
        "importance": 9,
        "dependencies": [2, 3]  # This blocks other tasks
    },
    {
        "id": 2,
        "title": "Write documentation",
        "due_date": (today + timedelta(days=14)).strftime('%Y-%m-%d'),
        "estimated_hours": 8,
        "importance": 6,
        "dependencies": [1]  # Depends on task 1
    },
    {
        "id": 3,
        "title": "Quick UI improvement",
        "due_date": None,
        "estimated_hours": 1,
        "importance": 5,
        "dependencies": []
    },
    {
        "id": 4,
        "title": "Important feature",
        "due_date": (today + timedelta(days=3)).strftime('%Y-%m-%d'),
        "estimated_hours": 6,
        "importance": 8,
        "dependencies": []
    }
]

print("=== Testing Smart Task Analyzer Algorithm ===\n")

# Test different strategies
strategies = ["smart_balance", "fastest_wins", "high_impact", "deadline_driven"]

for strategy in strategies:
    print(f"\n--- {strategy.upper()} Strategy ---")
    result = analyze_and_sort_tasks(test_tasks, strategy)
    
    for i, task in enumerate(result['sorted_tasks'][:3], 1):
        print(f"{i}. {task['title']}")
        print(f"   Score: {task['priority_score']:.3f}")
        print(f"   Breakdown: Urgency={task['score_breakdown']['urgency']:.3f}, "
              f"Importance={task['score_breakdown']['importance']:.3f}, "
              f"Effort={task['score_breakdown']['effort']:.3f}, "
              f"Dependencies={task['score_breakdown']['dependencies']:.3f}")
        print(f"   Reason: {task['explanation']}\n")