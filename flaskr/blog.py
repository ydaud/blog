"""
Authentication views for flask blog app
"""
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from flask.views import MethodView
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

BP_NAME = "blog"
blog_bp = Blueprint(BP_NAME, __name__)


class BlogView(MethodView):
    """
    Base Views for blogs
    """

    def get_post(self, post_id, check_author=True):
        """
        Get post from database given id

        Args:
            id          :   the id of the post
            check_author:   check whether user is auther of post

        Returns: post
        """
        post = (
            get_db()
            .execute(
                "SELECT p.id, title, body, created, author_id, username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE p.id = ?",
                (post_id,),
            )
            .fetchone()
        )

        if post is None:
            abort(404, f"Post id {post_id} doesn't exist.")

        if check_author and post["author_id"] != g.user["id"]:
            abort(403)

        return post


class Blog(BlogView):
    """
    Base Views for blog home
    """

    def get(self):
        """
        HTTP GET method for blog home
        """
        db = get_db()
        posts = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()
        return render_template("blog/index.html", posts=posts)


class Create(BlogView):
    """
    Base Views for create blog
    """

    @login_required
    def get(self):
        """
        HTTP GET method for create blog
        """
        return render_template("blog/create.html")

    @login_required
    def post(self):
        """
        HTTP POST method for create blog
        """
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

        return render_template("blog/create.html")


class Update(BlogView):
    """
    Base Views for update blog
    """

    @login_required
    def get(self, id):  # pylint: disable=redefined-builtin
        """
        HTTP GET method for update blog
        """
        post = self.get_post(id)
        return render_template("blog/update.html", post=post)

    @login_required
    def post(self, id):  # pylint: disable=redefined-builtin
        """
        HTTP POST method for update blog
        """
        post = self.get_post(id)
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id = ?",
                (title, body, id),
            )
            db.commit()
            return redirect(url_for("blog.index"))

        return render_template("blog/update.html", post=post)


class Delete(BlogView):
    """
    Base View for delete blog
    """

    @login_required
    def post(self, id):  # pylint: disable=redefined-builtin
        """
        HTTP POST method for delete blog
        """
        self.get_post(id)
        db = get_db()
        db.execute("DELETE FROM post WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("blog.index"))


blog_view = Blog.as_view("blog")
create_view = Create.as_view("create")
update_view = Update.as_view("update")
delete_view = Delete.as_view("delete")


blog_bp.add_url_rule(
    "/", view_func=blog_view, methods=["GET", "POST"], endpoint="index"
)

blog_bp.add_url_rule("/create", view_func=create_view, methods=["GET", "POST"])

blog_bp.add_url_rule("/<int:id>/update", view_func=update_view, methods=["GET", "POST"])

blog_bp.add_url_rule("/<int:id>/delete", view_func=delete_view, methods=["POST"])
