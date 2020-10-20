# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import *  # noqa

# don't use an unicode string
localeID = 'ru_RU'
dateSep = ['-', '.']
timeSep = [':']
meridian = []
usesMeridian = False
uses24 = True

Weekdays = [
    'понедельник', 'вторник', 'среда', 'четверг',
    'пятница', 'суббота', 'воскресенье',
]
shortWeekdays = [
    'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс',
]
# library does not know how to conjugate words
# библиотека не умеет спрягать слова
Months = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
    'августа', 'сентября', 'октября', 'ноября', 'декабря',
]
shortMonths = [
    'янв', 'фев', 'мрт', 'апр', 'май', 'июн',
    'июл', 'авг', 'сен', 'окт', 'нбр', 'дек',
]
dateFormats = {
    'full': 'EEEE, dd MMMM yyyy',
    'long': 'dd MMMM yyyy',
    'medium': 'dd-MM-yyyy',
    'short': 'dd-MM-yy',
}

timeFormats = {
    'full': 'HH:mm:ss v',
    'long': 'HH:mm:ss z',
    'medium': 'HH:mm:ss',
    'short': 'HH:mm',
}

dp_order = ['d', 'm', 'y']

decimal_mark = '.'

units = {
    'seconds': ['секунда', 'секунды', 'секунд', 'сек', 'с'],
    'minutes': ['минута', 'минуты', 'минут', 'мин', 'м'],
    'hours': ['час', 'часов', 'часа', 'ч'],
    'days': ['день', 'дней', 'д'],
    'weeks': ['неделя', 'недели', 'н'],
    'months': ['месяц', 'месяца', 'мес'],
    'years': ['год', 'года', 'годы', 'г'],
}

re_values = re_values.copy()
re_values.update({
    'specials': 'om',
    'timeseparator': ':',
    'rangeseparator': '-',
    'daysuffix': 'ого|ой|ий|тье',
    'qunits': 'д|мес|г|ч|н|м|с',
    'now': ['сейчас'],
})

Modifiers = {
    'после': 1,
    'назад': -1,
    'предыдущий': -1,
    'последний': -1,
    'далее': 1,
    'ранее': -1,
}

dayOffsets = {
    'завтра': 1,
    'сегодня': 0,
    'вчера': -1,
    'позавчера': -2,
    'послезавтра': 2,
}

re_sources = {
    'полдень': {'hr': 12, 'mn': 0, 'sec': 0},
    'день': {'hr': 13, 'mn': 0, 'sec': 0},
    'обед': {'hr': 12, 'mn': 0, 'sec': 0},
    'утро': {'hr': 6, 'mn': 0, 'sec': 0},
    'завтрак': {'hr': 8, 'mn': 0, 'sec': 0},
    'ужин': {'hr': 19, 'mn': 0, 'sec': 0},
    'вечер': {'hr': 18, 'mn': 0, 'sec': 0},
    'полночь': {'hr': 0, 'mn': 0, 'sec': 0},
    'ночь': {'hr': 21, 'mn': 0, 'sec': 0},
}

small = {
    'ноль': 0,
    'один': 1,
    'два': 2,
    'три': 3,
    'четыре': 4,
    'пять': 5,
    'шесть': 6,
    'семь': 7,
    'восемь': 8,
    'девять': 9,
    'десять': 10,
    'одиннадцать': 11,
    'двенадцать': 12,
    'тринадцать': 13,
    'четырнадцать': 14,
    'пятнадцать': 15,
    'шестнадцать': 16,
    'семнадцать': 17,
    'восемнадцать': 18,
    'девятнадцать': 19,
    'двадцать': 20,
    'тридцать': 30,
    'сорок': 40,
    'пятьдесят': 50,
    'шестьдесят': 60,
    'семьдесят': 70,
    'восемьдесят': 80,
    'девяносто': 90,
}

numbers = {
    'ноль': 0,
    'один': 1,
    'два': 2,
    'три': 3,
    'четыре': 4,
    'пять': 5,
    'шесть': 6,
    'семь': 7,
    'восемь': 8,
    'девять': 9,
    'десять': 10,
    'одиннадцать': 11,
    'двенадцать': 12,
    'тринадцать': 13,
    'четырнадцать': 14,
    'пятнадцать': 15,
    'шестнадцать': 16,
    'семнадцать': 17,
    'восемнадцать': 18,
    'девятнадцать': 19,
    'двадцать': 20,
}

magnitude = {
    'тысяча': 1000,
    'миллион': 1000000,
    'миллиард': 1000000000,
    'триллион': 1000000000000,
    'квадриллион': 1000000000000000,
    'квинтиллион': 1000000000000000000,
    'секстиллион': 1000000000000000000000,
    'септиллион': 1000000000000000000000000,
    'октиллион': 1000000000000000000000000000,
    'нониллион': 1000000000000000000000000000000,
    'дециллион': 1000000000000000000000000000000000,
}
