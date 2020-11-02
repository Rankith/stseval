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
        if ($("#hdnTopPosition").val() != 'divSL-1')
            document.getElementById($("#hdnTopPosition").val()).scrollIntoView(true);
    });
}

function ShowStartList(sl) {

    //$("#modalMainDoc").addClass("modal-lg");
    $("#modalSecondTitle").html("Swap Athlete Positions");
    $("#modalSecondArea1").empty();
    $("#modalSecondArea1").load("/athlete_start_list_swap/" + sl, function () {

    });

    $("#modalSecondArea1").show();
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
            $("#modalSecond").modal('hide');
        }
    });
}