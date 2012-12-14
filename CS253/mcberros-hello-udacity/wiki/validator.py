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
import re
import salt
from google.appengine.ext import db

#Clase para validar las entradas del Form

class Validator:
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PWD_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE=re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    MSG_ERR_USER="That's not a valid username."
    MSG_EXIST_USER="That user already exists"
    MSG_ERR_PWD="That wasn't a valid password."
    MSG_ERR_V_PWD="Your passwords didn't match."
    MSG_ERR_EMAIL="That's not a valid email."

    def valid_username(self,username=""):
        is_valid=True
    	if not self.USER_RE.match(username):
       	   is_valid=False
    	return is_valid

    def exist_username(self,username=""):
	exist=False
	users=db.GqlQuery("SELECT * FROM User WHERE username=:1",username)
	if users.count()>0:
	   exist=True
        return exist

    def valid_sign_password(self,password=""):
        is_valid=True
        if not self.PWD_RE.match(password):
           is_valid=False
        return is_valid

    def valid_bbdd_password(self,username,password):
        user=db.GqlQuery("SELECT * FROM User WHERE username=:1",username).get()
	return salt.valid_pw(username, password, user.password+","+user.salt)   

    def valid_match_pwd(self,password="",verify=""):
        is_valid=True
        if password!=verify:
           is_valid=False
        return is_valid

    def valid_email(self,email=""):
        if email=="":
	   return True
	else:
	   return self.EMAIL_RE.match(email)

