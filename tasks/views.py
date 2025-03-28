from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, TaskForm
from .models import Task


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()


            messages.success(request, 'Registration successful!')
            return redirect('tasks:login')  # Redirect to login page (make sure to create a login view later)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'tasks/register.html', {'form': form})
from django.shortcuts import render


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # Get user credentials and authenticate
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # Log the user in
                messages.success(request, 'Login successful!')
                return redirect('tasks:create_task')  # Redirect to the task list page (create this page later)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()

    return render(request, 'tasks/login.html', {'form': form})


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # Assign the task to the current user
            task.save()
            return redirect('tasks:create_task')  # Redirect to the task list view
    else:
        form = TaskForm()

    return render(request, 'tasks/create_task.html', {'form': form})

def user_logout(request):
    logout(request)  # Logs the user out
    return redirect('tasks:login')  # Redirect to login page

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)  # Ensure task belongs to the user
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks:task_list')  # Redirect to the task list page after editing
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/edit_task.html', {'form': form, 'task': task})

def delete_task(request, task_id):
    # Get the task by ID or return a 404 error if not found
    task = get_object_or_404(Task, id=task_id)

    # Check if the request is a POST (to prevent accidental deletion)
    if request.method == 'POST':
        task.delete()  # Delete the task from the database
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')  # Redirect to the task list page after deletion

    return render(request, 'tasks/confirm_delete.html', {'task': task})  # Render a confirmation page