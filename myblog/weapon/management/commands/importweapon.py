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
        
        try:
            with open(path_csv_jenis_senjata, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        weapon_type_name = baris_data['name']
                        icon_filename_from_csv = baris_data.get('icon_image', '').strip()

                        ext = icon_filename_from_csv.split('.')[-1] if '.' in icon_filename_from_csv else 'png'
                        sanitized_base_filename = weapon_type_name.replace(' ', '_')
                        icon_img_path_db = os.path.join('type', f"{sanitized_base_filename}.{ext}")

                        obj, created = WeaponType.objects.get_or_create(
                            name=weapon_type_name, 
                            defaults={'icon_type': icon_img_path_db}
                        )
                        
                        if not created:
                            updated = False
                            if str(obj.icon_type) != icon_img_path_db:
                                obj.icon_type = icon_img_path_db
                                updated = True
                            
                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated WeaponType: {weapon_type_name} with icon: {icon_img_path_db}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'WeaponType exists: {weapon_type_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created WeaponType: {weapon_type_name} with icon: {icon_img_path_db}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapon_types.csv. Pastikan header "name" dan "icon_image" benar.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di weapon_types.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor WeaponTypes.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_jenis_senjata} tidak ditemukan. Silakan buat file weapon_types.csv.'))
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
                        
                        # ***** BAGIAN UNTUK ICON_IMAGE *****
                        icon_img_filename_from_csv = baris_data.get('icon_image', '').strip()
                        ext = icon_img_filename_from_csv.split('.')[-1] if '.' in icon_img_filename_from_csv else 'png'
                        sanitized_base_filename = weapon_name.replace(' ', '_')
                        icon_img_path_db = os.path.join('weapon', f"{sanitized_base_filename}.{ext}")

                        # Get or create WeaponType
                        weapon_type_obj = None
                        try:
                            weapon_type_obj = WeaponType.objects.get(name=weapon_type_name)
                        except WeaponType.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Peringatan baris {no_baris}: WeaponType '{weapon_type_name}' tidak ditemukan. Membuat baru dengan ikon default."))
                            ext_default_type = 'png'
                            sanitized_base_filename_type = weapon_type_name.replace(' ', '_')
                            default_type_icon_path = os.path.join('weapontype', f"{sanitized_base_filename_type}.{ext_default_type}")
                            weapon_type_obj = WeaponType.objects.create(name=weapon_type_name, icon_type=default_type_icon_path)

                        # Create or update Weapon with all fields
                        weapon_obj, created = Weapon.objects.get_or_create(
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

                        if not created:
                            updated = False
                            if weapon_obj.rarity != rarity:
                                weapon_obj.rarity = rarity
                                updated = True
                            if weapon_obj.weapon_type != weapon_type_obj:
                                weapon_obj.weapon_type = weapon_type_obj
                                updated = True
                            if weapon_obj.base_atk != base_atk:
                                weapon_obj.base_atk = base_atk
                                updated = True
                            if weapon_obj.secondary_stat != secondary_stat:
                                weapon_obj.secondary_stat = secondary_stat
                                updated = True
                            if weapon_obj.secondary_value != secondary_value:
                                weapon_obj.secondary_value = secondary_value
                                updated = True
                            if weapon_obj.passive_skill_description != passive_skill_description:
                                weapon_obj.passive_skill_description = passive_skill_description
                                updated = True
                            if str(weapon_obj.icon_image) != icon_img_path_db:
                                weapon_obj.icon_image = icon_img_path_db
                                updated = True

                            if updated:
                                weapon_obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Weapon: {weapon_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Weapon exists: {weapon_name} (no updates to main fields or icon)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Weapon: {weapon_name}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di weapons.csv. Pastikan header benar.'))
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