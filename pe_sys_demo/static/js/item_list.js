var DEL_TID;
var EDIT_TID;

$(function () {
    bindBtnAddEvent();
    bindBtnSaveEvent();
    bindBtnDelEvent();
    bindBtnDelConfirmEvent();
    bindBtnEditEvent();
})

function bindBtnAddEvent() {
    $('#btnAdd').click(function () {
        EDIT_TID = undefined;
        $(".error-msg").empty();
        $('#formAdd')[0].reset();

        $('#infoModalLabel').text('新建项目');
        $('#infoModal').modal('show');
    })
}

function bindBtnSaveEvent() {
    $("#btnSave").click(function () {
        // 清除错误信息
        $(".error-msg").empty();

        if (EDIT_TID) {
            // 如果有ID，则是编辑
            $.ajax({
                url: "edit/?item_id=" + EDIT_TID,
                type: "POST",
                data: $("#formAdd").serialize(),
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                        // 局部刷新
                        $('#infoModal').modal('hide');
                        $('#res').load(window.location.href+" #res-content");
                    } else {
                        $.each(res.error, function (name, error_list) {
                            $("#" + name + "_err").text(error_list[0])
                        })
                    }
                }
            })
        } else {
            // 否则是添加
            $.ajax({
                url: "add/",
                type: "POST",
                data: $("#formAdd").serialize(),
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                        // 局部刷新
                        $('#infoModal').modal('hide');
                        $('#res').load(window.location.href+" #res-content");
                    } else {
                        $.each(res.error, function (name, error_list) {
                            $("#" + name + "_err").text(error_list[0])
                        })
                    }
                }
            })
        }
    });
}

function bindBtnDelEvent() {
    $(document).on('click','.btn-del',function () {
        //弹出删除对话框
        $('#delModal').modal('show');

        // 获取要删除的id
        DEL_TID = $(this).attr('item_id');

    });
}

function bindBtnDelConfirmEvent() {
    $('#btn-del-conf').click(function () {
        //确认删除 发送
        $.ajax({
            url: "del/",
            type: "POST",
            data: { "item_id": DEL_TID },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    // 局部刷新
                    $('#delModal').modal('hide');
                    $('#res').load(window.location.href+" #res-content");
                    
                    DEL_TID = undefined;
                } else {
                    alert(res.error)
                }
            }
        })
    });
}

function bindBtnEditEvent() {
    $(document).on('click','.btn-edit',function () {
        // 获取当前行id
        EDIT_TID = $(this).attr('item_id');

        // 获取当前行数据
        $.ajax({
            url: 'detail/',
            type: 'GET',
            data: { 'item_id': EDIT_TID },
            dataType: 'JSON',
            success: function (res) {
                if (res.status) {
                    $('#formAdd')[0].reset();
                    // 填入对话框
                    $.each(res.data, function (k, v) {
                        $('#formAdd #id_' + k).val(v)
                    });

                    // 显示对话框
                    $('#infoModalLabel').text('编辑项目');
                    $('#infoModal').modal('show');

                } else {
                    alert(res.error);
                }
            }
        })

    });
}
