// const openPopupButton = document.getElementById('openPopupButton');
const closePopupButton = document.getElementById('closePopupButton');
const popupContainer = document.getElementById('popupContainer');
const overlay = document.querySelector('.overlay');

// openPopupButton.addEventListener('click', () => {
//     popupContainer.style.display = 'block';
//     overlay.style.display = 'block';
// });

closePopupButton.addEventListener('click', () => {
    popupContainer.style.display = 'none';
    overlay.style.display = 'none';
});



// const openPopupButton = document.getElementById('openPopupButton');
const closeSettingsPopup2 = document.getElementById('closeSettingsPopup2');
const settingsPopup = document.getElementById('settingsPopup');
const openPopupButton2 = document.getElementById('openPopupSettings');

openPopupButton2.addEventListener('click', () => {
    settingsPopup.style.display = 'block';
    overlay.style.display = 'block';
});

closeSettingsPopup2.addEventListener('click', () => {
    settingsPopup.style.display = 'none';
    overlay.style.display = 'none';
});

overlay.addEventListener('click', () => {
    popups=document.getElementsByClassName('popup');
    for (var i = 0; i < popups.length; i++) {
        popups[i].style.display = 'none';
    }
    // popupContainer.style.display = 'none';
    // settingsPopup.style.display = 'none';
    overlay.style.display = 'none';
});
const closeButtons=document.getElementsByClassName('button-popup-close');
for (var i = 0; i < closeButtons.length; i++) {
    closeButtons[i].addEventListener('click', () => {
        popups=document.getElementsByClassName('popup');
        for (var i = 0; i < popups.length; i++) {
            popups[i].style.display = 'none';
        }
        // popupContainer.style.display = 'none';
        // settingsPopup.style.display = 'none';
        overlay.style.display = 'none';
    });
}