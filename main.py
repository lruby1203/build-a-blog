#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, cgi, jinja2, os, re
from google.appengine.ext import db
from datetime import datetime
#import hashutils

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class BlogEntry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def get_posts(limit, offset=0):
    # TODO: query the database for posts, and return them
    query = BlogEntry.all().order("-created")
    posts = query.fetch(limit=limit, offset=offset)
    return posts

class MainHandler(webapp2.RequestHandler):
    def get(self):
        current_page = self.request.get("page")
        page_limit = 5
        if current_page == "":
            current_page = 1
        else:
            current_page = int(current_page)
        offset = (current_page - 1) * page_limit
        posts = get_posts(page_limit, offset)
        prev_page = current_page - 1
        next_offset = current_page * page_limit
        next_posts = get_posts(page_limit, next_offset)
        if next_posts:
            next_page = current_page + 1
        else:
            next_page = 0

        t = jinja_env.get_template("blog.html")
        content = t.render(posts = posts, current_page = current_page, prev_page = prev_page, next_page = next_page)
        self.response.write(content)

class NewPost(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")
        error = False
        if title and entry:
            a = BlogEntry(title=title, entry=entry)
            a.put()
            blog_id = a.key().id()
            self.redirect('/blog/'+ str(blog_id))
        else:
            error = True
            t = jinja_env.get_template("newpost.html")
            content = t.render(error = error, title=title, entry=entry)
            self.response.write(content)


class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
#        self.response.write("The id is {0}".format(id))
        key = db.Key.from_path('BlogEntry', int(id))
        entry = db.get(key)
        if not entry:
           self.error(404)
           return
        t = jinja_env.get_template("permalink.html")
        content = t.render(entry=entry)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/blog/newpost',  NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
