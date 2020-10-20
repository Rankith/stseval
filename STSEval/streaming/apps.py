from django.apps import AppConfig



class streamingConfig(AppConfig):
    name = 'streaming'

    def ready(self):
        from streaming import updater
        updater.start()
