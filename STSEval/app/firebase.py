import datetime
import threading
import os
from firebase_admin import firestore, initialize_app
from app.models import Competition,Judge,Athlete,Twitch,Routine

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

def routine_set_stream(cde,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'routines').document(str(cde))
    doc_ref.set({
        u'id': cde,
        u'status': routine.status,
        u'athlete': routine.athlete.name,
        u'athlete_id': routine.athlete.id,
        u'stream':routine.stream,
        u'routine':routine.id,
        u'e1done':False,
        u'e2done':False,
        u'e3done':False,
        u'e4done':False,
    },merge=True)