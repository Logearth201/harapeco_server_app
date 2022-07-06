from django.shortcuts import render
from .models import Stamp, DiamondCount
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

        # スタンプを取得
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

def get_diamonds(request):
    try:
        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # 合計
        total = 0

        # ダイヤモンドの数を取得
        diamond_counts = DiamondCount.objects.filter(user=user)
        diamond_classifications = []
        for diamond_count in diamond_counts:
            total += diamond_count.count
            diamond_classifications.append({
                "ID": diamond_count.id,
                "PlatformName": diamond_count.platform.platform_name,
                "Count": diamond_count.count,
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Total": total, "Classification": diamond_classifications})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})