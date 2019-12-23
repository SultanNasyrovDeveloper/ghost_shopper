from celery import shared_task


@shared_task
def delete_old_audio():
    from .garbage_collector import GarbageCollector

    collector = GarbageCollector()
    collector.perform()
    print('Garbage collector succeed')


@shared_task
def invoke_check_close_manager():
    from .close_manager import CheckCloseManger
    manager = CheckCloseManger()
    manager.perform()
