from flask import Flask, render_template, redirect, url_for, request
from app import app
from markupsafe import Markup

petitions = [
    {
        'id': 1,
        'title': 'Improve Library Hours',
        'tag_line': 'Statue of Owen Johnson',
        'description': 'Extend the library hours during exam periods.',
        'author': 'Jane Doe',
        'created_at': '2024-11-15',
        'signaturesNum': 320,
        'target_signatures': 500,
        'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJTcLeoDwmVmpJHNs8Ni9-4MHDhcFDQ-yr-g&s',
        'status': 'Victory!',
        'status_badge': 'success',
        'signatures': [
            {'author': 'Student A', 'text': 'Great initiative!'}
        ],
        'signers': []
    },
    {
        'id': 2,
        'title': 'Statue of Owen Johnson',
        'tag_line': 'Statue of Owen Johnson',
        'description': 'Introduce a statue of our lord and saviour Owen Johnson.',
        'author': 'John Smith',
        'created_at': '2024-11-14',
        'signaturesNum': 450,
        'target_signatures': 1000,
        'image_url': 'https://www.leeds.ac.uk/images/resized/800x400-0-0-1-80-Parkinson_building_from_road_800x400.jpg',
        'status': 'Waiting',
        'status_badge': 'warning',
        'signatures': []
    }
]


@app.route('/')
def home():
    return render_template('home.html', petitions=petitions)


@app.route('/browse')
def browse():
    return render_template('browse.html', petitions=petitions)


@app.route('/petition/<int:petition_id>')
def petition_detail(petition_id):
    petition = next((p for p in petitions if p['id'] == petition_id), None)
    if not petition:
        return "Petition not found", 404
    return render_template('petition_detail.html', petition=petition)


@app.route('/petition/<int:petition_id>/sign', methods=['POST'])
def sign_petition(petition_id):
    reason_text = request.form['reason']
    petition = next((p for p in petitions if p['id'] == petition_id), None)
    if petition:
        petition['signaturesNum'] += 1
        petition['signers'].append({'reason': reason_text})
    return redirect(url_for('petition_detail', petition_id=petition_id))


@app.route('/create', methods=['GET', 'POST'])
def create_petition():
    if request.method == 'POST':
        # Process the form data and save the petition
        category = request.form['category']
        title = request.form['title']
        description = request.form['description']
        tag_line = request.form['tag_line']
        # Add logic to save the petition
        return redirect(url_for('home'))
    return render_template('create.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add login logic here
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Add signup logic here
        return redirect(url_for('home'))
    return render_template('signup.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
    # Add settings logic here
        return redirect(url_for('home'))
    return render_template('settings.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query', '').lower()
    if len(query) < 3:
        return render_template('search.html', results=[], message="Query must be more than 3 characters long.")

    def highlight(text, query):
        start = 0
        highlighted = ""
        lower_text = text.lower()
        while start < len(text):
            index = lower_text.find(query, start)
            if index == -1:
                highlighted += text[start:]
                break
            highlighted += text[start:index] + f"<mark>{text[index:index + len(query)]}</mark>"
            start = index + len(query)
        return Markup(highlighted)

    results = [
        {
            'id': petition['id'],
            'title': highlight(petition['title'], query),
            'description': highlight(petition['description'], query),
            'author': highlight(petition['author'], query),
            'created_at': petition['created_at'],
            'signaturesNum': petition['signaturesNum'],
            'image_url': petition['image_url'],
            'status': petition['status'],
            'status_badge': petition['status_badge']
        }
        for petition in petitions if query in petition['title'].lower() or
                                     query in petition['description'].lower() or
                                     query in petition['author'].lower()
    ]

    return render_template('search.html', results=results)