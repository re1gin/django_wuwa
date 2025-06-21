# weapon/management/commands/import_weapon_data.py
import csv
import os
# import re # re tidak lagi diperlukan karena hanya mengganti spasi
from django.core.management.base import BaseCommand
from django.conf import settings
from weapon.models import WeaponType, Weapon

class Command(BaseCommand):
    help = 'Mengimpor data WeaponType dan Weapon dari file CSV.'

    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        self.stdout.write(self.style.NOTICE(f'Mencari file CSV di: {csv_data_dir}'))

        # --- Impor Data WeaponType ---
        path_csv_jenis_senjata = os.path.join(csv_data_dir, 'weapon_types.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Jenis Senjata dari {path_csv_jenis_senjata}...'))
        try:
            with open(path_csv_jenis_senjata, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        obj, created = WeaponType.objects.get_or_create(name=baris_data['name'])
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created WeaponType: {baris_data["name"]}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'WeaponType exists: {baris_data["name"]}'))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapon_types.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di weapon_types.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor WeaponTypes.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_jenis_senjata} tidak ditemukan.'))
            return
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
                        weapon_name = baris_data['weapon_name']
                        rarity = int(baris_data['rarity'])
                        weapon_type_name = baris_data['weapon_type']
                        
                        # Bangun jalur ikon: ambil nama senjata, ganti spasi dengan underscore, tambahkan ekstensi.
                        ext = baris_data.get('icon_image', '').split('.')[-1] if '.' in baris_data.get('icon_image', '') else 'png'
                        
                        # Terapkan transformasi spesifik: hanya ganti spasi dengan underscore.
                        sanitized_base_filename = weapon_name.replace(' ', '_')
                        icon_img_path_db = os.path.join('weapon', f"{sanitized_base_filename}.{ext}")

                        # Cari WeaponType
                        weapon_type_obj = None
                        try:
                            weapon_type_obj = WeaponType.objects.get(name=weapon_type_name)
                        except WeaponType.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Peringatan baris {no_baris}: WeaponType '{weapon_type_name}' tidak ditemukan. Mengatur ke NULL."))

                        # Buat atau perbarui objek Weapon
                        weapon_obj, created = Weapon.objects.get_or_create(
                            weapon_name=weapon_name,
                            defaults={
                                'rarity': rarity,
                                'weapon_type': weapon_type_obj,
                                'icon_image': icon_img_path_db
                            }
                        )
                        if not created:
                            updated = False
                            if weapon_obj.rarity != rarity:
                                weapon_obj.rarity = rarity
                                updated = True
                            if weapon_obj.weapon_type != weapon_type_obj:
                                weapon_obj.weapon_type = weapon_type_obj
                                updated = True
                            if str(weapon_obj.icon_image) != icon_img_path_db:
                                weapon_obj.icon_image = icon_img_path_db
                                updated = True
                            
                            if updated:
                                weapon_obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Weapon: {weapon_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Weapon exists: {weapon_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Weapon: {weapon_name}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapons.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Nilai tidak valid ({e}) di weapons.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di weapons.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Weapons.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_senjata} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Weapon: {e}'))