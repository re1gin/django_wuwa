import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from combat.models import Attribute, Role
from resonators.models import Resonator
from region.models import Region
from weapon.models import WeaponType

class Command(BaseCommand):
    help = 'Mengimpor data Resonator dari file CSV dengan penanganan ManyToMany Role'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping them'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        path_csv_resonators = os.path.join(csv_data_dir, 'resonators.csv')
        
        self.stdout.write(self.style.NOTICE(f'Mengimpor data dari: {path_csv_resonators}'))
        
        if not os.path.exists(path_csv_resonators):
            self.stdout.write(self.style.ERROR('File CSV tidak ditemukan!'))
            return

        # Pre-load existing objects for performance
        existing_weapons = {w.name: w for w in WeaponType.objects.all()}
        existing_attrs = {a.name: a for a in Attribute.objects.all()}
        existing_regions = {r.name: r for r in Region.objects.all()}
        existing_roles = {r.name: r for r in Role.objects.all()}

        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        with open(path_csv_resonators, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            total_rows = sum(1 for _ in reader)  # Count total rows
            file.seek(0)  # Reset file pointer
            next(reader)  # Skip header

            for row_num, row in enumerate(reader, 1):
                try:
                    name = row['name']
                    self.stdout.write(f"Processing {row_num}/{total_rows}: {name}", ending='\r')

                    # Get or create related objects
                    weapon_type = existing_weapons.get(row['weapon_type'])
                    if not weapon_type and row['weapon_type']:
                        weapon_type = WeaponType.objects.create(name=row['weapon_type'])
                        existing_weapons[row['weapon_type']] = weapon_type

                    attribute = existing_attrs.get(row['attribute'])
                    if not attribute and row['attribute']:
                        attribute = Attribute.objects.create(name=row['attribute'])
                        existing_attrs[row['attribute']] = attribute

                    birthplace = existing_regions.get(row['birthplace'])
                    if not birthplace and row['birthplace']:
                        birthplace = Region.objects.create(name=row['birthplace'])
                        existing_regions[row['birthplace']] = birthplace

                    # Process roles (handle multiple roles separated by comma)
                    role_names = [r.strip() for r in row['role_name'].split(',')] if row.get('role_name') else []
                    roles = []
                    for role_name in role_names:
                        role = existing_roles.get(role_name)
                        if not role and role_name:
                            role = Role.objects.create(name=role_name)
                            existing_roles[role_name] = role
                        if role:
                            roles.append(role)

                    # Create or update Resonator
                    resonator, created = Resonator.objects.get_or_create(
                        name=name,
                        defaults={
                            'rarity': int(row['rarity']),
                            'weapon_type': weapon_type,
                            'attribute': attribute,
                            'birthplace': birthplace,
                        }
                    )

                    if not created and options['update']:
                        update_fields = []
                        if resonator.rarity != int(row['rarity']):
                            resonator.rarity = int(row['rarity'])
                            update_fields.append('rarity')
                        if resonator.weapon_type != weapon_type:
                            resonator.weapon_type = weapon_type
                            update_fields.append('weapon_type')
                        if resonator.attribute != attribute:
                            resonator.attribute = attribute
                            update_fields.append('attribute')
                        if resonator.birthplace != birthplace:
                            resonator.birthplace = birthplace
                            update_fields.append('birthplace')
                        
                        if update_fields:
                            resonator.save(update_fields=update_fields)
                            stats['updated'] += 1
                            self.stdout.write(self.style.SUCCESS(f'Updated: {name}'))
                        else:
                            stats['skipped'] += 1
                            self.stdout.write(self.style.WARNING(f'Skipped: {name} (no changes)'))
                    elif not created:
                        stats['skipped'] += 1
                        self.stdout.write(self.style.WARNING(f'Skipped: {name} (exists)'))
                    else:
                        stats['created'] += 1
                        self.stdout.write(self.style.SUCCESS(f'Created: {name}'))

                    # Update roles (ManyToMany relationship)
                    if roles or options['update']:
                        resonator.role.set(roles)

                except KeyError as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'Baris {row_num}: Kolom {e} tidak ditemukan'))
                except ValueError as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'Baris {row_num}: Nilai tidak valid: {e}'))
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'Baris {row_num}: Error tak terduga: {e}'))

        # Print summary
        self.stdout.write("\n\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("HASIL IMPOR"))
        self.stdout.write(f"Total diproses: {total_rows}")
        self.stdout.write(f"Baris sukses: {total_rows - stats['errors']}")
        self.stdout.write(f"Resonator baru: {stats['created']}")
        self.stdout.write(f"Resonator diperbarui: {stats['updated']}")
        self.stdout.write(f"Resonator tidak berubah: {stats['skipped']}")
        self.stdout.write(f"Error: {stats['errors']}")
        self.stdout.write("="*50)

        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR("Ada error selama proses impor!"))
        else:
            self.stdout.write(self.style.SUCCESS("Impor berhasil diselesaikan!"))