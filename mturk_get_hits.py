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


def go():
   options = parseCommandLine()
   ACCESS_ID = options.access_id
   SECRET_KEY = options.secret_key

   if ACCESS_ID == None or SECRET_KEY == None:
      print("missing AWS credentials")
      sys.exit(1)

   HOST = 'mechanicalturk.amazonaws.com'

   mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)
   hits = mtc.get_all_hits()

   for k in dir(mtc):
      print(k)
   sys.exit(1)
   for hit in mtc.get_all_hits():
      hitMax = int(hit.MaxAssignments)
      hitAvailable = int(hit.NumberOfAssignmentsAvailable)
      if hitMax != hitAvailable:
         print(dir(hit))
         print(hit.HITId + " " + hit.Title + " " +  hit.HITStatus + " " + hit.NumberOfAssignmentsAvailable + "/" + hit.MaxAssignments)
         assignments =  mtc.get_assignments(hit.HITId)
         for assignment in assignments:
            print(dir(assignment))
            print(assignment.AssignmentId)
            uploadURL = mtc.get_file_upload_url(assignment.AssignmentId, 'fileupload')
            print(uploadURL)

#,Other parameters for get_assignments status=None, sort_by='SubmitTime', sort_direction='Ascending', page_size=10, page_number=1, response_groups=None)

      
if __name__ == '__main__':
   go()
