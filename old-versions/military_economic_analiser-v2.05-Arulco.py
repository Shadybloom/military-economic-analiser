#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Military economic analyser v2.05-Arulco
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
 
# Для примера возьмём Арулько, карликовое государство Южной Америки.
# http://jaggedalliance.wikia.com/wiki/Arulco
# http://fpaste.org/247523/77128143/
 
# Год начала отсчёта, принимаются любые целые числа:
YEAR_START = 1998
# До какого возраста исследовать популяцию:
AGE_END = 100
 
# Переменные геометрической прогрессии роста населения:
# Численность населения в год начала отсчёта:
POPULATION = 60000
# Уровень рождаемости (например: 0.03 значит 3%
# или 30 новорожденных на 1000 населения в год):
FERTILITY_RATE = 0.02
# Уровень смертности, аналогично:
MORTALITY_RATE = 0.015
 
# Переменные для расчёта военной экономики:
# ВВП на душу населения:
# https://ru.wikipedia.org/wiki/Список_стран_по_ВВП_(ППС)_на_душу_населения
GDP_RATE = 4000
# Годовой рост ВВП (без инфляции):
# Для примера, данные по росту ВВП США 1970-2013 годы:
# http://www.be5.biz/makroekonomika/gdp/gdp_usa.html
# За период в 43 года средний рост ВВП был равен:
# 1075.9*x^(43-1)=3580 x=1.029 (2.9%)
GDP_GROWTH = 0.01
# Доля военного бюджета в ВВП страны. В США, например 3.5%,
# В Германии конца второй мировой военный бюджет доходил до 60% ВВП.
GDP_ARMY = 0.25
 
# Далее идут переменные для распределения Гомпертца-Мейкхама:
# http://dic.academic.ru/dic.nsf/ruwiki/923652
# Можно ориентироваться на исследование популяции людей 20-го века:
# "Parametric models for life insurance mortality data: gompertz's law over time"
# Компонент Мейкхама, независимый от возраста риск:
COMPONENT_A = 0.002
# Коэффициент b:
COEFFICIENT_B = 0.000350
# Коэффициент c:
COEFFICIENT_C = 1.08
 
# Распределение полов.
MALE_NAME = 'Мужчины'
MALE_PERCENT = 0.5
FEMALE_NAME = 'Женщины'
FEMALE_PERCENT = 0.5
 
# Армия (или профессия):
# Процент рекрутов: 0.25 — отборные; 0.25-0.5 — середнячки;
# 0.5-0.75 — кривые, косые; 0.75+ — глухие, слепые, убогие умом.
prof_percent = 0.75
# Профессиональный риск, изменение компонента Мейкхама:
# (0.01 = 1% риск смерти каждый год)
prof_hazard = 0.01
# Призывники обоих полов? 0 - нет; 1 - да
prof_male_switch = 1
prof_female_switch = 0
# Возраст призыва:
prof_age_apprentice = 18
# Возраст перехода в резервисты:
prof_age_expert = 22
# Возраст отставки:
prof_age_retiree = 60
prof_name_apprentice = 'Солдаты'
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
        'ВПК':0,
        # Сухопутные войска:
        'СВ':0.6,
        # Военно-воздушные войска:
        'ВВС':0.2,
        # Войска противовоздушной обороны:
        'ПВО':0.2,
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

# Создаётся объединённый словарь — строки массива.
metadict_wpn = {}

# Выбирается первый из ключей — номер столбца.
dict_wpn_key = 0
dict_wpn = {
        'wpn_name':'Т-64А',
        # http://vignette3.wikia.nocookie.net/jaggedalliance/images/3/36/Ja2_tank.jpg
        'wpn_name_comment':'Основной боевой танк СССР, выпуск 1970-х годов, местная модернизация. Масса: 40 тонн. Запас хода: 500 км.',
        # Принадлежность к виду войск:
        'wpn_troops_type':'СВ',
        # Цена на мировом рынке оружия или стоимость производства:
        # Для примера, «Бредли» стоит около 3.166 млн долларов:
        # http://www.globalsecurity.org/military/systems/ground/m2-specs.htm
        'wpn_cost':1000000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        # Доля затрат на данный вид оружия в военном бюджете:
        # Департамент обороны США тратит 19% бюджета на все закупки:
        # https://upload.wikimedia.org/wikipedia/commons/6/67/US_DOD_budget_2014_RUS.png
        'wpn_budget':0.03,
        'wpn_name_new':'Т-64А модернизированные',
        'wpn_name_mid':'Т-64А старой серии',
        'wpn_name_old':'Т-64 устаревшие',
        # Возраст потрёпанности:
        'wpn_age_mid':20,
        # Возраст старости:
        'wpn_age_old':30,
        # Переменные распределения Гомпертца-Мейкхама для оружия:
        # Строка 'wpn_a':0.05 значит 5% вероятность потери в год.
        # wpn_b и wpn_c корректируют вероятность по возрасту оружия,
        # Чем выше эти параметры, тем быстрее растут потери.
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Вооружение техники №1 (125-мм пушка):
        'wpn_ammo_1_name':'Снаряды 125-мм ОФС',
        # Один боекомплект:
        'wpn_ammo_1_capacity':37,
        # Максимум расхода боеприпасов в год:
        'wpn_ammo_1_expense':370,
        # Вооружение техники №2 (крупнокалиберный пулемёт):
        'wpn_ammo_2_name':'Патроны 12.7x108',
        'wpn_ammo_2_capacity':500,
        'wpn_ammo_2_expense':5000,
        # Вооружение техники №3 (малокалиберный пулемёт):
        'wpn_ammo_3_name':'Патроны 7.62x54',
        'wpn_ammo_3_capacity':2000,
        'wpn_ammo_3_expense':10000,
        # Топливо/источник энергии (дизельное топливо):
        'wpn_fuel_name':'Дизельное топливо (литры)',
        # Разовый запас топлива/энергии:
        'wpn_fuel_capacity':1000,
        # Расход топлива на километр (максимум):
        # 2 литра на километр, скорость 40 км/час.
        'wpn_fuel_consumption':2,
        # Годовой расход топлива (на 10 000 км):
        'wpn_fuel_expense':20000,
        }
# Данные записываются в общий словарь, как столбец двумерного массива.
metadict_wpn[dict_wpn_key] = dict_wpn

# Переход на новый столбец:
dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Humvee',
        'wpn_name_comment':'Американский армейский вездеход, производства 1990-х годов. Масса: 4.6 тонны. Запас хода: 500 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.01,
        'wpn_name_new':'Humvee новейшие',
        'wpn_name_mid':'Humvee старой серии',
        'wpn_name_old':'Внедорожники устаревшие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 12.7x108',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':5000,
        'wpn_fuel_name':'Дизельное топливо (литры)',
        'wpn_fuel_capacity':100,
        'wpn_fuel_consumption':0.2,
        'wpn_fuel_expense':2000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Eurocopter Dauphin',
        # http://vignette1.wikia.nocookie.net/jaggedalliance/images/0/08/Helicopter.jpeg
        'wpn_name_comment':'Гражданские вертолёты производства 1980-х. 12 пассажиров, или 1200 кг груза. Максимум дальности: 850 км.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':6000000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.06,
        'wpn_name_new':'Eurocopter Dauphin новейшие',
        'wpn_name_mid':'Eurocopter Dauphin старой серии',
        'wpn_name_old':'Транспортные вертолёты устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_fuel_name':'Дизельное топливо (литры)',
        'wpn_fuel_capacity':1100,
        'wpn_fuel_consumption':1.3,
        'wpn_fuel_expense':11000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стационарные ЗРК',
        # https://en.wikipedia.org/wiki/Rapier_missile
        'wpn_name_comment':'Пусковые установки для ракет Rapier 1980-х годов. Масса: 10 тонн. Четыре ракеты. Дальность захвата цели: 11 км.',
        'wpn_troops_type':'ПВО',
        'wpn_cost':2000000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.08,
        'wpn_name_new':'Стационарные ЗРК новые',
        'wpn_name_mid':'Стационарные ЗРК устаревшие',
        'wpn_name_old':'Стационарные ЗРК под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Зенитные ракеты Rapier',
        'wpn_ammo_1_capacity':4,
        'wpn_ammo_1_expense':8,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'АК74',
        'wpn_name_comment':'Автомат Калашникова 1970-х годов, под патрон 5.45x39. Масса: 3.3 кг. Прицельная дальность: 500 метров.',
        'wpn_troops_type':'СВ',
        'wpn_cost':300,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.005,
        'wpn_name_new':'АК74 новые',
        'wpn_name_mid':'АК74 старые',
        'wpn_name_old':'АК74 клинящие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 5.45x39',
        'wpn_ammo_1_capacity':450,
        'wpn_ammo_1_expense':1350,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ПКМ',
        'wpn_name_comment':'Пулемёт Калашникова 1970-х годов, под патрон 7.62x54. Масса: 7.5 кг. Прицельная дальность: 1500 метров.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1500,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.005,
        'wpn_name_new':'ПКМ новые',
        'wpn_name_mid':'ПКМ старые',
        'wpn_name_old':'ПКМ клинящие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 7.62x54',
        'wpn_ammo_1_capacity':600,
        'wpn_ammo_1_expense':1800,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'M224',
        'wpn_name_comment':'Миномёты американской армии 1980-х годов, для мин калибра 60-мм. Масса: 22 кг. Дальность огня: 3500 метров.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.002,
        'wpn_name_new':'M224 новые.',
        'wpn_name_mid':'M224 старые.',
        'wpn_name_old':'Миномёты устаревшие.',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Миномётные мины 60-мм',
        'wpn_ammo_1_capacity':30,
        'wpn_ammo_1_expense':300,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'СИБЗ',
        'wpn_name_comment':'Противоосколочные комбинезоны, бронежилеты, каски, пластины. Масса 10-20 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':5000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.02,
        'wpn_name_new':'Бронежилеты новые.',
        'wpn_name_mid':'Бронежилеты поношенные.',
        'wpn_name_old':'Бронежилеты под списание.',
        'wpn_age_mid':4,
        'wpn_age_old':8,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Дизельное топливо (литры)',
        'wpn_name_comment':'Топливо танков, внедорожников и вертолётов. Теплота сгорания: 42 МДж/кг. Плотность: 0.8 кг/литр',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.01,
        'wpn_name_new':'Дизельное топливо свежее.',
        'wpn_name_mid':'Дизельное топливо старых запасов.',
        'wpn_name_old':'Дизельное топливо просроченное.',
        'wpn_age_mid':1,
        'wpn_age_old':2,
        'wpn_a':0.2,
        'wpn_b':0.002,
        'wpn_c':3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны 5.45x39',
        # Формула кинетической энергии: E=(m*V^2)/2
        # Например: (0.0037*840^2)/2=1305
        'wpn_name_comment':'Для АК-74. Масса патрона: 11 грамм. Масса пули: 3.7 г. Начальная скорость: 840 м/с. Дульная энергия: 1305 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':0.05,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.003,
        'wpn_name_new':'Патроны 5.45x39 новые.',
        'wpn_name_mid':'Патроны 5.45x39 в старых цинках.',
        'wpn_name_old':'Патроны 5.45x39 несуществующие.',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны 7.62x54',
        # Обычно масса патрона в три раза больше массы пули.
        'wpn_name_comment':'Для ПК. Масса патрона: 35 грамм. Масса пули: 12 г. Начальная скорость: 770 м/с. Дульная энергия: 3500 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':0.3,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.005,
        'wpn_name_new':'Патроны 7.62x54 новые.',
        'wpn_name_mid':'Патроны 7.62x54 в старых цинках.',
        'wpn_name_old':'Патроны 7.62x54 просроченные.',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Патроны 12.7x108',
        'wpn_name_comment':'Для НСВ. Масса патрона: 145 грамм. Масса пули: 48 г. Начальная скорость: 820 м/с. Дульная энергия: 16 000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.002,
        'wpn_name_new':'Патроны 12.7x108 новые.',
        'wpn_name_mid':'Патроны 12.7x108 в старых цинках.',
        'wpn_name_old':'Патроны 12.7x108 просроченные.',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Снаряды 125-мм ОФС',
        'wpn_name_comment':'Осколочно-фугасные. Масса выстрела: 33 кг. Масса снаряда: 23 кг. Начальная скорость: 760 м/с.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':150,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.005,
        'wpn_name_new':'Снаряды 125-мм ОФС новые.',
        'wpn_name_mid':'Снаряды 125-мм ОФС старые.',
        'wpn_name_old':'Снаряды 125-мм ОФС просроченные.',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Миномётные мины 60-мм',
        # Радиус поражения осколками: 
        # http://www.saper.etel.ru/mines-2/razlet-osk.html
        'wpn_name_comment':'Осколочно-фугасные. Масса мины: 1.5 кг. Радиус сплошного поражения: 20 метров.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.005,
        'wpn_name_new':'Миномётные мины 60-мм новые.',
        'wpn_name_mid':'Миномётные мины 60-мм старые.',
        'wpn_name_old':'Миномётные мины 60-мм просроченные.',
        'wpn_age_mid':20,
        'wpn_age_old':40,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты Rapier',
        'wpn_name_comment':'Масса ракеты: 45 кг. Скорость полёта: 2.5 Маха. Радиус поражения: 6.8 км. Высота цели: 3 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20000,
        'wpn_cost_currency':'Доллары США 1998 года.',
        'wpn_budget':0.02,
        'wpn_name_new':'Зенитные ракеты Rapier новые.',
        'wpn_name_mid':'Зенитные ракеты Rapier старые.',
        'wpn_name_old':'Зенитные ракеты Rapier просроченные.',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
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
