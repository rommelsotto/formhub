from django.utils import simplejson
from django.shortcuts import render_to_response
from django.db.models import Avg, Max, Min, Count
from django.http import HttpResponse
from odk_dropbox import utils
from .models import ParsedSubmission

def performance_table(request):
    """
    As a first draft I want the rows of this table to be the surveyor
    name, the columns to be the survey name, and the cells to be the
    number of those surveys submitted by the given surveyor.
    """
    s = ParsedSubmission.objects.values("survey_type, surveyor").annotate(Count("survey_type"))
    print s

def dashboard(request):
    return render_to_response('dashboard.html')

def submission_counts(request):
    counts = ParsedSubmission.objects.values("survey_type__name", "phone__device_id").annotate(count=Count("survey_type"))
    table = {}
    rows = []
    cols = []
    for d in counts:
        print d
        phone = d["phone__device_id"]
        survey = d["survey_type__name"]
        if phone not in table:
            table[phone] = {}
        if survey not in table[phone]:
            table[phone][survey] = {}
        table[phone][survey] = d["count"]
        if phone not in rows:
            rows.append(phone)
        if survey not in cols:
            cols.append(survey)
        rows.sort()
        cols.sort()
    t = [[""] + cols]
    for row in rows:
        t.append([row] + [str(table[row].get(col, 0)) for col in cols])
    return render_to_response("submission_counts.html",
                              {"submission_counts" : t})

def csv(request, name):
    pss = ParsedSubmission.objects.filter(survey_type__name=name)
    handlers = [utils.parse_submission(ps.submission) for ps in pss]
    dicts = [handler.get_dict() for handler in handlers]
    itemss = [utils.flatten_dict(d) for d in dicts]
    flattened_dicts = [dict(items) for items in itemss]    
    table = utils.table(flattened_dicts)
    return HttpResponse(utils.csv(table), mimetype="application/csv")

def map_submissions(request):
    latlongs = []

    for loc in ParsedSubmission.objects.exclude(gps=None):
        gps = loc.gps
        title = loc.__str__()
        latlongs.append({
            'lat':gps.latitude,
            'lng': gps.longitude,
            'title': title,
#            'survey_type':loc.survey_type
        })

    return render_to_response("map.html", {'coords':simplejson.dumps(latlongs)})