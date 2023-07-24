from flask import Blueprint, render_template, request, redirect, url_for, render_template, request, session
from flask_login import login_user, current_user, logout_user, login_required
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from mongoengine.errors import NotUniqueError
from models.user import User
from models.message import Message
from models.job_postings import JobPosting
from flask import Flask, request
import spacy
from spacy.matcher import Matcher
import string
import re
import datetime
from flask import jsonify, request
import requests



# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Create a MongoDB client
client = MongoClient('mongodb+srv://bridge:1234@bridge.oisqkif.mongodb.net/bridge?retryWrites=true&w=majority')

# Access the database and collection
db = client['bridge']  # Replace 'Bridge' with your database name
users_collection = db['user']  # Replace 'bridge' with your collection name
# Access the database and collection for job postings
job_postings_collection = db['job_postings']


# Create an instance of the Bcrypt class
bcrypt = Bcrypt()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Check if a user with the same username already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new User instance
        new_user = User(username=username, password=hashed_password)

        try:
            # Insert the new user into the MongoDB collection
            new_user.save()
        except NotUniqueError:
            error = 'An error occurred while creating the user.'
            return render_template('signup.html', error=error)

        # Redirect the user to the login page
        return redirect(url_for('auth.login'))

    # Render the signup form
    return render_template('signup.html')


# ...

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Query the MongoDB collection for the user with the given username
        user = users_collection.find_one({'username': username})

        if user and 'password' in user:
            # Use Flask-Login's login_user() to manage the user session
            if bcrypt.check_password_hash(user['password'], password):
                user_obj = User.objects.get(id=user['_id'])  # Retrieve the User object based on the ObjectId
                login_user(user_obj)

                # Render the loading page with the JavaScript redirection
                return render_template('loading.html', next_page=url_for('auth.landing'))

        # Display an error message if the credentials are invalid
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

    # Render the login form
    return render_template('login.html')

# ...


@auth_bp.route('/logout')
@login_required  # Use the login_required decorator to protect this route
def logout():
    # Use Flask-Login's logout_user() to handle the user session
    logout_user()

    # Redirect to a logged-out page or the home page
    return redirect(url_for('auth.login'))


@auth_bp.route('/landing')
@login_required
def landing():
    
     # Check if the user is logged in and authenticated
    if current_user.is_authenticated:
        # Render the landing page
         return render_template('landing.html')
    else:
    # If the user is not authenticated, redirect to the login page
        return redirect(url_for('auth.login'))


@auth_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save the message to the database or perform any other desired action

        # Set the message_sent flag to True
        message_sent = True

        # Render the contact form with the success message
        return render_template('contact.html', message_sent=message_sent)

    # Render the contact form
    return render_template('contact.html')


@auth_bp.route('/aboutUs')
def aboutUs():
    # Render the aboutUs page
    return render_template('aboutUs.html')

@auth_bp.route('/loading')
def load():
    # Render the aboutUs page
    return render_template('loading.html')

@auth_bp.route('/landingContact')
@login_required
def landingContact():
    # Render the aboutUs page
    return render_template('landingContact.html')

@auth_bp.route('/landingAboutUs')
@login_required
def landingAboutUs():
    # Render the aboutUs page
    return render_template('landingAboutUs.html')

# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')

# Define an extended list of gendered terms to check for
gendered_terms = ['he', 'his', 'him', 'himself', 'she', 'her', 'hers', 'herself', 'male', 'female', 'man', 'woman']

# Define an extended list of non-gendered alternative suggestions
alternative_suggestions = ['they', 'their', 'them', 'themselves', 'person', 'individual']

# Define a list of patterns for identifying noun phrases with gendered terms
noun_phrase_patterns = [
    [{'POS': 'NOUN'}, {'POS': 'VERB', 'OP': '*'}, {'LOWER': {'IN': gendered_terms}}]
]

# Create a Matcher object
matcher = Matcher(nlp.vocab)

# Add the noun phrase pattern to the matcher
matcher.add('gendered_noun_phrase', noun_phrase_patterns)



# ...


# Create a dictionary of gendered terms and their corresponding alternatives
gender_alternatives = {
    'he': 'they',
    'his': 'their',
    'him': 'them',
    'himself': 'themselves',
    'she': 'they',
    'her': 'them',
    'hers': 'theirs',
    'herself': 'themselves',
    'man': 'person',
    'woman': 'person',
    'male': 'individual',
    'female': 'individual',
    'job': 'position',
}

# ...




@auth_bp.route('/gender_bias_analysis', methods=['GET', 'POST'])
@login_required
def gender_bias_analysis():
    if request.method == 'POST':
        # Get the job posting text from the form
        job_posting = request.form['job_posting']

        # Perform gender bias analysis using spaCy
        doc = nlp(job_posting)

        # Initialize counters for gendered terms and biased noun phrases
        gendered_count = 0
        biased_noun_phrases = []

        # Initialize lists for gender terms and their alternatives
        gender_terms = []
        alternative_terms = []

        # Iterate over tokens in the document
        for token in doc:
            # Check if the token is a gendered term
            if token.lower_ in gendered_terms:
                gendered_count += 1
                gender_terms.append(token.text)

                # Check if the token has a corresponding alternative term
                alternative_term = gender_alternatives.get(token.lower_)
                if alternative_term:
                    alternative_terms.append(alternative_term)
                else:
                    alternative_terms.append(token.text)
            else:
                alternative_terms.append(token.text)

            # Check if the token is part of a gendered noun phrase
            matches = matcher(doc)
            for match_id, start, end in matches:
                noun_phrase = doc[start:end]
                biased_noun_phrases.append(noun_phrase.text)

        # Generate non-gendered alternatives for biased noun phrases
        alternative_phrases = []
        for phrase in biased_noun_phrases:
            alternative_tokens = []
            for token in nlp(phrase):
                if token.lower_ in gendered_terms:
                    alternative_term = gender_alternatives.get(token.lower_)
                    if alternative_term:
                        alternative_tokens.append(alternative_term)
                    else:
                        alternative_tokens.append(token.text)
                else:
                    alternative_tokens.append(token.text)

            alternative_phrase = ' '.join(alternative_tokens)
            alternative_phrases.append(alternative_phrase)

        # Generate a list of alternative terms for gender terms
        alternative_terms = [gender_alternatives.get(term.lower(), term) for term in gender_terms]

        # Perform additional analysis or customization based on your requirements
        # For example, calculate the ratio of gendered terms to total words
        total_terms = len([token for token in doc if token.text not in string.punctuation])
        gendered_ratio = round(gendered_count / total_terms * 100, 1) if total_terms > 0 else 0

        # Identify specific bias patterns or keywords
        bias_patterns = ['managerial positions', 'nurturing qualities', 'technical expertise']
        biased_keywords = [token.text for token in doc if token.text.lower() in bias_patterns]

        # Generate a new posting with alternative terms and correct capitalization and punctuation
        new_tokens = []
        capitalize_next = True
        for token in doc:
            if token.text.lower() == 'given':
                new_tokens.append(token.text)
            elif token.lower_ in gendered_terms:
                alternative_term = gender_alternatives.get(token.lower_)
                if alternative_term:
                    new_tokens.append(alternative_term)
                else:
                    new_tokens.append(token.text)
                capitalize_next = False
            elif token.lower_ == 'his' or token.lower_ == 'her':
                # Check the context to determine the appropriate alternative
                if token.head.tag_ == 'PRP$':
                    alternative_term = gender_alternatives.get(token.head.text.lower())
                    if alternative_term:
                        new_tokens.append(alternative_term)
                    else:
                        new_tokens.append(token.text)
                else:
                    new_tokens.append(token.text)
                capitalize_next = False
            elif token.lower_ == 'they':
                # Check if "they" is followed by "is" and replace "is" with "are"
                if token.i + 1 < len(doc) and doc[token.i + 1].lower_ == 'is':
                    new_tokens.append('they')
                    new_tokens.append('are')
                    capitalize_next = False
                else:
                    new_tokens.append(token.text)
                    capitalize_next = False
            elif token.lower_ == 'is' and new_tokens[-1].lower() == 'they':
                new_tokens.append('are')  # Replace "is" with "are"
                capitalize_next = False
            else:
                if capitalize_next:
                    new_tokens.append(token.text.capitalize())
                else:
                    new_tokens.append(token.text)

                if re.match(r'[.!?]', token.text):
                    capitalize_next = True
                else:
                    capitalize_next = False

        # Join the new tokens into a new posting string
        new_posting = ' '.join(new_tokens)

        # Remove duplicate full stops
        new_posting = re.sub(r'\.{2,}', '.', new_posting)

        # Add a full stop at the end of a sentence if missing
        if not new_posting.endswith(('.', '!', '?')):
            new_posting += '.'

        # Remove the space before a full stop and keep a space after a full stop
        new_posting = re.sub(r'\s*(?<!\.)\.(?!\w)', '. ', new_posting)

        # Capitalize the first letter of each sentence after a full stop
        sentences = re.split(r'(?<=[.!?])\s+', new_posting)
        new_posting = ' '.join(sentence.capitalize() for sentence in sentences)

        # Perform additional fixes for grammar and capitalization
        new_posting = re.sub(r'\bwoman\b', 'person', new_posting, flags=re.IGNORECASE)
        new_posting = re.sub(r'\bwomen\b', 'people', new_posting, flags=re.IGNORECASE)

        # Customize the analysis results based on your requirements
        # You can add more variables, calculations, or conditions here

        # Create a new JobPosting document and save it to the database
        new_job_posting = JobPosting(
            title="Job Title",  # Set the job posting title as desired
            content= new_posting,
            user=current_user,  # Reference to the current user (assuming you have a way to get the current user)
            created_at=datetime.datetime.now()
        )
        new_job_posting.save()

        # Add the new job posting to the user's job postings list
        current_user.job_postings.append(new_job_posting)
        current_user.save()

        # Return the analysis results, gender terms, and alternative terms to the genderBias.html template
        return render_template('genderBias.html', job_posting=job_posting, gendered_count=gendered_count,
                               gendered_ratio=gendered_ratio, biased_noun_phrases=biased_noun_phrases,
                               alternative_phrases=alternative_phrases, biased_keywords=biased_keywords,
                               gender_terms=gender_terms, alternative_terms=alternative_terms,
                               new_posting=new_posting, given=job_posting)

    # Handle GET request if needed
    return render_template('genderBias.html')

@auth_bp.route('/job_postings', methods=['GET'])
@login_required
def job_postings():
    # Assuming you have a way to get the current user
    user = current_user
    job_postings = user.job_postings

    # Render a template to display the user's job postings
    return render_template('job_postings.html', job_postings=job_postings)

@auth_bp.route('/delete_job_posting/<job_posting_id>', methods=['POST'])
def delete_job_posting(job_posting_id):
    # Assuming you have a way to get the current user
    user = current_user
    job_posting = JobPosting.objects(id=job_posting_id).first()

    if job_posting and job_posting.user == user:
        # Remove the job posting from the user's job_postings list
        user.job_postings.remove(job_posting)
        user.save()

        # Delete the job posting from the database
        job_posting.delete()

    # Redirect the user back to the job_postings page
    return redirect(url_for('auth.job_postings'))


@auth_bp.route('/job_salaries', methods=['GET', 'POST'])
@login_required
def job_salaries():
    job_listings = []

    if request.method == 'POST':
        # Get the job title and country input from the form
        job_title = request.form['job_title']
        country = request.form['country']

        # Prepare the API request parameters
        url = "https://job-salary-data.p.rapidapi.com/job-salary"
        querystring = {"job_title": job_title, "location": country}

        # Set your Rapid API key here
        headers = {
            "X-RapidAPI-Key": "1f4ec03288msh5c158ffaaaf05a9p1030cejsnd3deacdf1fda",
            "X-RapidAPI-Host": "job-salary-data.p.rapidapi.com"
        }

        # Send the API request
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        # Print the raw API response data
        print(data)

        # Parse the response data and extract the required information
        for item in data.get('data', []):
            location_parts = item['location'].split(',')
            city = location_parts[-1].strip() if len(location_parts) > 1 else location_parts[0].strip()

            job_listing = {
                'job_title': item['job_title'],
                'country': country,
                'salary': item['median_salary'],
                'salary_currency': item['salary_currency'],
                'salary_period': item['salary_period']
            }
            job_listings.append(job_listing)

    # Render the job_search.html template along with the salary results (if available)
    return render_template('job_search.html', job_listings=job_listings)
