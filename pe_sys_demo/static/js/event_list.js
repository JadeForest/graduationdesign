var DEL_EID;
var EDIT_EID;
var LOCK_EID;
var ARC_EID;

$(function () {
    let datetimepicker_args = {
        format: 'yyyy-mm-dd',
        minView: 2,
        language: 'zh-CN',
        autoclose: true
    }
    $('#id_time__lt').datetimepicker(datetimepicker_args);
    $('#id_time__gt').datetimepicker(datetimepicker_args);
    bindBtnAddEvent();
    bindBtnSaveEvent();
    bindBtnDelEvent();
    bindBtnDelConfirmEvent();
    bindBtnEditEvent();
    bindBtnLockEvent();
    bindBtnLockConfirmEvent();
    bindBtnArchiveEvent();
    bindBtnArchiveConfirmEvent();
})

function bindBtnAddEvent() {
    $('#btnAdd').click(function () {
        var curr_time = new Date();
        EDIT_EID = undefined;
        $('#formAdd')[0].reset();

        $('#id_time').datetimepicker({
            format: 'yyyy-mm-dd hh:ii',
            startDate: curr_time,
            language: 'zh-CN',
            autoclose: true
        });

        $('#infoModalLabel').text('新建项目');
        $('#infoModal').modal('show');
    })
}

function bindBtnSaveEvent() {
    $("#btnSave").click(function () {
        // 清除错误信息
        $(".error-msg").empty();

        if (EDIT_EID) {
            // edit
            $.ajax({
                url: "edit/?eid=" + EDIT_EID,
                type: "POST",
                data: $("#formAdd").serialize(),
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {

                        // 刷新页面
                        location.reload();
                    } else {
                        $.each(res.error, function (name, error_list) {
                            $("#" + name + "_err").text(error_list[0])
                        })
                    }
                }
            })
        } else {
            // add
            $.ajax({
                url: "add/",
                type: "POST",
                data: $("#formAdd").serialize(),
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                        // alert('提交成功');

                        // 刷新页面
                        location.reload();
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
    $('.btn-del').click(function () {
        //弹出删除对话框
        $('#delModal').modal('show');

        // 获取要删除的id
        DEL_EID = $(this).attr('eid');
    });
}

function bindBtnDelConfirmEvent() {
    $('#btn-del-conf').click(function () {
        //确认删除 发送
        $.ajax({
            url: "del/",
            type: "POST",
            data: { "eid": DEL_EID },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    // alert('成功');
                    // 关闭对话框 
                    $('#delModal').modal('hide');

                    // 删除该行
                    $('tr[eid="' + DEL_EID + '"]').remove();
                    DEL_EID = 0
                } else {
                    alert(res.error)
                }
            }
        })
    });
}

function bindBtnEditEvent() {
    $('.btn-edit').click(function () {
        // 获取当前行id
        var eid = $(this).attr('eid');
        EDIT_EID = eid;

        // 获取当前行数据
        $.ajax({
            url: 'detail/',
            type: 'GET',
            data: { 'eid': eid },
            dataType: 'JSON',
            success: function (res) {
                if (res.status) {
                    $('#formAdd')[0].reset();

                    // 填入对话框
                    $.each(res.data, function (k, v) {
                        $('#id_' + k).val(v)
                    });

                    // 设置选择框
                    $('#id_time').datetimepicker({
                        format: 'yyyy-mm-dd hh:ii',
                        startDate: new Date($('#id_time').val()),
                        language: 'zh-CN',
                        autoclose: true
                    });

                    // 显示对话框
                    $('#infoModalLabel').text('编辑项目(时间只能向后调整)');
                    $('#infoModal').modal('show');

                } else {
                    alert(res.error);
                }
            }
        })

    });
}

function bindBtnLockEvent() {
    $('.btn-lock').click(function () {
        //弹出删除对话框
        $('#lockModal').modal('show');

        // 获取要删除的id
        LOCK_EID = $(this).attr('eid');
    });
}

function bindBtnLockConfirmEvent() {
    $('#btn-lock-conf').click(function () {
        //确认锁定
        $.ajax({
            url: "lock/",
            type: "POST",
            data: { "eid": LOCK_EID },
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    // 刷新页面
                    LOCK_EID = undefined;
                    location.reload();
                } else {
                    alert(res.error)
                }
            }
        })
    });
}

function bindBtnArchiveEvent() {
    $(".btn-archive").click(function () {
        $("#arcModal").modal('show');

        ARC_EID = $(this).attr('eid');
    })
}

function bindBtnArchiveConfirmEvent() {
    $("#btn-arc-conf").click(function () {
        $.ajax({
            url: 'arc/',
            type: 'POST',
            data: { 'eid': ARC_EID },
            dataType: 'JSON',
            success: function (res) {
                if (res.status) {
                    ARC_EID = undefined;
                    location.reload();
                }
            }
        });
    })
}