$(function () {
    bindBtnClearSEvent();
})

function bindBtnClearSEvent() {
    $('#clear').click(function () {
        window.location.replace(location.pathname);
    })
}