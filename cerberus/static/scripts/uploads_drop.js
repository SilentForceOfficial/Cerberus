// Modules
var dropArea = document.getElementById("drop-area-modules");
var inputFile = document.getElementById("dataFileModules");
var spanFile = document.getElementById("drop-area-span-file-modules");

// Tickets
var dropArea2 = document.getElementById("drop-area-tickets");
var inputFile2 = document.getElementById("dataFileTickets");
var spanFile2 = document.getElementById("drop-area-span-file-tickets");

// AD Dump
var dropArea3 = document.getElementById("drop-area-dump");
var inputFile3 = document.getElementById("dataFileDump");
var spanFile3 = document.getElementById("drop-area-span-file-dump");

// NMAPXML
var dropArea3 = document.getElementById("drop-area-dump");
var inputFile3 = document.getElementById("dataFileNmaps");
var spanFile3 = document.getElementById("drop-area-span-file-nmaps");

// function changeSpan(inputFile,spanFile) {
//     if (inputFile.files.length > 1) {
//         spanFile.textContent = inputFile.files.length + " files selected";
//     } else {
//         spanFile.textContent = inputFile.files[0].name;

//     }
// };
window.addEventListener('load', function () {
    inputFile.addEventListener("change", function (){
        if (inputFile.files.length > 1) {
            spanFile.textContent = inputFile.files.length + " files selected";
        } else {
            spanFile.textContent = inputFile.files[0].name;
    
        }
    });

    dropArea.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea.addEventListener("drop", function (e) {
            e.preventDefault();
            inputFile.files = e.dataTransfer.files;
            if (inputFile.files.length > 1) {
                spanFile.textContent = inputFile.files.length + " files selected";
            } else {
                spanFile.textContent = inputFile.files[0].name;
        
            }

        });
    });

    // 2
    inputFile2.addEventListener("change", function (){
        if (inputFile2.files.length > 1) {
            spanFile2.textContent = inputFile2.files.length + " files selected";
        } else {
            spanFile2.textContent = inputFile2.files[0].name;
    
        }
    });

    dropArea2.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea2.addEventListener("drop", function (e) {
            e.preventDefault();
            inputFile2.files = e.dataTransfer.files;
            if (inputFile2.files.length > 1) {
                spanFile2.textContent = inputFile2.files.length + " files selected";
            } else {
                spanFile2.textContent = inputFile2.files[0].name;
        
            }

        });
    });

    // 3
    inputFile3.addEventListener("change", function (){
        if (inputFile3.files.length > 1) {
            spanFile3.textContent = inputFile3.files.length + " files selected";
        } else {
            spanFile3.textContent = inputFile3.files[0].name;
    
        }
    });

    dropArea3.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea3.addEventListener("drop", function (e) {
            e.preventDefault();
            inputFile3.files = e.dataTransfer.files;
            if (inputFile3.files.length > 1) {
                spanFile3.textContent = inputFile3.files.length + " files selected";
            } else {
                spanFile3.textContent = inputFile3.files[0].name;
        
            }

        });
    });
});


