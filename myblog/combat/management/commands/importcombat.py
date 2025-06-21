# combat/management/commands/import_combat_data.py
import csv
import os
import re 
from django.core.management.base import BaseCommand
from django.conf import settings
from combat.models import Attribute, Role 

class Command(BaseCommand):
    help = 'Mengimpor data Attribute dan Role dari file CSV yang berada di direktori data/ pada root proyek.'

    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        self.stdout.write(self.style.NOTICE(f'Mencari file CSV di: {csv_data_dir}'))

        # --- Impor Data Attribute (Perubahan di sini untuk icon_attribute) ---
        path_csv_attributes = os.path.join(csv_data_dir, 'attributes.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Atribut dari {path_csv_attributes}...'))
        try:
            with open(path_csv_attributes, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        name = baris_data['name']
                        description = baris_data.get('description', '') 
                        
                        # ***** BAGIAN BARU UNTUK ICON_ATTRIBUTE *****
                        # Ambil langsung nama file dari kolom icon_attribute di CSV
                        icon_attribute_filename = baris_data.get('icon_attribute', '')
                        # Bentuk jalur relatif lengkap yang akan disimpan di database
                        # Ini akan menjadi 'attributes_icons/Fusion.png'
                        icon_attribute_path_db = os.path.join('attribute', icon_attribute_filename)
                        # *********************************************

                        obj, created = Attribute.objects.get_or_create(
                            name=name,
                            defaults={
                                'icon_attribute': icon_attribute_path_db # Simpan jalur ikon
                            }
                        )
                        if not created:
                            updated = False
                            if obj.description != description:
                                obj.description = description
                                updated = True
                            # Periksa apakah jalur ikon perlu diperbarui
                            if str(obj.icon_attribute) != icon_attribute_path_db:
                                obj.icon_attribute = icon_attribute_path_db
                                updated = True

                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Attribute: {name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Attribute exists: {name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Attribute: {name}'))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di attributes.csv. Pastikan header "name", "description", dan "icon_attribute" benar.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di attributes.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Attributes.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_attributes} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Attribute: {e}'))

        self.stdout.write("\n")


        # --- Impor Data Role (Tidak ada perubahan di sini) ---
        path_csv_roles = os.path.join(csv_data_dir, 'roles.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Role dari {path_csv_roles}...'))
        try:
            with open(path_csv_roles, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        role_name = baris_data['Role']
                        role_description = baris_data.get('Description', '')
                        
                        icon_filename_from_csv = baris_data.get('icon_role', '')
                        ext = icon_filename_from_csv.split('.')[-1] if '.' in icon_filename_from_csv else 'png'

                        sanitized_base_filename = role_name.replace(' ', '_')
                        sanitized_base_filename = re.sub(r'[^\w\']+', '', sanitized_base_filename)
                        sanitized_base_filename = re.sub(r'_+', '_', sanitized_base_filename).strip('_')
                        
                        icon_role_path_db = os.path.join('roles', f"Icon_{sanitized_base_filename}.{ext}")

                        obj, created = Role.objects.get_or_create(
                            name=role_name,
                            defaults={
                                'description': role_description,
                                'icon_role': icon_role_path_db
                            }
                        )
                        if not created:
                            updated = False
                            if obj.description != role_description:
                                obj.description = role_description
                                updated = True
                            if str(obj.icon_role) != icon_role_path_db:
                                obj.icon_role = icon_role_path_db
                                updated = True

                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Role: {role_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Role exists: {role_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Role: {role_name}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di roles.csv. Pastikan header "Role", "Description", dan "icon_role" benar.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di roles.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Roles.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_roles} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Role: {e}'))