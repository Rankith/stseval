import datetime
import threading
import os
from firebase_admin import firestore, initialize_app
from app.models import Competition,Judge,Athlete,Twitch,Routine,Session
from streaming.models import WowzaStream

initialize_app()


def routine_set_status(s,e,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_dict = doc_ref.get().to_dict()
    if doc_dict['rotation'] != routine.athlete.rotation:
        doc_ref.set({
        u'status': routine.status,
        u'athlete': routine.athlete.name,
        u'athlete_id': routine.athlete.id,
        u'rotation': routine.athlete.rotation,
        u'routine':routine.id,
        u'e1ready':False,
        u'e2ready':False,
        u'e3ready':False,
        u'e4ready':False,
        },merge=True)
    else:
        doc_ref.set({
            u'status': routine.status,
            u'athlete': routine.athlete.name,
            u'athlete_id': routine.athlete.id,
            u'rotation': routine.athlete.rotation,
            u'routine':routine.id,
        },merge=True)

def routine_set_ejudge_done(s,e,ejudge,done):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        u'e' + str(ejudge) + 'done': done
    },merge=True)

def routine_setup(session,e,athlete,camera):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(session.id)).collection(u'event_managers').document(str(e))
    if doc_ref.get().exists:
        doc_dict = doc_ref.get().to_dict()
        if doc_dict['rotation'] != athlete.rotation:
            doc_ref.set({
                u'id': e,
                u'status': Routine.NEW,
                u'athlete': athlete.name,
                u'athlete_id': athlete.id,
                u'rotation': athlete.rotation,
                u'routine':-1,
                u'e1done':False,
                u'e2done':False,
                u'e3done':False,
                u'e4done':False,
                u'e1include':True,
                u'e2include':True,
                u'e3include':True,
                u'e4include':True,
                u'e1ready':False,
                u'e2ready':False,
                u'e3ready':False,
                u'e4ready':False,
                u'stream':camera,
            },merge=True)
        else:
             doc_ref.set({
                u'id': e,
                u'status': Routine.NEW,
                u'athlete': athlete.name,
                u'athlete_id': athlete.id,
                u'rotation': athlete.rotation,
                u'routine':-1,
                u'e1done':False,
                u'e2done':False,
                u'e3done':False,
                u'e4done':False,
                u'e1include':True,
                u'e2include':True,
                u'e3include':True,
                u'e4include':True,
                u'stream':camera,
            },merge=True)
    else:
        doc_ref.set({
            u'id': e,
            u'status': Routine.NEW,
            u'athlete': athlete.name,
            u'athlete_id': athlete.id,
            u'rotation': athlete.rotation,
            u'routine':-1,
            u'e1done':False,
            u'e2done':False,
            u'e3done':False,
            u'e4done':False,
            u'e1include':True,
            u'e2include':True,
            u'e3include':True,
            u'e4include':True,
            u'e1ready':False,
            u'e2ready':False,
            u'e3ready':False,
            u'e4ready':False,
            u'stream':camera,
        },merge=True)

    # set startlist change if not in there
    if 'start_list_change' not in doc_ref.get().to_dict():
        doc_ref.set({
            u'start_list_change': 1,
        },merge=True)

    #update root
    doc_ref = db.collection(u'sessions').document(str(session.id))
    doc_ref.set({
        u'id': str(session.id),
        u'competition_name': session.competition.name,
        u'session_name': session.name,
        u'creator': session.competition.admin.email,
    },merge=True)

def routine_set_ejudge_include(s,e,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        u'e1include':routine.e1_include,
        u'e2include':routine.e2_include,
        u'e3include':routine.e3_include,
        u'e4include':routine.e4_include,
    },merge=True)

def routine_set_ejudge_ready(s,e,judge,ready):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        judge:ready,
    },merge=True)

def routine_set_stream(s,e,stream):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        u'id': e,
        u'stream':stream,
    },merge=True)

def set_stream(s,stream):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(stream.camera_set.first().id))
    doc_ref.set({
        u'stream_id':stream.stream_id,
        u'application_name':stream.application_name,
        u'sdp_url':stream.sdp_url,
        u'stream_name':stream.stream_name,
        u'status':stream.status,
        u'connected':stream.connected,
        u'hls_playback_url':stream.hls_playback_url,
    },merge=True)

def set_stream_status(s,stream_id,stream_status):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(stream_id))
    doc_ref.set({
        u'status':stream_status,
    },merge=True)

def set_stream_connected(s,stream_id,stream_connected):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(stream_id))
    doc_ref.set({
        u'connected':stream_connected,
    },merge=True)

def update_start_list(s,e):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_dict = doc_ref.get().to_dict()
    if 'start_list_change' not in doc_ref.get().to_dict():
        doc_ref.set({
            u'start_list_change': 1,
        },merge=True)
    else:
        doc_ref.set({
            u'start_list_change':doc_dict['start_list_change'] + 1,
        },merge=True)

def check_event_manager_setup(s,e):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc = doc_ref.get()
    return doc.exists