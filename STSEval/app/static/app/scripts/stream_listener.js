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