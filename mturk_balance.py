import os
import sys

from boto.mturk.connection import MTurkConnection
 
HOST = 'mechanicalturk.amazonaws.com'
ACCESS_ID=os.environ.get("MTURK_ACCESS_ID")
SECRET_KEY=os.environ.get("MTURK_SECRET_KEY")

if ACCESS_ID == None or SECRET_KEY == None:
   print("missing AWS credentials")
   sys.exit(1)
 
mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)
 
print mtc.get_account_balance()

