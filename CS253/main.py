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
import webapp2
from string import ascii_uppercase, ascii_lowercase, maketrans

form="""
<form method="post">
	What is your birthday?
	<br>
	<label> Month <input type="text" name="month" value="%(month)s"> </label>
	<label> Day <input type="text" name="day" value="%(day)s"> </label>
	<label> Year <input type="text" name="year" value="%(year)s"> </label>
	<div style="color: red">%(error)s</div>
	<br>
	<br>
        <input type="submit">
</form>
"""

form_problem2="""
<form method="post">
	<b>Enter some text to ROT13</b>
        <br>
	<textarea name="text">%(text)s</textarea>
        <br>
        <br>
        <input type="submit">
</form>
"""


months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
          
def valid_month(month):
    valid_month=None
    is_valid=False
    index_month=0
    months_len=len(months)
    
    while not(is_valid) and index_month<months_len:
        if month.lower()==months[index_month].lower():
            is_valid=True
        else:
            index_month=index_month+1
    
    if is_valid:
        valid_month=months[index_month]
    return valid_month

def valid_day(day):
    if day.isdigit() and int(day)>0 and int(day)<=31:
        return int(day)
    else:
        return None

def valid_year(year):
    if year and year.isdigit():
        year_int=int(year)
        if year_int>=1900 and year_int<=2020:
            return year_int

def escape_html(s):
    escape_list=(("&","&amp;"),(">","&gt;"),("<","&lt;"),('"',"&quot;"))
    for (i,o) in escape_list:
        s=s.replace(i,o)
    return s

class MainHandler(webapp2.RequestHandler):
    def write_form(self, error="", month="", day="", year=""):
	self.response.write(form % {'error':error, 'month':escape_html(month), 'day':escape_html(day), 'year':escape_html(year)})

    def get(self):
        self.write_form()

    def post(self):
	user_month=self.request.get('month')
	user_day=self.request.get('day')
	user_year=self.request.get('year')

	month=valid_month(user_month)
        day=valid_day(user_day)
        year=valid_year(user_year)

	if not (month and day and year):
		message="That doesn't look valid to me, friend."
		self.write_form(message, user_month, user_day, user_year)
	else:
		self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
	def get(self):
	    self.response.out.write("Thanks") 

class Problem2Handler(webapp2.RequestHandler):
	def write_form_problem2(self, text=""):
       	    self.response.write(form_problem2 % {'text':escape_html(text)})

	def encrypt(self,text):
            intab = ascii_uppercase + ascii_lowercase
	    outtab = intab[13:26] + intab[:13] + intab[39:52] + intab[26:39]
	    trantab = maketrans(intab, outtab)
	    return str(text).translate(trantab);

        def get(self):
            self.write_form_problem2()
	
	def post(self):
           texto=self.request.get('text')
	   self.write_form_problem2(self.encrypt(texto))


app = webapp2.WSGIApplication([('/', MainHandler),('/thanks',ThanksHandler),('/problem2',Problem2Handler)], debug=True)
