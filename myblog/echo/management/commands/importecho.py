# echoes/management/commands/import_echo_data.py
import csv
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from echo.models import Sonata, Echo

class Command(BaseCommand):
    help = 'Mengimpor data Sonata dan Echo dari file CSV yang berada di direktori data/ pada root proyek.'

    def handle(self, *args, **options):
        csv_data_dir = os.path.join(settings.BASE_DIR, 'data', 'csv')
        self.stdout.write(self.style.NOTICE(f'Mencari file CSV di: {csv_data_dir}'))
        

        # --- Impor Data Sonata (Tidak ada perubahan di sini) ---
        path_csv_sonatas = os.path.join(csv_data_dir, 'sonata.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Sonatas dari {path_csv_sonatas}...'))
        try:
            with open(path_csv_sonatas, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        sonata_name = baris_data['name']
                        icon_filename_from_csv = baris_data.get('icon_sonata', '')
                        ext = icon_filename_from_csv.split('.')[-1] if '.' in icon_filename_from_csv else 'png'
                        sanitized_base_filename = sonata_name.replace(' ', '_')
                        icon_sonata_path_db = os.path.join('sonata', f"{sanitized_base_filename}.{ext}")

                        obj, created = Sonata.objects.get_or_create(
                            name=sonata_name,
                            defaults={
                                'icon_sonata': icon_sonata_path_db
                            }
                        )
                        if not created:
                            updated = False
                            if str(obj.icon_sonata) != icon_sonata_path_db:
                                obj.icon_sonata = icon_sonata_path_db
                                updated = True

                            if updated:
                                obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Sonata: {sonata_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Sonata exists: {sonata_name} (no updates)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Sonata: {sonata_name}'))
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di sonatas.csv. Pastikan header "name" dan "icon_sonata" benar.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di sonatas.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Sonatas.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_sonatas} tidak ditemukan. Pastikan file ini ada.'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Sonata: {e}'))

        self.stdout.write("\n")


        # --- Impor Data Echo (Perubahan di sini untuk icon_echo) ---
        path_csv_echos = os.path.join(csv_data_dir, 'echo.csv')
        self.stdout.write(self.style.SUCCESS(f'Mengimpor Echos dari {path_csv_echos}...'))
        try:
            with open(path_csv_echos, 'r', encoding='utf-8') as file_csv:
                csv_reader = csv.DictReader(file_csv)
                for no_baris, baris_data in enumerate(csv_reader, 1):
                    try:
                        echo_name = baris_data['name']
                        cost = int(baris_data['cost'])
                        sonatas_str = baris_data.get('sonatas', '')

                        # ***** BAGIAN BARU UNTUK ICON_ECHO *****
                        # Ambil nama file icon dari CSV, atau asumsikan .png jika tidak ada ekstensi
                        icon_echo_filename_from_csv = baris_data.get('icon_echo', '')
                        ext = icon_echo_filename_from_csv.split('.')[-1] if '.' in icon_echo_filename_from_csv else 'png'
                        
                        sanitized_base_filename = echo_name.replace(' ', '_')
                        
                        icon_echo_path_db = os.path.join('echo', f"{sanitized_base_filename}_Icon.{ext}")

                        echo_obj, created = Echo.objects.get_or_create(
                            name=echo_name,
                            defaults={
                                'cost': cost,
                                'icon_echo': icon_echo_path_db
                            }
                        )

                        if not created:
                            updated = False
                            if echo_obj.cost != cost:
                                echo_obj.cost = cost
                                updated = True
                            # Periksa apakah jalur ikon perlu diperbarui
                            if str(echo_obj.icon_echo) != icon_echo_path_db:
                                echo_obj.icon_echo = icon_echo_path_db
                                updated = True

                            if updated:
                                echo_obj.save()
                                self.stdout.write(self.style.SUCCESS(f'Updated Echo: {echo_name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'Echo exists: {echo_name} (no updates to main fields or icon)'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'Created Echo: {echo_name}'))

                        echo_obj.sonatas.clear()
                        if sonatas_str:
                            sonata_names = [s.strip() for s in sonatas_str.split(',') if s.strip()]
                            for s_name in sonata_names:
                                try:
                                    sonata_obj = Sonata.objects.get(name=s_name)
                                    echo_obj.sonatas.add(sonata_obj)
                                except Sonata.DoesNotExist:
                                    self.stdout.write(self.style.ERROR(f"Error baris {no_baris}: Sonata '{s_name}' tidak ditemukan untuk Echo '{echo_name}'. Pastikan semua sonata tercantum di sonatas.csv."))
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f"Error tak terduga saat menambahkan sonata '{s_name}' ke Echo '{echo_name}': {e}"))

                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Kolom "{e}" hilang di echos.csv. Pastikan header "name", "cost", "sonatas", dan "icon_echo" benar.'))
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Error baris {no_baris}: Nilai tidak valid ({e}) untuk "cost" di echos.csv.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error tak terduga baris {no_baris}: {e} di echos.csv.'))
            self.stdout.write(self.style.SUCCESS('Selesai impor Echos.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {path_csv_echos} tidak ditemukan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error persiapan impor Echo: {e}'))