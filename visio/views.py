from django.shortcuts import render
from django.http import HttpResponse
# from django.template import loader
from django.shortcuts import redirect
from django.contrib import auth
from visio.dataModel.manageFromOldDatabase import ManageFromOldDatabase

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
      performancesAction(request.GET['action'], context)
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

def performancesAction(action, context):
  if action == "Vider la base de données":
    oldDb = ManageFromOldDatabase()
    context["messages"] = oldDb.distroyDatabase()
    oldDb.distroySelf()
  elif action == "Remplir la base de données":
    oldDb = ManageFromOldDatabase()
    context["messages"] = oldDb.populateDatabase()
    oldDb.distroySelf()
  else:
    context["messages"] = ["Action : {} inconnue".format(action)]

def login(request):
  return render(request, 'visio/login.html')
