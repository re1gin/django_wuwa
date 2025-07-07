/**
 * Character Builder JavaScript Module
 * Handles all interactive functionality for the character builder page
 */

class CharacterBuilder {
    constructor(config) {
        // Initialize configuration
        this.config = config || {};
        this.userInputStats = this.config.userInputStats || {};

        // DOM Elements
        this.weaponSelect = document.getElementById('weapon-select');
        this.echoSelect = document.getElementById('echo-select');
        this.sonataSelect = document.getElementById('sonata-select');
        this.weaponIcon = document.getElementById('weapon-icon');
        this.echoIcon = document.getElementById('echo-icon');
        this.sonataIcon = document.getElementById('sonata-icon');
        this.weaponRarityContainer = document.getElementById('weapon-rarity-display-container');
        this.characterLevelDisplay = document.getElementById('character-level-display');
        this.weaponLevelDisplay = document.getElementById('weapon-level-display');
        this.buildForm = document.getElementById('buildForm');
        this.resetButton = document.getElementById('reset-builder-button');
        this.messagesContainer = document.querySelector('.messages');

        // Initialize
        this.initEventListeners();
        this.initializeSelectedItems();
    }

    initEventListeners() {
        if (this.weaponSelect) {
            this.weaponSelect.addEventListener('change', (e) => this.handleSelectChange(e, 'weapon'));
        }
        if (this.echoSelect) {
            this.echoSelect.addEventListener('change', (e) => this.handleSelectChange(e, 'echo'));
        }
        if (this.sonataSelect) {
            this.sonataSelect.addEventListener('change', (e) => this.handleSelectChange(e, 'sonata'));
        }
        if (this.buildForm) {
            this.buildForm.addEventListener('submit', (e) => this.validateForm(e));
        }
        if (this.resetButton) {
            this.resetButton.addEventListener('click', (e) => this.resetBuilder(e));
        }
    }

    initializeSelectedItems() {
        // Initialize weapon if already selected
        if (this.userInputStats.selected_weapon) {
            this.fetchDetails('weapon', this.userInputStats.selected_weapon);
        }

        // Initialize echo if already selected
        if (this.userInputStats.selected_echo) {
            this.fetchDetails('echo', this.userInputStats.selected_echo);
        }

        // Initialize sonata if already selected with echo
        if (this.userInputStats.selected_sonata && this.userInputStats.selected_echo) {
            this.fetchDetails('sonata', this.userInputStats.selected_sonata, this.userInputStats.selected_echo);
        }

        // Initialize level displays
        if (this.characterLevelDisplay) {
            this.characterLevelDisplay.textContent = this.userInputStats.character_level || '1';
        }
        if (this.weaponLevelDisplay) {
            this.weaponLevelDisplay.textContent = this.userInputStats.weapon_level || '1';
        }
    }

    async fetchDetails(itemType, itemName, selectedEchoName = '') {
        const formData = new FormData();
        formData.append('item_type', itemType);
        formData.append('item_name', itemName);
        formData.append('selected_echo_name', selectedEchoName);
        formData.append('csrfmiddlewaretoken', this.config.csrfToken);

        try {
            const response = await fetch(this.config.detailsUrl, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            this.updateUI(itemType, data);
            this.userInputStats[`selected_${itemType}`] = itemName;

        } catch (error) {
            console.error('Error fetching item details:', error);
            this.updateDetails(itemType, null);

            if (itemType === 'echo') {
                this.updateSelectOptions(this.sonataSelect, [], '');
                this.userInputStats.selected_sonata = "";
            }
            this.displayGeneralError(`Gagal memuat detail ${itemType}. Silakan coba lagi.`);
        }
    }

    updateUI(itemType, data) {
        this.updateDetails(itemType, data);

        if (itemType === 'echo') {
            // If selected echo changes, filter sonatas
            this.updateSelectOptions(
                this.sonataSelect, 
                data.filtered_sonatas || [], 
                this.userInputStats.selected_sonata
            );

            // Reset sonata if current selection is invalid
            if (!data.filtered_sonatas?.some(s => s.name === this.sonataSelect.value)) {
                this.sonataSelect.value = "";
                this.updateDetails('sonata', null);
                this.userInputStats.selected_sonata = "";
            }
        }
    }

    updateDetails(itemType, data) {
        const config = {
            'weapon': {
                imgElement: this.weaponIcon,
                detailsContainer: this.weaponRarityContainer,
                defaultIcon: this.config.weaponIconPlaceholder,
                detailsHTML: data?.details ? this.generateStars(data.details.rarity) : ''
            },
            'echo': {
                imgElement: this.echoIcon,
                defaultIcon: this.config.echoIconPlaceholder,
            },
            'sonata': {
                imgElement: this.sonataIcon,
                defaultIcon: this.config.sonataIconPlaceholder,
            }
        };

        const { imgElement, detailsContainer, defaultIcon, detailsHTML } = config[itemType] || {};
        if (!imgElement) return;

        this.updateImage(imgElement, data?.image_url || defaultIcon);
        
        if (detailsContainer && detailsHTML !== undefined) {
            detailsContainer.innerHTML = detailsHTML;
        }
    }

    updateImage(imgElement, src) {
        if (imgElement && src) {
            imgElement.src = src;
            imgElement.style.display = 'block';
        }
    }

    generateStars(rarity) {
        if (typeof rarity !== 'number' || rarity < 1) return '';
        return '⭐'.repeat(rarity);
    }

    updateSelectOptions(selectElement, options, selectedValue) {
        if (!selectElement) return;

        selectElement.innerHTML = '';
        const placeholderOption = document.createElement('option');
        placeholderOption.value = "";
        placeholderOption.textContent = `Pilih ${selectElement.id.replace('-select', '')}`;
        selectElement.appendChild(placeholderOption);

        options.forEach(item => {
            const option = document.createElement('option');
            option.value = item.name || item.weapon_name;
            option.textContent = item.name || item.weapon_name;
            option.selected = (option.value === selectedValue);
            selectElement.appendChild(option);
        });
    }

    handleSelectChange(event, itemType) {
        const selectElement = event.target;
        const itemName = selectElement.value;

        const selectedEchoForFilter = itemType === 'sonata' ? this.echoSelect.value :
                                      (itemType === 'echo' ? itemName : '');

        if (itemType === 'echo') {
            this.sonataSelect.value = "";
            this.userInputStats.selected_sonata = "";
        }

        if (itemName) {
            this.fetchDetails(itemType, itemName, selectedEchoForFilter);
        } else {
            this.updateDetails(itemType, null);
            this.userInputStats[`selected_${itemType}`] = "";
        }
    }

    validateForm(event) {
        this.clearErrors();
        let isValid = true;

        // Validate required number inputs
        const requiredNumberInputs = [
            { name: 'hp', label: 'HP' },
            { name: 'attack', label: 'ATK' },
            { name: 'defense', label: 'DEF' },
            { name: 'energy', label: 'ENERGY REGEN' },
            { name: 'crit_rate', label: 'CRITICAL RATE' },
            { name: 'crit_dmg', label: 'CRITICAL DAMAGE' },
        ];

        requiredNumberInputs.forEach(({name}) => {
            const input = this.buildForm.querySelector(`input[name="${name}"]`);
            if (!input) return;

            const value = input.value.trim();
            if (value === '') {
                input.classList.add('input-error');
                isValid = false;
            } else {
                const numValue = parseFloat(value);
                if (isNaN(numValue)) {
                    input.classList.add('input-error');
                    isValid = false;
                }
            }
        });

        // Validate optional number inputs
        const optionalNumberInputs = [
            { name: 'basic_atk_dmg_bonus', label: 'Basic Attack DMG Bonus' },
            { name: 'resonance_skill_dmg_bonus', label: 'Resonance Skill DMG Bonus' },
            { name: 'resonance_lib_dmg_bonus', label: 'Resonance Liberation DMG Bonus' },
            { name: 'attribute_dmg_bonus', label: 'Attribute DMG Bonus' },
            { name: 'healing_bonus', label: 'Healing Bonus' },
        ];

        optionalNumberInputs.forEach(({name}) => {
            const input = this.buildForm.querySelector(`input[name="${name}"]`);
            if (!input) return;

            const value = input.value.trim();
            if (value !== '' && isNaN(value)) {
                input.classList.add('input-error');
                isValid = false;
            }
        });

        // Validate required selects
        const requiredSelects = [
            { element: this.weaponSelect, label: 'Senjata' },
            { element: this.echoSelect, label: 'Echo' },
            { element: this.sonataSelect, label: 'Efek Sonata' }
        ];

        requiredSelects.forEach(({element}) => {
            if (element && element.value === '') {
                element.classList.add('input-error');
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.displayGeneralError('Terdapat kesalahan pada input Anda. Mohon periksa kembali bidang yang ditandai.');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    async resetBuilder(event) {
        event.preventDefault();
        try {
            const response = await fetch(this.config.resetUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.config.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ character_name: this.config.characterName })
            });

            if (response.ok) {
                window.location.reload();
            } else {
                throw new Error('Failed to reset session');
            }
        } catch (error) {
            console.error('Reset error:', error);
            this.displayGeneralError('Gagal mereset builder. Silakan coba lagi.');
        }
    }

    clearErrors() {
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '';
            this.messagesContainer.style.display = 'none';
        }
        document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
    }

    displayGeneralError(message) {
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = `<li class="error">${message}</li>`;
            this.messagesContainer.style.display = 'block';
        } else {
            alert(message);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('buildForm')) {
        new CharacterBuilder(window.builderConfig);
    }
});