from flask import render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db, login_manager
from app.models import User, Petition, Signature, Like
from app.forms import SignupForm, LoginForm, CreatePetitionForm, SignPetitionForm, EditPetitionForm, EditSettingsForm

import markdown
from profanity_check import predict

# Flask Login: https://flask-login.readthedocs.io/en/latest/#how-it-works
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Additional security layer to prevent unauthorised access
@app.route('/lockdown', methods=['GET', 'POST'])
def lockdown():
    if request.method == 'POST':
        lockdown_key = request.form.get('lockdown_key')
        if lockdown_key == app.config.get('SECRET_KEY'):
            session['lockdown_passed'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid security key. Please try again.', 'danger')
            return render_template('lockdown.html')

    return render_template('lockdown.html')

# Lockdown access control
@app.before_request
def check_lockdown():
    if app.config.get('LOCKDOWN_ENABLED') and 'lockdown_passed' not in session and request.endpoint not in ['lockdown', 'static']:
        return redirect(url_for('lockdown'))

@app.route('/', methods=['GET'])
def home():
    """
    Renders the home page, providing the top 5 petitions for the carousel.
    :return: The rendered template
    """
    petitions = Petition.query.all()

    top_petitions = sorted(petitions, key=lambda p: len(p.signatures), reverse=True)[:5]

    return render_template('home.html', petitions=top_petitions)


@app.route('/browse', methods=['GET'])
def browse():
    """
    Renders the browse petition page. The petition list can be filtered by a paramater
    :return: The rendered template
    """
    category = request.args.get('filter', 'all')

    if category == 'popular':
        petitions = Petition.query.all()

        petitions = sorted(petitions, key=lambda p: len(p.signatures), reverse=True)
    elif category == 'latest':
        petitions = Petition.query.order_by(Petition.created_at.desc()).all()
    elif category == 'victories':
        petitions = Petition.query.filter(Petition.status_badges.contains(['Victory'])).all()
    else:
        petitions = Petition.query.all()

    return render_template('browse.html', petitions=petitions)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Renders the settings page and accepts POST requests to update the user profile
    :return: The rendered template or success messages
    """
    # https://stackoverflow.com/questions/6196622/using-wtforms-populate-obj-method-with-flask-micro-framework
    form = EditSettingsForm(obj=current_user)

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() and form.username.data != current_user.username:
            flash('Username already taken', 'error')
            return redirect(url_for('settings'))

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('TOAST|Settings updated successfully!', 'success')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'POST':
        # Send JSON response back to invalid POST request
        return jsonify({'success': False, 'message': 'Invalid edit body'}), 400

    return render_template('settings.html', form=form)


@app.route('/user/<username>')
@login_required
def user_profile(username):
    """
    Renders the specified user profile from their username
    :param username: The username of the user to render
    :return: The rendered template with the specified user data
    """
    user = User.query.filter_by(username=username).first_or_404()
    created_petitions = Petition.query.filter_by(author_id=user.id).all()
    signed_petitions = Petition.query.join(Signature).filter(Signature.author_id == user.id).all()

    user_about_me = markdown.markdown(user.about_me) if user.about_me else None

    return render_template('user_profile.html', user=user, created_petitions=created_petitions,
                           signed_petitions=signed_petitions, user_about_me=user_about_me)


@app.route('/petition/<int:petition_id>', methods=['GET'])
@login_required
def petition_detail(petition_id):
    """
    Renders the specified petition from the petition id
    :param petition_id: The id of the petition
    :return: The rendered template with the specified petition data
    """
    petition = Petition.query.get_or_404(petition_id)
    form = SignPetitionForm()

    sort_by = request.args.get('filter', 'most_recent')

    if sort_by == 'most_liked':
        signatures = db.session.query(Signature, db.func.count(Like.id).label('like_count')).filter_by(
            petition_id=petition_id).outerjoin(Like, Signature.id == Like.signature_id).group_by(Signature.id).order_by(
            db.func.count(Like.id).desc()).all()
    else:
        signatures = Signature.query.filter_by(petition_id=petition_id).order_by(Signature.signed_at.desc()).all()

    # Calculate the target signatures
    signatures_num = len(signatures)
    if signatures_num == 0:
        target_signatures = 5
    else:
        target_signatures = (signatures_num // 5 + 1) * 5

    # Render the description in Markdown
    petition.description = markdown.markdown(petition.description)

    # Check if the user has already signed the petition
    already_signed = Signature.query.filter_by(petition_id=petition_id, author_id=current_user.id).first() is not None
    can_sign = not already_signed and 'Victory' not in petition.status_badges and 'Closed' not in petition.status_badges

    return render_template('petition_detail.html', petition=petition, signatures=signatures,
                           target_signatures=target_signatures, form=form, can_sign=can_sign, sort_by=sort_by)


@app.route('/my_petitions')
@login_required
def my_petitions():
    """
    Renders the petitions owned by the authed user
    :return: The rendered template
    """
    petitions = Petition.query.filter_by(author_id=current_user.id).all()
    return render_template('my_petitions.html', petitions=petitions)


@app.route('/petition/delete', methods=['POST'])
@login_required
def delete_petition():
    """
    Handles the deletion of a petition from an authed users AJAX request
    :return: A JSON response of the deletion operation
    """
    data = request.get_json()
    petition_id = data.get('petition_id')

    if petition_id is None:
        # Send JSON response back to invalid POST request
        return jsonify({'error': 'Invalid petition ID'}), 400

    petition = Petition.query.get_or_404(petition_id)

    if petition.author_id != current_user.id:
        # Send JSON response back to invalid POST request
        return jsonify({'error': 'You do not have permission to delete this petition.'}), 403

    # Delete all signatures associated with the petition
    Signature.query.filter_by(petition_id=petition_id).delete()
    db.session.delete(petition)
    db.session.commit()

    # Send JSON response back to AJAX request
    return jsonify({'message': 'Petition deleted successfully.'}), 200


@app.route('/petition/<int:petition_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_petition(petition_id):
    """
    Renders the petition edit page and accepts POST requests to update the specified petition
    :param petition_id: The id of the petition
    :return:
    """
    status_list = ['Closed', 'Waiting', 'Victory']

    petition = Petition.query.get_or_404(petition_id)

    if petition.author_id != current_user.id:
        flash('You do not have permission to edit this petition.', 'error')
        return redirect(url_for('my_petitions'))

    form = EditPetitionForm(obj=petition)

    if form.validate_on_submit():
        petition.title = form.title.data
        petition.tag_line = form.tag_line.data
        petition.description = form.description.data
        petition.image_url = form.image_url.data

        status = form.status.data

        petition.status_badges = [status] + list(filter(lambda x: x not in status_list, petition.status_badges))

        db.session.commit()

        flash('Petition updated successfully.', 'success')
        return redirect(url_for('petition_detail', petition_id=petition.id))
    elif request.method == 'POST':
        # Send JSON response back to invalid POST request
        return jsonify({'success': False, 'message': 'Invalid edit body'}), 400

    return render_template('edit.html', form=form, petition=petition)


@app.route('/petition/<int:petition_id>/sign', methods=['POST'])
@login_required
def sign_petition(petition_id):
    """
    Handles the signing of a petition from an authed users AJAX request
    :param petition_id: The id of the petition
    :return: A JSON response of the signing operation
    """
    petition = Petition.query.get(petition_id)

    form = SignPetitionForm(obj=petition)

    if form.validate_on_submit():
        # Check if the user has already signed the petition
        already_signed = Signature.query.filter_by(petition_id=petition_id, author_id=current_user.id).first() is not None
        can_sign = not already_signed and 'Victory' not in petition.status_badges and 'Closed' not in petition.status_badges

        if not can_sign:
            flash('You are unable to sign this petition', 'info')
            # Send JSON response back to invalid POST request
            return jsonify({'success': False, 'message': 'You are unable to sign this petition.', 'can_sign': True}), 200

        # Filter the signature reasoning utilising: https://pypi.org/project/alt-profanity-check/ ML model
        reason_text = request.form['reason']
        profanity_level = predict([reason_text])[0]
        reason_flagged = profanity_level > 1.0

        is_anonymous = request.form['is_anonymous'] == "1"

        new_signature = Signature(
            author_id=current_user.id,
            petition_id=petition_id,
            reason=reason_text,
            is_anonymous=is_anonymous,
            flagged=reason_flagged
        )
        db.session.add(new_signature)
        db.session.commit()

        flash('Petition created successfully!', 'success')
    elif form.errors:
        for _, errors in form.errors.items():
            for error in errors:
                print(error)
    return redirect(url_for("petition_detail", petition_id=petition.id))


@app.route('/signature/<int:signature_id>/like', methods=['POST'])
@login_required
def like_signature(signature_id):
    existing_like = Like.query.filter_by(user_id=current_user.id, signature_id=signature_id).first()

    if existing_like:
        db.session.delete(existing_like)
        message = 'removed'
    else:
        new_like = Like(user_id=current_user.id, signature_id=signature_id)
        db.session.add(new_like)
        message = 'added'

    db.session.commit()

    like_count = Like.query.filter_by(signature_id=signature_id).count()

    # Send JSON response back to AJAX request
    return jsonify({'success': True, 'like_count': like_count, 'message': message})


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_petition():
    form = CreatePetitionForm()
    if form.validate_on_submit():
        try:
            category = form.category.data
            title = form.title.data
            description = form.description.data
            tag_line = form.tag_line.data
            # Image from University of Leeds Website: https://www.leeds.ac.uk/around-campus
            image_url = form.image_url.data or 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJTcLeoDwmVmpJHNs8Ni9-4MHDhcFDQ-yr-g&s'
            status_badges = ['Waiting', category]

            new_petition = Petition(
                title=title,
                tag_line=tag_line,
                description=description,
                image_url=image_url,
                author_id=current_user.id,
                status_badges=status_badges
            )
            db.session.add(new_petition)
            db.session.commit()

            flash('Petition created successfully!', 'success')
            return redirect(url_for('petition_detail', petition_id=new_petition.id))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('create_petition'))
    elif request.method == 'POST':
        # Send JSON response back to invalid POST request
        return jsonify({'success': False, 'message': 'Invalid petition body'}), 400

    return render_template('create.html', form=form)


# ENSURE UNIQUE
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists. Please choose a different one.', 'danger')
            if existing_user.email == email:
                flash('Email already exists. Please choose a different one.', 'danger')
            return render_template('signup.html', form=form)

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('TOAST|Signup Successful!', 'success')
        return redirect(url_for('home'))
    elif form.errors:
        for _, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('TOAST|Login Successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    elif request.method == 'POST':
        # Send JSON response back to invalid POST request
        return jsonify({'success': False, 'message': 'Invalid login body'}), 400

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('TOAST|Logged out!', 'success')
    return redirect(url_for('home'))


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query', '').lower()

    if len(query) < 3:
        flash('ERRTOAST|Query must be 3 or more characters!', 'success')
        return render_template('search.html')

    petitions = Petition.query.all()

    # Wrap the keyword in the html mark tags
    def highlight(text, keyword):
        return text.lower().replace(keyword, f'<mark>{keyword}</mark>')

    # Sort the results into an array
    results = [
        petition
        for petition in petitions if query in petition.title.lower() or
                                     query in petition.description.lower() or
                                     query in petition.user.username.lower()
    ]

    # Apply highlighting to the matched parts
    for petition in results:
        petition.title = highlight(petition.title, query)
        petition.description = highlight(petition.description, query)
        petition.user.username = highlight(petition.user.username, query)

    message = None
    if not results:
        message = 'No results found'

    return render_template('search.html', results=results, message=message)


@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')


@app.route('/terms')
def terms_and_conditions():
    return render_template('terms.html')
