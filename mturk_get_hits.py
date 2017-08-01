#
# upload script with support for file upload HITs
#
# Thanks to http://www.toforge.com/2011/04/boto-mturk-tutorial-create-hits/ for
# inspiration!
#

import argparse
import csv
import magic
import os
import os.path
import pycurl
import sys
from StringIO import StringIO

from boto.mturk.connection import MTurkConnection


def parseCommandLine():
    parser = argparse.ArgumentParser()
    parser.add_argument('--access_id', type=str,
                        default=os.environ.get("MTURK_ACCESS_ID"), help="access key")
    parser.add_argument('--secret_key', type=str,
                        default=os.environ.get("MTURK_SECRET_KEY"), help="secret key")
    parser.add_argument('--accept', action='store_true', default=False,
                        help="approve assignments that meet our requirements")
    parser.add_argument('--reject', action='store_true', default=False,
                        help="reject assignments that don't meet our requirements")

    parser.add_argument('--skip-approved', action='store_true', default=False,
                        help="skip any assignment we've already accepted")
    parser.add_argument('--skip-rejected', action='store_true', default=False,
                        help="skip any assignment we've already rejected")
    parser.add_argument('--download', action='store_true', default=False,
                        help="download files")
    options = parser.parse_args()
    #print(options)
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


def counter():
    i = 0
    while True:
        yield i
        i = i + 1


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
        'JPEG': '.jpeg',
        'PNG': '.png'
    }

    hit_count = counter()
    assignment_count = counter()
    accept_count = counter()
    reject_count = counter()

    for hit in mtc.get_all_hits():
        hit_count.next()
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
            if options.skip_approved and assignment.AssignmentStatus == 'Approved':
                continue

            if options.skip_rejected and assignment.AssignmentStatus == 'Rejected':
                continue
       
            print("Assignment Status %s" % assignment.AssignmentStatus)
            assignment_count.next()
            assignment_filename = assignment.AssignmentId
            output_filename = os.path.join(output_dir, assignment_filename)
            url = get_file_upload_url_only(mtc, assignment.AssignmentId)
            if not url:
                print("-> No URL found for %s" % assignment.AssignmentId)
            else:
                if options.download:
                    bytes_written = curl_url_to_output_file(
                        url, output_filename)
                    magic_info = magic.from_file(output_filename)
                    magic_type = magic_info.split()[0]
                    add_extension = magic_extension_map.get(magic_type, '.dat')

                    # If we don't get .png, .jpeg, we really can't use the files.

                    print("Processing assignment: " + assignment.AssignmentId)
                    if add_extension == '.dat':
                        reject_count.next()
                        if options.reject:
                            print("   Rejecting " + assignment.AssignmentId)
                            mtc.reject_assignment(
                                assignment.AssignmentId, "We require a .png file as a result per the instructions. You submitted " + magic_type)
                        else:
                            print("   Use --reject to reject " +
                                  assignment.AssignmentId)
                    else:
                        accept_count.next()
                        if options.accept:
                            print("   Accepting " + assignment.AssignmentId)
                            mtc.approve_assignment(assignment.AssignmentId)
                        else:
                            print("   Use --accept to accept " +
                                  assignment.AssignmentId)
                        os.rename(output_filename,
                                  output_filename + add_extension)

                else:
                    print("   Use --download to fetch " + url)

    print("Total hits = %d; assignments = %d; accept = %d; reject = %d" % (
        hit_count.next(), assignment_count.next(), accept_count.next(), reject_count.next()))


if __name__ == '__main__':
    go()
