function SLCheck(id) {
    let checked = $("#chkSL" + id).prop("checked");
    if (checked)
        checked = 1;
    else
        checked = 0;

    $.ajax({
        type: 'POST',
        url: '/athlete_set_active/' + id,
        headers: { "X-CSRFToken": token },
        data: {
            'active': checked,
        },
        success: function (data) {
            if (checked)
                LoadStartList();
        }
    });
}

function LoadStartList() {
    $("#divStartList").load("/athlete_start_list_admin/" + ev + "/", function () {
        document.getElementById($("#hdnTopPosition").val()).scrollIntoView(true);
    });
}

function ShowStartList(sl) {

    //$("#modalMainDoc").addClass("modal-lg");
    $("#modalMainTitle").html("Swap Athlete Positions");
    $("#modalBodyArea2").hide();
    $("#modalBodyArea1").empty();
    $("#modalBodyArea1").load("/athlete_start_list_swap/" + sl, function () {

    });

    $("#modalBodyArea1").show();
}

function StartListSwapClick(sl) {
    $.ajax({
        type: 'POST',
        url: '/athlete_start_list_swap_do/',
        headers: { "X-CSRFToken": token },
        data: {
            'sl_orig': $("#hdnSLtoSwap").val(),
            'sl_target':sl,
        },
        success: function (data) {
            LoadStartList();
            $("#modalMain").modal('hide');
        }
    });
}