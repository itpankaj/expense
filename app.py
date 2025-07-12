from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_key'

# File to store expenses
EXPENSES_FILE = 'expenses.json'

def load_expenses():
    """Load expenses from the JSON file"""
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_expenses(expenses):
    """Save expenses to the JSON file"""
    with open(EXPENSES_FILE, 'w') as file:
        json.dump(expenses, file, indent=4)

@app.route('/')
def index():
    """Main page showing expense summary"""
    expenses = load_expenses()
    
    # Calculate total expenses
    total = sum(expense['amount'] for expense in expenses)
    
    # Group expenses by category
    categories = {}
    for expense in expenses:
        category = expense['category']
        if category in categories:
            categories[category] += expense['amount']
        else:
            categories[category] = expense['amount']
    
    # Load budget if exists
    budget = 0
    if os.path.exists('budget.json'):
        with open('budget.json', 'r') as file:
            try:
                budget_data = json.load(file)
                budget = budget_data.get('monthly_budget', 0)
            except json.JSONDecodeError:
                budget = 0
    
    return render_template('index.html', expenses=expenses, total=total, categories=categories, budget=budget, categories_json=json.dumps(categories))

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        date_str = request.form['date']
        category = request.form['category']
        amount_str = request.form['amount']
        description = request.form['description']
        
        # Validate inputs
        errors = []
        
        # Validate date format
        try:
            # Parse date to ensure it's in the correct format
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format")
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Amount must be positive")
        except ValueError:
            errors.append("Amount must be a number")
        
        # Validate category and description
        if not category:
            errors.append("Category is required")
        if not description:
            errors.append("Description is required")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('add.html', today_date=today_date)
        
        # Create expense dictionary
        expense = {
            'date': date,
            'category': category,
            'amount': amount,
            'description': description
        }
        
        # Load existing expenses, add new one, and save
        expenses = load_expenses()
        expenses.append(expense)
        save_expenses(expenses)
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html', today_date=today_date)

@app.route('/view')
def view_expenses():
    """View all expenses"""
    expenses = load_expenses()
    return render_template('view.html', expenses=expenses, expenses_json=json.dumps(expenses))

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    """Set monthly budget"""
    if request.method == 'POST':
        try:
            budget = float(request.form['budget'])
            if budget <= 0:
                flash('Budget must be positive', 'error')
                return render_template('budget.html')
            
            # Store budget in a file
            with open('budget.json', 'w') as file:
                json.dump({'monthly_budget': budget}, file)
            
            flash('Budget set successfully!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Budget must be a number', 'error')
    
    # Load current budget if exists
    budget = 0
    if os.path.exists('budget.json'):
        with open('budget.json', 'r') as file:
            try:
                budget_data = json.load(file)
                budget = budget_data.get('monthly_budget', 0)
            except json.JSONDecodeError:
                budget = 0
    
    return render_template('budget.html', budget=budget)

if __name__ == '__main__':
    app.run(debug=True)
