var Stream = '';
var StreamListener;
var StreamConnected = false;

function CheckStream(doc) {
    console.log("Check Stream");
    if (doc.data().video == -1) {
        BackupVideo = -1;
        $("#video-playback").hide();
        $("#play-video-container").addClass("d-flex");
        $("#play-video-container").show();
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
    else {
        Stream = '';
        if (StreamListener != undefined)
            StreamListener();//release stream listener since its a video
        if (BackupVideo != doc.data().video) {
            //set video
            BackupVideo = doc.data().video;
            let vp = document.getElementById("video-playback");
            vp.pause();
            vp.currentTime = 0;
            vp.src = BackupVideo;
            vp.load();
            $("#video-playback").show();
            $("#play-video-container").hide();
            $("#play-video-container").removeClass("d-flex");

        }
    }
}
function CheckStreamManual(StreamIn) {
    console.log("Check Stream Manual");
    if (StreamIn != Stream) {
        if (StreamListener != undefined)
            StreamListener();//release stream listener
        Stream = StreamIn;
        console.log("Setting Stream Listener To " + Stream);
        StreamListener = db.collection("sessions").doc(Session).collection("streams").doc(Stream.toString()).onSnapshot(function (doc) {
            HandleStreamChanges(doc);
        });
    }
}
function HandleStreamChanges(doc) {
    if (doc.data() != undefined) {
        console.log(doc.data());
        if (doc.data().connected == true) {
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
        }
    }
}
function StartStream() {
    $("#play-toggle").click();
    setTimeout(CheckStreamIsStreaming,2000);
}

function CheckStreamIsStreaming() {
    if ($("#player-video").css("display") == "none" && StreamConnected)
        StartStream();
}