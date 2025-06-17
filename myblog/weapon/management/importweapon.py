# build/management/commands/import_weapons_csv.py

import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from weapon.models import Weapon

class Command(BaseCommand):
    help = 'Imports Weapon data (name, rarity, type) from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            default=os.path.join(settings.BASE_DIR, 'data', 'weapon_data.csv'), # Mengubah nama default CSV
                            help='Path ke file CSV yang hanya berisi nama karakter. Default: data/character_names.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" does not exist.')

        self.stdout.write(self.style.SUCCESS(f'Starting Weapon data import from {csv_file_path}...'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    weapon, created = Weapon.objects.update_or_create(
                        weapon_name=row['weapon_name'], # Ini akan menjadi kunci unik
                        defaults={
                            'rarity': int(row['rarity']), # Konversi ke integer
                            'weapon_type': row['weapon_type']
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Successfully created Weapon: {weapon.weapon_name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Successfully updated Weapon: {weapon.weapon_name}'))

            self.stdout.write(self.style.SUCCESS('Weapon data import complete!'))

        except FileNotFoundError:
            raise CommandError(f'Error: File not found at {csv_file_path}')
        except Exception as e:
            raise CommandError(f'An error occurred during import: {e}. Check your CSV format and data types.')