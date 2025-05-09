from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key in production
app.config['SESSION_PERMANENT'] = False

# Comprehensive translations
translations = {
    'en': {
        'Expense Tracker': 'Expense Tracker',
        'Financial growth passport for Africa': 'Financial growth passport for Africa',
        'Personal Information': 'Personal Information',
        'Log Expense': 'Log Expense',
        'Review & Submit': 'Review & Submit',
        'First Name': 'First Name',
        'Enter your first name': 'Enter your first name',
        'Enter your first name for your report.': 'Enter your first name for your report.',
        'Looks good!': 'Looks good!',
        'First Name Required': 'First Name Required',
        'Email': 'Email',
        'Enter your email': 'Enter your email',
        'Get your expense report by email.': 'Get your expense report by email.',
        'Invalid Email': 'Invalid Email',
        'Language': 'Language',
        'Choose your language.': 'Choose your language.',
        'Language selected!': 'Language selected!',
        'Language required': 'Language required',
        'Date': 'Date',
        'Select the date of the expense.': 'Select the date of the expense.',
        'Date Required': 'Date Required',
        'Category': 'Category',
        'Select expense category.': 'Select expense category.',
        'Category Required': 'Category Required',
        'Housing': 'Housing',
        'Food': 'Food',
        'Transport': 'Transport',
        'Other': 'Other',
        'Amount': 'Amount',
        'Enter the expense amount.': 'Enter the expense amount.',
        'e.g. ₦5,000': 'e.g. ₦5,000',
        'Valid amount!': 'Valid amount!',
        'Invalid Number': 'Invalid Number',
        'Description': 'Description',
        'Optional description of the expense.': 'Optional description of the expense.',
        'e.g. Groceries for the week': 'e.g. Groceries for the week',
        'Auto Email': 'Send Report to Email',
        'Expense Dashboard': 'Expense Dashboard',
        'Welcome': 'Welcome',
        'Your Expense Summary': 'Your Expense Summary',
        'Total Expenses': 'Total Expenses',
        'Expense Breakdown': 'Expense Breakdown',
        'Expenses Over Time': 'Expenses Over Time',
        'Quick Tips': 'Quick Tips',
        'Keep tracking your expenses daily.': 'Keep tracking your expenses daily.',
        'Review your spending patterns weekly.': 'Review your spending patterns weekly.',
        'Recommended Learning': 'Recommended Learning',
        'Learn more about expense tracking!': 'Learn more about expense tracking!',
        'Whats Next': 'What’s Next',
        'Back to Home': 'Back to Home',
        'Send Email Report': 'Send Email Report',
        'Share Your Results': 'Share Your Results',
        'My Expenses': 'My Expenses',
        'My Expense Results': 'My Expense Results',
        'Check yours at': 'Check yours at',
        'Results copied to clipboard': 'Results copied to clipboard',
        'Failed to copy results': 'Failed to copy results',
        'Provide Feedback': 'Provide Feedback',
        'Join Waitlist': 'Join Waitlist',
        'Book Consultancy': 'Book Consultancy',
        'Contact Us': 'Contact Us',
        'Click to Email': 'Click to Email',
        'for support': 'for support',
        'Your Expense Report': 'Your Expense Report',
        'Dear': 'Dear',
        'Here is your expense summary.': 'Here is your expense summary.',
        'Expense Summary': 'Expense Summary',
        'Thank you for choosing Ficore Africa!': 'Thank you for choosing Ficore Africa!',
        'Expense Report Subject': 'Your Expense Report from Ficore Africa'
    },
    'ha': {
        'Expense Tracker': 'Mai Bibiyar Kashe Kuɗi',
        'Financial growth passport for Africa': 'Fasfo na ci gaban kuɗi na Afirka',
        'Personal Information': 'Bayanan Sirri',
        'Log Expense': 'Rikodin Kashe Kuɗi',
        'Review & Submit': 'Bita & Mika',
        'First Name': 'Sunan Farko',
        'Enter your first name': 'Shigar da sunanka na farko',
        'Enter your first name for your report.': 'Shigar da sunanka na farko don rahotanka.',
        'Looks good!': 'Yayi kyau!',
        'First Name Required': 'Ana buƙatar sunan farko',
        'Email': 'Imel',
        'Enter your email': 'Shigar da imel ɗinka',
        'Get your expense report by email.': 'Samu rahoton kashe kuɗinka ta imel.',
        'Invalid Email': 'Imel mara inganci',
        'Language': 'Harsa',
        'Choose your language.': 'Zaɓi harshenka.',
        'Language selected!': 'An zaɓi harshe!',
        'Language required': 'Ana buƙatar harshe',
        'Date': 'Kwanan Wata',
        'Select the date of the expense.': 'Zaɓi kwanan wata na kashe kuɗin.',
        'Date Required': 'Ana buƙatar kwanan wata',
        'Category': 'Rukuni',
        'Select expense category.': 'Zaɓi rukunin kashe kuɗi.',
        'Category Required': 'Ana buƙatar rukuni',
        'Housing': 'Gidaje',
        'Food': 'Abinci',
        'Transport': 'Sufuri',
        'Other': 'Sauri',
        'Amount': 'Adadi',
        'Enter the expense amount.': 'Shigar da adadin kashe kuɗin.',
        'e.g. ₦5,000': 'misali ₦5,000',
        'Valid amount!': 'Adadin da ya dace!',
        'Invalid Number': 'Lambar da ba ta dace ba',
        'Description': 'Bayani',
        'Optional description of the expense.': 'Bayani na zaɓi na kashe kuɗin.',
        'e.g. Groceries for the week': 'misali Sayayyar mako',
        'Auto Email': 'Aika Rahoto ta Imel',
        'Expense Dashboard': 'Dashboard na Kashe Kuɗi',
        'Welcome': 'Barka da Zuwa',
        'Your Expense Summary': 'Takaitaccen Kashe Kuɗinka',
        'Total Expenses': 'Jimlar Kashewa',
        'Expense Breakdown': 'Rarraba Kashe Kuɗi',
        'Expenses Over Time': 'Kashe Kuɗi A Tsawon Lokaci',
        'Quick Tips': 'Shawara Mai Sauri',
        'Keep tracking your expenses daily.': 'Ci gaba da bin diddigin kashe kuɗinka kowace rana.',
        'Review your spending patterns weekly.': 'Duba tsarin kashe kuɗinka kowane mako.',
        'Recommended Learning': 'Koyon da Aka Shawarta',
        'Learn more about expense tracking!': 'Ƙara koyo game da bin diddigin kashe kuɗi!',
        'Whats Next': 'Me Zai Biyo Baya',
        'Back to Home': 'Koma Gida',
        'Send Email Report': 'Aika Rahoton Imel',
        'Share Your Results': 'Raba Sakamakon Ka',
        'My Expenses': 'Kashe Kuɗina',
        'My Expense Results': 'Sakamakon Kashe Kuɗina',
        'Check yours at': 'Duba naka a',
        'Results copied to clipboard': 'An kwafi sakamakon zuwa allo',
        'Failed to copy results': 'An kasa kwafi sakamakon',
        'Provide Feedback': 'Bayar da Shawara',
        'Join Waitlist': 'Shiga Jerin Jira',
        'Book Consultancy': 'Yi Rijista don Shawara',
        'Contact Us': 'Tuntube Mu',
        'Click to Email': 'Danna don Imel',
        'for support': 'don tallafi',
        'Your Expense Report': 'Rahoton Kashe Kuɗinka',
        'Dear': 'Dear',
        'Here is your expense summary.': 'Ga takaitaccen rahoton kashe kuɗinka.',
        'Expense Summary': 'Takaitaccen Kashe Kuɗi',
        'Thank you for choosing Ficore Africa!': 'Muna godiya da zaɓar Ficore Africa!',
        'Expense Report Subject': 'Rahoton Kashe Kuɗinka daga Ficore Africa'
    }
}

class Step1Form(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    language = SelectField('Language', choices=[('en', 'English'), ('ha', 'Hausa')], validators=[DataRequired()])
    submit = SubmitField('Next')

class Step2Form(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Housing', 'Housing'), ('Food', 'Food'), ('Transport', 'Transport'), ('Other', 'Other')], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Next')

class Step3Form(FlaskForm):
    auto_email = BooleanField('Auto Email')
    submit = SubmitField('Review & Submit')

@app.route('/', methods=['GET', 'POST'])
def step1():
    form = Step1Form()
    if form.validate_on_submit():
        session['expense_data'] = {
            'first_name': form.first_name.data,
            'email': form.email.data,
            'language': form.language.data,
            'expenses': []
        }
        return redirect(url_for('step2'))
    return render_template('expense_step1.html', form=form, translations=translations.get(session.get('expense_data', {}).get('language', 'en'), translations['en']))

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    form = Step2Form()
    if form.validate_on_submit():
        expense = {
            'date': form.date.data.strftime('%Y-%m-%d'),
            'category': form.category.data,
            'amount': form.amount.data,
            'description': form.description.data or ''
        }
        session['expense_data']['expenses'].append(expense)
        return redirect(url_for('step3'))
    return render_template('expense_step2.html', form=form, translations=translations.get(session.get('expense_data', {}).get('language', 'en'), translations['en']))

@app.route('/step3', methods=['GET', 'POST'])
def step3():
    form = Step3Form()
    if form.validate_on_submit():
        session['expense_data'].update({'auto_email': form.auto_email.data})
        data = session['expense_data']
        total_expenses = sum(expense['amount'] for expense in data['expenses'])
        category_breakdown = defaultdict(float)
        for expense in data['expenses']:
            category_breakdown[expense['category']] += expense['amount']
        chart_data = {
            'labels': list(category_breakdown.keys()),
            'datasets': [{'data': list(category_breakdown.values()), 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']}]
        }
        time_data = defaultdict(float)
        for expense in data['expenses']:
            time_data[expense['date']] += expense['amount']
        bar_data = {
            'labels': list(time_data.keys()),
            'datasets': [{'data': list(time_data.values()), 'backgroundColor': '#36A2EB'}]
        }
        flash('Expenses logged successfully!', 'success')
        if data.get('auto_email') and data.get('email'):
            send_expense_email(data, total_expenses, chart_data, bar_data)
        return render_template('expense_dashboard.html',
                              translations=translations[data['language']],
                              first_name=data['first_name'],
                              total_expenses=total_expenses,
                              expenses=data['expenses'],
                              chart_data=json.dumps(chart_data),
                              bar_data=json.dumps(bar_data),
                              course_url="https://example.com/expense-tracking-course",
                              course_title="Expense Tracking 101",
                              user_data_json=json.dumps(data))
    return render_template('expense_step3.html', form=form, translations=translations.get(session.get('expense_data', {}).get('language', 'en'), translations['en']), expenses=session.get('expense_data', {}).get('expenses', []))

@app.route('/send_expense_email', methods=['POST'])
def send_expense_email():
    data = json.loads(request.form['user_data_json'])
    total_expenses = sum(expense['amount'] for expense in data['expenses'])
    category_breakdown = defaultdict(float)
    for expense in data['expenses']:
        category_breakdown[expense['category']] += expense['amount']
    chart_data = {
        'labels': list(category_breakdown.keys()),
        'datasets': [{'data': list(category_breakdown.values()), 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']}]
    }
    time_data = defaultdict(float)
    for expense in data['expenses']:
        time_data[expense['date']] += expense['amount']
    bar_data = {
        'labels': list(time_data.keys()),
        'datasets': [{'data': list(time_data.values()), 'backgroundColor': '#36A2EB'}]
    }
    send_expense_email(data, total_expenses, chart_data, bar_data)
    flash('Email report sent successfully!', 'success')
    return redirect(url_for('step3'))

def send_expense_email(data, total_expenses, chart_data, bar_data):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = translations[data['language']]['Expense Report Subject']
    msg['From'] = 'ficore.ai.africa@gmail.com'  # Replace with your email
    msg['To'] = data['email']

    html = render_template('expense_email.html',
                          translations=translations[data['language']],
                          user_name=data['first_name'],
                          total_expenses=total_expenses,
                          expenses=data['expenses'],
                          FEEDBACK_FORM_URL="https://example.com/feedback",
                          WAITLIST_FORM_URL="https://example.com/waitlist",
                          CONSULTANCY_FORM_URL="https://example.com/consultancy",
                          course_url="https://example.com/expense-tracking-course",
                          course_title="Expense Tracking 101")
    part = MIMEText(html, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('ficore.ai.africa@gmail.com', 'your-password')  # Replace with your email password
            server.sendmail('ficore.ai.africa@gmail.com', data['email'], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True)