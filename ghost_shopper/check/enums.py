

class CheckStatusesEnum:
    
    CREATED = 'CREATED'
    AVAILABLE = 'AVAILABLE'
    PROCESSING = 'PROCESSING'
    FILLED = 'FILLED'
    CONFORMATION = 'CONFORMATION'
    APPEAL = 'APPEAL'
    CLOSED = 'CLOSED'

    values = {
        'CREATED': 'Создана',
        'AVAILABLE': 'Доступна',
        'PROCESSING': 'В работе',
        'FILLED': 'Проверка',
        'CONFORMATION': 'Одобрение',
        'APPEAL': 'Аппеляция',
        'CLOSED': 'Закрыта'
    }


CHECK_TYPES = {
    'TEMPLATE': 'Шаблон',
    'USUAL': 'Обычная'
}
