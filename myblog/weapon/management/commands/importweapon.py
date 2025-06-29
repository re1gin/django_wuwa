# weapon/management/commands/import_weapon_data.py
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from weapon.models import WeaponType, Weapon

class Command(BaseCommand):
    help = 'Mengimpor data WeaponType dan Weapon dari file CSV dengan semua field.'

    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        self.stdout.write(self.style.NOTICE(f'Mencari file CSV di: {csv_data_dir}'))

        # --- Impor Data WeaponType ---
        path_csv_jenis_senjata = os.path.join(csv_data_dir, 'weapon_types.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Jenis Senjata dari {path_csv_jenis_senjata}...'))
        
        # Create default weapon types if file doesn't exist
        if not os.path.exists(path_csv_jenis_senjata):
            self.stdout.write(self.style.WARNING('File weapon_types.csv tidak ditemukan, membuat default weapon types...'))
            default_types = ['Sword', 'Broadblade', 'Gauntlets', 'Rectifier', 'Pistols', 'Gauntlet']
            for weapon_type in default_types:
                WeaponType.objects.get_or_create(name=weapon_type)
            self.stdout.write(self.style.SUCCESS('Berhasil membuat default weapon types'))
        else:
            try:
                with open(path_csv_jenis_senjata, 'r', encoding='utf-8') as file_csv:
                    csv_reader = csv.DictReader(file_csv)
                    for no_baris, baris_data in enumerate(csv_reader, 1):
                        try:
                            obj, created = WeaponType.objects.get_or_create(name=baris_data['name'])
                            if created:
                                self.stdout.write(self.style.SUCCESS(f'Created WeaponType: {baris_data["name"]}'))
                        except KeyError as e:
                            self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapon_types.csv.'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di weapon_types.csv.'))
                self.stdout.write(self.style.SUCCESS('Selesai impor WeaponTypes.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error persiapan impor WeaponType: {e}'))
                return

        self.stdout.write("\n")

        # --- Impor Data Weapon ---
        path_csv_senjata = os.path.join(csv_data_dir, 'weapons.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Senjata dari {path_csv_senjata}...'))
        
        try:
            with open(path_csv_senjata, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        # Parse required fields
                        weapon_name = baris_data['weapon_name']
                        rarity = int(baris_data['rarity'])
                        weapon_type_name = baris_data['weapon_type']
                        base_atk = int(baris_data['base_atk'])
                        secondary_stat = baris_data['secondary_stat']
                        secondary_value = baris_data['secondary_value']
                        passive_skill_description = baris_data['passive_skill_description']
                        
                        # Handle icon image path
                        icon_img_path_db = baris_data.get('icon_image', '')
                        if not icon_img_path_db:
                            # Generate default path if not provided
                            ext = 'png'
                            sanitized_base_filename = weapon_name.replace(' ', '_')
                            icon_img_path_db = os.path.join('weapon', f"{sanitized_base_filename}.{ext}")

                        # Get or create WeaponType
                        weapon_type_obj = None
                        try:
                            weapon_type_obj = WeaponType.objects.get(name=weapon_type_name)
                        except WeaponType.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Peringatan baris {no_baris}: WeaponType '{weapon_type_name}' tidak ditemukan. Membuat baru."))
                            weapon_type_obj = WeaponType.objects.create(name=weapon_type_name)

                        # Create or update Weapon with all fields
                        weapon_obj, created = Weapon.objects.update_or_create(
                            weapon_name=weapon_name,
                            defaults={
                                'rarity': rarity,
                                'weapon_type': weapon_type_obj,
                                'base_atk': base_atk,
                                'secondary_stat': secondary_stat,
                                'secondary_value': secondary_value,
                                'passive_skill_description': passive_skill_description,
                                'icon_image': icon_img_path_db
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Weapon: {weapon_name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Updated Weapon: {weapon_name}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapons.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Nilai tidak valid ({e}) di weapons.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di weapons.csv.'))
                        continue

            self.stdout.write(self.style.SUCCESS('Selesai impor Weapons.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_senjata} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Weapon: {e}'))