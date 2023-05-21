let UID;
let EID;

$(function () {
    UID = $('#res').attr('name')
    EID = $('#event').attr('eid');
    bindBtnChooseEvent();
    bindBtnSubEvent();
    bindASelectEvent();
    bindItemSelectEvent();
})

function bindBtnChooseEvent() {
    $('#user-choose').click(function () {
        var idnum = $('#idnum').val();
        $.ajax({
            url: 'get_user/',
            type: 'POST',
            data: { 'idnum': idnum },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    UID = res.uid;
                    window.location.replace(location.pathname + '?eid=' + EID + '&uid=' + UID);
                } else {
                    alert(res.error);
                }
            }
        })
    });
}

function bindBtnSubEvent() {
    $('#btnSub').click(function () {
        $.ajax({
            url: "submit/",
            type: "POST",
            data: {
                'uid': UID,
                'eid': EID,
                'info': $("#review-content").serialize()
            },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    $('#infoModal').modal('show');
                    setTimeout("location.reload();", 970);
                } else {
                    alert(res.error);
                }
            }
        })
    });
}

function bindASelectEvent() {
    $('.sitem').click(function () {
        $('#idnum').val($(this).attr('value'));
    })
}

function bindItemSelectEvent() {
    $('#event-choose').click(function () {
        EID = $('#etime').find('option:selected').attr('eid');
        window.location.replace(location.pathname + '?eid=' + EID);
    })
}