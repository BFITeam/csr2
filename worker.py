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
_BATCH = 'pilot2'

mturk = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    host = sandbox_host,
    debug=1
)

def job():
    start = time.time()
    responses = []
    for hitid in mturk.get_all_hits():
    #print hitid.HITId
        for assignment in mturk.get_assignments(hitid.HITId):
            answers = assignment.answers[0]
            for a in answers:
                if a.qid == "AccessCode":
                    responses.append(dict(workerId=assignment.WorkerId, access_key=a.fields[0], assignmentId=assignment.AssignmentId))

    for response in responses:
        try:
            user = User.objects.get(username=response['access_key'])
        except ObjectDoesNotExist:
            response['verified'] = 0
        else:
            exists = Mturker.objects.filter(mturkid=response['workerId'])
            if len(exists) > 0:
                continue
            else:
                print response
                mturker, created = Mturker.objects.get_or_create(user_id=user.id)
                tc = TreatmentCell.objects.filter(batch=_BATCH).filter(finished=0).order_by('?')[0]
                mturker.assign_treatmentcell(tc.id, response['workerId'], response['assigmentId'])


    print "MTURK API Runtime: {}".format((time.time() - start))


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=1)

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
