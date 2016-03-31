#
# upload script with support for file upload HITs
# 
# Thanks to http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/ for
# inspiration!
#

import sys
import os

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm, Overview, \
     AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer,FileUploadAnswer
 
# TODO: These can be done at the command line via argparse.

ACCESS_ID=os.environ.get("MTURK_ACCESS_ID")
SECRET_KEY=os.environ.get("MTURK_SECRET_KEY")

if ACCESS_ID == None or SECRET_KEY == None:
   print("missing AWS credentials")
   sys.exit(1)

HOST = 'mechanicalturk.amazonaws.com'

def create_question_form(mtc, uuid, url):
   title = 'Test HIT Toothless id %(uuid)s- PLEASE DO NOT WORK ON THIS HIT' % vars()
   description = ('Help us extract a polygon from this research image.')
   keywords = 'image, extraction, gimp'
 
   overview = Overview()
   overview.append_field('Title', 'Instructions')

   # Overview text is where we'll put the details about the HIT
   # img previews the tooth image
   # a allows user to download the image and save as

   text = """
      Here is a tooth for you to modify using Gimp. Instructional video URL to to HERE.

      <a href="%(url)s">
         <img src="%(url)s" alt="download %(uuid)s"/>
      </a>
      """ % vars()

   overview.append(FormattedContent(text))

   qc1 = QuestionContent()
   qc1.append_field('Title','File Upload Question')

   fu1 = FileUploadAnswer(1024, 1024*1024*10)

   q1 = Question(identifier="fileupload",
              content=qc1,
              answer_spec=AnswerSpecification(fu1))

 
   question_form = QuestionForm()
   question_form.append(overview)
   question_form.append(q1)
 
   # TODO: We want to separate creation of form from uploading the hit
   # need to factor out arguments....
   mtc.create_hit(questions=question_form, max_assignments=1, title=title, description=description, keywords=keywords, duration = 60*5, reward=0.01)
 
# Main

def go():
   mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)
   # TODO: Read this from an input file. Still in proof of concept stage here.
   images = [
     ("tooth quick check", "https://dl.dropboxusercontent.com/u/35094868/DSCN3493m.JPG"),
#     ("tooth 2", "https://dl.dropboxusercontent.com/u/35094868/DSCN4170m.JPG"),
#     ("tooth 3", "https://dl.dropboxusercontent.com/u/35094868/DSCN5797m.JPG")
   ]

   for (uuid, url) in images:
      print("creating HIT with for %(uuid)s" % vars())
      create_question_form(mtc, uuid, url)
   print("Have a nice day!")
      
if __name__ == '__main__':
   go()
