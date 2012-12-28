from google.appengine.ext import db

class WikiPost(db.Model):
    uri=db.StringProperty()
    uri_history_view=db.StringProperty()
    uri_history_edit=db.StringProperty()
    content=db.TextProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)
