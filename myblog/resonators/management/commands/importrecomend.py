import os
import csv

from django.core.management.base import BaseCommand
from myblog.echo.models import Echo, Sonata
from myblog.weapon.models import Weapon
from resonators.models import Resonator, ResonatorRecommendedEcho, ResonatorRecommendedSonata, ResonatorRecommendedWeapon

class Command(BaseCommand):
    help = 'Import recommended weapons, echos, and sonatas for resonators from CSV files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-data-dir',
            type=str,
            default='.',
            help='Directory where the CSV files are located.'
        )

    def handle(self, *args, **options):
        csv_data_dir = options['csv_data_dir']

        # --- Impor Data ResonatorRecommendedWeapon (tidak ada perubahan) ---
        path_csv_rec_weapons = os.path.join(csv_data_dir, 'resonator_recommended_weapons.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Resonator Recommended Weapons dari {path_csv_rec_weapons}...'))
        try:
            with open(path_csv_rec_weapons, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        resonator_name = baris_data['resonator_name']
                        weapon_name = baris_data['weapon_name']
                        priority_level = int(baris_data['priority_level'])
                        notes = baris_data.get('notes', '')

                        resonator = Resonator.objects.get(name=resonator_name)
                        weapon = Weapon.objects.get(weapon_name=weapon_name)

                        obj, created = ResonatorRecommendedWeapon.objects.get_or_create(
                            resonator=resonator,
                            weapon=weapon,
                            defaults={
                                'priority_level': priority_level,
                                'notes': notes
                            }
                        )
                        if not created:
                            updated = False
                            if obj.priority_level != priority_level:
                                obj.priority_level = priority_level
                                updated = True
                            if obj.notes != notes:
                                obj.notes = notes
                                updated = True
                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Rec Weapon: {resonator_name} - {weapon_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Rec Weapon exists: {resonator_name} - {weapon_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Rec Weapon: {resonator_name} - {weapon_name}'))

                    except Resonator.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Resonator '{resonator_name}' tidak ditemukan untuk rekomendasi senjata."))
                    except Weapon.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Weapon '{weapon_name}' tidak ditemukan untuk rekomendasi senjata."))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di resonator_recommended_weapons.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Invalid value ({e}) di resonator_recommended_weapons.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di resonator_recommended_weapons.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Resonator Recommended Weapons.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_rec_weapons} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Resonator Recommended Weapons: {e}'))

        self.stdout.write("\n")

        # --- Impor Data ResonatorRecommendedEcho (tidak ada perubahan) ---
        path_csv_rec_echos = os.path.join(csv_data_dir, 'resonator_recommended_echos.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Resonator Recommended Echos dari {path_csv_rec_echos}...'))
        try:
            with open(path_csv_rec_echos, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        resonator_name = baris_data['resonator_name']
                        echo_name = baris_data['echo_name']
                        priority_level = int(baris_data['priority_level'])
                        notes = baris_data.get('notes', '')

                        resonator = Resonator.objects.get(name=resonator_name)
                        echo = Echo.objects.get(name=echo_name)

                        obj, created = ResonatorRecommendedEcho.objects.get_or_create(
                            resonator=resonator,
                            echo=echo,
                            defaults={
                                'priority_level': priority_level,
                                'notes': notes
                            }
                        )
                        if not created:
                            updated = False
                            if obj.priority_level != priority_level:
                                obj.priority_level = priority_level
                                updated = True
                            if obj.notes != notes:
                                obj.notes = notes
                                updated = True
                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Rec Echo: {resonator_name} - {echo_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Rec Echo exists: {resonator_name} - {echo_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Rec Echo: {resonator_name} - {echo_name}'))

                    except Resonator.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Resonator '{resonator_name}' tidak ditemukan untuk rekomendasi Echo."))
                    except Echo.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Echo '{echo_name}' tidak ditemukan untuk rekomendasi Echo."))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di resonator_recommended_echos.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Invalid value ({e}) di resonator_recommended_echos.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di resonator_recommended_echos.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Resonator Recommended Echos.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_rec_echos} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Resonator Recommended Echos: {e}'))

        self.stdout.write("\n")

        # --- Impor Data ResonatorRecommendedSonata (tidak ada perubahan) ---
        path_csv_rec_sonatas = os.path.join(csv_data_dir, 'resonator_recommended_sonatas.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Resonator Recommended Sonatas dari {path_csv_rec_sonatas}...'))
        try:
            with open(path_csv_rec_sonatas, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        resonator_name = baris_data['resonator_name']
                        sonata_name = baris_data['sonata_name']
                        priority_level = int(baris_data['priority_level'])
                        notes = baris_data.get('notes', '')

                        resonator = Resonator.objects.get(name=resonator_name)
                        sonata = Sonata.objects.get(name=sonata_name)

                        obj, created = ResonatorRecommendedSonata.objects.get_or_create(
                            resonator=resonator,
                            sonata=sonata,
                            defaults={
                                'priority_level': priority_level,
                                'notes': notes
                            }
                        )
                        if not created:
                            updated = False
                            if obj.priority_level != priority_level:
                                obj.priority_level = priority_level
                                updated = True
                            if obj.notes != notes:
                                obj.notes = notes
                                updated = True
                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Rec Sonata: {resonator_name} - {sonata_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Rec Sonata exists: {resonator_name} - {sonata_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Rec Sonata: {resonator_name} - {sonata_name}'))

                    except Resonator.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Resonator '{resonator_name}' tidak ditemukan untuk rekomendasi Sonata."))
                    except Sonata.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Sonata '{sonata_name}' tidak ditemukan untuk rekomendasi Sonata."))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di resonator_recommended_sonatas.csv.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Invalid value ({e}) di resonator_recommended_sonatas.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di resonator_recommended_sonatas.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Resonator Recommended Sonatas.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_rec_sonatas} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Resonator Recommended Sonatas: {e}'))