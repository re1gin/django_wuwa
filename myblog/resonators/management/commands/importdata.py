import os
import csv
from decimal import Decimal # Tambahkan import Decimal

from django.conf import settings # Import settings untuk BASE_DIR
from django.core.management.base import BaseCommand, CommandError

from resonators.models import Resonator # Pastikan ini mengarah ke model Resonator Anda

class Command(BaseCommand):
    help = 'Mengimpor data resonator dari file CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            default=os.path.join(settings.BASE_DIR, 'data', 'character_data.csv'),
                            help='Path ke file CSV data karakter. Default: data/character_data.csv')

    def handle(self, *args, **kwargs):
        filepath = kwargs['csv_file']

        if not os.path.exists(filepath):
            raise CommandError(f"File CSV tidak ditemukan: {filepath}")

        self.stdout.write(self.style.SUCCESS(f"Memulai impor data dari: {filepath}"))

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Mapping nama kolom CSV ke nama field model Django
            # Pastikan nama di sini sesuai dengan header CSV dan nama field di model Resonator Anda
            field_mapping = {
                'Character': 'character',
                'Rarity': 'rarity',
                'Weapon': 'weapon',
                'Sex': 'sex',
                'Codename': 'codename',
                'Birthday': 'birthday',
                'Affiliation': 'affiliation',
                'Birthplace': 'birthplace',
                'Attribute': 'attribute',
                'Role': 'role',
                'HP': 'hp',
                'ATK': 'atk',
                'DEF': 'defense',
                'Energy': 'energy',
                'Crit Rate': 'crit_rate',
                'Crit Dmg': 'crit_dmg',
            }

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for row in reader:
                data = {}
                current_character_name = row.get('Character', 'N/A')

                for csv_col, model_field in field_mapping.items():
                    value = row.get(csv_col, '').strip()
                    if value == 'Unknown' or value == '':
                        data[model_field] = None
                    else:
                        if model_field in ['hp', 'atk', 'defense', 'energy']:
                            try:
                                data[model_field] = int(value)
                            except ValueError:
                                self.stderr.write(self.style.WARNING(
                                    f"Skipping row for {current_character_name}: Invalid integer for {csv_col}: '{value}'"
                                ))
                                skipped_count += 1
                                break # Keluar dari loop inner, lanjut ke baris berikutnya
                        elif model_field in ['crit_rate', 'crit_dmg']:
                            try:
                                data[model_field] = Decimal(value) # Gunakan Decimal untuk float
                            except ValueError:
                                self.stderr.write(self.style.WARNING(
                                    f"Skipping row for {current_character_name}: Invalid decimal for {csv_col}: '{value}'"
                                ))
                                skipped_count += 1
                                break
                        else:
                            data[model_field] = value
                else: # Ini akan dieksekusi jika loop inner tidak di-break
                    try:
                        obj, created = Resonator.objects.update_or_create(
                            character=data['character'], # Kunci unik untuk mencari/membuat
                            defaults=data # Data untuk memperbarui atau membuat
                        )
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f"Created: {obj.character}"))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.MIGRATE_HEADING(f"Updated: {obj.character}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"Error processing row for character {current_character_name}: {e}"
                        ))
                        skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n--- Import Selesai ---"))
        self.stdout.write(self.style.SUCCESS(f"Total Resonator Dibuat: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Total Resonator Diperbarui: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Total Baris Dilewati (Error): {skipped_count}"))