# echo/management/commands/import_sonatas.py

import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from echo.models import Sonata # Pastikan Anda mengimpor model Sonata

class Command(BaseCommand):
    help = 'Mengimpor nama-nama Sonata dari file CSV. Diasumsikan CSV hanya berisi kolom "name".'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            # Set default path ke file CSV khusus Sonata
                            default=os.path.join(settings.BASE_DIR, 'data', 'sonata_data.csv'),
                            help='Path ke file CSV yang hanya berisi nama Sonata. Default: data/sonata_names.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File CSV tidak ditemukan: {csv_file_path}')

        self.stdout.write(self.style.SUCCESS(f'Memulai impor nama Sonata dari: {csv_file_path}'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Memastikan header CSV memiliki kolom 'name'
                if 'name' not in reader.fieldnames:
                    raise CommandError("File CSV harus memiliki kolom header bernama 'name'.")

                created_count = 0
                updated_count = 0 # Untuk get_or_create, ini biasanya berarti "sudah ada"
                skipped_count = 0

                for row_num, row in enumerate(reader, start=2): # Mulai dari baris 2 untuk error reporting
                    sonata_name_from_csv = row.get('name', '').strip()
                    
                    if not sonata_name_from_csv:
                        self.stderr.write(self.style.WARNING(
                            f"Melewatkan baris {row_num}: Nama Sonata kosong atau tidak ditemukan."
                        ))
                        skipped_count += 1
                        continue

                    try:
                        # get_or_create akan membuat objek jika tidak ada, atau mengembalikannya jika sudah ada
                        sonata_obj, created = Sonata.objects.get_or_create(
                            name=sonata_name_from_csv
                        )
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f"Dibuat: {sonata_obj.name}"))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.MIGRATE_HEADING(f"Sudah ada, dilewati: {sonata_obj.name}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"Error saat memproses nama Sonata '{sonata_name_from_csv}' di baris {row_num}: {e}"
                        ))
                        skipped_count += 1

            self.stdout.write(self.style.SUCCESS(f"\n--- Impor Sonata Selesai ---"))
            self.stdout.write(self.style.SUCCESS(f"Total Sonata Dibuat: {created_count}"))
            self.stdout.write(self.style.SUCCESS(f"Total Sonata Sudah Ada: {updated_count}"))
            self.stdout.write(self.style.WARNING(f"Total Baris Dilewati (Error): {skipped_count}"))

        except FileNotFoundError:
            raise CommandError(f'Error: File CSV tidak ditemukan di {csv_file_path}')
        except Exception as e:
            raise CommandError(f'Terjadi error saat pengaturan impor Sonata: {e}')