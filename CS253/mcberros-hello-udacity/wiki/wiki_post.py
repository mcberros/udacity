from google.appengine.ext import db

def get_post():
    entries=db.GqlQuery("SELECT * FROM WikiPost limit 10")
    entries=list(entries)
    entry="hola"
    return entry

class WikiPost(db.Model):
    uri=db.StringProperty()
    content=db.TextProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)

