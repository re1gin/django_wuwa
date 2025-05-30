import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from resonators.models import Character

class Command(BaseCommand):
    help = 'Import karakter dari Character_Data.csv'

    def handle(self, *args, **kwargs):
        filepath = os.path.join(settings.BASE_DIR, 'data', 'character_data.csv')

        if not os.path.exists(filepath):
            self.stderr.write("File CSV tidak ditemukan di folder data/")
            return

        with open(filepath, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                Character.objects.create(
                    character=row['Character'].strip(),
                    rarity=row['Rarity'].strip(),
                    weapon=row['Weapon'].strip(),
                    sex=row['Sex'].strip() if row['Sex'].strip() else 'Unknown',
                    codename=row['Codename'].strip(),
                    birthday=row['Birthday'].strip(),
                    affiliation=row['Affiliation'].strip(),
                    birthplace=row['Birthplace'].strip(),
                    attribute=row['Attribute'].strip(),
                    role=row['Role'].strip(),
                    hp=int(row['HP']),
                    atk=int(row['ATK']),
                    defense=int(row['DEF']),
                    energy=int(row['Energy']),
                    crit_rate=int(row['Crit Rate']),
                    crit_dmg=int(row['Crit Dmg']),
                )
        self.stdout.write(self.style.SUCCESS('Data karakter berhasil diimport'))
