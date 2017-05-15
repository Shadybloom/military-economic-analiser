#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Military economic analyser v2.04
# Old name: Pony demographic calculator
# Author: one not a very clever pony
# License: WTFPL2 http://www.wtfpl.net/about/

# Скрипт исследует демографию произвольного государства, по общим данным,
# таким как численность популяции, рост населения и показатели смертности.
# Затем вычисляются возможности к мобилизации, срочный состав армии,
# численность резервистов. Всё это раскидывается по таблицам, по годам.
# И наконец, исследуется экономика. По данным о стоимости оружия наглядно
# показывается оснащение армии. Любое оснащение, которое только может быть.
# Этот скрипт способен учесть всё: от авианосцев и крейсеров, до грузовиков,
# автоматов, патронов и даже носовых платков. Число опций не ограничено.
# Разумеется, учитывается старение оружие, поломки и списание.
# Нужно лишь только параметры правильно задать.

# Методы: распределение Гомпертца-Мейкхама и геометрические прогрессии.
# Скрипт проверялся на интерпретаторе:
# Python 3.4.3 (default, Sep  7 2015, 15:40:35) 
# [GCC 5.2.0] on linux

#-------------------------------------------------------------------------
# Опции:

# В данном примере исследуется цивилизация маленьких пони в сеттинге FoE:
# http://falloutequestria.wikia.com/wiki/Fallout:_Equestria_Wiki

# Год начала отсчёта, принимаются любые целые числа:
YEAR_START = 1977
# До какого возраста исследовать популяцию:
AGE_END = 100

# Переменные геометрической прогрессии роста населения:
# Численность населения в год начала отсчёта:
POPULATION = 120000000
# Уровень рождаемости (например: 0.03 значит 3%
# или 30 новорожденных на 1000 населения в год):
FERTILITY_RATE = 0.03
# Уровень смертности, аналогично:
MORTALITY_RATE = 0.011

# Переменные для расчёта военной экономики:
# ВВП на душу населения:
# https://ru.wikipedia.org/wiki/Список_стран_по_ВВП_(ППС)_на_душу_населения
GDP_RATE = 50000
# Годовой рост ВВП (без инфляции):
# Для примера, данные по росту ВВП США 1970-2013 годы:
# http://www.be5.biz/makroekonomika/gdp/gdp_usa.html
# За период в 43 года средний рост ВВП был равен:
# 1075.9*x^(43-1)=3580 x=1.029 (2.9%)
GDP_GROWTH = 0.03
# Доля военного бюджета в ВВП страны. В США, например 3.5%,
# Во время Второй мировой войны бюджеты армий доходили до 50-100% ВВП:
# http://aillarionov.livejournal.com/811219.html
GDP_ARMY = 0.25

# Далее идут переменные для распределения Гомпертца-Мейкхама:
# http://dic.academic.ru/dic.nsf/ruwiki/923652
# Можно ориентироваться на исследование популяции людей 20-го века:
# "Parametric models for life insurance mortality data: gompertz's law over time"
# Компонент Мейкхама, независимый от возраста риск (0.003 = 0.3% каждый год):
COMPONENT_A = 0.003
# Коэффициент b:
COEFFICIENT_B = 0.000350
# Коэффициент c:
COEFFICIENT_C = 1.08

# Распределение полов.
MALE_NAME = 'Жеребцы'
MALE_PERCENT = 0.4
FEMALE_NAME = 'Кобылки'
FEMALE_PERCENT = 0.6

# Армия (или профессия):
# Процент рекрутов: 0.25 — отборные; 0.25-0.5 — середнячки;
# 0.5-0.75 — кривые, косые; 0.75+ — глухие, слепые, убогие умом.
prof_percent = 0.5
# Профессиональный риск, изменение компонента Мейкхама:
# (0.01 = 1% риск смерти каждый год)
prof_hazard = 0.01
# Призывники обоих полов? 0 - нет; 1 - да
prof_male_switch = 1
prof_female_switch = 1
# Возраст призыва:
prof_age_apprentice = 17
# Возраст перехода в резервисты:
prof_age_expert = 20
# Возраст отставки:
prof_age_retiree = 50
prof_name_apprentice = 'Срочники'
prof_name_expert = 'Резервисты'
prof_name_retiree = 'Отставники'

# Список видов войск. Используется базой данных военной техники,
# Смотрите параметр 'wpn_troops_type'.
# Для замены хорошо подойдут регулярные выражения, например в Vim'е:
# %s/'РВ'/'РВСН'/g — подправит всю базу данных. Кавычки важны.
dict_troops_types = {
        # Формат:
        # 'Вид_войск':процент,
        'ALL':1,
        # Сухопутные войска:
        'СВ':0.4,
        # Артиллерийские войска
        'АВ':0.1,
        # Ракетные войска и дальняя ПВО:
        'РВ':0.1,
        # Военно-воздушные войска:
        'ВВС':0.1,
        # Военно-морской флот:
        'ВМФ':0.1,
        # Инженерные войска:
        'ИВ':0.2,
        }

#-------------------------------------------------------------------------
# База данных оружия. Двумерный массив.

# Дополняется блоками, без ограничений и очень легко. Пользуйтесь этим.
# Пожалуйста, пишите в строке 'wpn_name_comment' краткое описание оружия,
# а в строке 'wpn_cost_currency' точно указывайте валюту и год.
# История скажет вам спасибо.

# Для поиска данных можно использовать списки оружия из википедии, например:
# https://ru.wikipedia.org/wiki/Список_оружия_сухопутных_войск_Российской_Федерации
# https://en.wikipedia.org/wiki/Equipment_of_the_United_States_Armed_Forces
# Эквестрийские биты = доллары США 2015 года.

# Создаётся объединённый словарь — строки массива.
metadict_wpn = {}

# Выбирается первый из ключей — номер столбца.
dict_wpn_key = 0
dict_wpn = {
        'wpn_name':'Бронетранспортёры',
        'wpn_name_comment':'БТРы и БМП. Колёсные и гусеничные, с различным вооружением. Десант: 9 солдат; экипаж — трое.',
        # Принадлежность к виду войск:
        'wpn_troops_type':'СВ',
        # Цена на мировом рынке оружия или стоимость производства:
        # Для примера, «Бредли» стоит около 3.166 млн долларов:
        # http://www.globalsecurity.org/military/systems/ground/m2-specs.htm
        'wpn_cost':3000000,
        'wpn_cost_currency':'Эквестрийские биты',
        # Доля затрат на данный вид оружия в военном бюджете:
        # Для примера, департамент обороны США тратит 19% бюджета на все закупки:
        # https://upload.wikimedia.org/wikipedia/commons/6/67/US_DOD_budget_2014_RUS.png
        'wpn_budget':0.02,
        'wpn_name_new':'Бронетранспортёры новые',
        'wpn_name_mid':'Бронетранспортёры устаревшие',
        'wpn_name_old':'Бронетранспортёры под списание',
        # Возраст потрёпанности:
        'wpn_age_mid':10,
        # Возраст старости:
        'wpn_age_old':20,
        # Переменные распределения Гомпертца-Мейкхама для оружия:
        # Строка 'wpn_a':0.05 значит 5% вероятность поломки в год.
        # Остальные корректируют вероятность по возрасту оружия.
        # (пока что всё это очень неточно)
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
# Данные записываются в общий словарь, как столбец двумерного массива.
metadict_wpn[dict_wpn_key] = dict_wpn

# Переход на новый столбец:
dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Основные боевые танки',
        'wpn_name_comment':'Гесеничные машины массой в 50 тонн. Пушечное и ракетное вооружение. Трое членов экипажа.',
        'wpn_troops_type':'СВ',
        'wpn_cost':6000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Основные боевые танки новые',
        'wpn_name_mid':'Основные боевые танки старой серии',
        'wpn_name_old':'Основные боевые танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРПК малой дальности',
        'wpn_name_comment':'Зенитные ракетно-пушечные комплексы с дальностью ракет до 20 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'ЗРПК малой дальности новые',
        'wpn_name_mid':'ЗРПК малой дальности устаревшие',
        'wpn_name_old':'ЗРПК малой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевые роботы',
        'wpn_name_comment':'Летающие и колёсные машины; на маховиках; различное вооружение. Вес до 200 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':200000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Боевые роботы новые',
        'wpn_name_mid':'Боевые роботы устаревшие',
        'wpn_name_old':'Боевые роботы на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные ракетные комплексы',
        'wpn_name_comment':'Противотанковые и противовоздушные, с дальностью до 5 км, а весом до 30 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'ПТРК/ПЗРК новые',
        'wpn_name_mid':'ПТРК/ПЗРК устаревшие',
        'wpn_name_old':'ПТРК/ПЗРК под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'РПГ и РПО',
        'wpn_name_comment':'Противотанковые гранатомёты и реактивные огнемёты: одноразовые, в контейнерах массой 3 и 12 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1500,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'РПГ и РПО новые',
        'wpn_name_mid':'РПГ и РПО устаревшие',
        'wpn_name_old':'РПГ и РПО под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевая экипировка',
        'wpn_name_comment':'Разгрузка, прицелы, связь. СИБЗ: шлемы, защитные комбинезоны, пластины, химкостюмы. Вес 10-20 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Боевая экипировка новая',
        'wpn_name_mid':'Боевая экипировка поношенная',
        'wpn_name_old':'Боевая экипировка под списание',
        'wpn_age_mid':6,
        'wpn_age_old':12,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Силовая броня',
        'wpn_name_comment':'Для спецопераций. Скафандры с экзоскелетами, штурмовые щиты. Гидроприводы и маховики, 100 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':500000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Силовая броня современная',
        'wpn_name_mid':'Силовая броня устаревшая',
        'wpn_name_old':'Силовая броня под списание',
        'wpn_age_mid':6,
        'wpn_age_old':12,
        'wpn_a':0.05,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходная артиллерия',
        'wpn_name_comment':'Гусеничные и колёсные САУ, батальонные/полковые; калибр: 120-мм; дальность огня — 10 км.',
        'wpn_troops_type':'АВ',
        'wpn_cost':3000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Самоходные артиллерийские установки новые',
        'wpn_name_mid':'Самоходные артиллерийские установки устаревшие',
        'wpn_name_old':'Самоходные артиллерийские установки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Буксируемая артиллерия',
        'wpn_name_comment':'Дивизионные пегасо-буксируемые орудия, калибр 150-мм, дальность огня 30 км.',
        'wpn_troops_type':'АВ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Буксируемые артиллерийские установки новые',
        'wpn_name_mid':'Буксируемые артиллерийские установки устаревшие',
        'wpn_name_old':'Буксируемые артиллерийские установки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивная артиллерия',
        'wpn_name_comment':'РСЗО с ракетами различных калибров, от 120-мм (30 км) до 300-мм (70 км).',
        'wpn_troops_type':'АВ',
        'wpn_cost':2000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Реактивные системы залпового огня новые',
        'wpn_name_mid':'Реактивные системы залпового огня устаревшие',
        'wpn_name_old':'Реактивные системы залпового огня под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивные снаряды (тонны)',
        'wpn_name_comment':'Различные реактивные снаряды (от 60 кг на 120-мм, до 800 кг на 300-мм)',
        'wpn_troops_type':'АВ',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Реактивные снаряды новые (тонны)',
        'wpn_name_mid':'Реактивные снаряды устаревшие (тонны)',
        'wpn_name_old':'Реактивные снаряды под списание (тонны)',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.20,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Артиллерийские снаряды (тонны)',
        'wpn_name_comment':'Снаряды ствольной артиллерии различных типов (20 кг на 120-мм, 40 кг на 150-мм)',
        'wpn_troops_type':'АВ',
        'wpn_cost':10000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Артиллерийские снаряды новые (тонны)',
        'wpn_name_mid':'Артиллерийские снаряды устаревшие (тонны)',
        'wpn_name_old':'Артиллерийские снаряды под списание (тонны)',
        'wpn_age_mid':10,
        'wpn_age_old':40,
        'wpn_a':0.20,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Дивизионы ЗРС большой дальности',
        'wpn_name_comment':'Мобильная радиолокационная станция и десять установок (40 ракет с дальностью до 400 км.)',
        'wpn_troops_type':'РВ',
        'wpn_cost':50000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.007,
        'wpn_name_new':'ЗРС третьего поколения',
        'wpn_name_mid':'ЗРС второго поколения',
        'wpn_name_old':'ЗРС первого поколения',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты большой дальности',
        'wpn_name_comment':'Для мобильных и шахтных пусковых установок, кораблей, авиации. Дальность 200-400 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':500000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Зенитные ракеты новые',
        'wpn_name_mid':'Зенитные ракеты устаревшие',
        'wpn_name_old':'Зенитные ракеты под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стратегические ракетные комплексы',
        'wpn_name_comment':'Баллистические ракеты с дальностью до 10 000 км, 50-тонная ракета, 6 ядерных боеголовок.',
        'wpn_troops_type':'РВ',
        'wpn_cost':50000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Пусковые установки СР новые',
        'wpn_name_mid':'Пусковые установки СР устаревшие',
        'wpn_name_old':'Пусковые установки СР под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тактические ракетные комплексы',
        'wpn_name_comment':'Крылатые ракеты с дальностью до 3000 км, 1.5 тонны ракета, ядерная боеголовка.',
        'wpn_troops_type':'РВ',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Пусковые установки ТР новые',
        'wpn_name_mid':'Пусковые установки ТР устаревшие',
        'wpn_name_old':'Пусковые установки ТР под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Крылатые ракеты',
        'wpn_name_comment':'Крылатые ракеты с дальностью до 1500 км, 1.5 тонны ракета, 400-кг боевая часть.',
        'wpn_troops_type':'РВ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Крылатые ракеты новые',
        'wpn_name_mid':'Крылатые ракеты устаревшие',
        'wpn_name_old':'Крылатые ракеты под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тандерхеды',
        'wpn_name_comment':'Крепости в живых облаках. 200 тысяч тонн грузоподъёмности, магнитная левитация, ядерный реактор.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':5000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Тандерхеды третьего поколения',
        'wpn_name_mid':'Тандерхеды второго поколения',
        'wpn_name_old':'Тандерхеды первого поколения',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Рапторы',
        'wpn_name_comment':'Десантные корабли. 500 тонн взлётного веса, 100 тонн груза; турбовинтовые двигатели, атомная СУ.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':250000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Рапторы новые',
        'wpn_name_mid':'Рапторы устаревшие',
        'wpn_name_old':'Рапторы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Многоцелевые истребители',
        # https://ru.wikipedia.org/wiki/МиГ-21
        'wpn_name_comment':'Фронтовые истребители и истребители-перехватчики. 5-10 тонн, 1-2 Маха, до 1500 км дальность.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Истребители новые',
        'wpn_name_mid':'Истребители устаревшие',
        'wpn_name_old':'Истребители под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Универсальные планеры',
        'wpn_name_comment':'Скорость до 200 км/час. Грузоподъёмность до 200 кг. Вместо двигателя пегас с 60 Квт крылосил.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Универсальные планеры новые',
        'wpn_name_mid':'Универсальные планеры потрёпанные',
        'wpn_name_old':'Универсальные под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Неуправляемые ракеты (тонны)',
        'wpn_name_comment':'Всевозможные НАРы: от 4 кг 60-мм, до 25 кг 160-мм. Для истребителей, планеров, десантных кораблей.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Неуправляемые ракеты новые (тонны)',
        'wpn_name_mid':'Неуправляемые ракеты устаревшие (тонны)',
        'wpn_name_old':'Неуправляемые ракеты под списание (тонны)',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.20,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Управляемые ракеты',
        'wpn_name_comment':'Для бронетехники, кораблей, авиации. Противотанковые, противовоздушные, противорадарные.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Управляемые ракеты новые',
        'wpn_name_mid':'Управляемые ракеты устаревшие',
        'wpn_name_old':'Управляемые ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.2,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Подводные ракетоносцы',
        'wpn_name_comment':'Водоизмещение: 5000 тонн. Атомные силовые установки. 10 пусковых шахт, торпеды.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':2000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Подводные ракетоносцы новые',
        'wpn_name_mid':'Подводные ракетоносцы устаревшие',
        'wpn_name_old':'Подводные ракетоносцы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Эсминцы',
        'wpn_name_comment':'Водоизмещение: 5000 тонн. Атомные силовые установки. Ракетное и торпедное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':1000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Фрегаты новые',
        'wpn_name_mid':'Фрегаты устаревшие',
        'wpn_name_old':'Фрегаты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Корветы',
        'wpn_name_comment':'Водоизмещение: 2000 тонн. АСУ, воздушная каверна — скорость до 50 узлов. Ракеты и торпеды.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':300000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Корветы новые',
        'wpn_name_mid':'Корветы устаревшие',
        'wpn_name_old':'Корветы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Вспомогательные суда',
        'wpn_name_comment':'Суда снабжения. Водоизмещение 2-5 тысяч тонн. Вместо двигателей пегасы и маховики.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':50000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Вспомогатлеьные суда новые',
        'wpn_name_mid':'Вспомогательные суда устаревшие',
        'wpn_name_old':'Вспомогательные суда под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Сторожевые катера',
        'wpn_name_comment':'Водоизмещение до 500 тонн. Маховики и пегасы вместо двигателей. Ракетное и пушечное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':20000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Сторожевые катера новые',
        'wpn_name_mid':'Сторожевые катера устаревшие',
        'wpn_name_old':'Сторожевые катера под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Торпеды и мины',
        'wpn_name_comment':'Торпеды массой 0.3-1.5 тонны и автономные мины-торпеды 1-2 тонны.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Торпеды и мины новые',
        'wpn_name_mid':'Торпеды и мины устаревшие',
        'wpn_name_old':'Торпеды и мины под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Военные городки',
        'wpn_name_comment':'Для войсковых частей типа полк/бригада, 1500-5000 солдат.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':300000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.03,
        'wpn_name_new':'Военные городки современные',
        'wpn_name_mid':'Военные городки старого типа',
        'wpn_name_old':'военные городки устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Военно-промышленные комплексы',
        'wpn_name_comment':'Предприятия оборонной промышленности: ремонтные мастерские, заводы и конструкторские бюро.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':1000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.03,
        'wpn_name_new':'Предприятия ВПК современные',
        'wpn_name_mid':'Предприятия ВПК старого типа',
        'wpn_name_old':'Предприятия ВПК устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Инженерные машины',
        'wpn_name_comment':'Минные заградители и разградители, мостоукладчики и путепрокладчики, ремонтные машины.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':6000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Инженерные машины новые',
        'wpn_name_mid':'Инженерные машины устаревшие',
        'wpn_name_old':'Инженерные машины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тяжёлые грузовые машины',
        'wpn_name_comment':'Маховики, двигатели внутреннего сгорания. Грузоподъёмность 10-60 тонн.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':200000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Тяжёлые грузовики современные',
        'wpn_name_mid':'Тяжёлые грузовики старого типа',
        'wpn_name_old':'Тяжёлые грузовики устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиационно-защитные костюмы',
        'wpn_name_comment':'Скафандры: системы фильтров, охлаждение, огнеупорная ткань. Масса 30 кг.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Радиационно-защитные костюмы новые',
        'wpn_name_mid':'Радиационно-защитные костюмы поношенные',
        'wpn_name_old':'Радиационно-защитные костюмы под списание',
        'wpn_age_mid':6,
        'wpn_age_old':12,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Автоматические турели',
        'wpn_name_comment':'Неподвижные боевые роботы. Различное вооружение, масса до 200 кг',
        'wpn_troops_type':'ИВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Автоматические турели новые',
        'wpn_name_mid':'Автоматические турели устаревшие',
        'wpn_name_old':'Автоматические турели под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Инженерные боеприпасы (тонны)',
        'wpn_name_comment':'Мины контактные и направленного действия. Противотанковые 10-20 кг, Противопехотные 0.5-1 кг.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':50000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Инженерные боеприпасы (тонны) новые',
        'wpn_name_mid':'Инженерные боеприпасы (тонны) устаревшие',
        'wpn_name_old':'Инженерные боеприпасы (тонны) под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.20,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стрелковое оружие',
        'wpn_name_comment':'Пулемёты, станковые и лёгкие; снайперские и штурмовые винтовки; короткоствольное оружие.',
        'wpn_troops_type':'ALL',
        'wpn_cost':3000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.007,
        'wpn_name_new':'Стрелковое оружие новое',
        'wpn_name_mid':'Стрелковое оружие устаревшее',
        'wpn_name_old':'Стрелковое оружие под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны',
        'wpn_name_comment':'Для стрелкового оружия различных калибров. В цинках, ящиках и патронных лентах.',
        'wpn_troops_type':'ALL',
        'wpn_cost':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Патроны новые',
        'wpn_name_mid':'Патроны устаревшие',
        'wpn_name_old':'Патроны под списание',
        'wpn_age_mid':10,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Гранатомётные выстрелы',
        'wpn_name_comment':'Для подствольных гранатомётов и автоматических гранатомётных систем. Калибр 30-40 мм, 0.1-0.3 кг',
        'wpn_troops_type':'ALL',
        'wpn_cost':60,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Гранатомётные выстрелы новые',
        'wpn_name_mid':'Гранатомётные выстрелы устаревшие',
        'wpn_name_old':'Гранатомётные выстрелы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

#-------------------------------------------------------------------------
# Внутренние переменные.

# Создаём рабочие переменные на основе данных из опций (для удобства):
year_real = YEAR_START
age_real = AGE_END
pop = POPULATION
fert = FERTILITY_RATE
mort = MORTALITY_RATE
a = COMPONENT_A
b = COEFFICIENT_B
c = COEFFICIENT_C


#-------------------------------------------------------------------------
# Функции, подпрограммы. Последующие вызывают предыдущие.

def population_size(year):
    """Вычисляем численность популяции.

    Рост популяции, это геометрическая прогрессия, например:
    100000*1.002^(100-1)=121872
    Начальная численность, годовой прирост, период в сто лет.
    Функция вычисляет исходную численность, зная конечную:
    121872*1.002^(1-100)=100000
    """
    population = POPULATION * ((FERTILITY_RATE - MORTALITY_RATE + 1) ** (-year))
    # Округляем число
    population = round (population)
    return population
 
def generation_size(year, percent):
    """Определяем численность поколения.

    Поколение, это процент от популяции, например, если рождаемость 0.02:
    121872*1.002^(1-100)*0.02=2000 (2% новорожденных в популяции)
    Точно так же можно определить число умерших, прирост населения, состав:
    121872*1.002^(1-100)*0.02*0.5=1000 (50% новорожденных мужского пола)
    """
    generation = round(population_size(year) * percent)
    return generation

def GDP_size(year):
    """ВВП страны в определённый год.

    Рост благосостояния, это та же геометрическая прогрессия:
    10000*1.03^(1-100)=536
    В данном случае от 536$ за столетие ВВП вырос до 10 000$
    """
    GDP_in_year = GDP_RATE * ((GDP_GROWTH + 1) ** (-year)) * population_size(year)
    GDP_in_year = round (GDP_in_year)
    return GDP_in_year

def gompertz_distribution(a, b, c, age):
    """Распределение Гомпертца. Риск смерти в зависимости от возраста.

    Распределение Гомпертца-Мейкхама неплохо работает в
    демографических расчётах для самых разных популяций.
    Единственный недостаток — оно склонно занижать
    смертность в начале и завышать в конце (экспонента, что поделать).
    Для популяции людей даёт хорошие результаты в диапазоне — 30-70 лет.
    Формула: p=a+b*(c^x)
    Где:
    p — вероятность смерти в процентах
    a — независимый от возраста риск (0.002%)
    b — коэффициент 2 (0.000350)
    c — коэффициент 3 (1.08)
    x — возраст в годах
    Коэффициенты подобраны с учётом исследования:
    "Parametric models for life insurance mortality data: gompertz's law over time".
    """
    chance_of_dying = a + b * (c ** age)
    # Проверка. Если получилось больше 1, значит 100% смерть.
    if (chance_of_dying > 1):
        chance_of_dying = 1
    return chance_of_dying


def generation_alive(generation, a, b, c, age_real):
    """Число живых в поколении.

    Каждый год умирает некий процент из поколения.
    Этот цикл вычисляет точное число живых в определённый год.
    """
    # Задаём рабочую переменную для цикла:
    age = 0
    # Из численности поколения вычитаем число погибших в первый год:
    generation_survivors = generation - \
            generation * \
            gompertz_distribution(a, b , c, age)
    # Далее это вычитание продолжается циклично.
    while (age <= age_real):
        age = age + 1
        generation_survivors = generation_survivors - \
                generation_survivors * \
                gompertz_distribution(a, b, c, age)
        # Проверка. Если число выживших уходит в минус, значит все мертвы.
        if (generation_survivors <= 0):
            generation_survivors = 0
            break
    # Округляем число
    generation_survivors = round(generation_survivors)
    return generation_survivors


def generation_profession(prof_percent, prof_hazard):
    """Число представителей определённой профессии, с учётом риска."""
    prof_number = 0
    if (prof_male_switch != 0):
        # Берём из словаря численность живых в нужном поколении
        # и пропускаем через ещё один цикл, чтобы учесть риск профессии.
        prof_number = prof_number + \
                generation_alive(dict_population['generation_alive'] * MALE_PERCENT * prof_percent,
                        # Отчёт начинается с возраста профессии.
                        prof_hazard, b, c, age_real - prof_age_apprentice)
    if (prof_female_switch != 0):
        prof_number = prof_number + \
                generation_alive(dict_population['generation_alive'] * FEMALE_PERCENT * prof_percent,
                        prof_hazard, b, c, age_real - prof_age_apprentice)
    return prof_number


#-------------------------------------------------------------------------
# Главный цикл скрипта.

# Эта база данных станет индексом для словарей.
metadict = {}

# Рабочие переменные:
progression_year = 0
year = 0

# Цикл перебирает годы, уходя в прошлое,
# пока возраст популяции не сравняется с возрастом конца исследования.
while (progression_year <= AGE_END):
    # Определяем текущий год (для прогрессии роста населения).
    year = AGE_END - progression_year
    year_real = YEAR_START - year

    # Создаём основной словарь (базу данных) для этого возраста:
    dict_population = {
            'age_real':age_real,
            'year_real':year_real,
            'population_size':population_size(year),
            'generation_size':generation_size(year, fert),
            'generation_alive':generation_alive(generation_size(year, fert), a, b, c, age_real),
            'GDP_size':GDP_size(year)
            }

    # Определяем численность призывников:
    prof_number_apprentice = 0
    if (prof_age_apprentice <= age_real < prof_age_expert):
        prof_number_apprentice = prof_number_apprentice + \
                generation_profession(prof_percent, prof_hazard)
    # Определяем численность резервистов:
    prof_number_expert = 0
    if (prof_age_expert <= age_real < prof_age_retiree):
        prof_number_expert = prof_number_expert + \
                generation_profession(prof_percent, prof_hazard)
    # И, наконец, пенсионеры:
    prof_number_retiree = 0
    if (prof_age_retiree <= age_real):
        prof_number_retiree = prof_number_retiree + \
                generation_profession(prof_percent, prof_hazard)

    # Создаём временный словарь гендеров и профессий:
    dict_demography = {
            MALE_NAME:generation_alive(generation_size(year, fert * MALE_PERCENT), a, b, c, age_real),
            FEMALE_NAME:generation_alive(generation_size(year, fert * FEMALE_PERCENT), a, b, c, age_real),
            prof_name_apprentice:prof_number_apprentice,
            prof_name_expert:prof_number_expert,
            prof_name_retiree:prof_number_retiree,
            }
 
    # Дополняем первый словарь вторым
    dict_population.update(dict_demography)
    # Создаём объединённый словарь,
    # он будет пополняться при каждом проходе цикла:
    metadict[age_real] = dict_population

    # Завершение главного цикла:
    progression_year = progression_year + 1
    age_real = age_real - 1


#-------------------------------------------------------------------------
# Модуль. Вычисляет производство и количество оружия в войсках.

# База данных с количеством оружия за весь период. Двумерный массив:
metadict_equipment = {}

# Исследование объединённого словаря. Создание базы данных оружия.
# Перебираем вложенные словари начиная с последнего:
for meta_key in sorted(metadict.keys(), reverse=True):
    # Временный словарь вооружений (за один год):
    dict_equipment = {}
    # Перебираем опции из базы данных вооружений:
    for wpn_key in sorted(metadict_wpn.keys()):
        # Количество созданных машин, это бюджет на них, делённый на стоимость.
        wpn_create = round(metadict[meta_key]['GDP_size'] * GDP_ARMY * \
                metadict_wpn[wpn_key]['wpn_budget'] / metadict_wpn[wpn_key]['wpn_cost'])
        wpn_alive = generation_alive(wpn_create,
                metadict_wpn[wpn_key]['wpn_a'],
                metadict_wpn[wpn_key]['wpn_b'],
                metadict_wpn[wpn_key]['wpn_c'],
                metadict[meta_key]['age_real'])
        # Создаём временный словарь:
        dict_equipment[metadict_wpn[wpn_key]['wpn_name']] = wpn_alive
    # Объединяем временные словари в базу данных:
    metadict_equipment[meta_key] = dict_equipment


#-------------------------------------------------------------------------
# Вывод результатов.

# Вывод по годам:
for meta_key in sorted(metadict.keys(), reverse=True):
    # Вывод данных о населении:
    print('Год:', metadict[meta_key]['year_real'],
            'Возраст:', metadict[meta_key]['age_real'],
            'Родившиеся:', metadict[meta_key]['generation_size'],
            'Живые:', metadict[meta_key]['generation_alive'])
    print(MALE_NAME, metadict[meta_key][MALE_NAME],
            FEMALE_NAME, metadict[meta_key][FEMALE_NAME])
    # Вывод данных о солдатах:
    if (prof_age_apprentice <= metadict[meta_key]['age_real'] < prof_age_expert):
        print(prof_name_apprentice, metadict[meta_key][prof_name_apprentice])
    if (prof_age_expert <= metadict[meta_key]['age_real'] < prof_age_retiree):
        print(prof_name_expert, metadict[meta_key][prof_name_expert])
    if (prof_age_retiree <= metadict[meta_key]['age_real']):
        print(prof_name_retiree, metadict[meta_key][prof_name_retiree])
    # Вывод данных о вооружении:
    for wpn_key in sorted(metadict_wpn.keys()):
        # Отмена вывода, если число машинок по нулям.
        if (metadict_equipment[meta_key][metadict_wpn[wpn_key]['wpn_name']] != 0):
            if (metadict[meta_key]['age_real'] < metadict_wpn[wpn_key]['wpn_age_mid']):
                print(metadict_wpn[wpn_key]['wpn_name_new'],
                        # Обращение аж к двум словарям, одно вложено в другое.
                        metadict_equipment[meta_key][metadict_wpn[wpn_key]['wpn_name']])
            if (metadict_wpn[wpn_key]['wpn_age_mid'] <= metadict[meta_key]['age_real'] <
                    metadict_wpn[wpn_key]['wpn_age_old']):
                print(metadict_wpn[wpn_key]['wpn_name_mid'],
                        metadict_equipment[meta_key][metadict_wpn[wpn_key]['wpn_name']])
            if (metadict_wpn[wpn_key]['wpn_age_old'] <= metadict[meta_key]['age_real']):
                print(metadict_wpn[wpn_key]['wpn_name_old'],
                        metadict_equipment[meta_key][metadict_wpn[wpn_key]['wpn_name']])
    print('------------------------------------------------------------')

# Подведение итогов:
print('Ожидаемая численность:', POPULATION)
population_alive = 0
army_soldiers= 0
army_reservists = 0
for meta_key in sorted(metadict.keys()):
    population_alive = population_alive + metadict[meta_key]['generation_alive']
    army_soldiers = army_soldiers + metadict[meta_key][prof_name_apprentice]
    army_reservists = army_reservists + metadict[meta_key][prof_name_expert]
print('Численность популяции:', population_alive)
print(prof_name_apprentice, 'и', prof_name_expert, 'по видам войск:')
for troop_key in sorted(dict_troops_types.keys()):
    print('    ', troop_key, ' (', round(dict_troops_types[troop_key] * 100), '%) ',
            round(army_soldiers * dict_troops_types[troop_key]),
            ' — ', round((army_soldiers + army_reservists) * dict_troops_types[troop_key]), sep='')
print('Несчастные случаи (в год):', round(POPULATION * COMPONENT_A))
print('Военные потери: ', round((army_soldiers + army_reservists) * prof_hazard),
        ' (', round((army_soldiers + army_reservists) * prof_hazard / (POPULATION * COMPONENT_A) * 100),
        '% от несчастных случаев)', sep='')
print('------------------------------------------------------------')

# И наконец, суммируем всё вооружение, вычисляем отношение единиц к числу солдат,
# а также суммарный бюджет на вооружения и бюджеты по родам войск:
budget_percent = 0
budget_troops_percent = 0
# Создаётся рабочий словарь, обнуляются значения:
budget_troops_types = {}
budget_troops_types.update(dict_troops_types)
for troop_key in budget_troops_types:
    budget_troops_types[troop_key] = 0
# Перебор столбцов в базе данных оружия:
for wpn_key in sorted(metadict_wpn.keys()):
    equipment_all = 0
    # Затем перебор по годам:
    for meta_key in sorted(metadict_equipment.keys()):
        equipment_all = equipment_all + metadict_equipment[meta_key][metadict_wpn[wpn_key]['wpn_name']]
    # Если есть проект, значит есть оружие, хотя бы один экземпляр:
    if (equipment_all < 1):
        equipment_all = 1
        print('Не хватает бюджета на',metadict_wpn[wpn_key]['wpn_name'])
    # Вывод суммы оружия, сохранившегося за все годы:
    print(metadict_wpn[wpn_key]['wpn_troops_type'], metadict_wpn[wpn_key]['wpn_name'], '—' , equipment_all, end=' ')
    # Вывод отношения числа вооружений к числу солдат определённых видов войск:
    army_type_percent = dict_troops_types[metadict_wpn[wpn_key]['wpn_troops_type']]
    print('на', round(army_soldiers * army_type_percent / equipment_all),
            prof_name_apprentice, metadict_wpn[wpn_key]['wpn_troops_type'],
            'или на', round((army_reservists + army_soldiers) * army_type_percent / equipment_all),
            prof_name_apprentice, '+',
            prof_name_expert, metadict_wpn[wpn_key]['wpn_troops_type'])
    # Вывод описания вооружения:
    print('    ', metadict_wpn[wpn_key]['wpn_name_comment'])
    # Подсчитываем потери (без учёта старения оружия):
    wpn_create = round(GDP_size(0) * GDP_ARMY * \
                metadict_wpn[wpn_key]['wpn_budget'] / metadict_wpn[wpn_key]['wpn_cost'])
    print('        Создано:', wpn_create)
    print('        Потери:', round(wpn_create * metadict_wpn[wpn_key]['wpn_a'] + \
            equipment_all * metadict_wpn[wpn_key]['wpn_a']))
    print('        ---')
    # Считаем общий бюджет и бюджет по родам войск:
    budget_percent = budget_percent + metadict_wpn[wpn_key]['wpn_budget']
    for troop_key in budget_troops_types:
        if troop_key == metadict_wpn[wpn_key]['wpn_troops_type']:
            budget_troops_types[troop_key] = budget_troops_types[troop_key] + \
                    metadict_wpn[wpn_key]['wpn_budget'] * 100

# Сумма бюджета всех проектов из базы данных оружия:
print('Расходы военного бюджета на виды войск:')
for troop_key in sorted(budget_troops_types.keys()):
    print('    ', troop_key, ' (', round(dict_troops_types[troop_key] * 100), '%)',
            ' — ', round(budget_troops_types[troop_key], 1), '%', sep='')
print('Использовано ', round(budget_percent * 100), '% бюджета армии',
        ' (или ', round(GDP_ARMY * budget_percent * 100), '% ВВП страны)',
        sep='')
