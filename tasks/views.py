from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import Taskform
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        print('GET')
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Registrar usuario
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Usuario ya existe!',
                })

    return render(request, 'signup.html', {
    'form': UserCreationForm,
    'error': 'Contraseñaas no coinciden!', })

@login_required
def tasks(request):
    #filtrar campo vacio, fecha__isnull=True
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks':tasks})
@login_required
def tasks_completed(request):
    #filtrar campo vacio, fecha__isnull=True
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks':tasks})

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):

    if request.method == 'GET':
        print('GET')
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
             return render(request, 'signin.html', {
            'form': AuthenticationForm,
            'error': 'Usuario o contraseña incorrecta!'
        })
        else:
            login(request, user)
            return redirect('tasks')
@login_required
def created_task(request):
     if request.method == 'GET':
        return render(request, 'created_task.html', {
            'form' : Taskform
        })
     else:
         try:
            form = Taskform(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
         except ValueError:
             return render(request, 'created_task.html', {
            'form' : Taskform,
            'error' : 'Intentar nuevamente ingrese datos validos!'
        })
@login_required
def detail_task(request, task_id):
    #obtiene desde un id task = Task.objects.get(pk=task_id)

    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = Taskform(instance=task)
        return render(request, 'task_detail.html', {'task':task, 'form':form})
    else:
          try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = Taskform(request.POST, instance=task)
            form.save()
            return redirect('tasks')
          except ValueError:
               return render(request, 'task_detail.html', {'task':task,'error': 'Hubo un error al actualizar!','form':form})
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
