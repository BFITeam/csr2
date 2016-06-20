import boto.mturk.connection
from apscheduler.schedulers.blocking import BlockingScheduler
import website.wsgi
from django.contrib.auth.models import User
import os
from django.core.exceptions import ObjectDoesNotExist

sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
real_host = 'mechanicalturk.amazonaws.com'


mturk = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    host = sandbox_host,
    debug=1
)
#hitid = '3MID1PD49GG1TQTVAIOMOK6RKJUKWX'
#hitid = '3TRB893CSJVXBXOSIRQD01OSYEYG7T'
responses = []
for hitid in mturk.get_reviewable_hits():
    print hitid.HITId
    for assignment in mturk.get_assignments(hitid.HITId):
        answers = assignment.answers[0]
        for a in answers:
            if a.qid == "Age":
                responses.append(dict(workerId=assignment.WorkerId, access_key=a.fields[0]))

for response in responses:
    try:
        user = User.object.get(username=response['access_key'])
    except ObjectDoesNotExist:
        r['verified'] = 0
    else:
        Mtuker.objects.filter(user_id=user.id).update(verified=1)
        r['verified'] = 1

#assignments = [a.answers[0][0].fields[0] for a in mturk.get_assignments('3TRB893CSJVXBXOSIRQD01OSYEYG7T')]
#print assignments
scheduler = BlockingScheduler()

#mturk.create_hit(hit_layout='3EC4IFE3XHELSEQ9RHPWH6DCRJ40V7', max_assignments=1, reward=.06)
def main():
    #GET ALL THE HITS. THEN TRY TO GET USER OBJECT
    #IF ERROR, SEND MESSAGE THAT KEY WAS INCORRET
    #IF CORRECT, SEND MESSAGE THE KEY HAS BEEN VERIFIED
    #AND ACTIVATED
    pass


#scheduler.add_job(main, 'interval', minutes=1)
