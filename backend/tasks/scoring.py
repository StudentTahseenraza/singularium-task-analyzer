import json
from datetime import datetime, date
from typing import List, Dict, Any

def detect_circular_dependencies(tasks: List[Dict]) -> List[str]:
    """
    Detect circular dependencies in the task list.
    Returns a list of error messages for circular dependencies found.
    """
    errors = []
    
    # Build adjacency list for dependency graph
    graph = {}
    task_ids = {task.get('id', i): i for i, task in enumerate(tasks)}
    
    for task in tasks:
        task_id = task.get('id', tasks.index(task))
        graph[task_id] = task.get('dependencies', [])
    
    # DFS cycle detection
    def has_cycle(node, visited, recursion_stack):
        visited[node] = True
        recursion_stack[node] = True
        
        for neighbor in graph.get(node, []):
            if neighbor not in task_ids:
                continue  # Skip invalid task IDs
            neighbor_idx = task_ids[neighbor]
            if not visited.get(neighbor_idx, False):
                if has_cycle(neighbor_idx, visited, recursion_stack):
                    return True
            elif recursion_stack.get(neighbor_idx, False):
                errors.append(f"Circular dependency detected involving task '{tasks[node].get('title', 'Unknown')}'")
                return True
        
        recursion_stack[node] = False
        return False
    
    visited = {}
    recursion_stack = {}
    
    for node in graph:
        if not visited.get(node, False):
            has_cycle(node, visited, recursion_stack)
    
    return errors

def calculate_urgency_score(due_date: str, today: date = None) -> float:
    """
    Calculate urgency score based on due date.
    Higher score = more urgent.
    """
    if today is None:
        today = date.today()
    
    if not due_date:
        return 0.3  # No due date = low urgency
    
    try:
        due = datetime.strptime(due_date, '%Y-%m-%d').date()
        days_until_due = (due - today).days
        
        if days_until_due < 0:
            # Past due - very high urgency (negative days get high score)
            return 1.0
        elif days_until_due == 0:
            # Due today - very high urgency
            return 0.9
        elif days_until_due <= 1:
            # Due tomorrow
            return 0.8
        elif days_until_due <= 3:
            # Due in 3 days
            return 0.7
        elif days_until_due <= 7:
            # Due in a week
            return 0.5
        elif days_until_due <= 14:
            # Due in two weeks
            return 0.3
        else:
            # Far future - low urgency that decays
            return max(0.1, 10 / days_until_due)
    except (ValueError, TypeError):
        return 0.3  # Invalid date format

def calculate_effort_score(estimated_hours: float) -> float:
    """
    Calculate effort score (inverted - lower effort = higher score).
    Higher score = better (less effort required).
    """
    if not estimated_hours or estimated_hours <= 0:
        return 0.5  # Default for invalid effort
    
    # Quick wins get higher scores, long tasks get lower scores
    if estimated_hours <= 1:
        return 1.0  # Very quick task
    elif estimated_hours <= 2:
        return 0.8
    elif estimated_hours <= 4:
        return 0.6
    elif estimated_hours <= 8:
        return 0.4
    else:
        # Long tasks get diminishing returns
        return max(0.1, 8 / estimated_hours)

def calculate_importance_score(importance: int) -> float:
    """
    Calculate normalized importance score.
    """
    if not importance or importance < 1 or importance > 10:
        return 0.5  # Default for invalid importance
    
    # Normalize 1-10 scale to 0.1-1.0
    return importance / 10.0

def calculate_dependency_score(task: Dict, all_tasks: List[Dict]) -> float:
    """
    Calculate dependency score - tasks that block others get higher priority.
    """
    task_id = task.get('id')
    
    # If no ID, can't calculate dependencies
    if task_id is None:
        return 0.1
    
    # Count how many other tasks depend on this task
    blocking_count = 0
    for other_task in all_tasks:
        # Get dependencies list safely
        dependencies = other_task.get('dependencies', [])
        if task_id in dependencies:
            blocking_count += 1
    
    # Normalize: 0 dependencies = 0.1, 3+ dependencies = 1.0
    if blocking_count == 0:
        return 0.1
    elif blocking_count == 1:
        return 0.4
    elif blocking_count == 2:
        return 0.7
    else:
        return 1.0

def get_strategy_weights(strategy: str) -> Dict[str, float]:
    """
    Get weighting factors for different sorting strategies.
    """
    strategies = {
        "smart_balance": {
            "urgency": 0.4,
            "importance": 0.3,
            "effort": 0.2,
            "dependencies": 0.1
        },
        "fastest_wins": {
            "urgency": 0.2,
            "importance": 0.2,
            "effort": 0.6,
            "dependencies": 0.0
        },
        "high_impact": {
            "urgency": 0.2,
            "importance": 0.6,
            "effort": 0.1,
            "dependencies": 0.1
        },
        "deadline_driven": {
            "urgency": 0.7,
            "importance": 0.2,
            "effort": 0.1,
            "dependencies": 0.0
        }
    }
    
    return strategies.get(strategy, strategies["smart_balance"])

def calculate_priority_score(task: Dict, all_tasks: List[Dict], strategy: str = "smart_balance") -> Dict[str, Any]:
    """
    Calculate overall priority score for a task using weighted factors.
    Returns the score breakdown and explanation.
    """
    # Handle missing or invalid data with defaults
    due_date = task.get('due_date')
    estimated_hours = task.get('estimated_hours', 1)
    importance = task.get('importance', 5)
    
    # Calculate individual scores
    urgency_score = calculate_urgency_score(due_date)
    effort_score = calculate_effort_score(estimated_hours)
    importance_score = calculate_importance_score(importance)
    dependency_score = calculate_dependency_score(task, all_tasks)
    
    # Get weights for the selected strategy
    weights = get_strategy_weights(strategy)
    
    # Calculate weighted total score (0-1 scale)
    total_score = (
        urgency_score * weights["urgency"] +
        importance_score * weights["importance"] +
        effort_score * weights["effort"] +
        dependency_score * weights["dependencies"]
    )
    
    # Generate explanation
    explanation_parts = []
    if urgency_score > 0.7:
        explanation_parts.append("very urgent")
    elif urgency_score > 0.4:
        explanation_parts.append("time-sensitive")
    
    if importance_score > 0.7:
        explanation_parts.append("high importance")
    elif importance_score > 0.4:
        explanation_parts.append("moderately important")
    
    if effort_score > 0.7:
        explanation_parts.append("quick win")
    elif effort_score < 0.3:
        explanation_parts.append("significant effort")
    
    if dependency_score > 0.6:
        explanation_parts.append("blocks other tasks")
    
    explanation = "This task is " + ", ".join(explanation_parts) if explanation_parts else "This task has average priority across all factors."
    
    return {
        'total_score': round(total_score, 4),
        'score_breakdown': {
            'urgency': round(urgency_score, 4),
            'importance': round(importance_score, 4),
            'effort': round(effort_score, 4),
            'dependencies': round(dependency_score, 4)
        },
        'weights_used': weights,
        'explanation': explanation
    }

def analyze_and_sort_tasks(tasks: List[Dict], strategy: str = "smart_balance") -> Dict[str, Any]:
    """
    Main function: Analyze tasks, calculate scores, and return sorted list.
    """
    # Validate input
    if not tasks:
        return {
            'sorted_tasks': [],
            'errors': ['No tasks provided'],
            'warnings': []
        }
    
    errors = []
    warnings = []
    
    # Check for circular dependencies
    circular_errors = detect_circular_dependencies(tasks)
    errors.extend(circular_errors)
    
    # Calculate scores for each task
    scored_tasks = []
    for i, task in enumerate(tasks):
        # Ensure each task has an ID for dependency tracking
        if 'id' not in task:
            task['id'] = i + 1  # Use 1-based indexing to avoid confusion with 0
            warnings.append(f"Task '{task.get('title', 'Unknown')}' assigned automatic ID {i + 1}")
        
        # Validate required fields with better error handling
        if not task.get('title'):
            errors.append(f"Task at index {i} is missing a title")
            continue
        
        # Validate and fix estimated_hours
        estimated_hours = task.get('estimated_hours')
        if estimated_hours is None or estimated_hours <= 0:
            warnings.append(f"Task '{task.get('title')}' has invalid estimated hours, using default 1")
            task['estimated_hours'] = 1
        
        # Validate and fix importance
        importance = task.get('importance')
        if importance is None or not (1 <= importance <= 10):
            warnings.append(f"Task '{task.get('title')}' has invalid importance, using default 5")
            task['importance'] = 5
        
        # Ensure dependencies is a list
        if 'dependencies' not in task:
            task['dependencies'] = []
        elif not isinstance(task['dependencies'], list):
            warnings.append(f"Task '{task.get('title')}' has invalid dependencies format, using empty list")
            task['dependencies'] = []
        
        # Calculate priority score
        try:
            score_result = calculate_priority_score(task, tasks, strategy)
            scored_task = {
                **task,
                'priority_score': score_result['total_score'],
                'score_breakdown': score_result['score_breakdown'],
                'explanation': score_result['explanation']
            }
            scored_tasks.append(scored_task)
        except Exception as e:
            errors.append(f"Error calculating score for task '{task.get('title')}': {str(e)}")
            continue
    
    # Sort by priority score (descending)
    sorted_tasks = sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)
    
    return {
        'sorted_tasks': sorted_tasks,
        'errors': errors,
        'warnings': warnings,
        'strategy_used': strategy
    }