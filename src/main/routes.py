from flask import render_template, request, Blueprint
from src.models import Post
from src.main.utils import make_summary

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    make_summary(posts.items)
    return render_template('home.html', posts=posts, title='Post and share your own blogs')


@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/archive")
def sort_by_oldest():
    posts = Post.query.all()
    make_summary(posts)
    return render_template('posts.html', posts=posts, title='Oldest blog posts')
