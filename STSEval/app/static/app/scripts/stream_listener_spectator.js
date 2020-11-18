var Stream = new Array();
Stream[1] = '';
Stream[2] = '';
var StreamListener = new Array();
var StreamConnected = new Array();
StreamConnected[1] = false;
StreamConnected[2] = false;
var ReCheck = new Array();
var ReadyStateCheck = new Array();
var hls_playback_url = new Array();
hls_playback_url[1] = "";
hls_playback_url[2] = "";

function CheckStream(doc,which) {
    console.log("Check Stream " + which);
    if (doc.data().stream != Stream[which]) {
        if (StreamListener[which] != undefined)
            StreamListener[which]();//release stream listener
        Stream[which] = doc.data().stream;
        console.log("Setting Stream Listener " + which + " To " + Stream[which]);
        StreamListener = db.collection("sessions").doc(Session).collection("streams").doc(Stream[which].toString()).onSnapshot(function (doc) {
            HandleStreamChanges(doc,which);
        });
    }
}
function HandleStreamChanges(doc,which) {
    console.log("stream change " + which);
    if (doc.data() != undefined) {
        console.log(doc.data());
        if (doc.data().hls_playback_url != undefined && doc.data().hls_playback_url != "" && doc.data().connected == true) {
            StreamConnected[which] = true;
            hls_playback_url[which] = doc.data().hls_playback_url;
            clearTimeout(ReCheck[which]);
            clearInterval(ReadyStateCheck[which]);
            StartStream(which);
        }
        else if (doc.data().connected == false) {
            StreamConnected[which] = false;
            console.log("dispose " + which);
            clearTimeout(ReCheck[which]);
            clearInterval(ReadyStateCheck[which]);
            if (VidJSPlayer[which] != undefined) {
                VidJSPlayer[which].src({
                    "type": "none",
                    "src": ""
                });
            }
        }
        /*if (doc.data().connected == true) {
            $("#playSdpURL").val(doc.data().sdp_url);
            $("#playApplicationName").val(doc.data().application_name);
            $("#playStreamName").val(doc.data().stream_name);
            StreamConnected = true;
            setTimeout(StartStream, 1000);
        }
        else {
            StreamConnected = false;
            $("#player-video").hide();
            $("#player-waiting").css("display","flex");
        }*/
    }

}
function StartStream(which) {
    if (VidJSPlayer[which] == undefined) {
        VidJSPlayer[which] = videojs("player-video" + which);
        $(".vjs-tech").show();
        VidJSPlayer[which].on('error', function () {
            console.log("error " + which);
            if (VidJSPlayer[which].error().code == 4) {
                ReCheck[which] = setTimeout(function () {
                    CheckStreamIsStreaming(which);
                }, 2000);
                console.log("4");
                $("#player-video" + which).hide();
                $("#player-waiting" + which).css("display", "flex");
            }
            /*else if (VidJSPlayer.error().code == 2) {
                ReCheck = setInterval(StartStream, 2000);
                $("#player-video").hide();
                $("#player-waiting").css("display", "flex");
            }*/
        });
        /*VidJSPlayer[which].tech().on('retryplaylist', () => {
            console.log('retryplaylist');
        });
        VidJSPlayer[which].on('warning', function () {
            console.log(VidJSPlayer.warning());
        });*/

    }
    clearInterval(ReadyStateCheck[which]);
    ReadyStateCheck[which] = setInterval(function () {
        CheckReadyState(which);
    }, 4000);
    $("#player-waiting" + which).hide();
    $("#player-video" + which).show();
    clearTimeout(ReCheck[which]);
    VidJSPlayer[which].src({
        "type": "application/x-mpegURL",
        "src": hls_playback_url[which]
    });
   
}

function CheckStreamIsStreaming(which) {
    console.log("Check streaming");
    if (StreamConnected[which])
        StartStream(which);
}

function CheckReadyState(which) {
    console.log("Ready State Check: " + VidJSPlayer[which].readyState());
    if (VidJSPlayer[which].readyState() == 1) {
        clearInterval(ReadyStateCheck[which]);

        StartStream(which);
    }
}
