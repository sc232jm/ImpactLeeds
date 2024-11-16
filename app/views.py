from flask import Flask, render_template, redirect, url_for, request, flash
from app import app, db, login_manager
from markupsafe import Markup
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Petition, Signature
from app.forms import SignupForm, LoginForm

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
@login_required
def sign_petition(petition_id):
    reason_text = request.form['reason']
    petition = Petition.query.get(petition_id)
    if petition:
        new_signature = Signature(
            author_id=current_user.id,
            petition_id=petition_id,
            reason=reason_text
        )
        db.session.add(new_signature)
        db.session.commit()
        db.session.commit()
    return redirect(url_for('petition_detail', petition_id=petition_id))



@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_petition():
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        description = request.form['description']
        tag_line = request.form['tag_line']

        new_petition = Petition(
            title=title,
            tag_line=tag_line,
            description=description,
            author_id=current_user.id
        )
        db.session.add(new_petition)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
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
