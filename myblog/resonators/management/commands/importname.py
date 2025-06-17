# resonator/management/commands/import_resonators.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from resonators.models import Resonator

class Command(BaseCommand):
    help = 'Mengimpor data Resonator (Name, Rarity, Weapon, Attribute, Birthplace, Role) dari file CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, nargs='?',
                            # Mengubah nama default file CSV
                            default=os.path.join(os.getcwd(), 'data', 'resonator_names.csv'),
                            help='Path ke file CSV yang berisi data Resonator (Name, Rarity, Weapon, Attribute, Birthplace, Role). Default: <project_root>/data/resonator_minimal_data.csv')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" tidak ditemukan. Harap berikan path yang valid.')

        self.stdout.write(self.style.SUCCESS(f'Memulai impor data Resonator dari: {csv_file_path}'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # HANYA header yang diminta (sesuai dengan CSV yang Anda berikan)
                expected_headers = ['Character', 'Rarity', 'Weapon', 'Attribute', 'Birthplace', 'Role']

                # Periksa apakah semua header yang diharapkan ada di CSV
                if not all(header in reader.fieldnames for header in expected_headers):
                    missing_headers = [h for h in expected_headers if h not in reader.fieldnames]
                    raise CommandError(
                        f"CSV harus memiliki header berikut: {', '.join(expected_headers)}. "
                        f"Header yang hilang: {', '.join(missing_headers)}. "
                        f"Header yang ditemukan: {', '.join(reader.fieldnames)}"
                    )

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for row_num, row in enumerate(reader, start=2): # Mulai dari baris 2 untuk pesan error
                    resonator_name = row['Character'].strip()

                    if not resonator_name:
                        self.stderr.write(self.style.WARNING(
                            f"Melewatkan baris {row_num}: Nama karakter kosong. Data: {row}"
                        ))
                        skipped_count += 1
                        continue

                    try:
                        # --- Pembersihan Data dan Konversi Tipe ---
                        
                        # Rarity: Konversi "X Star" menjadi integer X
                        rarity_str = row['Rarity'].replace(' Star', '').strip()
                        rarity = int(rarity_str)

                        # Ambil nilai string untuk weapon, attribute, birthplace, dan role langsung
                        weapon_val = row['Weapon'].strip()
                        attribute_val = row['Attribute'].strip()
                        birthplace_val = row['Birthplace'].strip() # Pastikan ini ada di CSV
                        role_val = row['Role'].strip()             # Pastikan ini ada di CSV

                        # Siapkan data untuk update_or_create
                        defaults = {
                            'rarity': rarity,
                            'weapon': weapon_val,
                            'attribute': attribute_val,
                            'birthplace': birthplace_val, # Tambahkan ini
                            'role': role_val,             # Tambahkan ini
                        }

                        # Buat atau perbarui objek Resonator
                        # Pastikan 'name' cocok dengan field di model Anda
                        resonator_obj, created = Resonator.objects.update_or_create(
                            name=resonator_name,
                            defaults=defaults
                        )

                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f'Dibuat: {resonator_obj.name} (Rarity: {resonator_obj.rarity})'))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.MIGRATE_HEADING(f'Diperbarui: {resonator_obj.name} (Rarity: {resonator_obj.rarity})'))

                    except ValueError as ve:
                        self.stderr.write(self.style.ERROR(
                            f"Error konversi data untuk '{resonator_name}' di baris {row_num}: {ve}. Dilewati."
                        ))
                        skipped_count += 1
                    except KeyError as ke:
                         self.stderr.write(self.style.ERROR(
                            f"Kolom CSV yang diharapkan tidak ada untuk '{resonator_name}' di baris {row_num}: {ke}. Periksa header CSV. Dilewati."
                        ))
                         skipped_count += 1
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"Terjadi error tak terduga untuk '{resonator_name}' di baris {row_num}: {e}. Dilewati."
                        ))
                        skipped_count += 1

            self.stdout.write(self.style.SUCCESS('\n--- Ringkasan Impor Resonator ---'))
            self.stdout.write(self.style.SUCCESS(f'Total Resonator Dibuat: {created_count}'))
            self.stdout.write(self.style.SUCCESS(f'Total Resonator Diperbarui: {updated_count}'))
            self.stdout.write(self.style.WARNING(f'Total Baris Dilewati (Error): {skipped_count}'))

        except FileNotFoundError:
            raise CommandError(f'Error: File CSV tidak ditemukan di {csv_file_path}')
        except Exception as e:
            raise CommandError(f'Terjadi error saat pengaturan impor Resonator: {e}')