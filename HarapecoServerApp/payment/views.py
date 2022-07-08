from django.shortcuts import render
from .models import DiamondCount, Platform, BuyMenu
from app.models import User, UserManager
from util import apiutil, util
from django.utils import timezone
from django.db import transaction

# Create your views here.
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

def get_buy_menu(request, platform_id):
    try:
        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # プラットフォームの取得
        platform = Platform.objects.get_or_none(id=platform_id)
        if platform is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        
        # ダイヤモンドの数を取得
        buy_menus = BuyMenu.objects.filter(platform=platform)
        buy_menu_responses = []
        for buy_menu in buy_menus:
            buy_menu_responses.append({
                "ID": buy_menu.id,
                "Cost": str(buy_menu.cost),
                "Diamonds": buy_menu.diamonds,
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "BuyMenu": buy_menu_responses})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
