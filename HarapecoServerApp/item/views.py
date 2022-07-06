from django.shortcuts import render
from .models import Stamp
from app.models import User, UserManager
from util import apiutil, util
from django.utils import timezone
from django.db import transaction

# Create your views here.
def stamp_list(request):
    try:
        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # コメントを取得
        stamps = Stamp.objects.all()
        stamps_obj = []
        for stamp in stamps:
            stamps_obj.append({
                "ID": stamp.id,
                "Name": stamp.stamp_name,
                "FromUser": stamp.stamp_filename,
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Stamps": stamps_obj})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})