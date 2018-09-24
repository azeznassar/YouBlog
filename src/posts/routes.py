from flask import render_template, url_for, flash, abort, redirect, request, Blueprint
from flask_login import current_user, login_required
from src import db
from src.models import Post
from src.posts.forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route("/submit", methods=['GET', 'POST'])
@login_required
def submit_post():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your blog post has been submitted', 'success')
        return redirect(url_for('main.home'))

    return render_template('submit.html', title='Submit a post', legend='Submit a blog post', form=form)

@posts.route("/post/<int:post_id>")
def post(post_id):
    current_post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=current_post.title, post=current_post)

@posts.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    current_post = Post.query.get_or_404(post_id)

    if current_post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        current_post.title = form.title.data
        current_post.content = form.content.data
        db.session.commit()
        flash('Your post have been updated.', 'success')
        return redirect(url_for('posts.post', post_id=current_post.id))

    elif request.method == 'GET':
        form.title.data = current_post.title
        form.content.data = current_post.content

    return render_template('submit.html', title='Edit post', legend='Edit your blog post', form=form)


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    current_post = Post.query.get_or_404(post_id)

    if current_post.author != current_user:
        abort(403)

    db.session.delete(current_post)
    db.session.commit()
    flash('Your post have been deleted.', 'success')
    return redirect(url_for('main.home'))
    