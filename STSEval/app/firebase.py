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
    doc_ref.set({
        u'status': routine.status,
        u'athlete': routine.athlete.name,
        u'athlete_id': routine.athlete.id,
        u'routine':routine.id
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
    doc_ref.set({
        u'id': e,
        u'status': Routine.NEW,
        u'athlete': athlete.name,
        u'athlete_id': athlete.id,
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

def routine_set_stream(s,e,stream):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        u'id': e,
        u'stream':stream,
    },merge=True)

def set_stream(s,stream):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(stream.id))
    doc_ref.set({
        u'stream_id':stream.stream_id,
        u'application_name':stream.application_name,
        u'sdp_url':stream.sdp_url,
        u'stream_name':stream.stream_name,
        u'status':stream.status,
        u'connected':stream.connected,
        u'player_id':stream.wowza_player_code,
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

