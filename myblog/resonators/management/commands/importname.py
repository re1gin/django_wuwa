# resonators/management/commands/import_resonator_data.py
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
                        weapon_type= baris_data.get('weapon_type')
                        attribute= baris_data.get('attribute')
                        birthplace= baris_data.get('birthplace')
                        role_name = baris_data.get('role_name')

                        weapon_type = None
                        if weapon_type:
                            try:
                                weapon_type = WeaponType.objects.get(name=weapon_type)
                            except WeaponType.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: WeaponType '{weapon_type}' tidak ditemukan untuk Resonator '{name}'."))

                        attribute = None
                        if attribute:
                            try:
                                attribute = Attribute.objects.get(name=attribute)
                            except Attribute.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Attribute '{attribute}' tidak ditemukan untuk Resonator '{name}'."))

                        birthplace = None
                        if birthplace:
                            try:
                                birthplace = Region.objects.get(name=birthplace)
                            except Region.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Region '{birthplace}' tidak ditemukan untuk Resonator '{name}'."))
                        
                        role = None
                        if role_name:
                            try:
                                role = Role.objects.get(name=role_name)
                            except Role.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Role '{role_name}' tidak ditemukan untuk Resonator '{name}'."))

                        # Buat atau perbarui objek Resonator
                        # Field gambar akan diisi di langkah terpisah setelah ini
                        resonator_obj, created = Resonator.objects.get_or_create(
                            name=name,
                            defaults={
                                'rarity': rarity,
                                'weapon_type': weapon_type,
                                'attribute': attribute,
                                'birthplace': birthplace,
                                'role': role,
                            }
                        )

                        if not created:
                            updated = False
                            if resonator_obj.rarity != rarity:
                                resonator_obj.rarity = rarity
                                updated = True
                            if resonator_obj.weapon_type != weapon_type:
                                resonator_obj.weapon_type = weapon_type
                                updated = True
                            if resonator_obj.attribute != attribute:
                                resonator_obj.attribute = attribute
                                updated = True
                            if resonator_obj.birthplace != birthplace:
                                resonator_obj.birthplace = birthplace
                                updated = True
                            if resonator_obj.role != role:
                                resonator_obj.role = role
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

       