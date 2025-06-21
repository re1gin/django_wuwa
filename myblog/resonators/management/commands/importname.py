import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from combat.models import Attribute, Role
from resonators.models import Resonator
from region.models import Region
from weapon.models import WeaponType


class Command(BaseCommand):
    help = 'Mengimpor data Resonator, rekomendasinya, dan gambar-gambarnya dari file CSV dan folder static.'

    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        self.stdout.write(self.style.NOTICE(f'Mencari file CSV di: {csv_data_dir}'))

        # --- Impor Data Resonator (Bagian ini tidak perlu kolom gambar di CSV lagi) ---
        path_csv_resonators = os.path.join(csv_data_dir, 'resonators.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Resonator dari {path_csv_resonators}...'))
        try:
            with open(path_csv_resonators, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        name = baris_data['name']
                        rarity = int(baris_data['rarity'])

                        # Ambil nilai dari CSV terlebih dahulu
                        weapon_type_name = baris_data.get('weapon_type')
                        attribute_name = baris_data.get('attribute')
                        birthplace_name = baris_data.get('birthplace')
                        role_name = baris_data.get('role_name') # Pastikan nama kolom di CSV sesuai

                        # Inisialisasi objek terkait ke None
                        weapon_type_obj = None
                        attribute_obj = None
                        birthplace_obj = None
                        role_obj = None

                        # Lakukan pencarian objek hanya jika nama ditemukan di CSV
                        if weapon_type_name:
                            try:
                                weapon_type_obj = WeaponType.objects.get(name=weapon_type_name)
                            except WeaponType.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: WeaponType '{weapon_type_name}' tidak ditemukan untuk Resonator '{name}'."))

                        if attribute_name:
                            try:
                                attribute_obj = Attribute.objects.get(name=attribute_name)
                            except Attribute.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Attribute '{attribute_name}' tidak ditemukan untuk Resonator '{name}'."))

                        if birthplace_name:
                            try:
                                birthplace_obj = Region.objects.get(name=birthplace_name)
                            except Region.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Region '{birthplace_name}' tidak ditemukan untuk Resonator '{name}'."))
                        
                        if role_name:
                            try:
                                role_obj = Role.objects.get(name=role_name)
                            except Role.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Role '{role_name}' tidak ditemukan untuk Resonator '{name}'."))

                        # Buat atau perbarui objek Resonator
                        # Gunakan objek yang telah dicari (atau None jika tidak ditemukan)
                        resonator_obj, created = Resonator.objects.get_or_create(
                            name=name,
                            defaults={
                                'rarity': rarity,
                                'weapon_type': weapon_type_obj,
                                'attribute': attribute_obj,
                                'birthplace': birthplace_obj,
                                'role': role_obj,
                            }
                        )

                        if not created:
                            updated = False
                            # Periksa dan perbarui hanya jika nilai berbeda
                            if resonator_obj.rarity != rarity:
                                resonator_obj.rarity = rarity
                                updated = True
                            if resonator_obj.weapon_type != weapon_type_obj:
                                resonator_obj.weapon_type = weapon_type_obj
                                updated = True
                            if resonator_obj.attribute != attribute_obj:
                                resonator_obj.attribute = attribute_obj
                                updated = True
                            if resonator_obj.birthplace != birthplace_obj:
                                resonator_obj.birthplace = birthplace_obj
                                updated = True
                            if resonator_obj.role != role_obj:
                                resonator_obj.role = role_obj
                                updated = True
                            
                            if updated:
                                resonator_obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Resonator: {name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Resonator exists: {name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Resonator: {name}'))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di resonators.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Invalid value ({e}) di resonators.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di resonators.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Resonator.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_resonators} tidak ditemukan.'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Resonator: {e}'))

        self.stdout.write("\n")