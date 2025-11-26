from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .scoring import analyze_and_sort_tasks

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    """
    Accept a list of tasks and return them sorted by priority score.
    """
    try:
        data = json.loads(request.body)
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')
        
        if not tasks:
            return JsonResponse({
                'status': 'error',
                'message': 'No tasks provided'
            }, status=400)
        
        # Analyze and sort tasks
        result = analyze_and_sort_tasks(tasks, strategy)
        
        if result['errors']:
            return JsonResponse({
                'status': 'error',
                'message': 'Validation errors occurred',
                'errors': result['errors'],
                'warnings': result['warnings']
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Analyzed {len(result["sorted_tasks"])} tasks using {strategy} strategy',
            'data': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def suggest_tasks(request):
    """
    Return the top 3 tasks the user should work on today.
    This is a simplified version that expects tasks as query parameters.
    """
    try:
        # For GET requests, we'll accept tasks as a JSON string in query params
        tasks_json = request.GET.get('tasks', '[]')
        strategy = request.GET.get('strategy', 'smart_balance')
        
        tasks = json.loads(tasks_json)
        
        if not tasks:
            return JsonResponse({
                'status': 'error',
                'message': 'No tasks provided. Use ?tasks=[...] query parameter'
            }, status=400)
        
        # Analyze tasks
        result = analyze_and_sort_tasks(tasks, strategy)
        
        if result['errors']:
            return JsonResponse({
                'status': 'error',
                'message': 'Validation errors occurred',
                'errors': result['errors']
            }, status=400)
        
        # Get top 3 tasks
        top_tasks = result['sorted_tasks'][:3]
        
        suggestions = []
        for i, task in enumerate(top_tasks, 1):
            suggestions.append({
                'rank': i,
                'task': task['title'],
                'priority_score': task['priority_score'],
                'reason': task['explanation'],
                'due_date': task.get('due_date', 'Not specified'),
                'estimated_hours': task.get('estimated_hours', 'Unknown'),
                'importance': task.get('importance', 'Unknown')
            })
        
        return JsonResponse({
            'status': 'success',
            'message': f'Top 3 task suggestions using {strategy} strategy',
            'suggestions': suggestions,
            'warnings': result['warnings']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in tasks parameter'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)