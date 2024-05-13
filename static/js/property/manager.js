
window.addEventListener('load', () => {
    const container = document.getElementById("add-unit-container");
    const button = document.getElementById("add-unit-btn");

    button.addEventListener("click", function() {
        if (container.classList.contains('hidden')) {
            container.classList.remove("hidden");
            container.classList.add("visible");
            button.innerHTML = "<i class='ti-close'> </i> Close";
            button.className = "btn btn-sm btn-danger mr-2"
        } else {
            container.classList.add("hidden");
            container.classList.remove("visible");
            button.innerHTML = "<i class='ti-save'></i> Add";
            button.className = "btn btn-sm btn-primary mr-2";
        }
    });
})



