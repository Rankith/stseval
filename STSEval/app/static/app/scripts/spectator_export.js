function GetSpectatorList(s,name) {
    $.ajax({
        url: "/account/spectator_list_csv/" + s,
        type: "GET",
        success: function (data) {
            const a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            const blob = new Blob([data], { type: "octet/stream" }),
                url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = "spectators " + name + ".csv";
            a.click();
            window.URL.revokeObjectURL(url);
        }
    });
}