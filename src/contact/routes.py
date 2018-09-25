from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user
from src.contact.forms import ContactForm
from src.contact.utils import send_contact_email

contact = Blueprint('contact', __name__)

@contact.route("/contact", methods=['GET', 'POST'])
def contact_form():
    form = ContactForm()

    if form.validate_on_submit():
        send_contact_email(form.name.data, form.email.data, form.message.data)
        flash('Your message has been sent.', 'success')
        return redirect(url_for('contact.contact_form'))

    elif request.method == 'GET':
        if current_user.is_authenticated:
            form.email.data = current_user.email

    return render_template('contact/contact.html', title='Contact', form=form)
    