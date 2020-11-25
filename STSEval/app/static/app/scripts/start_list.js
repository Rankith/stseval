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
function StartListDragSetup() {
    Sortable.create(document.getElementById("StartListDrag"), { onEnd: SortEnd, handle: ".start-list-drag-handle", draggable: ".start-list-draggable" });
}
function LoadStartList() {
    $("#divStartList").load("/athlete_start_list_admin/" + ev + "/", function () {
        if ($("#hdnTopPosition").val() != 'divSL-1')
            document.getElementById($("#hdnTopPosition").val()).scrollIntoView(true);
        StartListDragSetup();
    });
}

function SortEnd(evt) {
    UpdateStartlistOrder();
}
function UpdateStartlistOrder() {
    var OrderList = "";
    $("#StartListDrag").children("tr").each(function () {
        OrderList += "," + $(this).attr("athid");
    });
    OrderList = OrderList.substring(1);
    $.ajax({
        url: '/athlete_start_list_update_order/',
        data: {
            'ev': ev,
            'sl_order': OrderList
        },
        headers: { "X-CSRFToken": token },
        type: 'POST',
        success: function (data) {
        }
    });
}

function ShowRoutineOptions(sl) {

    //$("#modalMainDoc").addClass("modal-lg");
    $("#modalSecondTitle").html("Manage Athlete Routine");
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

function StartListRoutineDelete(sl) {
    $.ajax({
        type: 'POST',
        url: '/athlete_routine_remove/',
        headers: { "X-CSRFToken": token },
        data: {
            'sl_orig': $("#hdnSLtoSwap").val(),
        },
        success: function (data) {
            LoadStartList();
            $("#modalSecond").modal('hide');
        }
    });
}