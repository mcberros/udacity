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

def escape_html(s):
    escape_list=(("&","&amp;"),(">","&gt;"),("<","&lt;"),('"',"&quot;"))
    for (i,o) in escape_list:
        s=s.replace(i,o)
    return s

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

app = webapp2.WSGIApplication([('/problem2',Problem2Handler)], debug=True)
