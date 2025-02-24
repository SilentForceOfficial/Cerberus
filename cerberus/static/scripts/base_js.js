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
            
        const vuln_info = document.getElementById("id_vulnerabilities")
        const data_info = document.getElementById("id_data")
        const data_arrow=document.getElementById("data-arrow");
        const vuln_arrow=document.getElementById("vuln-arrow");

        // Validate that all variables exist
        if (toggle && nav && bodypd && headerpd) {
            toggle.addEventListener('click', () => {
                // show navbar
                nav.classList.toggle('show')
                // change icon
               
                toggle.classList.toggle('bx-chevron-left')
                toggle.classList.toggle('bx-menu')

                // add padding to body
                bodypd.classList.toggle('body-pd')
                // add padding to header
                headerpd.classList.toggle('body-pd')
                vuln_arrow.classList.remove("fa-caret-up");
                vuln_arrow.classList.add("fa-caret-down");
                data_arrow.classList.remove("fa-caret-up");
                data_arrow.classList.add("fa-caret-down");
                // show/hide all elements with class "hideSubLink"
                const hideSubLinks = document.getElementsByClassName("hideSubLink");
                for (let i = 0; i < hideSubLinks.length; i++) {
                    const element = hideSubLinks[i];
                    element.style.display = "none";
                }
            })

            vuln_info.addEventListener('click', () => {
                    // Establecer la visualización de nav
                
                if (!nav.classList.contains('show')) {
                    nav.classList.toggle('show')
                    toggle.classList.toggle('bx-chevron-left')
                    toggle.classList.toggle('bx-menu')
                    // add padding to body
                    bodypd.classList.toggle('body-pd')
                    // add padding to header
                    headerpd.classList.toggle('body-pd')
                    vuln_arrow.classList.remove("fa-caret-up");
                    vuln_arrow.classList.add("fa-caret-down");
                } 
                vuln_arrow.classList.toggle("fa-caret-down");
                vuln_arrow.classList.toggle("fa-caret-up");
                // show/hide all elements with class "hideSubLink"
                const hideSubLinks = document.getElementsByClassName("hideSubLinkVuln");
                for (let i = 0; i < hideSubLinks.length; i++) {
                    const element = hideSubLinks[i];
                    element.style.display = (element.style.display === "none") ? "block" : "none";
                }
            })

            data_info.addEventListener('click', () => {
                
            
                if (!nav.classList.contains('show')) {
                    nav.classList.toggle('show')
                    toggle.classList.toggle('bx-chevron-left')
                    toggle.classList.toggle('bx-menu')
                    // add padding to body
                    bodypd.classList.toggle('body-pd')
                    // add padding to header
                    headerpd.classList.toggle('body-pd')
                    data_arrow.classList.remove("fa-caret-up");
                    data_arrow.classList.add("fa-caret-down");
                } 
                // show/hide all elements with class "hideSubLink"
                
                data_arrow.classList.toggle("fa-caret-down");
                data_arrow.classList.toggle("fa-caret-up");
                const hideSubLinks = document.getElementsByClassName("hideSubLinkData");
                for (let i = 0; i < hideSubLinks.length; i++) {
                    const element = hideSubLinks[i];
                    element.style.display = (element.style.display === "none") ? "block" : "none";
                }
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