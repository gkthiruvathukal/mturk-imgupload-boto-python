#
# upload script with support for file upload HITs
# 
# Thanks to http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/ for
# inspiration!
#

import sys
import os
import argparse
import csv

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
   title = 'Bovid Labs HIT %(uuid)s - Batch 1' % vars()
   description = ('Help us extract a polygon from this research image.')
   keywords = 'image, extraction, gimp'
 
   overview = Overview()
   overview.append_field('Title', 'Instructions')

   # Overview text is where we'll put the details about the HIT
   # img previews the tooth image
   # a allows user to download the image and save as

   text = """
      <p>Your job is to extract the outline of the tooth in the following image.</p>
      
      <p>You need to install the current version of Gimp on your computer. It can
      be downloaded from
      <a href="https://www.gimp.org/downloads/">https://www.gimp.org/downloads/</a></p>

      <p>We have prepared a video at <a href="https://www.youtube.com/embed/nzxZqIp3XZY">
      youtube.com/embed/nzxZqIp3XZY</a> showing how to do the task. Once you have extracted
      the outline, you will upload the final result (file) to this HIT.
      </p>
      
      <p>For the HIT to be complete, you must upload a the black polygon against
      a white background. The image size must match the original image size.</p>

      <p>Image download URL: <br/>
         <a href="%(url)s">
            <img src="%(url)s" alt="direct link to image %(uuid)s"/>
         </a>
      </p>
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
   mtc.create_hit(questions=question_form, max_assignments=1, title=title, description=description, keywords=keywords, duration = 60*30, reward=0.10)
 
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
      reader = csv.DictReader(infile)
      for row in reader:
         id = row['id']
         uuid = row['filename']
         url = row['url']
         print(uuid + "=" + url)
         if options.pretend:
            print("pretending to upload HIT with for %(uuid)s" % vars())
         else:
            print("uploading HIT with for %(uuid)s" % vars())
            create_question_form(mtc, uuid, url)
      print("Have a nice day!")
      
if __name__ == '__main__':
   go()
