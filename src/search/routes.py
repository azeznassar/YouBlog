from flask import render_template, url_for, redirect, Blueprint
from src.search.forms import SearchForm
from src.models import Post
from src.main.utils import make_summary

search = Blueprint('search', __name__)

@search.route("/search", methods=['GET', 'POST'])
def search_form():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('search.search_results', query=form.search.data))

    return render_template('search.html', title='Search', form=form)

@search.route('/search_results/<query>')
def search_results(query):
    results = Post.query.whoosh_search(query)
    make_summary(results)
    return render_template('search_results.html', query=query, results=results)
