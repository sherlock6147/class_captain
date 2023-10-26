/* Project specific Javascript goes here. */
function closeMsg(element) {
    element.parentElement.parentElement.style.display = 'none';
}

function closeAll() {
    let msgElement = document.getElementById('msg-element');
    if (msgElement) {
        msgElement.style.display = "none";
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const myTimeout = setTimeout(closeAll, 4500);
});