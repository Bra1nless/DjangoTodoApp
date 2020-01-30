from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import TodoItem
from .forms import AddTaskForm, TodoItemForm, TodoItemExportForm
from django.views import View
from django.views.generic import ListView
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Q


@login_required
def index(request):
    return HttpResponse("Surprise, motherf**r!")


@login_required
def complete_task(request, uid):
    task = TodoItem.objects.get(id=uid)
    task.is_completed = True
    task.save()
    return HttpResponse('OK')


@login_required
def delete_task(request, uid):
    task = TodoItem.objects.get(id=uid)
    task.delete()
    messages.success(request, 'Задача удалена')
    return HttpResponseRedirect(reverse('tasks:list'))


@login_required
def add_task(request):
    if request.method == "POST":
        desc = request.POST['description']
        t = TodoItem(description=desc)
        t.save()

    return redirect('/tasks/list')


class TaskListView(LoginRequiredMixin, ListView):
    model = TodoItem
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_anonymous:
            return []
        return qs.filter(owner=u)


class TaskCreateView(LoginRequiredMixin, View):
    def my_render(self, request, form):
        return render(request, 'tasks/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = TodoItemForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            send_mail("Добавлена задача", f'Здравствуйте, {request.user.username} У вас новая задача: {new_task.description}',
                      settings.EMAIL_HOST_USER, [request.user.email], fail_silently=False)
            return redirect('/tasks/list')

        return self.my_render(request, form)

    def get(self, request, *args, **kwargs):
        form = TodoItemForm()
        return self.my_render(request, form)


class TaskDetailsView(LoginRequiredMixin, DetailView):
    model = TodoItem
    template_name = 'tasks/details.html'


class TaskEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(request.POST, instance=t)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            return redirect(reverse('tasks:list'))

        return render(request, 'tasks/edit.html', {'form': form, 'task': t})

    def get(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(instance=t)
        return render(request, 'tasks/edit.html', {'form': form, 'task': t})


class TaskExportView(LoginRequiredMixin, View):
    def generate_body(self, user, priorities):
        q = Q()
        if priorities['prio_high']:
            q = q | Q(priority=TodoItem.PRIORITY_HIGH)
        if priorities['prio_med']:
            q = q | Q(priority=TodoItem.PRIORITY_MEDIUM)
        if priorities['prio_low']:
            q = q | Q(priority=TodoItem.PRIORITY_LOW)
        tasks = TodoItem.objects.filter(owner=user).filter(q).all()

        body = 'Ваши задачи и приоритеты: \n'
        for t in list(tasks):
            if t.is_completed:
                body += f'[x] {t.description} ({t.get_priority_display()})\n'
            else:
                body += f'[ ] {t.description} ({t.get_priority_display()})\n'

        return body

    def post(self, request, *args, **kwargs):
        form = TodoItemExportForm(request.POST)
        if form.is_valid():
            email = request.user.email
            body = self.generate_body(request.user, form.cleaned_data)
            send_mail('Задачи', body, settings.EMAIL_HOST_USER, [email])
            messages.success(request, 'Задачи были отправлены на почту %s' % email)
        else:
            messages.error(request, "Что-то пошло не так, попробуйте еще раз")
        return redirect(reverse('tasks:list'))

    def get(self, request, *args, **kwargs):
        form = TodoItemExportForm()
        return render(request, 'tasks/export.html', {'form': form})
