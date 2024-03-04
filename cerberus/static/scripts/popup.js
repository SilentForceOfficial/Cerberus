// const openPopupButton = document.getElementById('openPopupButton');
const closePopupButton = document.getElementById('closePopupButton');
const popupContainer = document.getElementById('popupContainer');
const overlay = document.querySelector('.overlay');
const overlay_trasparente = document.querySelector('.overlay_trasparente');

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
const settingsPopup = document.getElementById('options_menu');
const settingsNeo4jPopup = document.getElementById('settingsNeo4jPopup');
const openPopupButton2 = document.getElementById('openPopupSettings');
const openPopupNeo4j = document.getElementById('openNeo4jSettings');

openPopupButton2.addEventListener('click', () => {
    settingsPopup.style.display = 'block';
    overlay_trasparente.style.display = 'block';
});
openPopupNeo4j.addEventListener('click', () => {
    settingsNeo4jPopup.style.display = 'block';
    overlay.style.display = 'block';
    settingsPopup.style.display = 'none';
    overlay_trasparente.style.display = 'none';
});

closeSettingsPopup2.addEventListener('click', () => {
    settingsNeo4jPopup.style.display = 'none';
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
overlay_trasparente.addEventListener('click', () => {
    // popups=document.getElementsByClassName('popup');
    // for (var i = 0; i < popups.length; i++) {
    //     popups[i].style.display = 'none';
    // }
    settingsPopup.style.display = 'none';
    // popupContainer.style.display = 'none';
    // settingsPopup.style.display = 'none';
    overlay_trasparente.style.display = 'none';
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