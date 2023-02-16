function openModal(e) {
    const modalButton = document.querySelector("#waste-select-modal-button")
    modalButton.setAttribute("data-fr-opened", true)
}

document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        const modalButton = document.querySelector("#waste-select-modal-button")
        modalButton.addEventListener("click", openModal)
        modalButton.disabled = false
    }, 1000)
})