document.addEventListener('DOMContentLoaded', function() {
    // --- Your existing number input validation JS ---
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('keypress', function(event) {
            const allowedKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'];
            if (!allowedKeys.includes(event.key) &&
                event.key !== 'Backspace' &&
                event.key !== 'Delete' &&
                event.key !== 'Tab' &&
                event.key !== 'Enter' &&
                event.key !== 'ArrowLeft' &&
                event.key !== 'ArrowRight') {
                event.preventDefault();
            }
            if (event.key === '.' && input.value.includes('.')) { event.preventDefault(); }
            if (event.key === '-' && (input.value.includes('-') || input.selectionStart !== 0)) { event.preventDefault(); }
        });
        input.addEventListener('paste', function(event) {
            const pasteData = event.clipboardData.getData('text');
            if (!/^-?\d*\.?\d+$/.test(pasteData)) { event.preventDefault(); }
        });
    });

    // JavaScript for active icon effect
    const activeIcon = document.querySelector('.character-icon.active');
    if (activeIcon) {
        activeIcon.style.border = '2px solid gold';
        activeIcon.style.transform = 'scale(1.1)';
        activeIcon.style.boxShadow = '0 0 10px gold';
    }

    // --- Weapon Select Logic ---
    const weaponSelect = document.getElementById('weapon-select');
    const selectedWeaponImg = document.getElementById('selected-weapon-img');
    const selectedWeaponName = document.getElementById('selected-weapon-name');
    const selectedWeaponStats = document.getElementById('selected-weapon-stats');
    const selectedWeaponPassive = document.getElementById('selected-weapon-passive');

    function updateWeaponDisplay() {
        const selectedOption = weaponSelect.options[weaponSelect.selectedIndex];
        const weaponName = selectedOption.value;

        if (weaponName) {
            const baseAtk = selectedOption.dataset.baseAtk;
            const secondaryStat = selectedOption.dataset.secondaryStat;
            const secondaryValue = selectedOption.dataset.secondaryValue;
            const passiveSkill = selectedOption.dataset.passiveSkill;
            
            const weaponType = document.getElementById('character-weapon-type-hidden').value.toLowerCase();
            const staticUrl = document.getElementById('static-url-hidden').value;

            let imageName = weaponName.replace(/ /g, '_').replace(/#/g, '');
            let imageUrl = `${staticUrl}weapon/${weaponType}/${imageName}.png`;


            selectedWeaponImg.src = imageUrl;
            selectedWeaponName.textContent = weaponName;
            selectedWeaponStats.textContent = `Base ATK: ${baseAtk}, ${secondaryStat}: ${secondaryValue}`;
            selectedWeaponPassive.textContent = `Passive: ${passiveSkill}`;
        } else {
            selectedWeaponImg.src = document.getElementById('weapon-default-img-url').value;
            selectedWeaponName.textContent = "Pilih Senjata";
            selectedWeaponStats.textContent = "";
            selectedWeaponPassive.textContent = "";
        }
    }
    weaponSelect.addEventListener('change', updateWeaponDisplay);
    updateWeaponDisplay(); // Initial call

    // --- Echo Select Logic ---
    const echoSelect = document.getElementById('echo-select');
    const selectedEchoImg = document.getElementById('selected-echo-img');
    const selectedEchoDetails = document.getElementById('selected-echo-details');

    function updateEchoDisplay() {
        const selectedOption = echoSelect.options[echoSelect.selectedIndex];
        const echoName = selectedOption.value;

        if (echoName) {
            const rarity = selectedOption.dataset.rarity;
            const primaryStat = selectedOption.dataset.primaryStat;
            const cost = selectedOption.dataset.cost;

            let imageName = echoName.replace(/ /g, '_').replace(/#/g, '');
            const staticUrl = document.getElementById('static-url-hidden').value;
            let imageUrl = `${staticUrl}ikon/Echo/${imageName}.png`;

            selectedEchoImg.src = imageUrl;
            selectedEchoDetails.textContent = `Rarity: ${rarity}*, Primary Stat: ${primaryStat}, Cost: ${cost}`;
        } else {
            selectedEchoImg.src = document.getElementById('echo-default-img-url').value;
            selectedEchoDetails.textContent = "";
        }
    }
    echoSelect.addEventListener('change', updateEchoDisplay);
    updateEchoDisplay(); // Initial call

    // --- Sonata Select Logic ---
    const sonataSelect = document.getElementById('sonata-select');
    const selectedSonataImg = document.getElementById('selected-sonata-img');
    const selectedSonata2pc = document.getElementById('selected-sonata-2pc');
    const selectedSonata5pc = document.getElementById('selected-sonata-5pc');

    function updateSonataDisplay() {
        const selectedOption = sonataSelect.options[sonataSelect.selectedIndex];
        const sonataName = selectedOption.value;

        if (sonataName) {
            // Mengakses data-attributes. Pastikan ini cocok dengan data-attribute di HTML.
            // Jika HTML Anda memiliki data-2-pc-effect dan data-5-pc-effect
            // maka di JS Anda gunakan:
            const effect2pc = selectedOption.dataset.twoPcEffect;
            const effect5pc = selectedOption.dataset.fivePcEffect;
            
            // Perhatikan bahwa di template HTML yang Anda berikan, 
            // saya kembali mengubahnya menjadi data-2-pc-effect dan data-5-pc-effect
            // agar sesuai dengan penamaan camelCase di JavaScript.

            let imageName = sonataName.replace(/ /g, '_').replace(/#/g, '');
            const staticUrl = document.getElementById('static-url-hidden').value;
            let imageUrl = `${staticUrl}ikon/sonata/${imageName}.png`;

            selectedSonataImg.src = imageUrl;
            selectedSonata2pc.textContent = `2-PC: ${effect2pc}`;
            selectedSonata5pc.textContent = `5-PC: ${effect5pc}`;
        } else {
            selectedSonataImg.src = document.getElementById('sonata-default-img-url').value;
            selectedSonata2pc.textContent = "";
            selectedSonata5pc.textContent = "";
        }
    }
    sonataSelect.addEventListener('change', updateSonataDisplay);
    updateSonataDisplay(); // Initial call
});