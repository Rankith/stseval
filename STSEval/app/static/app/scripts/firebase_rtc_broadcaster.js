var database = firebase.database().ref();
var yourVideo = document.getElementById("yourVideo");
var friendsVideo = document.getElementById("friendsVideo");
var yourId = Math.floor(Math.random() * 1000000000);
var vidID = "123";
var Comp = "1";
var Disc = "MAG";
var ev = "FX";
var servers = { 'iceServers': [{ 'urls': 'stun:stun.services.mozilla.com' }, { 'urls': 'stun:stun.l.google.com:19302' }] };
var pc = new RTCPeerConnection(servers);
pc.onicecandidate = (event => event.candidate ? sendMessage(yourId, JSON.stringify({ 'ice': event.candidate })) : console.log("Sent All Ice"));
pc.onaddstream = (event => friendsVideo.srcObject = event.stream);

var db = firebase.firestore();
db.collection("routines").doc(Comp + Disc + ev)
    .onSnapshot(function (doc) {
        //console.log(doc);
        ReadInfo(doc);
    });

function SetBasedOnStatus(doc) {
    if (doc.data() != undefined) {
        if (Status != doc.data().status || RoutineID != doc.data().routine) {
            RoutineID = doc.data().routine;
            if (doc.data().status == "N" || doc.data().status == "D" || doc.data().status == "F") {
                console.log("reset");
                Reset();
            }
            else if (doc.data().status == "S") {
                console.log("start judging");
                StartJudging();
            }
            else if (doc.data().status == "AD") {
                console.log("athlete done");
                AthleteDone();
            }
            Status = doc.data().status;
        }
        console.log("Current data: ", doc.data());
        //$("#divStatus").html(doc.data().stream + " | " + doc.data().status);
    }
}

function SendMessage(data) {
    $.ajax({
        url: "/streaming_send_message/",
        type: "POST",
        headers: { "X-CSRFToken": token },
        data: {
            'cde': Comp + Disc + ev,
            'sender': yourId,
            'message':data
        },
        success: function (data) {
        }
    });
}


function sendMessage(senderId, data) {
    var msg = database.push({ sender: senderId, message: data });
    msg.remove();
}

function readMessage(data) {
    var msg = JSON.parse(data.val().message);
    var sender = data.val().sender;
    if (sender != yourId) {
        if (msg.ice != undefined)
            pc.addIceCandidate(new RTCIceCandidate(msg.ice));
        else if (msg.sdp.type == "offer")
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp))
                .then(() => pc.createAnswer())
                .then(answer => pc.setLocalDescription(answer))
                .then(() => sendMessage(yourId, JSON.stringify({ 'sdp': pc.localDescription })));
        else if (msg.sdp.type == "answer")
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
    }
};

database.on('child_added', readMessage);

function showMyFace() {
    navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(stream => yourVideo.srcObject = stream)
        .then(stream => pc.addStream(stream));
}

function showFriendsFace() {
    pc.createOffer()
        .then(offer => pc.setLocalDescription(offer))
        .then(() => sendMessage(yourId, JSON.stringify({ 'sdp': pc.localDescription })));
}