# resonators/management/commands/import_resonators.py
import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from resonators.models import Resonator

class Command(BaseCommand):
    help = 'Mengimpor nama resonator dari file CSV. Diasumsikan CSV hanya berisi kolom nama karakter.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            default=os.path.join(settings.BASE_DIR, 'data', 'resonator_names.csv'), # Mengubah nama default CSV
                            help='Path ke file CSV yang hanya berisi nama karakter. Default: data/character_names.csv')

    def handle(self, *args, **kwargs):
        filepath = kwargs['csv_file']

        if not os.path.exists(filepath):
            raise CommandError(f"File CSV tidak ditemukan: {filepath}")

        self.stdout.write(self.style.SUCCESS(f"Memulai impor nama karakter dari: {filepath}"))

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Memastikan header CSV memiliki kolom 'Name'
            if 'Name' not in reader.fieldnames:
                raise CommandError("File CSV harus memiliki kolom header bernama 'Name'.")

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for row in reader:
                character_name_from_csv = row.get('Name', '').strip()
                
                if not character_name_from_csv:
                    self.stderr.write(self.style.WARNING(
                        f"Melewatkan baris: Nama karakter kosong atau tidak ditemukan."
                    ))
                    skipped_count += 1
                    continue # Lanjut ke baris berikutnya

                try:
                    # Mencari atau membuat objek Resonator berdasarkan character_name
                    obj, created = Resonator.objects.update_or_create(
                        character_name=character_name_from_csv,
                        # Tidak ada 'defaults' tambahan karena CSV hanya berisi nama
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Dibuat: {obj.character_name}"))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.MIGRATE_HEADING(f"Sudah ada, dilewati (atau diperbarui jika ada default lain): {obj.character_name}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(
                        f"Error saat memproses nama karakter '{character_name_from_csv}': {e}"
                    ))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n--- Import Selesai ---"))
        self.stdout.write(self.style.SUCCESS(f"Total Resonator Dibuat: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Total Resonator Diperbarui: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Total Baris Dilewati (Error): {skipped_count}"))