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
    if (doc.data().video == -1) {
        BackupVideo[which] = -1;
        let vp = document.getElementById("video-playback" + which);
        vp.pause();
        $("#video-playback" + which).hide();
        $("#player-video" + which).show();
        if (doc.data().stream != Stream[which]) {
            if (StreamListener[which] != undefined) {
                //console.log("Release Stream Listener " + which);
                StreamListener[which]();//release stream listener
            }
            Stream[which] = doc.data().stream;
            console.log("Setting Stream Listener " + which + " To " + Stream[which]);
            StreamListener[which] = db.collection("sessions").doc(Session).collection("streams").doc(Stream[which].toString()).onSnapshot(function (doc) {
                HandleStreamChanges(doc, which);
            });
        }
    }
    else {
        Stream[which] = '';
        if (StreamListener[which] != undefined) {
            StreamListener[which]();//release stream listener
        }
        if (BackupVideo[which] != doc.data().video) {
            //set video
            BackupVideo[which] = doc.data().video;
            let vp = document.getElementById("video-playback" + which);
            vp.pause();
            vp.currentTime = 0;
            vp.src = BackupVideo[which];
            vp.load();
            $("#video-playback" + which).show();
            $("#player-waiting" + which).hide();
            $("#player-video" + which).hide();

        }

    }
}
function HandleStreamChanges(doc,which) {
    console.log("stream change " + which);
    if (doc.data() != undefined) {
        console.log(doc.data());
        if (doc.data().hls_playback_url != undefined && doc.data().hls_playback_url != "" && doc.data().connected == true) {
            if (doc.data().event == ev[which]) {
                StreamConnected[which] = true;
                hls_playback_url[which] = doc.data().hls_playback_url;
                //clearTimeout(ReCheck[which]);
                //clearInterval(ReadyStateCheck[which]);
                if (HLSPlayer[which] != undefined) {
                    HLSPlayer[which].destroy();
                    //HLSPlayer[which].loadSource("");
                    HLSPlayer[which] = undefined;
                }
                StartStream(which);
            }
            else {
                StreamConnected[which] = false;
                $("#player-waiting" + which).show();
                $("#player-video" + which).hide();
                $("#player-waiting" + which).html("<div><h1>Currently No Athletes on This Event</h1><h5>See Scoreboard for Completed Exercises</h5></div>");
            }
        }
        else if (doc.data().connected == false) {
            StreamConnected[which] = false;
            console.log("dispose " + which);
            $("#player-waiting" + which).show();
            $("#player-video" + which).hide();
            $("#player-waiting" + which).html("<div><h1>No Video at This Time</h1><h5>See Scoreboard for Completed Exercises</h5></div >");
            //clearTimeout(ReCheck[which]);
            //clearInterval(ReadyStateCheck[which]);
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
        VideoPlayer[which] = document.getElementById("player-video" + which);
        if (Hls.isSupported()) { 
            HLSPlayer[which] = new Hls();
            
            //console.log(document.getElementById("player-video" + which));
            HLSPlayer[which].attachMedia(VideoPlayer[which]);
            HLSPlayer[which].on(Hls.Events.MANIFEST_PARSED, function () {
                VideoPlayer[which].play();
                console.log("Manifest Parsed");
            });
            HLSPlayer[which].on(Hls.Events.ERROR, function (event, data) {
                if (data.fatal) {
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            // try to recover network error
                            console.log("fatal network error encountered, try to recover");
                            HLSPlayer[which].startLoad();
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            console.log("fatal media error encountered, try to recover");
                            HLSPlayer[which].recoverMediaError();
                            break;
                        default:
                            // cannot recover
                            HLSPlayer[which].destroy();
                            break;
                    }
                }
            });
            HLSPlayer[which].loadSource(hls_playback_url[which]);
        }
        else if (VideoPlayer[which].canPlayType('application/vnd.apple.mpegurl')) {
            VideoPlayer[which].src = hls_playback_url[which];
            VideoPlayer[which].addEventListener('loadedmetadata', function () {
                VideoPlayer[which].play();
            });
            VideoPlayer[which].addEventListener('canplaythrough', function () {
                VideoPlayer[which].play();
            });
        }
        //$(".vjs-tech").show();
        HLSPlayer[which].on('error', function () {
            console.log("error " + which);
            if (HLSPlayer[which].error().code == 4) {
                ReCheck[which] = setTimeout(function () {
                    CheckStreamIsStreaming(which);
                }, 2000);
                console.log("4");
                $("#player-video" + which).hide();
                $("#player-waiting" + which).css("display", "flex");
            }
            
        });
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
