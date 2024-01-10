function project() {
    let p = document.cookie.split("=")[1];
    if (p !== undefined) {
        document.getElementById("projects").value = p;
        // redirigir(p);
    }
}
function redirigir(value) {
    // console.log(value);
    if (value !== undefined) {
        if (value === "new") {
            popupContainer.style.display = 'block';
            overlay.style.display = 'block';
            var miMenu = document.getElementById("projects");
            miMenu.value= "";
        } else {
            window.location.href = window.location.origin + "/projects/set/" + value;
        }
        // window.location.href = window.location.origin+"/setProject/" + value;
    }
    // document.cookie = "project=" + value;
}

// ------------------------------------------------
document.addEventListener("DOMContentLoaded", function (event) {

    const showNavbar = (toggleId, navId, bodyId, headerId, tablesId) => {
        const toggle = document.getElementById(toggleId),
            nav = document.getElementById(navId),
            bodypd = document.getElementById(bodyId),
            headerpd = document.getElementById(headerId),
            tables_info = document.getElementById(tablesId)

        // Validate that all variables exist
        if (toggle && nav && bodypd && headerpd) {
            toggle.addEventListener('click', () => {
                // show navbar
                nav.classList.toggle('show')
                // change icon
                toggle.classList.toggle('bx-x')
                // add padding to body
                bodypd.classList.toggle('body-pd')
                // add padding to header
                headerpd.classList.toggle('body-pd')
            })
            tables_info.addEventListener('click', () => {
                // show navbar
                nav.classList.add('show')
                // change icon
                toggle.classList.add('bx-x')
                // add padding to body
                bodypd.classList.add('body-pd')
                // add padding to header
                headerpd.classList.add('body-pd')
            })
        }
    }

    showNavbar('header-toggle', 'nav-bar', 'body-pd', 'header', 'id_data' )

    // console.log(' {{ self.title() }}'); // Remove special characters and spaces
    // const linkColor = document.querySelector('#{{self.title() }}');
    // if (linkColor) {
    //   linkColor.classList.add('active');
    // }
    // Texto que deseas buscar dentro de los elementos <span>
    const textoBuscado = "{{ self.title() }}";

    // Seleccionar todos los elementos <a> con la clase "nav_link"
    const enlaces = document.querySelectorAll("a.nav_link");

    // Iterar sobre los elementos <a> y verificar el texto de su <span> hijo
    enlaces.forEach(enlace => {
        const span = enlace.querySelector("span.nav_name");
        if (span && span.textContent === textoBuscado) {
            // Has encontrado el enlace con el texto buscado
            // Puedes hacer lo que necesites con el elemento <a> aquí
            // console.log("Enlace encontrado:", enlace);
            enlace.classList.add('active');
        }
    });


});

// ------------------------------------------------

var myLink = document.querySelector('a[href="#"]');
    myLink.addEventListener('click', function (e) {
      e.preventDefault();
    });


// ------------------------------------------------
async function copyToClipboard(button) {
    const copyText = button.previousElementSibling.textContent;
    const copyText2 = button.parentNode.firstElementChild.textContent;

    try {
        await navigator.clipboard.writeText(copyText2);
        console.log("Texto copiado al portapapeles:", copyText2);
    } catch (err) {
        console.error("Error al copiar el texto al portapapeles:", err);
    }
}