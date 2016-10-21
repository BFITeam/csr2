import boto.mturk.connection
from apscheduler.schedulers.blocking import BlockingScheduler
import website.wsgi
from django.contrib.auth.models import User
from data.models import TreatmentCell, Mturker
import os
from django.core.exceptions import ObjectDoesNotExist
import logging
import time
logging.basicConfig()


sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
real_host = 'mechanicalturk.amazonaws.com'
_BATCH = 'exp1'

mturk = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    host = sandbox_host,
    debug=1
)

def get_assignments_by_page(hitid, page):
    responses = []
    assignments = mturk.get_assignments(hitid, status="Submitted", page_number=page)
    for assignment in assignments:
        for answers in assignment.answers:
            for a in answers:
                if a.qid == "AccessCode":
                    responses.append(dict(workerId=assignment.WorkerId, access_key=a.fields[0], assignmentId=assignment.AssignmentId))
    return responses

def job():
    start = time.time()
    responses = []
    all_hits = [hit for hit in mturk.get_all_hits()]
    for hitid in all_hits:
        more = True
        page = 1
        while more:
            pageResponses = get_assignments_by_page(hitid.HITId, page)
            responses += pageResponses
            if len(pageResponses) == 0:
                more = False
            page += 1

    print "Number of responses in list: {}".format(len(responses))

    for response in responses:
        try:
            user = User.objects.get(username=str(response['access_key']).replace(" ",""))
        except ObjectDoesNotExist:
            response['verified'] = 0
        else:
            exists = Mturker.objects.filter(mturkid=response['workerId'])
            if len(exists) > 0:
                continue
            else:
                print response
                mturker, created = Mturker.objects.get_or_create(user_id=user.id)
               #tc = TreatmentCell.objects.filter(batch=_BATCH).filter(finished=0).order_by('?')[0]
                tc = TreatmentCell.objects.filter(batch=_BATCH).filter(treatment="upfront90")[0]
                mturker.assign_treatmentcell(tc.id, response['workerId'], response['assignmentId'])
                feedback = "Your response to our Mturk HIT was just auto-approved and your $0.10 reward was paid on your Amazon Payment account.  Please use this code: {} to login at https://tranquil-meadow-42703.herokuapp.com to receive information about our short task and earn EXTRA payment as a bonus.".format(mturker.user.username)
                mturk.notify_workers([response['workerId']], "Assess Code Verified", feedback)
                mturk.approve_assignment(response['assignmentId'], feedback=feedback)

    print "MTURK API Runtime: {}".format((time.time() - start))


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=1)

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
