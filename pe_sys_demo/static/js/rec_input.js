let UID;
let EID;

$(function () {
    UID = $('#res').attr('name')
    EID = $('#event').attr('eid');
    if (UID && EID){
        fillRecordData();
    }
    bindBtnChooseEvent();
    bindBtnSubEvent();
    bindASelectEvent();
    bindItemSelectEvent();
})

function fillRecordData(){
    $.ajax({
        url:'get_rec/?eid='+EID+'&uid='+UID,
        type:'GET',
        success: function(res){
            if (res.status){
                $.each(res.data, function (index, dict){
                    $('input[name="'+dict.item_id+'"]').val(dict.rec);
                });
            }
        }
    });
}

function bindBtnChooseEvent() {
    $('#user-choose').click(function () {
        var idnum = $('#idnum').val();
        if (EID && idnum){
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
        }
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
                'info': $("#input-content").serialize()
            },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    $('#btnSub').button('submitted');
                    $('#infoModal').modal('show');
                    setTimeout("$('#infoModal').modal('hide');", 800);
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