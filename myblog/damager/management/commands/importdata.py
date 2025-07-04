# damager/management/commands/import_combat_data.py

import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# Impor model yang relevan dari aplikasi damager
from resonators.models import Resonator # Impor Resonator dari resonators app
from damager.models import Skill, SkillMultiplier

class Command(BaseCommand):
    help = 'Mengimpor data skill dan multiplier combat dari file CSV yang ada di folder data/csv. Asumsi data Resonator sudah ada.'

    def add_arguments(self, parser):
        # Argumen opsional untuk menentukan direktori data utama (data/)
        # Subfolder 'csv' akan ditambahkan secara otomatis
        parser.add_argument(
            '--base-data-dir',
            type=str,
            help='Direktori dasar tempat folder "csv" berada (default: <project_root>/data)',
            default=None,
        )

    def handle(self, *args, **options):
        # Logika penentuan path CSV dipindahkan ke sini (handle method)
        if options['base_data_dir']:
            base_data_dir = options['base_data_dir']
        else:
            # Menggunakan settings.BASE_DIR, yang tersedia di sini
            base_data_dir = os.path.join(settings.BASE_DIR, 'data')

        csv_data_dir = os.path.join(base_data_dir, 'csv')

        skills_file_path = os.path.join(csv_data_dir, 'skills.csv')
        multipliers_file_path = os.path.join(csv_data_dir, 'skill_multipliers.csv')

        # Pesan informasi path
        self.stdout.write(self.style.NOTICE(f"Mencari file CSV di: {csv_data_dir}"))

        if not os.path.exists(skills_file_path):
            raise CommandError(f"File skills.csv tidak ditemukan di: {skills_file_path}")
        if not os.path.exists(multipliers_file_path):
            raise CommandError(f"File skill_multipliers.csv tidak ditemukan di: {multipliers_file_path}")

        self.stdout.write(self.style.NOTICE("Memulai proses impor data combat..."))
        self.stdout.write(self.style.WARNING("PERHATIAN: Asumsi data Resonator sudah ada di database Anda."))

        self.import_skills(skills_file_path)
        self.import_skill_multipliers(multipliers_file_path)

        self.stdout.write(self.style.SUCCESS("\nProses impor data combat selesai."))

    def import_skills(self, file_path):
        """Mengimpor data skill dari CSV."""
        self.stdout.write(f"Mengimpor skill dari {file_path}...")
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Mengambil Resonator berdasarkan nama
                    resonator = Resonator.objects.get(name=row['character__name'])
                    skill, created = Skill.objects.get_or_create(
                        resonator=resonator,
                        name=row['name'],
                        defaults={
                            'description': row['description'],
                            'skill_type_category': row['skill_type_category']
                        }
                    )
                    if created:
                        self.stdout.write(f"  Membuat Skill: {skill.name} untuk {resonator.name}")
                    else:
                        self.stdout.write(f"  Skill sudah ada: {skill.name} untuk {resonator.name}")
                except Resonator.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"  Error: Resonator '{row['character__name']}' tidak ditemukan untuk skill '{row['name']}'. Dilewati."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error saat mengimpor skill '{row.get('name', 'N/A')}' untuk resonator '{row.get('character__name', 'N/A')}': {e}. Dilewati."))


    def import_skill_multipliers(self, file_path):
        """Mengimpor data multiplier skill dari CSV."""
        self.stdout.write(f"Mengimpor multiplier skill dari {file_path}...")
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Mengambil Resonator berdasarkan nama
                    resonator = Resonator.objects.get(name=row['skill__character__name'])
                    # Mengambil Skill berdasarkan resonator dan nama skill
                    skill = Skill.objects.get(resonator=resonator, name=row['skill__name'])
                    multiplier, created = SkillMultiplier.objects.get_or_create(
                        skill=skill,
                        attack_name=row['attack_name'],
                        defaults={
                            'multiplier_value': float(row['multiplier_value']),
                            'attack_type': row['attack_type']
                        }
                    )
                    if created:
                        self.stdout.write(f"  Membuat Multiplier: {multiplier.attack_name} untuk {skill.name}")
                    else:
                        self.stdout.write(f"  Multiplier sudah ada: {multiplier.attack_name} untuk {skill.name}")
                except (Resonator.DoesNotExist, Skill.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f"  Error: Objek induk tidak ditemukan untuk multiplier '{row['attack_name']}'. Error: {e}. Dilewati."))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"  Error: nilai multiplier_value tidak valid '{row['multiplier_value']}' untuk '{row['attack_name']}'. Dilewati."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error saat mengimpor multiplier '{row.get('attack_name', 'N/A')}': {e}. Dilewati."))
