#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Military economic analyser v2.05-Fallout:Equestria
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
YEAR_START = 2077
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


#-------------------------------------------------------------------------
# Список видов войск. Используется базой данных военной техники,
# Смотрите параметр 'wpn_troops_type'.

# Для замены хорошо подойдут регулярные выражения, например в Vim'е:
# %s/'РВ'/'РВСН'/g — подправит всю базу данных. Кавычки важны.
dict_troops_types = {
        # Формат:
        # 'Вид_войск':процент,
        # Военно-промышленный комплекс (боеприпасы):
        'ВПК':1,
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
        'wpn_name_comment':'15-тонные колёсные и гусеничные БТР, вооружены пулемётом, АГС и ПТУР. Десант: 9 солдат; экипаж — трое.',
        # Принадлежность к виду войск:
        'wpn_troops_type':'СВ',
        # Цена на мировом рынке оружия или стоимость производства:
        # Для примера, «Бредли» стоит около 3.166 млн долларов:
        # http://www.globalsecurity.org/military/systems/ground/m2-specs.htm
        'wpn_cost':2000000,
        'wpn_cost_currency':'Эквестрийские биты',
        # Доля затрат на данный вид оружия в военном бюджете:
        # Департамент обороны США тратит 19% бюджета на все закупки:
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
        # Строка 'wpn_a':0.05 значит 5% вероятность потери в год.
        # wpn_b и wpn_c корректируют вероятность по возрасту оружия,
        # Чем выше эти параметры, тем быстрее растут потери.
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Вооружение техники №1 (крупнокалиберный пулемёт):
        'wpn_ammo_1_name':'Патроны 15x120',
        # Один боекомплект:
        'wpn_ammo_1_capacity':500,
        # Максимум расхода боеприпасов в год:
        'wpn_ammo_1_expense':10000,
        # Вооружение техники №2 (малокалиберный пулемёт):
        'wpn_ammo_2_name':'Патроны 6x42',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        # Вооружение техники №3 (автоматический гранатомёт):
        'wpn_ammo_3_name':'Выстрелы АГС',
        'wpn_ammo_3_capacity':400,
        'wpn_ammo_3_expense':1200,
        # Вооружение техники №4 (противотанковый ракетный комплекс):
        'wpn_ammo_4_name':'Управляемые ракеты',
        'wpn_ammo_4_capacity':4,
        'wpn_ammo_4_expense':12,
        # Топливо/источник энергии (супермаховик 10 МДж/кг):
        'wpn_fuel_name':'Маховики (МДж)',
        # Разовый запас топлива/энергии:
        'wpn_fuel_capacity':10000,
        # Расход топлива на километр (максимум):
        # 200 квт мощность, скорость 30 км/час.
        'wpn_fuel_consumption':25,
        # Годовой расход топлива:
        'wpn_fuel_expense':250000,
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
        'wpn_budget':0.01,
        'wpn_name_new':'Основные боевые танки новые',
        'wpn_name_mid':'Основные боевые танки старой серии',
        'wpn_name_old':'Основные боевые танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        'wpn_ammo_2_name':'Снаряды 120-мм',
        'wpn_ammo_2_capacity':40,
        'wpn_ammo_2_expense':400,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':8,
        'wpn_ammo_3_expense':24,
        # Активная защита, две батареи лазеров:
        'wpn_ammo_4_name':'300-ГВт лазеры',
        'wpn_ammo_4_capacity':16,
        'wpn_ammo_4_expense':48,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':40000,
        'wpn_fuel_consumption':100,
        'wpn_fuel_expense':1000000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРПК малой дальности',
        'wpn_name_comment':'Зенитные ракетно-пушечные комплексы. 4 пушки, 12 ракет. Масса 30 тонн. Дальность 3-20 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'ЗРПК малой дальности новые',
        'wpn_name_mid':'ЗРПК малой дальности устаревшие',
        'wpn_name_old':'ЗРПК малой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':1600,
        'wpn_ammo_1_expense':16000,
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':12,
        'wpn_ammo_2_expense':36,
        'wpn_ammo_3_name':'300-ГВт лазеры',
        'wpn_ammo_3_capacity':16,
        'wpn_ammo_3_expense':48,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Сторожевые роботы',
        'wpn_name_comment':'Роботизированные танкетки. Вооружены крупнокалиберным пулемётом и управляемыми ракетами. Масса: 1.5 тонны.',
        'wpn_troops_type':'СВ',
        'wpn_cost':600000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Боевые роботы-стражи новые',
        'wpn_name_mid':'Боевые роботы-стражи устаревшие',
        'wpn_name_old':'Боевые роботы-стражи на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        # Оружие с боеприпасами весит 300 кг.
        'wpn_ammo_1_name':'Патроны 15x120',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Патроны 6x42',
        'wpn_ammo_2_capacity':1000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':2,
        'wpn_ammo_3_expense':6,
        # Вес маховика — 150 кг.
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':1500,
        # 23 кВт мощность, скорость 30 км/час.
        'wpn_fuel_consumption':2.7,
        'wpn_fuel_expense':28000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Штурмовые роботы',
        'wpn_name_comment':'Летающие машины, мультикоптеры. Вооружены пулемётом и АГС. Радиус действия: 60 км; вес 200 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':300000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Боевые роботы-штурмовики новые',
        'wpn_name_mid':'Боевые роботы-штурмовики устаревшие',
        'wpn_name_old':'Боевые роботы-штурмовики на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        # Оружие с боеприпасами весит 50 кг.
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':10000,
        'wpn_ammo_2_name':'Выстрелы АГС',
        'wpn_ammo_2_capacity':40,
        'wpn_ammo_2_expense':400,
        # Вес маховика — 30 кг.
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':300,
        # Скорость до 25 м/с, 60 киловатт. Дальность 125 км.
        'wpn_fuel_consumption':1.6,
        'wpn_fuel_expense':32000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Разведывательные роботы',
        'wpn_name_comment':'Мультикоптеры с электромагнитный снайперской пушкой. Радиус действия: 300 км; вес 200 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Боевые роботы-разведчики новые',
        'wpn_name_mid':'Боевые роботы-разведчики устаревшие',
        'wpn_name_old':'Боевые роботы-разведчики на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0008,
        'wpn_c':2,
        # Оружие с боеприпасами весит 30 кг.
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':1000,
        'wpn_ammo_1_expense':1000,
        # Вес аккумулятора — 50 кг.
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        'wpn_fuel_capacity':1500,
        # Скорость до 25 м/с, 60 киловатт. Дальность 625 км.
        'wpn_fuel_consumption':1.6,
        'wpn_fuel_expense':64000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Станковые крупнокалиберные пулемёты',
        'wpn_name_comment':'Пегасо-переносимый пулемёт калибра 15-мм. Масса: 100 кг (50 кг станок). Прицельная дальность: 2000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Станковые крупнокалиберные пулемёты новые',
        'wpn_name_mid':'Станковые крупнокалиберные пулемёты устаревшие',
        'wpn_name_old':'Станковые крупнокалиберные пулемёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 15x120',
        # Вес патронной ленты и короба 60 кг.
        'wpn_ammo_1_capacity':250,
        'wpn_ammo_1_expense':5000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Станковые автоматические гранатомёты',
        'wpn_name_comment':'Пегасо-переносимый АГС под гранаты калибра 30-мм. Масса: 50 кг. Дальность огня: 2000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':30000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Станковые автоматические гранатомёты новые',
        'wpn_name_mid':'Станковые автоматические гранатомёты устаревшие',
        'wpn_name_old':'Станковые автоматические гранатомёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Выстрелы АГС',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':6000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные реактивные гранатомёты',
        'wpn_name_comment':'Прицел, крепления, ствол. Для различных типов гранат. Масса: 6 кг (заряженный 9-12 кг) Дальность: 500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0004,
        'wpn_name_new':'Переносные реактивные гранатомёты новые',
        'wpn_name_mid':'Переносные реактивные гранатомёты устаревшие',
        'wpn_name_old':'Переносные реактивные гранатомёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Реактивные гранаты',
        'wpn_ammo_1_capacity':2,
        'wpn_ammo_1_expense':20,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные ракетные комплексы',
        'wpn_name_comment':'Пусковые установки управляемых ракет. Тепловизор, система наведения. Масса: 30 кг (с ракетой 60 кг)',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Переносные ракетные комплексы новые',
        'wpn_name_mid':'Переносные ракетные комплексы устаревшие',
        'wpn_name_old':'Переносные ракетные комплексы под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Управляемые ракеты',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Электромагнитные снайперские пушки',
        'wpn_name_comment':'Сверхпроводящий аккумулятор, соленоиды, метровый ствол. Вес: 20 кг. Прицельная дальность: 2000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Электромагнитные снайперские пушки серийные',
        'wpn_name_mid':'Электромагнитные снайперские пушки опытные',
        'wpn_name_old':'Электромагнитные снайперские пушки не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0008,
        'wpn_c':2,
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':1000,
        'wpn_ammo_1_expense':1000,
        # Аккумулятор весом в 4 кг.
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        'wpn_fuel_capacity':120,
        # Затраты энергии на выстрел (25% КПД)
        'wpn_fuel_consumption':0.120,
        'wpn_fuel_expense':1200,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Электролазерные пушки',
        'wpn_name_comment':'Лазер ионизирует воздух, молния идёт через электропроводящий канал. Вес: 20 кг. Прицельная дальность: 1000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Электролазерные пушки серийные',
        'wpn_name_mid':'Электролазерные пушки опытные',
        'wpn_name_old':'Электролазерные пушки не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0008,
        'wpn_c':2,
        # Аккумулятор весом в 4 кг.
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        'wpn_fuel_capacity':120,
        # Затраты энергии на выстрел (10% КПД)
        'wpn_fuel_consumption':0.120,
        'wpn_fuel_expense':1200,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Лёгкое стрелковое оружие',
        'wpn_name_comment':'Различные автоматические винтовки под унифицированный патрон 6x42. Вес: 3-5 кг. Прицельная дальность: 500 м',
        'wpn_troops_type':'СВ',
        'wpn_cost':2000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Автоматические винтовки новые',
        'wpn_name_mid':'Автоматические винтовки устаревшие',
        'wpn_name_old':'Автоматические винтовки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':5000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стрелково-гранатомётные комплексы',
        'wpn_name_comment':'Индивидуальное оружие, сочетание пулемёта и 30-мм гранатомёта. Вес: 8 кг. Прицельная дальность: 500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Стрелково-гранатомётные комплексы новые',
        'wpn_name_mid':'Стрелково-гранатомётные комплексы устаревшие',
        'wpn_name_old':'Стрелково-гранатомётные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        # Патронный короб и рукав плюс магазин гранатомёта — 12 кг.
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':10000,
        'wpn_ammo_2_name':'Выстрелы АГС',
        'wpn_ammo_2_capacity':10,
        'wpn_ammo_2_expense':200,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевая экипировка',
        'wpn_name_comment':'Разгрузка, прицелы, связь. СИБЗ: шлемы, защитные комбинезоны, пластины, химкостюмы. Вес: 10-20 кг.',
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
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        'wpn_fuel_capacity':12,
        # Сутки работы оборудования на 20 Ватт.
        'wpn_fuel_consumption':1.7,
        'wpn_fuel_expense':620,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Силовая броня',
        'wpn_name_comment':'Для сил специальных операций. Экзоскелеты, сервоприводы, штурмовые щиты. Масса: 100 кг; автономность 8 часов.',
        'wpn_troops_type':'СВ',
        'wpn_cost':600000,
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
        # Аккумулятор весом в 10 кг.
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        'wpn_fuel_capacity':300,
        # Скорость бега 50 км/ч, 10 киловатт.
        # Это 8.4 часа работы, или дальность в 420 км.
        'wpn_fuel_consumption':0.72,
        'wpn_fuel_expense':30000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Станковые 120-мм миномёты',
        'wpn_name_comment':'Пегасо-переносимый миномёт калибра 120-мм. Масса: 150 кг (50 кг станок). Дальность огня: 7000 м.',
        'wpn_troops_type':'АВ',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Станковые 120-мм миномёты новые',
        'wpn_name_mid':'Станковые 120-мм миномёты устаревшие',
        'wpn_name_old':'Станковые 120-мм миномёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Миномётные мины 120-мм',
        'wpn_ammo_1_capacity':30,
        'wpn_ammo_1_expense':3000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходные 120-мм гаубицы',
        'wpn_name_comment':'Гусеничные и колёсные САУ, батальонные/полковые. Масса: 15 тонн; калибр: 120-мм; дальность огня: 10 км.',
        'wpn_troops_type':'АВ',
        'wpn_cost':3000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Самоходные 120-мм гаубицы новые',
        'wpn_name_mid':'Самоходные 120-мм гаубицы устаревшие',
        'wpn_name_old':'Самоходные 120-мм гаубицы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        'wpn_ammo_2_name':'Снаряды 120-мм',
        'wpn_ammo_2_capacity':30,
        'wpn_ammo_2_expense':6000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Буксируемые 150-мм гаубицы',
        'wpn_name_comment':'Дивизионные пегасо-буксируемые орудия. Масса: 5 тонн; калибр: 150-мм; дальность огня: 30 км.',
        'wpn_troops_type':'АВ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Буксируемые 150-мм гаубицы новые',
        'wpn_name_mid':'Буксируемые 150-мм гаубицы устаревшие',
        'wpn_name_old':'Буксируемые 150-мм гаубицы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 150-мм',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':6000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивная 210-мм артиллерия',
        'wpn_name_comment':'РСЗО с десятью направляющими для ракет калибра 210-мм. Масса 15 тон; дальность огня 60 км.',
        'wpn_troops_type':'АВ',
        'wpn_cost':2000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Реактивная 210-мм артиллерия новая',
        'wpn_name_mid':'Реактивная 210-мм артиллерия устаревшая',
        'wpn_name_old':'Реактивная 210-мм артиллерия на списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_2_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_2_capacity':40,
        'wpn_ammo_2_expense':6000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиолокаторы дальнего обнаружения',
        'wpn_name_comment':'Надгоризонтные и загоризонтные, стационарные и плавучие РЛС. Дальность 3000-6000 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':200000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Дальние РЛС третьего поколения',
        'wpn_name_mid':'Дальние РЛС второго поколения',
        'wpn_name_old':'Дальние РЛС первого поколения',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиолокаторы ближнего обнаружения',
        'wpn_name_comment':'Мобильные РЛС сантиметрового, дециметрового и метрового диапазонов. Масса 30 тонн. Дальность 600 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':5000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Ближние РЛС новые',
        'wpn_name_mid':'Ближние РЛС устаревшие',
        'wpn_name_old':'Ближние РЛС под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Лазеры противоракетной обороны',
        'wpn_name_comment':'Стационарные лазерные пушки. Одноразовые, управляемые по кабелю. Масса около 60 тонн.',
        'wpn_troops_type':'РВ',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Лазеры противоракетной обороны новые',
        'wpn_name_mid':'Лазеры противоракетной обороны устаревшие',
        'wpn_name_old':'Лазеры противоракетной обороны не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        'wpn_ammo_1_name':'300-ТВт лазеры',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРК большой дальности',
        'wpn_name_comment':'Пусковые установки зенитных ракет. Масса 30 тонн; x4 ракеты по 2 тонны; радар с радиусом до 300 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Зенитные ракетные комплексы новые',
        'wpn_name_mid':'Зенитные ракетные комплексы устаревшие',
        'wpn_name_old':'Зенитные ракетные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_1_capacity':4,
        'wpn_ammo_1_expense':16,
        'wpn_ammo_2_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_2_capacity':1,
        'wpn_ammo_2_expense':1,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тактические ракетные комплексы',
        'wpn_name_comment':'Мобильные комплексы для запуска крылатых ракет с ядерными боеголовками.',
        'wpn_troops_type':'РВ',
        'wpn_cost':6000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Тактические ракетные комплексы новые',
        'wpn_name_mid':'Тактические ракетные комплексы устаревшие',
        'wpn_name_old':'Тактические ракетные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Тактические ядерные ракеты',
        'wpn_ammo_1_capacity':2,
        'wpn_ammo_1_expense':4,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стратегические ракетные комплексы',
        'wpn_name_comment':'Мобильные комплексы для запуска 50-тонных баллистических ракет с ядерными боеголовками.',
        'wpn_troops_type':'РВ',
        'wpn_cost':20000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Стратегические ракетные комплексы новые',
        'wpn_name_mid':'Стратегические ракетные комплексы устаревшие',
        'wpn_name_old':'Стратегические ракетные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Стратегические ядерные ракеты',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':100000,
        'wpn_fuel_consumption':200,
        'wpn_fuel_expense':2000000,
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
        'wpn_ammo_1_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_1_capacity':400,
        'wpn_ammo_1_expense':400,
        'wpn_ammo_2_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_2_capacity':100,
        'wpn_ammo_2_expense':100,
        'wpn_ammo_3_name':'Тактические ядерные ракеты',
        'wpn_ammo_3_capacity':100,
        'wpn_ammo_3_expense':100,
        'wpn_ammo_4_name':'Стратегические ядерные ракеты',
        'wpn_ammo_4_capacity':50,
        'wpn_ammo_4_expense':50,
        'wpn_ammo_5_name':'300-ТВт лазеры',
        'wpn_ammo_5_capacity':100,
        'wpn_ammo_5_expense':100,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Рапторы',
        'wpn_name_comment':'Десантные экранолёты. 500 тонн взлётного веса; 120 тонн груза; 800 км/ч скорость; атомная СУ.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':500000000,
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
        # Пятиствольная электромагнитная пушка.
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Ракеты воздух-воздух',
        'wpn_ammo_2_capacity':8,
        'wpn_ammo_2_expense':40,
        'wpn_ammo_3_name':'Тактические ядерные ракеты',
        'wpn_ammo_3_capacity':2,
        'wpn_ammo_3_expense':2,
        # Десять лазерных батарей активной защиты
        'wpn_ammo_4_name':'300-ГВт лазеры',
        'wpn_ammo_4_capacity':80,
        'wpn_ammo_4_expense':240,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Летающие танки',
        # https://ru.wikipedia.org/wiki/ЭКИП
        'wpn_name_comment':'Транспортные экранолёты. 50 тонн взлётного веса; 20 тонн груза; 800 км/ч скорость; реактивные двигатели.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':60000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Летающие танки новые',
        'wpn_name_mid':'Летающие танки устаревшие',
        'wpn_name_old':'Летающие танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Управляемые ракеты',
        'wpn_ammo_2_capacity':12,
        'wpn_ammo_2_expense':24,
        # Четыре лазерные батареи активной защиты
        'wpn_ammo_3_name':'300-ГВт лазеры',
        'wpn_ammo_3_capacity':32,
        'wpn_ammo_3_expense':96,
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        # На 1.5 часа полёта, или на 1200 км.
        'wpn_fuel_capacity':180000,
        'wpn_fuel_consumption':150,
        'wpn_fuel_expense':21600000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Многоцелевые истребители',
        # https://ru.wikipedia.org/wiki/МиГ-21
        'wpn_name_comment':'Фронтовые истребители и истребители-перехватчики. Масса: 6-8 тонн, 1-2 Маха скорость, до 1000 км дальность.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':40000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Истребители новые',
        'wpn_name_mid':'Истребители устаревшие',
        'wpn_name_old':'Истребители под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Ракеты воздух-воздух',
        'wpn_ammo_2_capacity':4,
        'wpn_ammo_2_expense':40,
        # Две лазерные батареи активной защиты
        'wpn_ammo_3_name':'300-ГВт лазеры',
        'wpn_ammo_3_capacity':16,
        'wpn_ammo_3_expense':48,
        'wpn_fuel_name':'Энергокристаллы (МДж)',
        # На 1000 км с крейсерской скоростью в 1000 км/час.
        'wpn_fuel_capacity':90000,
        'wpn_fuel_consumption':90,
        'wpn_fuel_expense':10800000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевые планеры',
        'wpn_name_comment':'Вооружены НАРами и управляемыми ракетами. Масса: 200 кг; скорость до 200 км/час; двигатель — пегас.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':200000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Боевые планеры новые',
        'wpn_name_mid':'Боевые планеры потрёпанные',
        'wpn_name_old':'Боевые планеры под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        # Масса вооружения около 100 кг.
        'wpn_ammo_1_name':'Реактивные гранаты',
        'wpn_ammo_1_capacity':24,
        'wpn_ammo_1_expense':120,
        'wpn_ammo_2_name':'Управляемые ракеты',
        'wpn_ammo_2_capacity':1,
        'wpn_ammo_2_expense':5,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Грузовые планеры',
        'wpn_name_comment':'Пегасо-носимая авиация с грузоподъёмностью в 200 кг. Масса: 50 кг; скорость до 200 км/час.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':20000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Грузовые планеры новые',
        'wpn_name_mid':'Грузовые планеры потрёпанные',
        'wpn_name_old':'Грузовые планеры под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Подводные ракетоносцы',
        'wpn_name_comment':'Водоизмещение: 10 000 тонн. Атомные силовые установки. 10 пусковых шахт, торпеды.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':3000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Подводные ракетоносцы новые',
        'wpn_name_mid':'Подводные ракетоносцы устаревшие',
        'wpn_name_old':'Подводные ракетоносцы под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Торпеды большой дальности',
        'wpn_ammo_1_capacity':2,
        'wpn_ammo_1_expense':8,
        'wpn_ammo_2_name':'Стратегические ядерные ракеты',
        'wpn_ammo_2_capacity':16,
        'wpn_ammo_2_expense':16,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ракетные крейсера',
        'wpn_name_comment':'Водоизмещение: 10 000 тонн. АСУ, воздушная каверна — скорость до 50 узлов. Ракетное и торпедное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':2000000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Ракетные крейсера новые',
        'wpn_name_mid':'Ракетные крейсера устаревшие',
        'wpn_name_old':'Ракетные крейсера под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Две пятиствольные 30-мм пушки
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':5000,
        # Две артиллерийские 120-мм установки
        'wpn_ammo_2_name':'Снаряды 120-мм',
        'wpn_ammo_2_capacity':1000,
        'wpn_ammo_2_expense':6000,
        # Два торпедных аппарата
        'wpn_ammo_3_name':'Торпеды большой дальности',
        'wpn_ammo_3_capacity':2,
        'wpn_ammo_3_expense':6,
        # Два реактивных бомбомёта
        'wpn_ammo_4_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_4_capacity':24,
        'wpn_ammo_4_expense':72,
        # Двенадцать лазерных батарей
        'wpn_ammo_5_name':'300-ГВт лазеры',
        'wpn_ammo_5_capacity':96,
        'wpn_ammo_5_expense':288,
        # 96 пусковых шахт:
        'wpn_ammo_6_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_6_capacity':36,
        'wpn_ammo_6_expense':36,
        'wpn_ammo_7_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_7_capacity':36,
        'wpn_ammo_7_expense':36,
        'wpn_ammo_8_name':'Тактические ядерные ракеты',
        'wpn_ammo_8_capacity':24,
        'wpn_ammo_8_expense':24,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Сторожевые корабли',
        'wpn_name_comment':'Водоизмещение: 2500 тонн. АСУ, воздушная каверна — скорость до 50 узлов. Ракеты и торпеды.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':500000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Сторожевые корабли новые',
        'wpn_name_mid':'Сторожевые корабли устаревшие',
        'wpn_name_old':'Сторожевые корабли под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Две пятиствольные 30-мм пушки
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':5000,
        # Артиллерийская 120-мм установка
        'wpn_ammo_2_name':'Снаряды 120-мм',
        'wpn_ammo_2_capacity':500,
        'wpn_ammo_2_expense':3000,
        # Два торпедных аппарата
        'wpn_ammo_3_name':'Торпеды большой дальности',
        'wpn_ammo_3_capacity':2,
        'wpn_ammo_3_expense':6,
        # Два реактивных бомбомёта
        'wpn_ammo_4_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_4_capacity':24,
        'wpn_ammo_4_expense':72,
        # Шесть лазерных батарей
        'wpn_ammo_5_name':'300-ГВт лазеры',
        'wpn_ammo_5_capacity':48,
        'wpn_ammo_5_expense':144,
        # Пусковые шахты зенитных ракет
        'wpn_ammo_6_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_6_capacity':36,
        'wpn_ammo_6_expense':36,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Вспомогательные суда',
        'wpn_name_comment':'Суда снабжения, войсковые транспорты и плавучие доки. Водоизмещение 10 000 тонн. Атомные силовые установки',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':200000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Вспомогательные суда новые',
        'wpn_name_mid':'Вспомогательные суда устаревшие',
        'wpn_name_old':'Вспомогательные суда под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Пара крупнокалиберных пулемётов
        'wpn_ammo_1_name':'Патроны 15x120',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        # Две лазерные батареи
        'wpn_ammo_5_name':'300-ГВт лазеры',
        'wpn_ammo_5_capacity':16,
        'wpn_ammo_5_expense':48,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патрульные катера',
        'wpn_name_comment':'Водоизмещение: 50 тонн. Маховики вместо двигателей, 30 узлов скорость. Ракетное и пушечное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':20000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Патрульные катера новые',
        'wpn_name_mid':'Патрульные катера устаревшие',
        'wpn_name_old':'Патрульные катера под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 15x120',
        'wpn_ammo_1_capacity':1000,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Управляемые ракеты',
        'wpn_ammo_2_capacity':8,
        'wpn_ammo_2_expense':24,
        'wpn_ammo_3_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':12,
        'wpn_ammo_4_name':'300-ГВт лазеры',
        'wpn_ammo_4_capacity':8,
        'wpn_ammo_4_expense':24,
        'wpn_fuel_name':'Маховики (МДж)',
        # 14 часов автономного плавания, или 700 км дальность.
        'wpn_fuel_capacity':80000,
        'wpn_fuel_consumption':114,
        'wpn_fuel_expense':2000000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Военные городки',
        'wpn_name_comment':'Базы для войсковых частей типа полк/бригада, 1500-5000 солдат.',
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
        'wpn_ammo_1_name':'Патроны 6x42',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':40000,
        'wpn_fuel_consumption':100,
        'wpn_fuel_expense':1000000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Грузовые машины',
        'wpn_name_comment':'Тягачи для перевозки прицепов и полуприцепов массой до 60 тонн. Для бездорожья, с бронированной кабиной.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':200000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Грузовые машины современные',
        'wpn_name_mid':'Грузовые машины старого типа',
        'wpn_name_old':'Грузовые машины устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Автоматические турели',
        'wpn_name_comment':'Неподвижные боевые роботы. Вооружены крупнокалиберным пулемётом и управляемыми ракетами. Масса 600 кг',
        'wpn_troops_type':'ИВ',
        'wpn_cost':300000,
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
        'wpn_ammo_1_name':'Патроны 15x120',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Патроны 6x42',
        'wpn_ammo_2_capacity':1000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':2,
        'wpn_ammo_3_expense':6,
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
        'wpn_name':'Противотанковые мины',
        'wpn_name_comment':'Контактные и направленного действия, с различными датчиками. Масса: 10-20 кг.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':500,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Противотанковые мины новые',
        'wpn_name_mid':'Противотанковые мины устаревшие',
        'wpn_name_old':'Противотанковые мины под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.20,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Противопехотные мины',
        'wpn_name_comment':'Контактные и направленного действия, с различными датчиками. Масса: 0.5-1 кг.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':50,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Противопехотные мины новые',
        'wpn_name_mid':'Противопехотные мины устаревшие',
        'wpn_name_old':'Противопехотные мины под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.20,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ядерные фугасы',
        'wpn_name_comment':'Для минирования инженерных сооружений, дорог и мостов. Масса: 200 кг; мощность взрыва 5-200 килотонн.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':500000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Ядерные фугасы новые',
        'wpn_name_mid':'Ядерные фугасы устаревшие',
        'wpn_name_old':'Ядерные фугасы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные боеголовки',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стреловидные пули',
        'wpn_name_comment':'Для электромагнитных снайперских пушек. Пуля: 10 г; нач.скорость 2500 м/с; энергия 30 000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00001,
        'wpn_name_new':'Стреловидные пули новые',
        'wpn_name_mid':'Стреловидные пули старого типа',
        'wpn_name_old':'Стреловидные пули неуместные',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0008,
        'wpn_c':2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны 6x42',
        'wpn_name_comment':'Для лёгкого стрелкового оружия. Патрон: 12 г; пуля: 4 г; нач.скорость 900 м/с; энергия 1400 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Патроны 6x42 новые',
        'wpn_name_mid':'Патроны 6x42 устаревшие',
        'wpn_name_old':'Патроны 6x42 под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны 15x120',
        'wpn_name_comment':'Для тяжёлых пулемётов. Патрон: 200 г; пуля: 65 г; нач.скорость 1000 м/с; энергия 32 000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':10,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Патроны 15x120 новые',
        'wpn_name_mid':'Патроны 15x120 устаревшие',
        'wpn_name_old':'Патроны 15x120 под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Снаряды 30x165',
        'wpn_name_comment':'Для автоматических пушек. Патрон: 840 г; снаряд: 400 г; нач.скорость 900 м/с; энергия 180 000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':100,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'Снаряды 30x165 новые',
        'wpn_name_mid':'Снаряды 30x165 устаревшие',
        'wpn_name_old':'Снаряды 30x165 под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Снаряды 120-мм',
        'wpn_name_comment':'Для танковых пушек и артиллерии, различные боеприпасы. Масса 20-30 кг. Дальность огня до 10 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':500,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.008,
        'wpn_name_new':'Снаряды 120-мм новые',
        'wpn_name_mid':'Снаряды 120-мм устаревшие',
        'wpn_name_old':'Снаряды 120-мм под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Снаряды 150-мм',
        'wpn_name_comment':'Для дивизионной артиллерии, различные боеприпасы. Масса 40-60 кг. Дальность огня до 30 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Снаряды 150-мм новые',
        'wpn_name_mid':'Снаряды 150-мм устаревшие',
        'wpn_name_old':'Снаряды 150-мм под списание',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Выстрелы АГС',
        'wpn_name_comment':'Для автоматических гранатомётных систем. Калибр 30x30 мм, патрон 350 грамм.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':50,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Выстрелы АГС новые',
        'wpn_name_mid':'Выстрелы АГС устаревшие',
        'wpn_name_old':'Выстрелы АГС под списание',
        'wpn_age_mid':10,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Миномётные мины 120-мм',
        'wpn_name_comment':'Для станковых миномётов и 120-мм артиллерии. Масса 15-25 кг',
        'wpn_troops_type':'ВПК',
        'wpn_cost':500,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'Миномётные мины 120-мм новые',
        'wpn_name_mid':'Миномётные мины 120-мм устаревшие',
        'wpn_name_old':'Миномётные мины 120-мм под списание',
        'wpn_age_mid':10,
        'wpn_age_old':40,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивные гранаты',
        'wpn_name_comment':'Для переносных гранатомётов. Осколочные, куммулятивные, термобарические. Масса 3-6 кг',
        'wpn_troops_type':'ВПК',
        'wpn_cost':500,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Реактивные гранаты новые',
        'wpn_name_mid':'Реактивные гранаты устаревшие',
        'wpn_name_old':'Реактивные гранаты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивные снаряды 210-мм',
        'wpn_name_comment':'Для реактивной артиллерии. Различные типы снарядов, масса 200 кг (50 кг БЧ) Дальность огня до 60 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':5000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.025,
        'wpn_name_new':'Реактивные снаряды 210-мм новые',
        'wpn_name_mid':'Реактивные снаряды 210-мм устаревшие',
        'wpn_name_old':'Реактивные снаряды 210-мм под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Управляемые ракеты',
        'wpn_name_comment':'Противотанковые ракеты управляемые с пусковой установки. Масса 30 кг. Дальность 10 км',
        'wpn_troops_type':'ВПК',
        'wpn_cost':25000,
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
        'wpn_name':'Ракеты воздух-воздух',
        'wpn_name_comment':'Управляемые авиационные ракеты. Масса: 500 кг (БЧ 50 кг) Дальность: 120 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':250000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Ракеты воздух-воздух новые',
        'wpn_name_mid':'Ракеты воздух-воздух устаревшие',
        'wpn_name_old':'Ракеты воздух-воздух под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты малой дальности',
        'wpn_name_comment':'Противовоздушные ракеты малого радиуса. Масса 60 кг; высота: 10 км; дальность: 20 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':50000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Зенитные ракеты малой дальности новые',
        'wpn_name_mid':'Зенитные ракеты малой дальности устаревшие',
        'wpn_name_old':'Зенитные ракеты малой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты средней дальности',
        'wpn_name_comment':'Противовоздушные ракеты среднего радиуса. Масса 500 кг; высота: 30; дальность 150 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':250000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'Зенитные ракеты средней дальности новые',
        'wpn_name_mid':'Зенитные ракеты средней дальности устаревшие',
        'wpn_name_old':'Зенитные ракеты средней дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты большой дальности',
        'wpn_name_comment':'Ракеты ПВО/ПРО большого радиуса с ядерной БЧ. Масса 2000 кг; высота: 250 км; дальность: 500 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':5000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Зенитные ракеты большой дальности новые',
        'wpn_name_mid':'Зенитные ракеты большой дальности устаревшие',
        'wpn_name_old':'Зенитные ракеты большой дальности под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        'wpn_ammo_1_name':'Ядерные боеголовки',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Торпеды большой дальности',
        'wpn_name_comment':'Торпеды с ядерными боеголовками. Масса: 4000 кг (200 кг БЧ); скорость 50 узлов; дальность 50 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Торпеды большой дальности новые',
        'wpn_name_mid':'Торпеды большой дальности устаревшие',
        'wpn_name_old':'Торпеды большой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные боеголовки',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тактические ядерные ракеты',
        'wpn_name_comment':'Крылатые ракеты с ядерными боеголовками. Масса 2000 кг. Дальность 2500 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0035,
        'wpn_name_new':'Тактические ядерные ракеты новые',
        'wpn_name_mid':'Тактические ядерные ракеты устаревшие',
        'wpn_name_old':'Тактические ядерные ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные боеголовки',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стратегические ядерные ракеты',
        'wpn_name_comment':'Баллистические ракеты с БЧ на шесть ядерных боеголовок. Масса 50 тонн. Дальность 10 000 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.012,
        'wpn_name_new':'Стратегические ядерные ракеты новые',
        'wpn_name_mid':'Стратегические ядерные ракеты устаревшие',
        'wpn_name_old':'Стратегические ядерные ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные боеголовки',
        'wpn_ammo_1_capacity':6,
        'wpn_ammo_1_expense':6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ядерные боеголовки',
        'wpn_name_comment':'Ядерные/термоядерные заряды изменяемой мощности, 5-500 килотонн. Масса 200 килограмм.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':5000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.04,
        'wpn_name_new':'Ядерные боеголовки новые',
        'wpn_name_mid':'Ядерные боеголовки устаревшие',
        'wpn_name_old':'Ядерные боеголовки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'300-ГВт лазеры',
        'wpn_name_comment':'Одноразовые кристаллы. Длительность импульса — одна микросекунда, энергия 3000 Дж, КПД 1%; «отдача» — 70 г тротила.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':10000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'3-ГВт лазеры новые',
        'wpn_name_mid':'3-ГВт лазеры устаревшие',
        'wpn_name_old':'3-ГВт лазеры не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'300-ТВт лазеры',
        'wpn_name_comment':'Одноразовые кристаллы. Длительность выстрела — одна микросекунда, энергия 3 МДж, КПД 1%; «отдача» — 70 кг тротила.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':10000000,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.02,
        'wpn_name_new':'3-ТВт лазеры новые',
        'wpn_name_mid':'3-ТВт лазеры устаревшие',
        'wpn_name_old':'3-ТВт лазеры не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0006,
        'wpn_c':1.8,
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

# Произведённое оружие:
metadict_equipment_create = {}
# Уцелевшее оружие:
metadict_equipment_alive = {}

# Исследование объединённого словаря. Создание баз данных оружия.
# Перебираем вложенные словари начиная с последнего:
for meta_key in sorted(metadict.keys(), reverse=True):
    # Временный словарь вооружений (за один год):
    dict_equipment_create = {}
    dict_equipment_alive = {}
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
        dict_equipment_create[metadict_wpn[wpn_key]['wpn_name']] = wpn_create
        dict_equipment_alive[metadict_wpn[wpn_key]['wpn_name']] = wpn_alive
    # Объединяем временные словари в базу данных:
    metadict_equipment_create[meta_key] = dict_equipment_create
    metadict_equipment_alive[meta_key] = dict_equipment_alive

# Далее, вычисляем общее число вооружений на складах:
dict_equipment_all = {}
for wpn_key in sorted(metadict_wpn.keys()):
    equipment_all = 0
    for meta_key in sorted(metadict_equipment_alive.keys()):
        equipment_all = equipment_all + metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']]
    dict_equipment_all[metadict_wpn[wpn_key]['wpn_name']] = equipment_all


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
        if (metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']] != 0):
            if (metadict[meta_key]['age_real'] < metadict_wpn[wpn_key]['wpn_age_mid']):
                print(metadict_wpn[wpn_key]['wpn_name_new'],
                        ' (Создано: ',
                        # Обращение аж к двум словарям, одно вложено в другое.
                        metadict_equipment_create[meta_key][metadict_wpn[wpn_key]['wpn_name']], ')',
                        ' Уцелело: ',
                        metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']], sep='')
            if (metadict_wpn[wpn_key]['wpn_age_mid'] <= metadict[meta_key]['age_real'] <
                    metadict_wpn[wpn_key]['wpn_age_old']):
                print(metadict_wpn[wpn_key]['wpn_name_mid'],
                        ' (Создано: ',
                        metadict_equipment_create[meta_key][metadict_wpn[wpn_key]['wpn_name']], ')',
                        ' Уцелело: ',
                        metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']], sep='')
            if (metadict_wpn[wpn_key]['wpn_age_old'] <= metadict[meta_key]['age_real']):
                print(metadict_wpn[wpn_key]['wpn_name_old'],
                        ' (Создано: ',
                        metadict_equipment_create[meta_key][metadict_wpn[wpn_key]['wpn_name']], ')',
                        ' Уцелело: ',
                        metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']], sep='')
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


#-------------------------------------------------------------------------
# И наконец, суммируем всё вооружение, вычисляем отношение единиц оружия к числу солдат,
# потребность армии в боеприпасаха, а также суммарный бюджет на вооружения и бюджеты по видам войск:

budget_percent = 0
budget_troops_percent = 0
# База данных потребностей в боеприпасах:
ammunition_needs = {}
# Названия боеприпасов превращаем в ключи базы данных:
for wpn_key in sorted(metadict_wpn.keys()):
    if metadict_wpn[wpn_key].get('wpn_ammo_1_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_1_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_2_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_2_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_3_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_3_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_4_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_4_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_5_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_5_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_6_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_6_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_7_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_7_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_8_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_8_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_ammo_9_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_9_name']] = 0
    if metadict_wpn[wpn_key].get('wpn_fuel_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_fuel_name']] = 0
# База данных бюджета по видам войск:
# Создаётся рабочий словарь, обнуляются значения:
budget_troops_types = {}
budget_troops_types.update(dict_troops_types)
for troop_key in budget_troops_types:
    budget_troops_types[troop_key] = 0

# Перебор столбцов в базе данных оружия:
for wpn_key in sorted(metadict_wpn.keys()):
    equipment_all = 0
    # Затем перебор по годам:
    for meta_key in sorted(metadict_equipment_alive.keys()):
        equipment_all = equipment_all + metadict_equipment_alive[meta_key][metadict_wpn[wpn_key]['wpn_name']]
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
    # Считаем потребность в боеприпасах (максимум 9 видов оружия) и топливо:
    if metadict_wpn[wpn_key].get('wpn_ammo_1_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_1_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_1_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_1_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_2_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_2_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_2_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_2_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_3_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_3_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_3_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_3_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_4_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_4_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_4_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_4_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_5_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_5_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_5_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_5_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_6_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_6_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_6_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_6_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_7_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_7_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_7_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_7_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_8_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_8_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_8_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_8_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_ammo_9_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_9_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_ammo_9_name']] + \
                metadict_wpn[wpn_key]['wpn_ammo_9_expense'] * equipment_all
    if metadict_wpn[wpn_key].get('wpn_fuel_name'):
        ammunition_needs[metadict_wpn[wpn_key]['wpn_fuel_name']] = \
                ammunition_needs[metadict_wpn[wpn_key]['wpn_fuel_name']] + \
                metadict_wpn[wpn_key]['wpn_fuel_expense'] * equipment_all
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
print('        ---')

# Соотношение производства боеприпасов и потребности в них:
print('Боеприпасы на складах (на год войны):')
for ammo_key in sorted(ammunition_needs.keys()):
    # (ammo_key, 0) — значит, если нет ключа, брать ноль.
    print('   ', ammo_key, ' — ', dict_equipment_all.get(ammo_key, 0), ' (',
            round(dict_equipment_all.get(ammo_key, ammunition_needs[ammo_key]) / \
                    ammunition_needs[ammo_key] * 100), '%)', sep='')
