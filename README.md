# 🎯 Smart Task Analyzer

A intelligent task management system that scores and prioritizes tasks based on multiple factors. Built for the Singularium Software Development Internship Assignment.

## 🚀 Features

- **Intelligent Priority Scoring**: Algorithm that considers urgency, importance, effort, and dependencies
- **Multiple Sorting Strategies**: Smart Balance, Fastest Wins, High Impact, and Deadline Driven
- **Circular Dependency Detection**: Automatically detects and flags circular dependencies
- **Responsive Web Interface**: Clean, modern UI that works on all devices
- **RESTful API**: Well-structured Django backend with proper error handling
- **Task Management**: Add, remove, and bulk import tasks via JSON

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Django 4.2+
- Django REST Framework
- SQLite

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 with Flexbox/Grid
- Responsive Design

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd singularium-task-analyzer
   
2. **Set up the backend**
   ```bash
   cd backend
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   # Install dependencies
   pip install -r requirements.txt
   # Run migrations
   python manage.py migrate
   # Start development server
   python manage.py runserve

Backend will be available at http://127.0.0.1:8000

Frontend Setup
Open a new terminal and navigate to frontend
cd frontend
**Start a local server**
   ```
   # Using Python (recommended)
   python -m http.server 3000
   # Or using Node.js
   npx http-server
   # Or using VS Code Live Server extension
   # Right-click index.html -> "Open with Live Server"
   GET /api/tasks/suggest/
   Get top 3 task recommendations.

   Query Parameters:

   tasks: JSON string of tasks array

   strategy: Sorting strategy (default: smart_balance)

🧠 Algorithm Explanation
The priority scoring algorithm uses a weighted approach with four key factors:

1. Urgency Score (40% in Smart Balance)
Based on due date proximity

Past due tasks get maximum urgency (1.0)

Tasks due today get high urgency (0.9)

Far future tasks get decaying scores

2. Importance Score (30% in Smart Balance)
Direct normalization of user-provided importance (1-10 scale)

Higher importance = higher score

3. Effort Score (20% in Smart Balance)
Inverted scoring: lower effort = higher score

Quick wins (<1 hour) get maximum score

Long tasks (>8 hours) get diminishing returns

4. Dependency Score (10% in Smart Balance)
Tasks that block others get higher priority

Based on number of dependent tasks

Strategy Variations:
Smart Balance: Balanced weights across all factors

Fastest Wins: Emphasizes low-effort tasks (60% weight)

High Impact: Focuses on importance (60% weight)

Deadline Driven: Prioritizes urgency (70% weight)

🎨 Design Decisions
Backend Architecture
Django without REST Framework: Chose lightweight approach since we only need basic API endpoints

Functional Views: Used function-based views for simplicity and clarity

SQLite: Default Django database - sufficient for this assignment

CORS Headers: Configured for frontend-backend communication

Algorithm Design
Weighted Scoring: Flexible system that can be easily tuned

Strategy Pattern: Easy to add new sorting strategies

Circular Dependency Detection: Graph-based DFS to prevent infinite loops

Robust Error Handling: Graceful handling of missing/invalid data

Frontend Architecture
Vanilla JavaScript: No framework dependencies for simplicity and performance

Modular Design: Separated concerns with clear function responsibilities

Local Storage: Persists tasks between sessions

Responsive CSS: Mobile-first design with Flexbox/Grid

⏱️ Time Breakdown
Project Setup & Backend Foundation: 45 minutes

Core Algorithm Development: 75 minutes

API Implementation & Testing: 40 minutes

Frontend Development: 90 minutes

Documentation & Polish: 30 minutes

Total: ~4 hours 40 minutes

🧪 Testing
Run the test suite:

bash
cd backend
python manage.py test
The project includes comprehensive unit tests for:

Scoring algorithm components

Edge cases (circular dependencies, invalid data)

API endpoints

Different strategy configurations

🚀 Future Improvements
Given more time, I would implement:

User Authentication: Personal task lists and preferences

Task Categories: Group tasks by project or context

Advanced Analytics: Historical data and trend analysis

Integration: Sync with popular task management tools

Machine Learning: Adaptive scoring based on user feedback

Real-time Updates: WebSocket support for collaborative features

Export Features: PDF reports, calendar integration

