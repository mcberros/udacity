from google.appengine.ext import db
#BBDD
class User(db.Model):
    username=db.StringProperty(required = True)
    password=db.StringProperty(required = True)
    salt=db.StringProperty(required = True)
