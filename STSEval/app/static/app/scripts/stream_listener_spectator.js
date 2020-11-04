var Stream = '';
var StreamListener;
var StreamConnected = false;
var ReCheck;
var hls_playback_url = "";

function CheckStream(doc) {
    console.log("Check Stream");
    if (doc.data().stream != Stream) {
        if (StreamListener != undefined)
            StreamListener();//release stream listener
        Stream = doc.data().stream;
        console.log("Setting Stream Listener To " + Stream);
        StreamListener = db.collection("sessions").doc(Session).collection("streams").doc(Stream.toString()).onSnapshot(function (doc) {
            HandleStreamChanges(doc);
        });
    }
}
function HandleStreamChanges(doc) {
    console.log("stream change");
    if (doc.data() != undefined) {
        console.log(doc.data());
        if (doc.data().hls_playback_url != undefined && doc.data().hls_playback_url != "" && doc.data().connected == true) {
            console.log(doc.data());
            StreamConnected = true;
            hls_playback_url = doc.data().hls_playback_url;
            clearTimeout(ReCheck);
            StartStream();
        }
        else if (doc.data().connected == false) {
            StreamConnected = false;
            console.log("dispose");
            clearTimeout(ReCheck);
            if (VidJSPlayer != undefined) {
                VidJSPlayer.src({
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
function StartStream() {
    if (VidJSPlayer == undefined) {
        VidJSPlayer = videojs("player-video");
        $(".vjs-tech").show();
        VidJSPlayer.on('error', function () {
            console.log("error");
            if (VidJSPlayer.error().code == 4) {
                ReCheck = setTimeout(CheckStreamIsStreaming, 2000);
                console.log("4");
                $("#player-video").hide();
                $("#player-waiting").css("display", "flex");
            }
            /*else if (VidJSPlayer.error().code == 2) {
                ReCheck = setInterval(StartStream, 2000);
                $("#player-video").hide();
                $("#player-waiting").css("display", "flex");
            }*/
        });
        /*VidJSPlayer.tech().on('retryplaylist', () => {
            console.log('retryplaylist');
        });*/
        /*VidJSPlayer.on('warning', function () {
            console.log(VidJSPlayer.warning());
        });*/

    }
    $("#player-waiting").hide();
    $("#player-video").show();
    clearTimeout(ReCheck);
    VidJSPlayer.src({
        "type": "application/x-mpegURL",
        "src": hls_playback_url
    });
   
}

function CheckStreamIsStreaming() {
    if (StreamConnected)
        StartStream();
}
