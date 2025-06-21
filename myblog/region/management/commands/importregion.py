# regions/management/commands/import_region_data.py
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from region.models import Region # Pastikan ini mengimpor model Region Anda

class Command(BaseCommand):
    help = 'Mengimpor data Region dari file CSV.'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'data', 'csv', 'regions.csv')
        self.stdout.write(self.style.SUCCESS(f'Mencoba mengimpor Regions dari: {csv_file_path}'))

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'Error: File CSV "{csv_file_path}" tidak ditemukan.'))
            return

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                if 'name' not in reader.fieldnames:
                    self.stdout.write(self.style.ERROR('Error: Kolom "name" tidak ditemukan di file CSV.'))
                    return

                for row_num, row in enumerate(reader, 1):
                    region_name = row['name'].strip()
                    if not region_name:
                        self.stdout.write(self.style.WARNING(f'Baris {row_num}: Nama region kosong, melewati.'))
                        continue
                    
                    try:
                        region, created = Region.objects.get_or_create(name=region_name)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Region: {region.name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Region already exists: {region.name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error importing Region "{region_name}" (baris {row_num}): {e}'))

            self.stdout.write(self.style.SUCCESS('Selesai mengimpor data Region.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Terjadi kesalahan saat membuka atau membaca file CSV: {e}'))