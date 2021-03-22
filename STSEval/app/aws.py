import boto3, json
from app.models import ConversionSetting,BackupVideo,Routine
from django.conf import settings
from django.core.files.storage import default_storage
from app.media_storage import MediaStorage
import os
from app import firebase

class AWS(object):

    def __init__(self):
        #check if endpoint set.
        endpoint = ConversionSetting.objects.all().first().endpoint_url
        if endpoint == '':
            client = boto3.client('mediaconvert',aws_access_key_id=settings.AWS_MEDIA_ID,aws_secret_access_key=settings.AWS_MEDIA_SECRET,region_name=settings.AWS_MEDIA_REGION_NAME)
            result = client.describe_endpoints()
            endpoint = result['Endpoints'][0]['Url']
            ConversionSetting.objects.all().update(endpoint_url=endpoint)
        self.id = id
        self.endpoint = endpoint

    def save_video(self,routine,video,filename):
        vidfile = 'routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + filename
        client = boto3.client('s3',aws_access_key_id=settings.AWS_MEDIA_ID,aws_secret_access_key=settings.AWS_MEDIA_SECRET,region_name=settings.AWS_MEDIA_REGION_NAME)
        client.put_object(Body=video, Bucket='routinevideos', Key=vidfile)
        #os.makedirs(os.path.dirname(vidfile), exist_ok=True)
        #output = open(vidfile, 'wb+')
        #output.write(request.FILES.get('video-blob').file.read())
        #for chunk in request.FILES['video-blob'].chunks():
            #output.write(chunk)
        #output.close()
        routine.video_saved = True
        routine.video_file.name = '/routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + filename
        routine.save()

    def check_conversion_jobs(self):
        bvs = BackupVideo.objects.filter(converted=False).exclude(job_id='')
        client = boto3.client('mediaconvert',endpoint_url=self.endpoint,aws_access_key_id=settings.AWS_MEDIA_ID,aws_secret_access_key=settings.AWS_MEDIA_SECRET,region_name=settings.AWS_MEDIA_REGION_NAME)
        for bv in bvs:
            job = client.get_job(Id=bv.job_id)
            if job['Job']['Status'] == 'COMPLETE':
                vidfile=bv.video_file.name
                bv.video_file.delete()
                bv.video_file.name = os.path.splitext(vidfile)[0] + ".mp4"
                bv.converted = True
                bv.save()
                firebase.set_backup_videos(bv.session.id,bv.event.name)
        #now do routines
        routines = Routine.objects.filter(video_converted=False,video_saved=True,status=Routine.FINISHED).exclude(job_id='')#.exclude(status=Routine.DELETED)
        for routine in routines:
            job = client.get_job(Id=routine.job_id)
            if job['Job']['Status'] == 'COMPLETE':
                vidfile=routine.video_file.name
                routine.video_file.delete()
                routine.video_file.name = os.path.splitext(vidfile)[0] + ".mp4"
                routine.video_converted = True
                routine.save()
                #os.remove(vidfile)

    def start_conversion(self,conversion_target=None):
        mediaconvert_client = boto3.client('mediaconvert', endpoint_url=self.endpoint,region_name=settings.AWS_MEDIA_REGION_NAME,aws_access_key_id=settings.AWS_MEDIA_ID,aws_secret_access_key=settings.AWS_MEDIA_SECRET)
        vidfile='s3://routinevideos/' + conversion_target.video_file.name
        output = os.path.dirname(vidfile) + '/'
        #load the json job
        #s3 = boto3.resource('s3',aws_access_key_id=settings.AWS_MEDIA_ID,aws_secret_access_key=settings.AWS_MEDIA_SECRET)
        #file = s3.Object('routinevideos','job.json')
        #file = file.get()['Body'].read().decode('utf-8')
        #job_object = json.loads(file)
        #job_object['Settings']['Inputs'][0]['FileInput'] = vidfile
        #job_object['Settings']['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings']['Destination'] = output
        json_to_pass = {
              "Queue": "arn:aws:mediaconvert:us-west-1:887397933955:queues/Default",
              "UserMetadata": {},
              "Role": "arn:aws:iam::887397933955:role/service-role/MediaConvert_Default_Role",
              "Settings": {
                "TimecodeConfig": {
                  "Source": "ZEROBASED"
                },
                "OutputGroups": [
                  {
                    "Name": "File Group",
                    "Outputs": [
                      {
                        "ContainerSettings": {
                          "Container": "MP4",
                          "Mp4Settings": {
                            "CslgAtom": "INCLUDE",
                            "CttsVersion": 0,
                            "FreeSpaceBox": "EXCLUDE",
                            "MoovPlacement": "PROGRESSIVE_DOWNLOAD",
                          }
                        },
                        "VideoDescription": {
                          "ScalingBehavior": "DEFAULT",
                          "TimecodeInsertion": "DISABLED",
                          "AntiAlias": "ENABLED",
                          "Sharpness": 50,
                          "CodecSettings": {
                            "Codec": "H_264",
                            "H264Settings": {
                              "InterlaceMode": "PROGRESSIVE",
                              "NumberReferenceFrames": 3,
                              "Syntax": "DEFAULT",
                              "Softness": 0,
                              "GopClosedCadence": 1,
                              "GopSize": 90,
                              "Slices": 1,
                              "GopBReference": "DISABLED",
                              "MaxBitrate": 6000000,
                              "SlowPal": "DISABLED",
                              "EntropyEncoding": "CABAC",
                              "FramerateControl": "INITIALIZE_FROM_SOURCE",
                              "RateControlMode": "QVBR",
                              "QvbrSettings": {
                                "QvbrQualityLevel": 8,
                                "QvbrQualityLevelFineTune": 0
                              },
                              "CodecProfile": "MAIN",
                              "Telecine": "NONE",
                              "MinIInterval": 0,
                              "AdaptiveQuantization": "AUTO",
                              "CodecLevel": "AUTO",
                              "FieldEncoding": "PAFF",
                              "SceneChangeDetect": "ENABLED",
                              "QualityTuningLevel": "SINGLE_PASS",
                              "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                              "UnregisteredSeiTimecode": "DISABLED",
                              "GopSizeUnits": "FRAMES",
                              "ParControl": "INITIALIZE_FROM_SOURCE",
                              "NumberBFramesBetweenReferenceFrames": 2,
                              "RepeatPps": "DISABLED",
                              "DynamicSubGop": "STATIC"
                            }
                          },
                          "AfdSignaling": "NONE",
                          "DropFrameTimecode": "ENABLED",
                          "RespondToAfd": "NONE",
                          "ColorMetadata": "INSERT"
                        },
                        "AudioDescriptions": [
                          {
                            "AudioTypeControl": "FOLLOW_INPUT",
                            "AudioSourceName": "Audio Selector 1",
                            "CodecSettings": {
                              "Codec": "AAC",
                              "AacSettings": {
                                "AudioDescriptionBroadcasterMix": "NORMAL",
                                "Bitrate": 96000,
                                "RateControlMode": "CBR",
                                "CodecProfile": "LC",
                                "CodingMode": "CODING_MODE_2_0",
                                "RawFormat": "NONE",
                                "SampleRate": 48000,
                                "Specification": "MPEG4"
                              }
                            },
                            "LanguageCodeControl": "FOLLOW_INPUT"
                          }
                        ]
                      }
                    ],
                    "OutputGroupSettings": {
                      "Type": "FILE_GROUP_SETTINGS",
                      "FileGroupSettings": {
                        "Destination": output
                      }
                    }
                  }
                ],
                "AdAvailOffset": 0,
                "Inputs": [
                  {
                    "AudioSelectors": {
                      "Audio Selector 1": {
                        "Offset": 0,
                        "DefaultSelection": "DEFAULT",
                        "ProgramSelection": 1
                      }
                    },
                    "VideoSelector": {
                      "ColorSpace": "FOLLOW",
                      "Rotate": "DEGREE_0",
                      "AlphaBehavior": "DISCARD"
                    },
                    "FilterEnable": "AUTO",
                    "PsiControl": "USE_PSI",
                    "FilterStrength": 0,
                    "DeblockFilter": "DISABLED",
                    "DenoiseFilter": "DISABLED",
                    "InputScanType": "AUTO",
                    "TimecodeSource": "ZEROBASED",
                    "FileInput": vidfile
                  }
                ]
              },
              "AccelerationSettings": {
                "Mode": "DISABLED"
              },
              "StatusUpdateInterval": "SECONDS_60",
              "Priority": 0
            }
        job = mediaconvert_client.create_job(**json_to_pass)
        conversion_target.job_id = job['Job']['Id']
        #bv.video_file.name = os.path.splitext(bv.video_file.name)[0] + ".mp4"
        conversion_target.save()