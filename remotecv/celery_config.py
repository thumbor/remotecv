from celery import Celery
from tasks import DetectTask

def init_celery(key_id, key_secret, region, timeout):
    celery = Celery('remotecv.worker',
        broker='sqs://%s:%s@' % (key_id, key_secret),
        backend=None
    )

    celery.conf.update(
        BROKER_TRANSPORT_OPTIONS = {
            'region': region,
            'visibility_timeout': timeout or 120,
            'polling_interval': 20,
        }
    )

    @celery.task(ignore_result=True)
    def detect_task(detection_type, image_path, key):
        DetectTask.perform(detection_type, image_path, key)

    return celery, detect_task

