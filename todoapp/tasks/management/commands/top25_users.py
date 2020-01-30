# coding: utf-8

from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = u"Displays TOP-25 users with largest amount of completed and uncompleted tasks"

    def handle(self, *args, **options):
        user_list = []
        for u in User.objects.all():
            u_len = len(u.tasks.all())
            u_couple = (u, u_len)
            user_list.append(u_couple)
            user_list.sort(key=lambda i: i[1])

        top25_list = user_list[-1:-26:-1]
        top_counter = 1

        for u in top25_list:
            print(top_counter, ": ", u)
            top_counter += 1
