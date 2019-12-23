from django.template.defaultfilters import date as django_date
from xlsxwriter import Workbook
from num2words import num2words

from .base import BaseDocument

from ghost_shopper.core.models import CheckKind
from ghost_shopper.check.models import Check


MONTH_IN_GENITIVE = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',
}


class PaymentDocument(BaseDocument):
    """
    Payment documents generator
    """

    def __init__(self, id, organisation, date, checks):
        self.id = id
        self.organisation = organisation
        self.date = date
        self.month_last_day = self._get_months_last_day()
        self.checks = checks
        self.wb = Workbook(self.path_to_file)
        self.wb.encoding = 'utf-8'
        self.ws = self.wb.add_worksheet('Main')
        self.products_number = 0
        self.products_total = 0
        self.styles = {
            'thin_border': self.wb.add_format({'border': 1}),
            'table_header': self.wb.add_format({'border': 2, 'align': 'center', 'bold': True}),
            'table_row_left': self.wb.add_format(
                {'border': 2, 'text_wrap': True, 'valign': 'vcenter', 'align': 'left'}),
            'table_row_center': self.wb.add_format(
                {'border': 2, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter'}),
            'table_num': self.wb.add_format(
                {'border': 2, 'text_wrap': True, 'align': 'right', 'num_format': '0.00', 'valign': 'vcenter'}),
            'big_bold_font': self.wb.add_format({'font_size': 14, 'bold': True, 'text_wrap': True}),
            'normal_bold_font': self.wb.add_format({'font_size': 11, 'bold': True, 'text_wrap': True}),
            'wrap_text': self.wb.add_format({'text_wrap': True}),
            'bold_num': self.wb.add_format({'align': 'right', 'num_format': '0.00', 'bold': True})
        }

    @property
    def file_name(self):
        """Generate file name."""
        return 'Счет_на_оплату_орг_{}_за_{}.xlsx'.format(
            self.organisation.id,
            self.date.strftime('{}_%Y'.format(django_date(self.date, 'F').lower()))
        )

    def create(self):
        """Fill document with necessary data and save it to the disk."""
        self._fill()
        self.wb.close()

    def _fill(self):
        """Fill table with necessary data."""
        self._set_column_width()
        self._fill_header()
        last_table_row = self._fill_body_table()
        self._fill_footer(last_table_row+2)

    def _set_column_width(self):
        """Set columns width."""
        map = {'A': 1, 'B': 3, 'C': 1, 'D': 1, 'E': 3, 'F': 4, 'G': 2, 'H': 0.5, 'I': 2, 'J': 3, 'K': 3, 'L': 3,
               'M': 3, 'N': 3, 'O': 3, 'P': 1, 'Q': 3, 'R': 1, 'S': 1, 'T': 3, 'U': 2, 'V': 2, 'W': 1, 'X': 1,
               'Y': 3, 'Z': 3, 'AA': 1.5, 'AB': 2, 'AC': 1.5, 'AD': 3, 'AE': 1, 'AF': 1, 'AG': 3, 'AH': 3, 'AI': 3,
               'AJ': 2, 'AK': 1.5, 'AL': 1, 'AM': 4, 'AN': 3, 'AO': 4, 'AP': 3, 'AQ': 1.5, 'AR': 1}

        for column_name, column_size in map.items():
            self.ws.set_column(f'{column_name}:{column_name}', column_size)

    def _fill_header(self):
        """Fill table header data."""
        header_data = {
            'B2:W3': (self.my_organisation.bank_name, self.styles['thin_border']),  # my organisation bank name
            'B4:W4': ('Банк получателя', self.styles['thin_border']),
            'X2:AC2': ('БИК', self.styles['thin_border']),
            'AD2:AR2': (self.my_organisation.bank_BIC, self.styles['thin_border']),  # my organisation BIC
            'X3:AC4': ('Сч №', self.styles['thin_border']),
            'AD3:AR4': (self.my_organisation.bank_account, self.styles['thin_border']),  # my organisation bank account
            'B5:D5': ('ИНН', self.styles['thin_border']),
            'E5:L5': (self.my_organisation.INN, self.styles['thin_border']),  # my organisation INN
            'M5:N5': ('КПП', self.styles['thin_border']),
            'O5:W5': (self.my_organisation.KPP, self.styles['thin_border']),  # my organisation KPP
            'B6:W7': (self.my_organisation.full_name, self.styles['thin_border']),  # my organisation full name
            'B8:W8': ('Получатель', self.styles['thin_border']),
            'X5:AC8': ('Сч. №', self.styles['thin_border']),
            'AD5:AR8': (self.my_organisation.account, self.styles['thin_border']),  # my organisation account
            'B10:AR11': (
                'Счет на оплату №{} от {} {} {} г'.format(
                    self.id, self.month_last_day, MONTH_IN_GENITIVE[self.date.month], self.date.year),
                self.styles['big_bold_font']),
            'B14:F15': ('Поставщик(Исполнитель):', self.styles['wrap_text']),
            'G14:AR15': (
                '{}, ИНН {}, {}, тел.: {}'.format(
                    self.my_organisation.short_name,
                    self.my_organisation.INN,
                    self.my_organisation.address,
                    self.my_organisation.phone_number
                ),
                self.styles['normal_bold_font']),

            'B17:F18': ('Покупатель (Заказчик):', self.styles['wrap_text']),
            'G17:AR18': ('{}, ИНН {}, КПП {}, {}'.format(
                self.organisation.full_name,
                self.organisation.INN,
                self.organisation.KPP,
                self.organisation.legal_address
            ), self.styles['normal_bold_font']),
            'B20:F20': ('Основание:', {})
        }
        for coordinate, cell_data in header_data.items():
            self.ws.merge_range(coordinate, cell_data[0], cell_data[1])

    def _fill_body_table(self):
        """Fill table with data."""

        table_header_data = {
            'B22:C22': ('№', self.styles['table_header']),
            'D22:X22': ('Товары(работы, услуги)', self.styles['table_header']),
            'Y22:AB22': ('Кол-во', self.styles['table_header']),
            'AC22:AF22': ('Ед.', self.styles['table_header']),
            'AG22:AJ22': ('Цена', self.styles['table_header']),
            'AK22:AR22': ('Сумма', self.styles['table_header']),
        }
        self._insert_data(table_header_data)
        return self._fill_products_table()

    def _fill_products_table(self):
        """Fill products table"""
        current_row = 23
        products_number = 0
        products_total = 0

        for kind in CheckKind.objects.all():
            if self.checks.filter(kind=kind).exists():
                products_number += 1
                product_data = self._make_product_data(current_row, kind, products_number)
                self._insert_data(product_data)
                self.ws.set_row(current_row-1, 50)
                current_row += 1
                products_total += kind.price * self.checks.filter(kind=kind).count()
        self.products_total = products_total
        self.products_number = products_number
        return current_row

    def _make_product_data(self, row_number, kind, products_number):
        """Make products table row data."""
        kind_checks_number = self.checks.filter(kind=kind).count()
        subtotal = kind.price * kind_checks_number
        data = {
            f'B{row_number}:C{row_number}': (products_number, self.styles['table_row_center']),
            f'D{row_number}:X{row_number}': (
                'Организация и проведение маркетинговых исследований в рамках Договора {}, "{}", Акт от {}'.format(
                    self.organisation.contract_name,
                    kind.name,
                    self.date.replace(day=self.month_last_day).strftime(
                        '%d/%m/%y'
                    )
                ),
                self.styles['table_row_left']
            ),
            f'Y{row_number}:AB{row_number}': (kind_checks_number, self.styles['table_row_center']),
            f'AC{row_number}:AF{row_number}': ('шт', self.styles['table_row_center']),
            f'AG{row_number}:AJ{row_number}': (kind.price, self.styles['table_num']),
            f'AK{row_number}:AR{row_number}': (subtotal, self.styles['table_num']),
        }
        return data

    def _fill_footer(self, start_row):
        """Fill table footer with data."""
        footer_data = {
            f'AH{start_row}:AK{start_row}': ('Итого:', self.styles['normal_bold_font']),
            f'AL{start_row}:AQ{start_row}': (self.products_total, self.styles['bold_num']),
            f'AE{start_row+1}:AK{start_row+1}': ('Без налога (НДС)', self.styles['normal_bold_font']),
            f'AE{start_row+2}:AK{start_row+2}': ('Всего к оплате:', self.styles['normal_bold_font']),
            f'AL{start_row+2}:AQ{start_row+2}': (self.products_total, self.styles['bold_num']),
            f'B{start_row+3}:AQ{start_row+3}': ('Всего наименований {}, на сумму {},00 руб.'.format(
                self.products_number, self.products_total), self.styles['normal_bold_font']),
            f'B{start_row+4}:AQ{start_row+4}': ('{} рублей 00 копеек'.format(
                num2words(self.products_total, lang='ru').capitalize()), self.styles['normal_bold_font'])
        }
        self._insert_data(footer_data)

    def _insert_data(self, data):
        """Insert given dictionary in file"""

        for coordinate, cell_data in data.items():
            self.ws.merge_range(coordinate, cell_data[0], cell_data[1])
