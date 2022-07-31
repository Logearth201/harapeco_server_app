from rootbox import util as rootboxutil
from django.shortcuts import render
from .models import RootBoxTerm, RootBoxItem, UserRootBoxState
from app.models import User
from django.shortcuts import render, HttpResponse
from util import apiutil, util
import datetime
import pytz
from .forms import RootBoxDrawForm

# from:https://qiita.com/mikage/items/8bd7afbe3300d9e39f90
def rootbox_draw(request):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # フォームを取得
        form = RootBoxDrawForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # ガチャ種別の取得
        term = RootBoxTerm.objects.get_or_none(id=form.cleaned_data["term_id"])
        if term is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # ガチャ種別が引いてもいいかどうかを確認
        if term.end_time.replace(tzinfo=pytz.utc) < datetime.datetime.now().replace(tzinfo=pytz.utc) or term.start_time.replace(tzinfo=pytz.utc) > datetime.datetime.now().replace(tzinfo=pytz.utc):
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        rootbox_state = UserRootBoxState.objects.get_or_none(user=user, term=term)
        if rootbox_state is None:
            rootbox_state = UserRootBoxState()
            rootbox_state.term = term
            rootbox_state.user = user
            rootbox_state.hash_key_usr = util.randomname(100)

        # 引く回数は1連 or 10連
        draw_times = form.cleaned_data["times"]
        if draw_times != 1 and draw_times != 10:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "400"})

        # 確率を求めるためのデータを作成
        rootbox_items = RootBoxItem.objects.filter(term=term)
        if len(rootbox_items) == 0:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        
        # レスポンスJSON
        response_json = []

        # ガチャを指定した数だけ引かせる
        for num in range(draw_times):
            rootbox_state.hash_key_index += 1
            rootbox_index = rootboxutil.calculate_rnd_hash(rootbox_items, term.common_prefix_key + rootbox_state.hash_key_usr + str(rootbox_state.hash_key_index))
            response_json.append({
                "RootBoxValue": rootbox_index,
                })

        # 引く回数状態をセーブ
        rootbox_state.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Data": response_json})
    
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})