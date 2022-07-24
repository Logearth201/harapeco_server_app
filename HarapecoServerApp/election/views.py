from django.shortcuts import render
from .models import ElectionTitle, ElectionUnit, ElectionCandidate, ElectionUserSubmit
from app.models import User
from django.shortcuts import render, HttpResponse
from util import apiutil, util

# Create your views here.
def get_can_election_list(request):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        election_json_obj = []
        election_submits = ElectionUserSubmit.objects.filter(user=user, election_unit__election_title__is_delete=False)
        for election_submit in election_submits:
            election_json_obj.append({
                "ElectionID": election_submit.election_unit.election_title.id,
                "ElectionName": election_submit.election_unit.election_title.name,
                "ElectionUnitID": election_submit.election_unit.id,
                "ElectionUnitName": election_submit.election_unit.name,
                "ElectionSubmitCandidateID": None if election_submit.election_candidate is None else election_submit.election_candidate.id,
                "ElectionSubmitName": None if election_submit.election_candidate is None else election_submit.election_candidate.name,
                "StartTime": election_submit.election_unit.election_start_time.strftime("%Y/%m/%d %H:%M:%S"),
                "EndTime": election_submit.election_unit.election_end_time.strftime("%Y/%m/%d %H:%M:%S"),
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Elections": election_json_obj})
    
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    
def get_electionunit_candidate(request):
    pass
