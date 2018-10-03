from flask import render_template, url_for, flash, abort, redirect, request, Blueprint
from flask_login import current_user, login_required
from src import db
from src.models import Post, Comment
from src.posts.forms import PostForm, CommentForm

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

    return render_template('posts/submit.html', title='Submit a post', legend='Submit a blog post', form=form)

@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    current_post = Post.query.get_or_404(post_id)
    form = CommentForm()
    #page = request.args.get('commentsPage', 1, type=int)
    comments = Comment.query.filter(Comment.post_id == post_id).order_by(Comment.date_posted.desc()).all()

    if request.method == 'POST':
        if current_user.is_authenticated:
            if form.validate_on_submit():
                new_comment = Comment(body=form.body.data, post_id=post_id, author=current_user)
                db.session.add(new_comment)
                db.session.commit()
                flash('Your comment has been submitted', 'success')
                return redirect(url_for('posts.post', post_id=post_id))
        else:
            flash('You need to be logged in to submit a comment.', 'warning')
            return redirect(url_for('users.login'))

    return render_template('posts/post.html', title=current_post.title, post=current_post, form=form, comments=comments)

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

    return render_template('posts/submit.html', title='Edit post', legend='Edit your blog post', form=form)


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    current_post = Post.query.get_or_404(post_id)

    if current_post.author != current_user:
        abort(403)

    db.session.delete(current_post)
    db.session.commit()
    flash('Your post has been deleted.', 'success')
    return redirect(url_for('main.home'))

@posts.route("/delete_comment/<int:comment_id>/", methods=['POST'])
@login_required
def delete_comment(comment_id):
    current_comment = Comment.query.get_or_404(comment_id)
    post_id = current_comment.post_id

    if current_comment.author != current_user:
        abort(403)

    db.session.delete(current_comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('posts.post', post_id=post_id))
    