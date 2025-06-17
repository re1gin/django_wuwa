# echo/management/commands/import_echos.py (pastikan ini sama seperti yang saya berikan sebelumnya)
import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from echo.models import Echo, Sonata

class Command(BaseCommand):
    help = 'Mengimpor data Echo dari file CSV dan menghubungkannya dengan Sonata.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            default=os.path.join(settings.BASE_DIR, 'data', 'echo_data.csv'),
                            help='Path ke file CSV yang hanya berisi nama karakter. Default: data/character_names.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" tidak ditemukan.')

        self.stdout.write(self.style.SUCCESS(f'Memulai impor data Echo dari {csv_file_path}...'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    echo_name = row['name'].strip()
                    echo_cost = int(row['cost'])
                    

                    echo_obj, created = Echo.objects.update_or_create(
                        name=echo_name,
                        defaults={
                            'cost': echo_cost,
                        }
                    )

                    sonata_names_str = row.get('sonatas', '').strip()
                    if sonata_names_str:
                        sonata_names = [name.strip() for name in sonata_names_str.split(',') if name.strip()]
                        echo_obj.sonatas.clear() # Hapus hubungan yang ada

                        for s_name in sonata_names:
                            try:
                                sonata_obj = Sonata.objects.get(name=s_name)
                                echo_obj.sonatas.add(sonata_obj)
                                self.stdout.write(self.style.SUCCESS(f'  Menghubungkan {echo_name} dengan Sonata: {s_name}'))
                            except Sonata.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f'  Peringatan: Sonata "{s_name}" tidak ditemukan untuk Echo "{echo_name}". Pastikan Sonata sudah diimpor terlebih dahulu.'))

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Berhasil membuat Echo: {echo_obj.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Berhasil memperbarui Echo: {echo_obj.name}'))

                self.stdout.write(self.style.SUCCESS('Impor data Echo selesai!'))

        except FileNotFoundError:
            raise CommandError(f'Error: File tidak ditemukan di {csv_file_path}')
        except Exception as e:
            raise CommandError(f'Terjadi error saat impor Echo: {e}. Periksa format CSV dan tipe datanya.')