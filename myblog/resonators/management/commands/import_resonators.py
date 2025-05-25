import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from resonators.models import Character

class Command(BaseCommand):
    help = 'Import karakter dari Character_Data.csv'

    def handle(self, *args, **kwargs):
        filepath = os.path.join(settings.BASE_DIR, 'data', 'Character_Data.csv')

        if not os.path.exists(filepath):
            self.stderr.write("File CSV tidak ditemukan di folder data/")
            return

        with open(filepath, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                character, created = Character.objects.get_or_create(
                    name=row['Character'],
                    defaults={
                        'rarity': row['Rarity'],
                        'weapon': row['Weapon'],
                        'attribute': row['Attribute'],
                        'role': row['Role'],
                        'birthday': row['Birthday'],
                        'birthplace': row['Birthplace'],
                        'affiliation': row['Affiliation'],
                        'hp': int(row['HP']),
                        'atk': int(row['ATK']),
                        'defense': int(row['DEF'])
                    }
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Import Selesai. {count} karakter baru ditambahkan.'))
