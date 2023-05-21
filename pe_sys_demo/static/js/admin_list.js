var DEL_UID;
var EDIT_UID;

$(function () {
    bindBtnAddEvent();
    bindBtnSaveEvent();
    bindBtnDelEvent();
    bindBtnDelConfirmEvent();
    bindBtnEditEvent();
})

function bindBtnAddEvent() {
    $('#btnAdd').click(function () {
        EDIT_UID = undefined;
        // 清除信息 
        $(".error-msg").empty();
        $('#formAdd')[0].reset();

        $('#infoModalLabel').text('添加用户');
        $('#infoModal').modal('show');
    })
}

function bindBtnSaveEvent() {
    $("#btnSave").click(function () {
        // 清除错误信息
        $(".error-msg").empty();

        if (EDIT_UID) {
            // 如果有ID，则是编辑
            $.ajax({
                url: "edit/?uid=" + EDIT_UID,
                type: "POST",
                data: $("#formAdd").serialize(),
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                        // 局部刷新
                        $('#infoModal').modal('hide');
                        $('#res').load(window.location.href + " #res-content");
                    } else {
                        $.each(res.a_err, function (name, err_list) {
                            $("#" + name + "_err").text(err_list[0])
                        });
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
                        $('#res').load(window.location.href + " #res-content");
                    } else {
                        $.each(res.a_err, function (name, err_list) {
                            $("#" + name + "_err").text(err_list[0])
                        });
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
        DEL_UID = $(this).attr('uid');
    });
}

function bindBtnDelConfirmEvent() {
    $('#btn-del-conf').click(function () {
        //确认删除 发送
        $.ajax({
            url: "del/",
            type: "POST",
            data: { "uid": DEL_UID },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    // 局部刷新
                    $('#delModal').modal('hide');
                    $('#res').load(window.location.href + " #res-content");

                    DEL_UID = undefined;
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
        EDIT_UID = $(this).attr('uid');

        // 获取当前行数据
        $.ajax({
            url: 'detail/',
            type: 'GET',
            data: { 'uid': EDIT_UID },
            dataType: 'JSON',
            success: function (res) {
                if (res.status) {
                    $('#formAdd')[0].reset();
                    // 填入对话框
                    $.each(res.data, function (k, v) {
                        $('#formAdd #id_' + k).val(v)
                    });

                    // 显示对话框
                    $('#infoModalLabel').text('编辑用户');
                    $('#infoModal').modal('show');

                } else {
                    alert(res.error);
                }
            }
        })
    });
}