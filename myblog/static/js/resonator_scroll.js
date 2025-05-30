
document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('iconContainer');
    const activeIcon = container.querySelector('.character-icon.active');

    if (activeIcon) {
        // Hitung posisi gulir supaya ikon aktif ada di tengah
        const offsetLeft  = activeIcon.offsetLeft;          // titik awal ikon
        const iconWidth   = activeIcon.offsetWidth;         // lebar ikon
        const containerWidth = container.clientWidth;       // lebar viewport kontainer

        const targetScrollLeft =
              offsetLeft - (containerWidth / 2) + (iconWidth / 2);

        container.scrollTo({ left: targetScrollLeft, behavior: 'smooth' });
        // pakai 'auto' atau hapus 'behavior' jika tidak ingin animasi
    }
});

