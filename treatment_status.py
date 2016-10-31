import website.wsgi
from data.models import TreatmentCell

_BATCH = 'exp1'

cells = TreatmentCell.objects.filter(batch=_BATCH)

treatments = set([t.treatment for t in cells])


for t in treatments:
    gro = TreatmentCell.objects.filter(batch=_BATCH).filter(treatment=t)
    print "{}:  {}".format(t, len(gro.filter(finished=1)))

finished = TreatmentCell.objects.filter(batch=_BATCH).filter(finished=1)

print "Total: {}".format(len(finished))
