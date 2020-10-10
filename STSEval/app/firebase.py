import datetime
import threading
import os
from firebase_admin import firestore, initialize_app
from app.models import Competition,Judge,Athlete,Twitch,Routine
from streaming.models import WowzaStream

initialize_app()


def routine_set_status(cde,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'routines').document(str(cde))
    doc_ref.set({
        u'status': routine.status,
        u'athlete': routine.athlete.name,
        u'athlete_id': routine.athlete.id,
    },merge=True)

def routine_set_ejudge_done(cde,ejudge,done):
    db = firestore.Client()

    doc_ref = db.collection(u'routines').document(str(cde))
    doc_ref.set({
        u'e' + str(ejudge) + 'done': done
    },merge=True)

def routine_setup(cde,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'routines').document(str(cde))
    doc_ref.set({
        u'id': cde,
        u'status': routine.status,
        u'athlete': routine.athlete.name,
        u'athlete_id': routine.athlete.id,
        u'routine':routine.id,
        u'e1done':False,
        u'e2done':False,
        u'e3done':False,
        u'e4done':False,
    },merge=True)

def routine_set_stream(cde,stream):
    db = firestore.Client()

    doc_ref = db.collection(u'routines').document(str(cde))
    doc_ref.set({
        u'id': cde,
        u'stream':stream,
    },merge=True)

def set_stream(stream):
    db = firestore.Client()

    doc_ref = db.collection(u'streams').document(str(stream.id))
    doc_ref.set({
        u'stream_id':stream.stream_id,
        u'application_name':stream.application_name,
        u'sdp_url':stream.sdp_url,
        u'stream_name':stream.stream_name,
        u'status':stream.status,
        u'connected':stream.connected,
    },merge=True)

def set_stream_status(stream_id,stream_status):
    db = firestore.Client()

    doc_ref = db.collection(u'streams').document(str(stream_id))
    doc_ref.set({
        u'status':stream_status,
    },merge=True)

def set_stream_connected(stream_id,stream_connected):
    db = firestore.Client()

    doc_ref = db.collection(u'streams').document(str(stream_id))
    doc_ref.set({
        u'connected':stream_connected,
    },merge=True)



def streaming_set(mode,type,sdp,id):
    db = firestore.Client()

    doc_ref = db.collection(u'rooms').document(id)
    doc_ref.set({
        mode: {
            u'type':type,
            u'sdp':sdp
            }
        }
        ,merge=True)

def add_candidate(candidate,sdpMid,sdpMLineIndex,usernameFragment,id):
    db = firestore.Client()

    doc_ref = db.collection(u'rooms').document(id).collection('calleeCandidates')
    doc_ref.add({u'candidate':candidate,
                 u'sdpMid':sdpMid,
                 u'sdpMLineIndex':sdpMLineIndex,
                 u'usernameFragment':usernameFragment
                 }
        )
