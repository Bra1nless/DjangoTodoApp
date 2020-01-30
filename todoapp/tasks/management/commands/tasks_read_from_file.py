# coding: utf-8

from django.core.management import BaseCommand
from tasks.models import TodoItem


class Command(BaseCommand):
    help = u"Read tasks from file (one line = one task) and saves them to db"

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='input_file', type=str)

    def handle(self, *args, **options):
        counter = 0
        with open(options['input_file']) as data:
            for line in data:
                if line:
                    t = TodoItem(description=line)
                    t.save()
                    counter += 1
        print(f"{counter} tasks have been imported")
