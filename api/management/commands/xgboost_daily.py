from django.core.management.base import BaseCommand, CommandError
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        # Insert logic here

        self.stdout.write('The xgboost_daily task was ran.')