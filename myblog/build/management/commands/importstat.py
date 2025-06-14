# build/management/commands/import_builds.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from resonators.models import Resonator
from build.models import Build

class Command(BaseCommand):
    help = 'Mengimpor data build ideal untuk karakter dari file CSV tanpa atribut dan parsing persen.'

    def handle(self, *args, **options):
        csv_filepath = os.path.join(settings.BASE_DIR, 'data', 'resonator_stats.csv')

        if not os.path.exists(csv_filepath):
            raise CommandError(f'File CSV tidak ditemukan di: {csv_filepath}')

        self.stdout.write(self.style.SUCCESS(f'Memulai import dari {csv_filepath}'))

        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_count = 0
            updated_count = 0
            skipped_count = 0

            # --- Validasi Kolom CSV ---
            required_columns = ['Character', 'hp', 'atk', 'def', 'energy', 'crit rate', 'crit dmg']
            if not all(col in reader.fieldnames for col in required_columns):
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                raise CommandError(f"File CSV tidak memiliki kolom yang diperlukan: {', '.join(missing_columns)}. Pastikan header CSV Anda benar.")

            # --- Fungsi Helper untuk Parsing Nilai Stat (TANPA PERSEN) ---
            def parse_stat_value(value_str):
            
                cleaned_value = value_str.strip().replace('>', '')
                
                if not cleaned_value: # Tangani string kosong setelah pembersihan
                    return 0.0

                if '-' in cleaned_value:
                    parts = cleaned_value.split('-')
                    if len(parts) == 2:
                        try:
                            # Mengambil rata-rata dari rentang
                            return (float(parts[0]) + float(parts[1])) / 2.0
                        except ValueError:
                            return 0.0
                    return 0.0 # Jika format '-' tidak valid
                else:
                    try:
                        # Angka biasa
                        return float(cleaned_value)
                    except ValueError:
                        return 0.0

            for row in reader:
                character_name_from_csv = row.get('Character', '').strip()

                if not character_name_from_csv:
                    self.stderr.write(self.style.WARNING(f"Melewatkan baris: Nama karakter kosong."))
                    skipped_count += 1
                    continue

                # 1. Pastikan Resonator ada atau buat jika tidak ada
                resonator, created_resonator = Resonator.objects.get_or_create(
                    character_name=character_name_from_csv,
                    defaults={} # Defaults kosong
                )
                if created_resonator:
                    self.stdout.write(self.style.SUCCESS(f'Membuat Resonator baru: {character_name_from_csv}'))
                
                # Mengambil dan parsing nilai stat dari baris CSV
                parsed_hp = parse_stat_value(row.get('hp', '0'))
                parsed_attack = parse_stat_value(row.get('atk', '0'))
                parsed_defense = parse_stat_value(row.get('def', '0'))
                parsed_energy = parse_stat_value(row.get('energy', '0'))
                parsed_crit_rate = parse_stat_value(row.get('crit rate', '0'))
                parsed_crit_dmg = parse_stat_value(row.get('crit dmg', '0'))

                # 2. Buat atau perbarui objek Build
                try:
                    build, created_build = Build.objects.update_or_create(
                        character=resonator,
                        defaults={
                            'hp': parsed_hp,
                            'attack': parsed_attack,
                            'defense': parsed_defense,
                            'energy': parsed_energy,
                            'crit_rate': parsed_crit_rate,
                            'crit_dmg': parsed_crit_dmg,
                        }
                    )
                    if created_build:
                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Berhasil mengimpor build ideal untuk {character_name_from_csv}'))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f'Berhasil memperbarui build ideal untuk {character_name_from_csv}'))
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f'Error mengimpor/memperbarui build untuk {character_name_from_csv}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nProses impor selesai.'))
        self.stdout.write(self.style.SUCCESS(f'Total diimpor: {imported_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total diperbarui: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'Total dilewati (error): {skipped_count}'))