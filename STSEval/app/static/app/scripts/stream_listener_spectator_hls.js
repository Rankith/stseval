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
var VideoPlayer = new Array();

function CheckStream(doc,which) {
    console.log("Check Stream " + which);
    if (doc.data().stream != Stream[which]) {
        if (StreamListener[which] != undefined) {
            //console.log("Release Stream Listener " + which);
            StreamListener[which]();//release stream listener
        }
        Stream[which] = doc.data().stream;
        console.log("Setting Stream Listener " + which + " To " + Stream[which]);
        StreamListener[which] = db.collection("sessions").doc(Session).collection("streams").doc(Stream[which].toString()).onSnapshot(function (doc) {
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
            if (HLSPlayer[which] != undefined) {
                HLSPlayer[which].destroy();
                //HLSPlayer[which].loadSource("");
                HLSPlayer[which] = undefined;
            }
            StartStream(which);
        }
        else if (doc.data().connected == false) {
            StreamConnected[which] = false;
            console.log("dispose " + which);
            $("#player-waiting" + which).show();
            $("#player-video" + which).hide();
            clearTimeout(ReCheck[which]);
            clearInterval(ReadyStateCheck[which]);
            if (HLSPlayer[which] != undefined) {
                HLSPlayer[which].destroy();
                //HLSPlayer[which].loadSource("");
                HLSPlayer[which] = undefined;
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
    console.log("Start Stream");
    if (HLSPlayer[which] == undefined) {
        HLSPlayer[which] = new Hls();
        VideoPlayer[which] = document.getElementById("player-video" + which);
        //console.log(document.getElementById("player-video" + which));
        HLSPlayer[which].attachMedia(VideoPlayer[which]);
        HLSPlayer[which].on(Hls.Events.MANIFEST_PARSED, function () {
            VideoPlayer[which].play();
        });
        //$(".vjs-tech").show();
        /*HLSPlayer[which].on('error', function () {
            console.log("error " + which);
            if (HLSPlayer[which].error().code == 4) {
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
            }
        });*/
        /*VidJSPlayer[which].tech().on('retryplaylist', () => {
            console.log('retryplaylist');
        });
        VidJSPlayer[which].on('warning', function () {
            console.log(VidJSPlayer.warning());
        });*/

    }
    //clearInterval(ReadyStateCheck[which]);
    /*ReadyStateCheck[which] = setInterval(function () {
        CheckReadyState(which);
    }, 4000);*/
    $("#player-waiting" + which).hide();
    $("#player-video" + which).show();
    //clearTimeout(ReCheck[which]);
    HLSPlayer[which].loadSource(hls_playback_url[which]);
   
   
}

function CheckStreamIsStreaming(which) {
    console.log("Check streaming");
    if (StreamConnected[which])
        StartStream(which);
}

function CheckReadyState(which) {
   /* console.log("Ready State Check: " + HLSPlayer[which].readyState());
    if (HLSPlayer[which].readyState() == 1) {
        clearInterval(ReadyStateCheck[which]);

        StartStream(which);
    }*/
}
