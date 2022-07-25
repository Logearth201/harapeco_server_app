from django.shortcuts import render
from .models import ElectionTitle, ElectionUnit, ElectionCandidate, ElectionUserSubmit
from app.models import User
from django.shortcuts import render, HttpResponse
from util import apiutil, util
from .forms import ElectionForm

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
                "SubmitID": election_submit.id,
                "StartTime": election_submit.election_unit.election_start_time.strftime("%Y/%m/%d %H:%M:%S"),
                "EndTime": election_submit.election_unit.election_end_time.strftime("%Y/%m/%d %H:%M:%S"),
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Elections": election_json_obj})
    
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    
def get_election_unit_candidate(request, election_unit_id):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        candidates_obj = []
        candidates = ElectionCandidate.objects.filter(election_unit__id=election_unit_id)
        for candidate in candidates:
            candidates_obj.append({
                "ID": candidate.id,
                "Name": candidate.name,
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Candidates": candidates_obj})
    
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def set_election_state(request):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # フォームを取得
        form = ElectionForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 投票の取得
        submit = ElectionUserSubmit.objects.get_or_none(id=form.cleaned_data["submit_id"])
        if submit is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 投票者の取得
        candidate = ElectionCandidate.objects.get_or_none(id=form.cleaned_data["candidate_id"], election_unit=submit.election_unit)
        if candidate is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 情報セーブ
        submit.election_candidate = candidate
        submit.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})