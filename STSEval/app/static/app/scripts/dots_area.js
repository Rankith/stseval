var VidWidth = 854;
var JudgeYOffset = 26;
var VideoLossRight = 2;
var DotSize = 16;
var Padding = 17;
var NumDots = 0;
var NumDotsArtistry = 0;
var NumDotsArtistryJudge = new Array();
var DedArray = new Array();
var DedArrayTempDots = new Array();
var DedArrayArtistry = new Array();
var DedArrayArtistryTemp = new Array();
var RoutineLength;
var JudgeDeductions = new Array();
var ChangeDedAddMode;
var ChangeDedAddJudge;
var OnlyOneJudge = false;
var VPhase = 1;
var VDedPhases = new Array();

function SetDotsArea() {
    if ((Disc != "WAG" || ev == "UB") && ev != "V")
        $("#divDotsAreaGlobal").hide();
}

function Deduct(deduction, ej_in = -1, spot_in = -1, artistry_type = '') {
    //console.log("deduct: " + deduction + " | " + ev + " | " + VPhase)
    let this_ej = ej_in;
    let this_spot = spot_in;
    if (this_ej == -1)
        this_ej = ej;
    if (this_spot == -1) {//live click so use backend time and vibrate
        TotalDeductions += deduction / 10;
        VibrateDeduction(deduction);
        $("#divTotalDeductions").html(TotalDeductions.toFixed(1));
    }
    if (ev == "V")//dumb vault things
    {
        this_spot = VPhase * 10;//store these as phase*10 + number.  so 10 11 20 21 22 30 etc
        this_spot = this_spot + VDedPhases[VPhase];
        VDedPhases[VPhase] += 1;
    }
    //console.log("Deducting " + deduction + " | " + this_spot);
    $.ajax({
        url: "/deduct/",
        type: "POST",
        headers: { "X-CSRFToken": token },
        data: {
            'routine': RoutineID,
            'judge': this_ej,
            'deduction': deduction,
            'spot': this_spot,
            'artistry_type':artistry_type,
        },
        //dataType: 'json',
        success: function (data) {
            //console.log("Updated " + this_spot);
            if (spot_in != -1) {
                //was an add so re-get and hide
                
                BuildDots();
                ChangeEjuryDone()
            }
            //RoutineID = data['routine'];
        }
    });
}

function BuildDots(CalcScoreAfter = false, PlaybackOnly = '0') {
    $.ajax({
        url: "/build_dots/",
        type: "POST",
        headers: { "X-CSRFToken": token },
        data: {
            'routine': RoutineID,
            'width': Math.round($("#divDotsArea").width()),
            'dot_size': DotSize,
            'e1done': EJudgesDone[1],
            'e2done': EJudgesDone[2],
            'e3done': EJudgesDone[3],
            'e4done': EJudgesDone[4],
            'playback_only': PlaybackOnly,
        },
        success: function (data) {
            $("#divDotsArea").empty();
            $("#divDotsArea").html(data);
            let i;
            for (i = 1; i <= 4; i++) {
                if (JudgeDeductions[i] != undefined) {
                    $("#divJT" + i).html(JudgeDeductions[i]);
                }
            }
            if (CalcScoreAfter && Status != "AD")
                GetDScore();
            if (PlaybackOnly == '1')
                CalculateScores();
            /*if (LoadRot != "") {
                if (ev != "V") {
                    RedLineInterval = setInterval("UpdateRedLine()", 100);
                    $("#divRedLine").show();
                }
            }*/
            //$("#divTotalDeductions").html(JudgeDeductions[ej]);
            //TotalDeductions = JudgeDeductions[ej];
        }
    });
}


function NewDeduction(e) {
    if (!DeductionsConfirmed && ((Status == undefined || Status == "AD" || Status == "RD") || (EditableDots && Status==""))) {
        DotChangingArtistry = false;
        var rect = e.target.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        var pos
        console.log(e.clientX + " - " + rect.left + " = " + x);
        console.log(e.clientY + " - " + rect.top + " = " + y);
        $("#lblChangeDed").html("Add Deduction");
        ChangeDedAddMode = true;

        if (typeof LoadRot == "undefined") {
           $("#divChangeDed").css({ top: e.clientY + DotSize + 4 });
            $("#divChangeDed").css({ left: e.clientX - ($("#divChangeDed").width() / 2) });

        }
        else {
            $("#divChangeDed").css({ top: e.clientY + DotSize + 4 -150});
            $("#divChangeDed").css({ left: e.clientX - ($("#divChangeDed").width() / 2) });

        }


        pos = x;
        pos -= Padding;
        pos += DotSize / 2
        pos = pos / ($("#divDotsArea").width() - Padding - Padding);
        pos = pos * (parseInt(RoutineLength) / 1000);

        pos = pos * 1000;
        console.log("mili: " + pos);
        DotChanging = pos;

        if (!OnlyOneJudge) {
            if (y < JudgeYOffset + DotSize / 2)
                ChangeDedAddJudge = 1;
            else if (y < JudgeYOffset * 2 + DotSize / 2)
                ChangeDedAddJudge = 2;
            else if (y < JudgeYOffset * 3 + DotSize / 2)
                ChangeDedAddJudge = 3;
            else
                ChangeDedAddJudge = 4;
        }
        else
            ChangeDedAddJudge = ej;

        if (ev == "V") {
            if (x < $("#divVP1").position().left)
                VPhase = 1;
            else if (x < $("#divVP2").position().left)
                VPhase = 2;
            else if (x < $("#divVP3").position().left)
                VPhase = 3;
            else
                VPhase = 4;

        }
        //DotChanging = 
        $("#DotsChangeBlackout").show();
        $("#lblChangeDed").html("Add Deduction");
        $("#divChangeDed").show();
    }
}

function CheckForNearbyDots(dot, artistry = false) {
    let thisdot = document.getElementById("imgDot" + dot);
    let dotsthisline = document.querySelectorAll('.' + thisdot.className), i;
    let thisrect = thisdot.getBoundingClientRect();
    let overlaps = [];

    for (i = 0; i < dotsthisline.length; ++i) {
        let comprect = dotsthisline[i].getBoundingClientRect();
        //console.log(dotsthisline[i]);
        //console.log("comp-left: " + comprect.left + " | orig-left: " + thisrect.left + " | comp-right: " + comprect.right + " | orig-right: " + thisrect.right);
        if (!(comprect.right - 1 < thisrect.left || comprect.left + 1 > thisrect.right))
            overlaps.push(dotsthisline[i]);
        else if (thisdot == dotsthisline[i])
            overlaps.push(dotsthisline[i]);
        
    }
    console.log(overlaps);
    return overlaps;
}

function ClickEjury(dot, artistry = false) {
     //check for overlaps if not artistry
    if (!DeductionsConfirmed && EditableDots) {
        if (!artistry) {
            let overlaps = CheckForNearbyDots(dot, artistry);
            console.log(overlaps);
            if (overlaps.length >= 2) { //2 since it always overlaps itself
                ShowDotSelect(overlaps, dot)
            }
            else
                ChangeEjury(dot, artistry);
        }
        else
            ChangeEjury(dot, artistry);
    }
}

function ShowDotSelect(overlaps, dot) {
    if (typeof LoadRot == "undefined") {
        $("#divChangeDedSelect").css({ top: $("#imgDot" + dot).offset().top + DotSize + 4 });
        $("#divChangeDedSelect").css({ left: $("#imgDot" + dot).offset().left + (DotSize / 2) - $("#divChangeDedSelect").width() / 2 });
    }
    else {
        $("#divChangeDedSelect").css({ top: $("#imgDot" + dot).offset().top + DotSize + 4 - 150 });
        $("#divChangeDedSelect").css({ left: $("#imgDot" + dot).offset().left + (DotSize / 2) - $("#divChangeDedSelect").width() / 2 });
    }
    $("#divSelectDots").empty();
    console.log(overlaps);
    overlaps.forEach(function (overlap) {
        console.log(overlap);
        let thisdot = overlap.id.replace("imgDot", "");
        $("#divSelectDots").append("<img id='SelectDot" + thisdot + "' src='" + overlap.src + "' width='32' height='32' onclick='ChangeEjury(" + thisdot + ")' class='pr-2'>");
    });
    $("#DotsChangeBlackout").show();
    $("#divChangeDedSelect").show();
}

function ChangeEjury(dot, artistry = false) {
    $("#divChangeDedSelect").hide();
    if (!DeductionsConfirmed  && EditableDots) {
        ChangeDedAddMode = false;
        //check for overlaps
        
        if (artistry) {
            $("#divChangeDed").css({ top: $("#imgDotA" + dot).offset().top + DotSize + 4 });
            $("#divChangeDed").css({ left: $("#imgDotA" + dot).offset().left + (DotSize / 2) - $("#divChangeDed").width() / 2 });
        }
        else {
            if (typeof LoadRot == "undefined") {
                $("#divChangeDed").css({ top: $("#imgDot" + dot).offset().top + DotSize + 4 });
                $("#divChangeDed").css({ left: $("#imgDot" + dot).offset().left + (DotSize / 2) - $("#divChangeDed").width() / 2 });
            }
            else {
                $("#divChangeDed").css({ top: $("#imgDot" + dot).offset().top + DotSize + 4 - 150 });
                $("#divChangeDed").css({ left: $("#imgDot" + dot).offset().left + (DotSize / 2) - $("#divChangeDed").width() / 2 });
            }
        }

        if (artistry) {
            $("#divChangeArt" + Disc + ev).show();
            $("#divChangeNormal").hide();
        }
        else {
            $("#divChangeArt" + Disc + ev).hide();
            $("#divChangeNormal").show();
        }

        DotChanging = dot;
        $("#DotsChangeBlackout").show();
        $("#lblChangeDed").html("Change Deduction");
        $("#divChangeDed").show();
        DotChangingArtistry = artistry;
    }
}

function ChangeEjuryDone() {
    $("#DotsChangeBlackout").hide();
    $("#divChangeDed").hide();
    $("#divChangeDedSelect").hide();
    DotChanging = -1;
}

function DedClick(ded) {
    if (ChangeDedAddMode) {
        Deduct(ded, ChangeDedAddJudge, DotChanging);
    }
    else {
        $.ajax({
            url: "/deduction_change/",
            type: "POST",
            headers: { "X-CSRFToken": token },
            data: {
                'id': DotChanging,
                'editor': JudgeType,
                'deduction': ded,
            },
            success: function (data) {
                BuildDots(true);
                ChangeEjuryDone()
            }
        });
    }
    //ChangeDeduction(DotChanging, ded, 'E');
}

function VibrateDeduction(ded) {
    try {
        if (ded == 1)
            window.navigator.vibrate(10);
        else if (ded == 3)
            window.navigator.vibrate(20);
        else if (ded == 5)
            window.navigator.vibrate(30);
        else if (ded == 10)
            window.navigator.vibrate(40);
    } catch (error) {

    }
}