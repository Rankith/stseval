function help_nav(shown, hidden) {
    document.getElementById(shown).style.display = 'block';
    document.getElementById(hidden).style.display = 'none';
    return false;
}

function HelpClick(screen) {
    $("#modalMainTitle").html("HELP");
    $("#modalBodyArea2").hide();
    $("#modalBodyArea1").empty();
    $("#modalBodyArea1").load("/help/" + screen + "/", function () {
    });

    $("#modalBodyArea1").show();
}
