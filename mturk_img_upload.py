#
# upload script with support for file upload HITs
# 
# Thanks to http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/ for
# inspiration!
#

import sys
import os
import argparse

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm, Overview, \
     AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer,FileUploadAnswer
 
def parseCommandLine():
   parser = argparse.ArgumentParser()
   parser.add_argument('--access_id', type=str, default=os.environ.get("MTURK_ACCESS_ID"), help="access key")
   parser.add_argument('--secret_key', type=str, default=os.environ.get("MTURK_SECRET_KEY"), help="secret key")
   parser.add_argument('--images', type=str, default=None, help="file containing ID,URL pairs")
   parser.add_argument('--pretend', action='store_true', help="show what would be done; don't do it")
   options = parser.parse_args()
   print(options)
   return options


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
   options = parseCommandLine()
   ACCESS_ID = options.access_id
   SECRET_KEY = options.secret_key

   if ACCESS_ID == None or SECRET_KEY == None:
      print("missing AWS credentials")
      sys.exit(1)

   if options.images == None:
      print("no image file specified")
      sys.exit(2)

   HOST = 'mechanicalturk.amazonaws.com'

   mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)
   with open(options.images) as infile:
      for line in infile:
         (uuid,url) = line.split(',')[:2]  # comma-separated; only 2 fields
         print(uuid + "=" + url)
         if options.pretend:
            print("creating HIT with for %(uuid)s" % vars())
         else:
            create_question_form(mtc, uuid, url)
      print("Have a nice day!")
      
if __name__ == '__main__':
   go()
