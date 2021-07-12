from django.shortcuts import render
from django.http import HttpResponse
# from django.template import loader
from django.shortcuts import redirect
from django.contrib import auth

def home(request):
  context = {}
  if request.user.is_authenticated:
    return redirect('/visio/performances/')
  return redirect('/accounts/login/')

def performances(request):
  context = {}
  if request.method == 'GET' and 'action' in request.GET:
    if request.GET['action'] == 'disconnect':
      auth.logout(request)
  if request.user.is_authenticated:
    context['userName'] = request.user.username
    return render(request, 'visio/performances.html', context)
  return redirect('/accounts/login/')
  # return render(request, 'visio/performances.html', context)
