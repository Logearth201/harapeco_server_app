from django.shortcuts import render, redirect, HttpResponse
import random, string, json
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseGone, HttpResponseRedirect
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

def convert_json_result(request, data):
    # APIの結果にCSRFデータを持たせる
    csrf = request.COOKIES["csrftoken"]
    data["CsrfToken"] = csrf
    
    # エラーメッセージに合わせて返すものを変える
    if data["ErrorCode"] == "404":
        return HttpResponseNotFound(json.dumps(data))

    if data["ErrorCode"] == "500":
        return HttpResponseServerError(json.dumps(data))

    if data["ErrorCode"] == "403":
        return HttpResponseForbidden(json.dumps(data))

    if data["ErrorCode"] == "405":
        return HttpResponseNotAllowed(json.dumps(data))

    if data["ErrorCode"] == "400":
        return HttpResponseBadRequest(json.dumps(data))

    if data["ErrorCode"] == "410":
        return HttpResponseGone(json.dumps(data))

    if data["ErrorCode"] == "302":
        return HttpResponseRedirect(json.dumps(data))
    
    return HttpResponse(json.dumps(data))
