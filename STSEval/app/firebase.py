import datetime
import threading
import os
from firebase_admin import firestore, initialize_app
from app.models import Competition,Judge,Athlete,Twitch,Routine,Session
from streaming.models import WowzaStream
from datetime import datetime

initialize_app()

def routine_update_athlete(s,e,athlete,camera):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
                u'athlete': athlete.name,
                u'athlete_id': athlete.id,
                u'rotation': athlete.rotation,
                u'stream':camera,
            },merge=True)

def routine_get(s,e):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_dict = doc_ref.get().to_dict()
    return doc_dict

def routine_set_status(s,e,routine):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_dict = doc_ref.get().to_dict()
    #make sure its right d judge actor
    if doc_dict['djudge'] == routine.d_judge:
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
    else:
        doc_ref.set({
                u'previous_routine_status': routine.status,
                u'previous_routine_id': routine.id,
                u'previous_routine_athlete_id': routine.athlete.id,
            },merge=True)

def routine_set_ejudge_done(s,e,ejudge,done):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e))
    doc_ref.set({
        u'e' + str(ejudge) + 'done': done
    },merge=True)

def routine_setup(session,e,athlete,camera,judge):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(session.id)).collection(u'event_managers').document(str(e))
    if doc_ref.get().exists:
        doc_dict = doc_ref.get().to_dict()
        if 'rotation' in doc_dict:
            if doc_dict['rotation'] != athlete.rotation:
                doc_ref.set({
                    u'id': e,
                    u'status': Routine.NEW,
                    u'athlete': athlete.name,
                    u'athlete_id': athlete.id,
                    u'rotation': athlete.rotation,
                    u'djudge':judge,
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
                    u'djudge':judge,
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
                    u'djudge':judge,
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
            u'djudge':judge,
            u'routine':-1,
            u'e1done':False,
            u'e2done':False,
            u'e3done':False,
            u'e4done':False,
            u'e1include':True,
            u'e2include':True,
            u'e3include':True,
            u'e4include':True,
            u'd1ready':False,
            u'd2ready':False,
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

def set_stream_status(s,camera_id,stream_status):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(camera_id))
    doc_ref.set({
        u'status':stream_status,
    },merge=True)

def set_stream_connected(s,camera_id,stream_connected):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'streams').document(str(camera_id))
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

def chat_get_create(s,p1,p2):
    db = firestore.Client()

    #check if its a panel
    if "Panel" in p2:
        chat_name = p2
        doc_ref = db.collection(u'sessions').document(str(s)).collection(u'chats').document(str(chat_name))
        if doc_ref.get().exists:
            return doc_ref
        else:
            judge = Judge.objects.filter(session_id=s,event__name=p2.split(' ')[0]).first()
            participants = []
            if judge.d1 != "" and judge.d1 != " ":
                participants.append(judge.event.name + " D1 - " + judge.d1)
            if judge.e1 != "" and judge.e1 != " ":
                participants.append(judge.event.name + " E1 - " + judge.e1)
            if judge.e2 != "" and judge.e2 != " ":
                participants.append(judge.event.name + " E2 - " + judge.e2)
            if judge.e3 != "" and judge.e3 != " ":
                participants.append(judge.event.name + " E3 - " + judge.e3)
            if judge.e4 != "" and judge.e4 != " ":
                participants.append(judge.event.name + " E4 - " + judge.e4)
            participants.append("Meet Administrator")
            doc_ref.set({
                u'id':chat_name,
                u'participants': participants,
            })
            return doc_ref
    else:
        chat_name = ''
        #set the names lexographically so always the same
        if p1 < p2:
            chat_name= p1 + '-' + p2
        else:
            chat_name= p2 + '-' + p1

        doc_ref = db.collection(u'sessions').document(str(s)).collection(u'chats').document(str(chat_name))
        if doc_ref.get().exists:
            return doc_ref
        else:
            #didnt exist so make one
            doc_ref.set({
                u'id':chat_name,
                u'participants': [p1,p2],
                })
            return doc_ref

def chat_send_message(s,sender,to,message,sender_name=''):
    db = firestore.Client()

    doc_ref = chat_get_create(s,sender,to)
    if sender_name=='':
        sender_name = sender
    doc_ref.collection("messages").add({
        u'sender':sender,
        u'sender_name':sender_name,
        u'message':message,
        u'timestamp':datetime.utcnow(),
    })

def set_fall(s,e,team,fall):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e) + "_falls")
    doc_ref.set({
        u'fall':fall,
        u'team':team,
        u'start':datetime.utcnow(),
        u'credit':'',
    })

def set_credit(s,e,team,credit):
    db = firestore.Client()

    doc_ref = db.collection(u'sessions').document(str(s)).collection(u'event_managers').document(str(e) + "_falls")
    doc_ref.set({
        u'team':team,
        u'credit':credit,
    },merge=True)