from django.test import TestCase
from django.urls import reverse
from .scoring import *
import json
from datetime import date, timedelta

class ScoringAlgorithmTests(TestCase):
    
    def setUp(self):
        self.today = date.today()
        self.tomorrow = self.today + timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)
        self.last_week = self.today - timedelta(days=7)
        
        self.sample_tasks = [
            {
                "id": 1,
                "title": "Urgent important task",
                "due_date": self.tomorrow.strftime('%Y-%m-%d'),
                "estimated_hours": 2,
                "importance": 9,
                "dependencies": []
            },
            {
                "id": 2,
                "title": "Low priority task",
                "due_date": self.next_week.strftime('%Y-%m-%d'),
                "estimated_hours": 8,
                "importance": 3,
                "dependencies": []
            },
            {
                "id": 3,
                "title": "Quick win",
                "due_date": None,
                "estimated_hours": 0.5,
                "importance": 5,
                "dependencies": []
            }
        ]
    
    def test_urgency_score_calculation(self):
        """Test urgency score calculation for different due dates"""
        # Past due should be highest
        past_score = calculate_urgency_score(self.last_week.strftime('%Y-%m-%d'))
        self.assertGreaterEqual(past_score, 0.9)
        
        # Due tomorrow should be high
        tomorrow_score = calculate_urgency_score(self.tomorrow.strftime('%Y-%m-%d'))
        self.assertGreaterEqual(tomorrow_score, 0.7)
        
        # Far future should be low
        future_score = calculate_urgency_score(self.next_week.strftime('%Y-%m-%d'))
        self.assertLessEqual(future_score, 0.5)
        
        # No due date should be low
        none_score = calculate_urgency_score(None)
        self.assertEqual(none_score, 0.3)
    
    def test_effort_score_calculation(self):
        """Test effort score calculation (inverted - lower effort = higher score)"""
        # Quick task should have high score
        quick_score = calculate_effort_score(0.5)
        self.assertGreaterEqual(quick_score, 0.8)
        
        # Long task should have low score
        long_score = calculate_effort_score(10)
        self.assertLessEqual(long_score, 0.5)
        
        # Invalid effort should return default
        invalid_score = calculate_effort_score(0)
        self.assertEqual(invalid_score, 0.5)
    
    def test_importance_score_calculation(self):
        """Test importance score normalization"""
        self.assertEqual(calculate_importance_score(10), 1.0)
        self.assertEqual(calculate_importance_score(5), 0.5)
        self.assertEqual(calculate_importance_score(1), 0.1)
        self.assertEqual(calculate_importance_score(15), 0.5)  # Invalid -> default
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        tasks_with_circle = [
            {"id": 1, "title": "Task 1", "dependencies": [2]},
            {"id": 2, "title": "Task 2", "dependencies": [1]}  # Circular!
        ]
        
        errors = detect_circular_dependencies(tasks_with_circle)
        self.assertTrue(len(errors) > 0)
        self.assertIn("circular", errors[0].lower())
    
    def test_different_strategies(self):
        """Test that different strategies produce different weights"""
        smart_weights = get_strategy_weights("smart_balance")
        fast_weights = get_strategy_weights("fastest_wins")
        impact_weights = get_strategy_weights("high_impact")
        deadline_weights = get_strategy_weights("deadline_driven")
        
        # Strategies should have different emphasis
        self.assertGreater(deadline_weights["urgency"], smart_weights["urgency"])
        self.assertGreater(fast_weights["effort"], impact_weights["effort"])
        self.assertGreater(impact_weights["importance"], fast_weights["importance"])
    
    def test_full_analysis(self):
        """Test complete task analysis and sorting"""
        result = analyze_and_sort_tasks(self.sample_tasks, "smart_balance")
        
        self.assertEqual(len(result['sorted_tasks']), 3)
        self.assertEqual(result['strategy_used'], "smart_balance")
        
        # Urgent important task should be first
        self.assertEqual(result['sorted_tasks'][0]['title'], "Urgent important task")
        self.assertGreater(result['sorted_tasks'][0]['priority_score'], 
                          result['sorted_tasks'][1]['priority_score'])

class APITests(TestCase):
    
    def test_analyze_tasks_endpoint(self):
        """Test the analyze tasks API endpoint"""
        sample_data = {
            "tasks": [
                {
                    "title": "Test task",
                    "due_date": "2025-12-01",
                    "estimated_hours": 2,
                    "importance": 8,
                    "dependencies": []
                }
            ],
            "strategy": "smart_balance"
        }
        
        response = self.client.post(
            reverse('analyze-tasks'),
            data=json.dumps(sample_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['sorted_tasks']), 1)