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
            //if (checked)
                //LoadStartList();
        }
    });
}
function StartListDragSetup() {
    Sortable.create(document.getElementById("StartListDrag"), { onEnd: SortEnd, handle: ".start-list-drag-handle", draggable: ".start-list-draggable" });
}
function LoadStartList(doc=-1) {
    $("#divStartList").load("/athlete_start_list_admin/" + ev + "/", function () {
        console.log("start list loaded doc: " + doc);
        if ($("#hdnTopPosition").val() != 'divSL-1')
            document.getElementById($("#hdnTopPosition").val()).scrollIntoView(true);
        StartListDragSetup();
        if (doc != -1)
            SetStartListDot(doc);
    });
}
function SetStartListDot(doc) {
    $(".athlete-dot").hide();
    console.log("Set start list dot: #divAthleteDots" + doc.data().athlete_id + " | " + doc.data().status);
    if (doc.data().status == "AD" || doc.data().status == "F" || doc.data().status == "RD") {
        
        $("#divAthleteDots" + doc.data().athlete_id).removeClass("status-dot-yellow").removeClass("status-dot-green").addClass("status-dot-red");
    }
    else if (doc.data().status == "N") {
        $("#divAthleteDots" + doc.data().athlete_id).addClass("status-dot-yellow").removeClass("status-dot-green").removeClass("status-dot-red");
    }
    else if (doc.data().status == "S") {
        $("#divAthleteDots" + doc.data().athlete_id).removeClass("status-dot-yellow").addClass("status-dot-green").removeClass("status-dot-red");
    }
    CurrentStatus = doc.data().status;
    $("#divAthleteDots" + doc.data().athlete_id).show();
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

    if (CurrentStatus != "S") {
        //$("#modalMainDoc").addClass("modal-lg");
        $("#modalSecondTitle").html("Manage Routine");
        $("#modalSecondArea1").empty();
        $("#modalSecondArea1").load("/athlete_start_list_swap/" + sl, function () {

        });

        $("#modalSecondArea1").show();
    }
    else {
        $("#modalSecondArea1").html("You cannot change this while an athlete is actively going.");
    }
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
            //LoadStartList();
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
            //LoadStartList();
            $("#modalSecond").modal('hide');
        }
    });
}