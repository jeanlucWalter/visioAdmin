from sys import prefix
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
# from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import auth
from visio.dataModel.manageFromOldDatabase import manageFromOldDatabase
from visio.dataModel.referentiel import Referentiel
import json

def home(request):
  if request.user.is_authenticated:
    return redirect('/visio/performances/')
  return redirect('/visio/login/')

def performances(request):
  context = {}
  if request.method == 'GET' and 'action' in request.GET:
    if request.GET['action'] == 'disconnect':
      auth.logout(request)
    else:
      print("query", request.GET)
      return JsonResponse(performancesAction(request.GET['action'], request.GET))
  elif request.method == 'POST' and request.POST.get('login') == "Se connecter":
    HtlmPage = performancesLogin(request)
    if HtlmPage: return HtlmPage
  if request.user.is_authenticated:
    context['userName'] = request.user.username
    return render(request, 'visio/performances.html', context)
  return redirect('/visio/login/')

def performancesLogin(request):
  userName = request.POST.get('userName')
  password = request.POST.get('password')
  user = auth.authenticate(username=userName, password=password)
  if user == None:
    context = {'userName': userName, 'password':password, 'message':"Le couple login password n'est pas conforme"}
    return render(request, 'visio/login.html', context)
  else:
    context = {"userName":'', 'password':''}
    auth.login(request, user)

def performancesAction(action, get):
  if action == "perfEmptyBase":
    return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
  elif action == "perfPopulateBase":
    if get['method'] == 'empty':
      return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
    else:
      return manageFromOldDatabase.populateDatabase(get['start'] == 'true', method=get['method'])
  elif action == "perfImportRef":
    return Referentiel.exportReferentiel()
  else:
    return {}

def login(request):
  return render(request, 'visio/login.html')
