// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/tasks';

// Global state
let tasks = [];
let nextTaskId = 1;

// DOM Elements
const taskForm = document.getElementById('taskForm');
const bulkInput = document.getElementById('bulkInput');
const loadBulkBtn = document.getElementById('loadBulk');
const taskList = document.getElementById('taskList');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const strategySelect = document.getElementById('strategySelect');
const outputSection = document.getElementById('outputSection');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const suggestionsList = document.getElementById('suggestionsList');
const resultsList = document.getElementById('resultsList');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadTasksFromStorage();
    attachEventListeners();
    updateTaskListDisplay();
});

// Event Listeners
function attachEventListeners() {
    taskForm.addEventListener('submit', handleAddTask);
    loadBulkBtn.addEventListener('click', handleBulkLoad);
    analyzeBtn.addEventListener('click', handleAnalyze);
    clearBtn.addEventListener('click', handleClearAll);
}

// Task Management Functions
function handleAddTask(e) {
    e.preventDefault();
    
    const formData = new FormData(taskForm);
    const title = formData.get('title').trim();
    const dueDate = formData.get('dueDate');
    const estimatedHours = parseFloat(formData.get('estimatedHours'));
    const importance = parseInt(formData.get('importance'));
    const dependencies = formData.get('dependencies').trim();
    
    // Validate required fields
    if (!title) {
        showError('Task title is required');
        return;
    }
    
    if (!estimatedHours || estimatedHours <= 0) {
        showError('Estimated hours must be greater than 0');
        return;
    }
    
    if (!importance || importance < 1 || importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }
    
    // Parse dependencies
    let dependencyList = [];
    if (dependencies) {
        dependencyList = dependencies.split(',')
            .map(id => parseInt(id.trim()))
            .filter(id => !isNaN(id));
    }
    
    // Create task object
    const task = {
        id: nextTaskId++,
        title: title,
        due_date: dueDate || null,
        estimated_hours: estimatedHours,
        importance: importance,
        dependencies: dependencyList
    };
    
    tasks.push(task);
    saveTasksToStorage();
    updateTaskListDisplay();
    taskForm.reset();
    
    showSuccess('Task added successfully!');
}

function handleBulkLoad() {
    try {
        const jsonText = bulkInput.value.trim();
        if (!jsonText) {
            showError('Please paste some JSON data');
            return;
        }
        
        const parsedTasks = JSON.parse(jsonText);
        
        if (!Array.isArray(parsedTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate and add tasks
        parsedTasks.forEach(task => {
            const newTask = {
                id: nextTaskId++,
                title: task.title || 'Untitled Task',
                due_date: task.due_date || null,
                estimated_hours: task.estimated_hours || 1,
                importance: task.importance || 5,
                dependencies: task.dependencies || []
            };
            tasks.push(newTask);
        });
        
        saveTasksToStorage();
        updateTaskListDisplay();
        showSuccess(`Successfully loaded ${parsedTasks.length} tasks from JSON!`);
        bulkInput.value = '';
        
    } catch (error) {
        showError('Invalid JSON format. Please check your input.');
        console.error('JSON Parse Error:', error);
    }
}

function removeTask(taskId) {
    tasks = tasks.filter(task => task.id !== taskId);
    saveTasksToStorage();
    updateTaskListDisplay();
    showSuccess('Task removed');
}

function handleClearAll() {
    if (tasks.length === 0) {
        showError('No tasks to clear');
        return;
    }
    
    if (confirm('Are you sure you want to clear all tasks?')) {
        tasks = [];
        nextTaskId = 1;
        saveTasksToStorage();
        updateTaskListDisplay();
        hideOutput();
        showSuccess('All tasks cleared');
    }
}

// Display Functions
function updateTaskListDisplay() {
    if (tasks.length === 0) {
        taskList.innerHTML = '<p class="empty-message">No tasks added yet. Add tasks using the form above or paste JSON.</p>';
        return;
    }
    
    taskList.innerHTML = tasks.map(task => `
        <div class="task-item">
            <div class="task-info">
                <h4>${escapeHtml(task.title)}</h4>
                <div class="task-meta">
                    ${task.due_date ? `Due: ${task.due_date} • ` : ''}
                    ${task.estimated_hours}h • 
                    Importance: ${task.importance}/10
                    ${task.dependencies.length > 0 ? `• Depends on: ${task.dependencies.join(', ')}` : ''}
                </div>
            </div>
            <button class="remove-task" onclick="removeTask(${task.id})">Remove</button>
        </div>
    `).join('');
}

function showSuccess(message) {
    // Simple success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #48bb78;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function showError(message) {
    errorMessage.textContent = message;
    errorState.style.display = 'block';
    
    setTimeout(() => {
        errorState.style.display = 'none';
    }, 5000);
}

function hideOutput() {
    outputSection.style.display = 'none';
}

// API Communication
async function handleAnalyze() {
    if (tasks.length === 0) {
        showError('Please add at least one task to analyze');
        return;
    }
    
    const strategy = strategySelect.value;
    
    // Show loading state
    outputSection.style.display = 'block';
    loadingState.style.display = 'block';
    errorState.style.display = 'none';
    suggestionsList.innerHTML = '';
    resultsList.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Analysis failed');
        }
        
        if (data.status === 'success') {
            displayResults(data.data);
        } else {
            throw new Error(data.message || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error('Analysis Error:', error);
        showError(`Analysis failed: ${error.message}`);
    } finally {
        loadingState.style.display = 'none';
    }
}

function displayResults(data) {
    // Display top suggestions
    const topTasks = data.sorted_tasks.slice(0, 3);
    suggestionsList.innerHTML = topTasks.map((task, index) => `
        <div class="suggestion-item rank-${index + 1}">
            <div class="suggestion-rank">#${index + 1}</div>
            <h4>${escapeHtml(task.title)}</h4>
            <div class="suggestion-meta">
                <strong>Priority Score: ${task.priority_score.toFixed(3)}</strong><br>
                Due: ${task.due_date || 'Not specified'} • 
                Effort: ${task.estimated_hours}h • 
                Importance: ${task.importance}/10
            </div>
            <div class="suggestion-reason">${task.explanation}</div>
        </div>
    `).join('');
    
    // Display full analysis results
    resultsList.innerHTML = data.sorted_tasks.map(task => {
        const priorityClass = getPriorityClass(task.priority_score);
        return `
            <div class="result-item">
                <div class="result-header">
                    <div class="result-title">${escapeHtml(task.title)}</div>
                    <div class="priority-score ${priorityClass}">
                        Score: ${task.priority_score.toFixed(3)}
                    </div>
                </div>
                
                <div class="result-meta">
                    <span>📅 Due: ${task.due_date || 'Not specified'}</span>
                    <span>⏱️ Effort: ${task.estimated_hours} hours</span>
                    <span>💎 Importance: ${task.importance}/10</span>
                    <span>🔗 Dependencies: ${task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}</span>
                </div>
                
                <div class="score-breakdown">
                    <h5>Score Breakdown:</h5>
                    ${Object.entries(task.score_breakdown).map(([factor, score]) => `
                        <div class="breakdown-item">
                            <span class="breakdown-label">${factor.charAt(0).toUpperCase() + factor.slice(1)}:</span>
                            <span class="breakdown-value">${score.toFixed(3)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="result-explanation">
                    <strong>Why this priority?</strong> ${task.explanation}
                </div>
            </div>
        `;
    }).join('');
}

function getPriorityClass(score) {
    if (score >= 0.7) return 'priority-high';
    if (score >= 0.4) return 'priority-medium';
    return 'priority-low';
}

// Utility Functions
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Local Storage Functions
function saveTasksToStorage() {
    localStorage.setItem('smartTaskAnalyzer_tasks', JSON.stringify(tasks));
    localStorage.setItem('smartTaskAnalyzer_nextId', nextTaskId.toString());
}

function loadTasksFromStorage() {
    const savedTasks = localStorage.getItem('smartTaskAnalyzer_tasks');
    const savedNextId = localStorage.getItem('smartTaskAnalyzer_nextId');
    
    if (savedTasks) {
        tasks = JSON.parse(savedTasks);
    }
    
    if (savedNextId) {
        nextTaskId = parseInt(savedNextId);
    }
}

// Sample Data Loader (for testing)
function loadSampleData() {
    const sampleData = [
        {
            "title": "Fix critical login bug",
            "due_date": "2025-11-28",
            "estimated_hours": 4,
            "importance": 9,
            "dependencies": [2, 3]
        },
        {
            "title": "Write API documentation",
            "due_date": "2025-12-05",
            "estimated_hours": 6,
            "importance": 7,
            "dependencies": [1]
        },
        {
            "title": "Update CSS styling",
            "due_date": null,
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": []
        },
        {
            "title": "Implement user authentication",
            "due_date": "2025-12-10",
            "estimated_hours": 8,
            "importance": 8,
            "dependencies": []
        }
    ];
    
    bulkInput.value = JSON.stringify(sampleData, null, 2);
    showSuccess('Sample data loaded into JSON field. Click "Load Tasks from JSON" to add them.');
}

// Add sample data button for testing (optional)
document.addEventListener('DOMContentLoaded', function() {
    const sampleBtn = document.createElement('button');
    sampleBtn.textContent = 'Load Sample Data';
    sampleBtn.className = 'btn btn-secondary';
    sampleBtn.style.marginLeft = '10px';
    sampleBtn.onclick = loadSampleData;
    
    document.querySelector('.bulk-input h3').appendChild(sampleBtn);
});