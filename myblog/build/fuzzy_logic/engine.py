from .rules import diff_stat_simulation, bonus_stat_simulation, overall_text_quality_sim

def calculate_fuzzy_stat_quality(ideal_val, user_val, stat_category='flat', is_role_priority=False):
    
    try:
        if stat_category in ['flat', 'percent']:
            diff = ideal_val - user_val
            if stat_category == 'flat':
                diff_stat_simulation.input['selisih_besar'] = diff
            else: # percent
                diff_stat_simulation.input['selisih_kecil'] = diff
            diff_stat_simulation.compute()
            return diff_stat_simulation.output['kualitas_stat']
        
        elif stat_category == 'bonus':
            if is_role_priority:
                # Untuk stat bonus yang diprioritaskan, nilai input absolutnya yang dinilai
                bonus_stat_simulation.input['bonus_nilai_input'] = user_val
                bonus_stat_simulation.compute()
                return bonus_stat_simulation.output['kualitas_stat']
            else:
                # Jika tidak diprioritaskan, nilai netral
                return 50 
    except ValueError:
        # Menangani kasus di mana nilai input berada di luar universe yang didefinisikan
        print(f"Peringatan: Nilai stat input ({user_val}) di luar rentang yang diharapkan untuk kategori '{stat_category}'. Mengembalikan skor netral.")
        return 50 
    except Exception as e:
        print(f"Error dalam perhitungan fuzzy stat: {e}") 
        return 0 


def get_overall_build_rating_text(overall_score):
    """
    Menghitung dan mengembalikan teks penilaian kualitas build keseluruhan
    berdasarkan skor numerik (0-100) menggunakan Fuzzy Logic.
    """
    if not isinstance(overall_score, (int, float)):
        return "Tidak Dapat Dinilai" # Menangani input non-numerik

    overall_text_quality_sim.input['overall_performance_score'] = overall_score
    try:
        overall_text_quality_sim.compute()
        deffuzified_value = overall_text_quality_sim.output['text_quality_output']

        # Mengonversi nilai defuzzified ke string teks
        if deffuzified_value < 35: # Ambang batas ini bisa disesuaikan
            return "Perlu Peningkatan"
        elif 35 <= deffuzified_value < 75:
            return "Cukup Baik"
        else:
            return "Sangat Baik"
    except Exception as e:
        print(f"Error dalam perhitungan teks kualitas build keseluruhan: {e}")
        return "Error Penilaian"