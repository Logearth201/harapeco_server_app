from django.shortcuts import render, redirect, get_object_or_404, \
    get_list_or_404, Http404, HttpResponse
import random, string, json
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

def convert_json_result(request, data):
    # APIの結果にCSRFデータを持たせる
    csrf = request.COOKIES["csrftoken"]
    data["CsrfToken"] = csrf
    return HttpResponse(json.dumps(data))
