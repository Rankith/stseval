var Stream = '';
var StreamListener;
var StreamConnected = false;

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
    if (doc.data() != undefined) {
        console.log(doc.data());
        if (doc.data().hls_playback_url != undefined && doc.data().hls_playback_url != "") {
            StartStream(doc.data().hls_playback_url);
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
function StartStream(hls_playback_url) {
    if (VidJSPlayer == undefined) {
        VidJSPlayer = videojs("player-video");
        VidJSPlayer.on('error', function () {
            if (VidJSPlayer.error().code == 4);
            $("#player-video").hide();
            $("#player-waiting").css("display", "flex");
        });
    }
    $("#player-waiting").hide();
    $("#player-video").show();
    VidJSPlayer.src({
        "type": "application/x-mpegURL",
        "src": hls_playback_url
    });
    

   
}
