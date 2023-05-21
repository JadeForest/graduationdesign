$(function () {
    getExistList();
    bindCheckEvent();
    bindBtnSubmitEvent();
    bindBtnExitEvent();
    bindBtnRefreshEvent();
    bindBtnClearAllEvent();
    bindBtnSelectAllEvent();
})

function getExistList() {
    $('.check').prop('checked',false);
    // 如果本地已有则读取
    let list = localStorage.getItem('list')
    if (list != null) {
        list = list === '' ? [] : list.split(',');
        $.each(list, function (index, value) {
            $('#' + value).prop('checked', true);
        });
        $('#totalnum').text(list.length);
    } else {// 否则向服务器获取
        $.ajax({
            url: 'get_exist/',
            type: 'POST',
            success: function (res) {
                if (res.status) {
                    list = res.data.split(',');
                } else {
                    list = [];
                }
                localStorage.setItem('list', list);
                $.each(list, function (index, value) {
                    $('#' + value).prop('checked', true);
                });
                $('#totalnum').text(list.length);
            }
        });
    }
}

function bindCheckEvent() {
    $('.check').change(function () {
        let list = localStorage.getItem('list');
        list = list === '' ? [] : list.split(',');
        let id = $(this).attr('id');
        if (this.checked) {
            list.push(id);
            console.log(list);
        } else {
            list.splice($.inArray(id, list), 1);
            console.log(list);
        }
        $('#totalnum').text(list.length);
        localStorage.setItem('list', list);
    })
}

function bindBtnSubmitEvent() {
    $('#sub').click(function () {
        ulist_str = localStorage.getItem('list');

        $.ajax({
            url: "submit/",
            type: "POST",
            data: { 'ulist': ulist_str },
            dataType: 'JSON',

            success: function (res) {
                if (res.status) {
                    localStorage.clear();
                    window.location.href = '../';
                }
            }
        })
    })
}

function bindBtnExitEvent() {
    $('#exit').click(function () {
        localStorage.clear();
    })
}

function bindBtnRefreshEvent() {
    $('#refresh').click(function () {
        localStorage.clear();
        location.reload();
    })
}

function bindBtnClearAllEvent(){
    $('#clearAll').click(function(){
        localStorage.setItem('list',[]);
        getExistList();
    })
}

function bindBtnSelectAllEvent(){
    $('#selectAll').click(function (){
        $.ajax({
            url: location.pathname + 'all/' + location.search,
            type: 'POST',
            data: {'method':'SELECT'},
            dataType: 'JSON',
            success: function(res) {
                if (res.status && res.hasValue) {
                    selected = res.data.split(',');
                }else if(res.status){
                    selected = [];
                }
                let list = localStorage.getItem('list');
                list = list === '' ? [] : list.split(',');
                list = list.concat(selected);
                list = list.filter((item,index) => list.indexOf(item)==index);

                localStorage.setItem('list',list);
                getExistList();
            }
        });
    });
}