#
# upload script with support for file upload HITs
# 
# Thanks to http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/ for
# inspiration!
#

import sys
import os
import os.path
import argparse
import csv
import pycurl
import magic
from StringIO import StringIO

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm, Overview, \
     AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer,FileUploadAnswer
 

def parseCommandLine():
   parser = argparse.ArgumentParser()
   parser.add_argument('--access_id', type=str, default=os.environ.get("MTURK_ACCESS_ID"), help="access key")
   parser.add_argument('--secret_key', type=str, default=os.environ.get("MTURK_SECRET_KEY"), help="secret key")
   parser.add_argument('--accept', action='store_true', default=False, help="approve assignments that meet our requirements")
   parser.add_argument('--reject', action='store_true', default=False, help="reject assignments that don't meet our requirements")
   parser.add_argument('--download', action='store_true', default=False, help="reject assignments that don't meet our requirements")
   options = parser.parse_args()
   print(options)
   return options


def get_file_upload_url_only(mtc, assignment_id):
   try:
      upload_url = mtc.get_file_upload_url(assignment_id, 'fileupload')
      return upload_url[0].FileUploadURL
   except:
      return None

def curl_url_to_output_file(url, output_path):

   buffer = StringIO()
   c = pycurl.Curl()
   c.setopt(c.URL, url)
   c.setopt(c.WRITEDATA, buffer)
   c.perform()
   c.close()

   body = buffer.getvalue()
   with open(output_path, "wb") as outfile:
      outfile.write(body)
   return len(body)

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

   results_dir = "./results"
 
   magic_extension_map = {
     'JPEG' : '.jpeg',
     'PNG' : '.png'
   }

   for hit in mtc.get_all_hits():
      title = hit.Title.lower()
      tokens = title.split()
      original_name = None
      if tokens[-1].endswith('.jpg') or tokens[-1].endswith('.png'):
         (basename, ext) = os.path.splitext(tokens[-1])
      else:
         print("Skipping HIT: " + hit.Title)
         continue
      output_dir = os.path.join(results_dir, basename)
      if not os.path.exists(output_dir):
         os.makedirs(output_dir)
      
      for assignment in mtc.get_assignments(hit.HITId):
          assignment_filename = assignment.AssignmentId
          output_filename = os.path.join(output_dir, assignment_filename)
          url = get_file_upload_url_only(mtc, assignment.AssignmentId)
          if url:
             if options.download:
                bytes_written = curl_url_to_output_file(url, output_filename)
                magic_info = magic.from_file(output_filename)
                magic_type = magic_info.split()[0]
                add_extension = magic_extension_map.get(magic_type, '.dat')

                # If we don't get .png, .jpeg, we really can't use the files.

                if add_extension == '.dat':
                   if options.reject:
                      mtc.reject_assignment(assignment.AssignmentId, "We require a .png file as a result. You submitted " + magic_type)
                   else:
                      print("   Use --reject to reject" + assignment.AssignmentId) 
                else:
                   if options.accept:
                      mtc.accept_assignment(assignment.AssignmentId)
                   else:
                      print("   Use --accept to accept " + assignment.AssignmentId) 
                   os.rename(output_filename, output_filename + add_extension)
           
             else:
                print("   Use --downlaod to fetch " + url)


      
if __name__ == '__main__':
   go()
