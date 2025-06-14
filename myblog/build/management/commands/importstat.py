import csv
import os
import re # Untuk regex parsing
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from resonators.models import Resonator
from build.models import Build

class Command(BaseCommand):
    help = 'Imports ideal build data for characters from a CSV file.'

    def handle(self, *args, **options):
        csv_filepath = os.path.join(settings.BASE_DIR, 'data', 'character_stats.csv')

        if not os.path.exists(csv_filepath):
            raise CommandError(f'CSV file not found at: {csv_filepath}')

        self.stdout.write(self.style.SUCCESS(f'Starting import from {csv_filepath}'))

        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_count = 0
            updated_count = 0
            skipped_count = 0

            for row in reader:
                character_name = row['Character'].strip()
                attribute_name = row['Attribute'].strip()

                # 1. Pastikan Resonator ada atau buat jika tidak ada
                resonator, created = Resonator.objects.get_or_create(
                    character=character_name,
                    defaults={'attribute': attribute_name}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new Resonator: {character_name}'))
                
                try:
                    hp = float(row['hp'])
                except ValueError:
                    hp = 0.0 # Default jika ada masalah parsing

                # Fungsi helper untuk membersihkan nilai stat non-numerik
                def parse_stat_value(value_str):
                    value_str = value_str.strip()
                    if value_str.startswith('>'):
                        # Contoh: ">1900" -> 1900.0
                        return float(value_str[1:])
                    elif '%' in value_str:
                        # Contoh: ">50%" -> 0.50, "100%" -> 1.00
                        num_part = re.sub(r'[^\d.]', '', value_str) # Hapus non-digit kecuali .
                        return float(num_part) / 100.0
                    elif '-' in value_str:
                        # Contoh: "1000-1500" -> (1000+1500)/2 = 1250.0
                        parts = value_str.split('-')
                        if len(parts) == 2:
                            try:
                                return (float(parts[0]) + float(parts[1])) / 2.0
                            except ValueError:
                                return 0.0
                        return 0.0
                    else:
                        # Angka biasa
                        try:
                            return float(value_str)
                        except ValueError:
                            return 0.0

                attack = parse_stat_value(row['atk'])
                defense = parse_stat_value(row['def'])
                energy = parse_stat_value(row['energy'])
                crit_rate = parse_stat_value(row['crit rate']) # Perhatikan "crita rate" di CSV
                crit_dmg = parse_stat_value(row['crit dmg'])

                # 3. Buat atau perbarui objek Build
                try:
                    build, created = Build.objects.update_or_create(
                        character=resonator, # Menggunakan objek Resonator
                        defaults={
                            'hp': hp,
                            'attack': attack,
                            'defense': defense,
                            'energy': energy,
                            'crit_rate': crit_rate,
                            'crit_dmg': crit_dmg,
                        }
                    )
                    if created:
                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported ideal build for {character_name}'))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f'Successfully updated ideal build for {character_name}'))
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f'Error importing build for {character_name}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Import process finished.'))
        self.stdout.write(self.style.SUCCESS(f'Total imported: {imported_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'Total skipped (errors): {skipped_count}'))
