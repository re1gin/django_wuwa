# echo/management/commands/import_sonatas.py

import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from echo.models import Sonata

class Command(BaseCommand):
    help = 'Mengimpor data Sonata (hanya nama) dari file CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            default=os.path.join(settings.BASE_DIR, 'data', 'echo_data.csv'),
                            help='Path ke file CSV yang hanya berisi nama karakter. Default: data/character_names.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        # Periksa apakah file CSV ada
        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" tidak ditemukan.')

        self.stdout.write(self.style.SUCCESS(f'Memulai impor nama Sonata dari {csv_file_path}...'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f) # Membaca baris sebagai dictionary menggunakan header CSV

                # Pastikan header 'name' ada di CSV
                if 'name' not in reader.fieldnames:
                    raise CommandError("CSV harus memiliki kolom 'name'.")

                for row in reader:
                    sonata_name = row['name'].strip() # Ambil nama dan hapus spasi ekstra

                    # get_or_create akan membuat objek Sonata jika belum ada,
                    # atau mengambilnya jika sudah ada. Ini mencegah duplikasi.
                    sonata, created = Sonata.objects.get_or_create(
                        name=sonata_name
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Berhasil membuat Sonata: {sonata.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Sonata sudah ada: {sonata.name} (tidak ada perubahan)'))

            self.stdout.write(self.style.SUCCESS('Impor nama Sonata selesai!'))

        except FileNotFoundError:
            raise CommandError(f'Error: File tidak ditemukan di {csv_file_path}')
        except Exception as e:
            # Tangani error umum lainnya selama proses impor
            raise CommandError(f'Terjadi error saat impor Sonata: {e}. Pastikan format CSV Anda benar.')