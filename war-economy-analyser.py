#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# Опции:

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
GDP_ARMY = 0.2

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
prof_age_retiree = 40
prof_name_apprentice = 'Срочники'
prof_name_expert = 'Резервисты'
prof_name_retiree = 'Отставники'


#-------------------------------------------------------------------------
# Список видов войск. Используется базой данных военной техники,
# Смотри параметр 'wpn_troops_type'.

# Для замены хорошо подойдут регулярные выражения, например в Vim'е:
# %s/'РВ'/'РВСН'/g — подправит всю базу данных. Кавычки важны.
dict_troops_types = {
        # Формат:
        # 'Вид_войск':процент,
        # Военно-промышленный комплекс (боеприпасы):
        'ВПК':1,
        # Сухопутные войска:
        'СВ':0.5,
        # Ракетные войска и дальняя ПВО:
        'РВ':0.1,
        # Военно-воздушные войска:
        'ВВС':0.15,
        # Военно-морской флот:
        'ВМФ':0.1,
        # Инженерные войска:
        'ИВ':0.15,
        }


#-------------------------------------------------------------------------
# База данных оружия. Двумерный массив.

# Дополняется блоками, без ограничений и очень легко. Пользуйтесь этим.
# Пожалуйста, пишите в строке 'wpn_name_comment' краткое описание оружия,
# а в строке 'wpn_cost_currency' точно указывайте валюту и год.
# История скажет вам спасибо.

# Для поиска данных можно использовать списки оружия из википедии, например:
    # https://ru.wikipedia.org/wiki/Список_оружия_и_военной_техники_сухопутных_войск_Российской_Федерации
    # https://en.wikipedia.org/wiki/Equipment_of_the_United_States_Armed_Forces
# Как ориентир, производство оружия во время Второй мировой войны:
    # https://ru.wikipedia.org/wiki/Военное_производство_во_время_Второй_мировой_войны
    # https://ru.wikipedia.org/wiki/Производство_бронетехники_в_СССР_во_время_Второй_мировой_войны
# Структура армий различный стран и периодов (кратко, pdf, en, wargame):
    # http://www.fireandfury.com/extra/ordersofbattle.shtml#CW
# Характеристики техники (кратко, неточно, en, wargame):
    # http://wargame-series.wikia.com/wiki/USSR
    # http://wargame-series.wikia.com/wiki/United_States
# Штаты частей и подразделений армии СССР (1970-1990 годы, подробно):
    # http://yv-gontar.io.ua/s204359/shtaty_tankovyh_motostrelkovyh_polkov_otdelnyh_batalonov_i_parashyutno-desantnyh_polkov
    # http://yv-gontar.io.ua/s204353/shtaty_artillerii_suhoputnyh_voysk_i_vdv
    # http://yv-gontar.io.ua/s204347/shtaty_pvo_msp_i_tp_sovetskoy_armii
# Вооружённые силы России, организация, штаты, вооружение (2015 год, подробно, но с ошибками):
    # http://www.milkavkaz.net/2015/12/vooruzhjonnye-sily-rossii.html
# Взгляды командования сухопутных войск США на реорганизацию боевых бригад (2016 год):
    # http://pentagonus.ru/publ/vzgljady_komandovanija_sukhoputnykh_vojsk_ssha_na_reorganizaciju_boevykh_brigad_2016/3-1-0-2675
# Военный бюджет США, закупки техники (2016 год):
    # http://pentagonus.ru/publ/proekt_voennogo_bjudzheta_ssha_na_2016_finansovyj_god_2015/8-1-0-2631
# Стоимость оружия (неточно, упрощённо, начало 2000-х):
    # http://monster-igstab.livejournal.com/42346.html
# И сравнение армий современных государств (en):
    # http://www.globalfirepower.com/countries-listing.asp

# Эквестрийские биты = доллары США 2015 года.

# Создаётся объединённый словарь — строки массива.
metadict_wpn = {}

# Выбирается первый из ключей — номер столбца.
dict_wpn_key = 0
dict_wpn = {
        'wpn_name':'Бронетранспортёры',
        # https://ru.wikipedia.org/wiki/БТР-70
        'wpn_name_comment':'10-тонные колёсные и гусеничные БТР, вооружены пулемётом и АГС. Десант: 10 солдат; экипаж — двое.',
        # Принадлежность к виду войск:
        'wpn_troops_type':'СВ',
        # Цена на мировом рынке оружия или стоимость производства:
        # Для примера, «Бредли» стоит около 3.166 млн долларов:
        # http://www.globalsecurity.org/military/systems/ground/m2-specs.htm
        'wpn_cost':1000000,
        'wpn_cost_currency':'Эквестрийские биты',
        # Стоимость технического обслуживания в год, доля от стоимости машины:
        'wpn_maintenance':0.01,
        # Доля затрат на данный вид оружия в военном бюджете:
        # Департамент обороны США тратит 19% бюджета на все закупки:
        # https://upload.wikimedia.org/wikipedia/commons/6/67/US_DOD_budget_2014_RUS.png
        'wpn_budget':0.006,
        'wpn_name_new':'Бронетранспортёры новые',
        'wpn_name_mid':'Бронетранспортёры устаревшие',
        'wpn_name_old':'Бронетранспортёры под списание',
        # Возраст потрёпанности:
        'wpn_age_mid':10,
        # Возраст старости:
        'wpn_age_old':20,
        # Переменные распределения Гомпертца-Мейкхама для оружия:
        # Строка 'wpn_a':0.03 значит 3% вероятность потери в год.
        # wpn_b и wpn_c корректируют вероятность по возрасту оружия,
        # Чем выше эти параметры, тем быстрее растут потери.
        'wpn_a':0.03,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Вооружение техники №1 (крупнокалиберный пулемёт):
        'wpn_ammo_1_name':'Патроны 15x120',
        # Один боекомплект:
        'wpn_ammo_1_capacity':500,
        # Максимум расхода боеприпасов в год:
        'wpn_ammo_1_expense':10000,
        # Вооружение техники №2 (малокалиберный пулемёт):
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        # Вооружение техники №3 (автоматический гранатомёт):
        'wpn_ammo_3_name':'Выстрелы АГС',
        'wpn_ammo_3_capacity':400,
        'wpn_ammo_3_expense':1200,
        # Топливо/источник энергии (супермаховик 10 МДж/кг):
        'wpn_fuel_name':'Маховики (МДж)',
        # Разовый запас топлива/энергии, 1-тонный маховик:
        'wpn_fuel_capacity':10000,
        # Расход топлива на километр (максимум):
        # 200 квт мощность, скорость 30 км/час по бездорожью.
        'wpn_fuel_consumption':25,
        # Годовой расход топлива (на 10 000 км, ресурс ходовой):
        'wpn_fuel_expense':250000,
        }
# Данные записываются в общий словарь, как столбец двумерного массива.
metadict_wpn[dict_wpn_key] = dict_wpn

# Переход на новый столбец:
dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевые машины десанта',
        # https://ru.wikipedia.org/wiki/БМД-2
        'wpn_name_comment':'10-тонные гусеничные машины. Вооружены 30-мм автопушкой и ПТУРС. Десант — 9 солдат; экипаж — трое.',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Боевые машины десанта новые',
        'wpn_name_mid':'Боевые машины десанта устаревшие',
        'wpn_name_old':'Лёгкие плавающие танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':2500,
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевые машины пехоты',
        'wpn_name_comment':'30-тонные гусеничные машины. Вооружены 30-мм автопушкой и ПТУРС. Десант — 9 солдат; экипаж — трое.',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Боевые машины пехоты новые',
        'wpn_name_mid':'Боевые машины пехоты устаревшие',
        'wpn_name_old':'Средние танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':2500,
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Основные боевые танки',
        'wpn_name_comment':'Гусеничные машины массой в 50 тонн. 120-мм пушка, радар, активная защита. Трое членов экипажа.',
        'wpn_troops_type':'СВ',
        'wpn_cost':6000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.008,
        'wpn_name_new':'Основные боевые танки новые',
        'wpn_name_mid':'Основные боевые танки старой серии',
        'wpn_name_old':'Тяжёлые штурмовые танки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.03,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # 120-мм орудие:
        'wpn_ammo_1_name':'Снаряды 120-мм',
        'wpn_ammo_1_capacity':40,
        'wpn_ammo_1_expense':400,
        # Спаренный пулемёт:
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        # Башенный крупнокалиберный пулемёт:
        'wpn_ammo_3_name':'Патроны 15x120',
        'wpn_ammo_3_capacity':250,
        'wpn_ammo_3_expense':10000,
        # Два электролазера активной защиты:
        'wpn_ammo_4_name':'Спарк-батареи',
        'wpn_ammo_4_capacity':200,
        'wpn_ammo_4_expense':2000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':40000,
        'wpn_fuel_consumption':100,
        'wpn_fuel_expense':1000000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРПК малой дальности',
        # https://ru.wikipedia.org/wiki/Тунгуска_(зенитный_ракетно-пушечный_комплекс)
        'wpn_name_comment':'Зенитные ракетно-пушечные комплексы. 2 пушки, 8 ракет. Масса: 30 тонн. Дальность огня: 10 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'ЗРПК малой дальности новые',
        'wpn_name_mid':'ЗРПК малой дальности устаревшие',
        'wpn_name_old':'Зенитные установки под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Две скорострельные пушки:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':20000,
        # Восемь контейнеров зенитных ракет:
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':8,
        'wpn_ammo_2_expense':24,
        # Два электролазера активной защиты:
        'wpn_ammo_3_name':'Спарк-батареи',
        'wpn_ammo_3_capacity':200,
        'wpn_ammo_3_expense':2000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРК средней дальности',
        # https://ru.wikipedia.org/wiki/Бук_(зенитный_ракетный_комплекс)
        'wpn_name_comment':'Пусковые установки зенитных ракет средней дальности. Масса: 30 тонн. 4 ракеты. Дальность огня: 50 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'ЗРК средней дальности новые',
        'wpn_name_mid':'ЗРК средней дальности устаревшие',
        'wpn_name_old':'Зенитные орудия под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Четыре контейнера зенитных ракет:
        'wpn_ammo_1_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_1_capacity':4,
        'wpn_ammo_1_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Штурмовые роботы',
        # https://ru.wikipedia.org/wiki/Wiesel
        'wpn_name_comment':'Роботизированные танкетки. Вооружены крупнокалиберным пулемётом и управляемыми ракетами. Масса: 2 тонны.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Штурмовые роботы новые',
        'wpn_name_mid':'Штурмовые роботы устаревшие',
        'wpn_name_old':'Самоходные ПТРК на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        # Оружие с боеприпасами весит 400 кг.
        'wpn_ammo_1_name':'Патроны 15x120',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':12,
        # Вес маховика — 200 кг.
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':2000,
        # 30 кВт мощность, скорость 30 км/час.
        'wpn_fuel_consumption':3.5,
        'wpn_fuel_expense':28000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Сторожевые роботы',
        'wpn_name_comment':'Летающие машины, мультикоптеры. Вооружены пулемётом и АГС. Радиус действия: 60 км; вес 200 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':500000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Сторожевые роботы новые',
        'wpn_name_mid':'Сторожевые роботы устаревшие',
        'wpn_name_old':'Сторожевые роботы не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        # Оружие с боеприпасами весит 60 кг.
        'wpn_ammo_1_name':'Патроны 6x48',
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
        # https://ru.wikipedia.org/wiki/IAI_Searcher
        'wpn_name_comment':'Тактические разведывательные БПЛА. Радиус действия: 250 км; вес 200 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':500000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Роботы-разведчики новые',
        'wpn_name_mid':'Роботы-разведчики устаревшие',
        'wpn_name_old':'Роботы-разведчики на списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.2,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        # Вес маховика — 60 кг.
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':600,
        # Скорость до 50 м/с, 30 киловатт. Дальность 500 км.
        'wpn_fuel_consumption':0.8,
        'wpn_fuel_expense':64000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Станковые 120-мм миномёты',
        'wpn_name_comment':'Пегасо-переносимый миномёт калибра 120-мм. Масса: 150 кг (50 кг станок). Дальность огня: 5 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00002,
        'wpn_name_new':'Станковые 120-мм миномёты новые',
        'wpn_name_mid':'Станковые 120-мм миномёты устаревшие',
        'wpn_name_old':'Станковые 120-мм миномёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Миномётные мины 120-мм',
        'wpn_ammo_1_capacity':30,
        'wpn_ammo_1_expense':1500,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходные 120-мм гаубицы',
        # https://ru.wikipedia.org/wiki/2С23
        'wpn_name_comment':'Гусеничные и колёсные САУ, батальонные/полковые. Масса: 15 тонн; калибр: 120-мм; дальность огня: 10 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':2000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0011,
        'wpn_name_new':'Самоходные 120-мм гаубицы новые',
        'wpn_name_mid':'Самоходные 120-мм гаубицы устаревшие',
        'wpn_name_old':'Буксируемые 120-мм гаубицы на хранении',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        'wpn_ammo_2_name':'Снаряды 120-мм',
        'wpn_ammo_2_capacity':30,
        'wpn_ammo_2_expense':3000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Буксируемые 150-мм гаубицы',
        # https://ru.wikipedia.org/wiki/2С3
        'wpn_name_comment':'Дивизионные облегчённые орудия. Масса: 5 тонн; калибр: 150-мм; дальность огня: 20 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':500000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Буксируемые 150-мм гаубицы новые',
        'wpn_name_mid':'Буксируемые 150-мм гаубицы устаревшие',
        'wpn_name_old':'Буксируемые 150-мм гаубицы на хранении',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 150-мм',
        'wpn_ammo_1_capacity':50,
        'wpn_ammo_1_expense':3000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходные 150-мм гаубицы',
        # https://ru.wikipedia.org/wiki/2С3
        'wpn_name_comment':'Дивизионные орудия. Масса: 30 тонн; калибр: 150-мм; дальность огня: 20 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':4000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0012,
        'wpn_name_new':'Самоходные 150-мм гаубицы новые',
        'wpn_name_mid':'Самоходные 150-мм гаубицы устаревшие',
        'wpn_name_old':'Самоходные 150-мм гаубицы на хранении',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Снаряды 150-мм',
        'wpn_ammo_1_capacity':50,
        'wpn_ammo_1_expense':3000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Реактивная 210-мм артиллерия',
        # https://ru.wikipedia.org/wiki/Ураган_(РСЗО)
        'wpn_name_comment':'РСЗО с 16 направляющими для ракет калибра 210-мм. Масса 15 тон; дальность огня 40 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Реактивная 210-мм артиллерия новая',
        'wpn_name_mid':'Реактивная 210-мм артиллерия устаревшая',
        'wpn_name_old':'Реактивная 210-мм артиллерия под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_1_capacity':16,
        'wpn_ammo_1_expense':2400,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Тактические ракетные комплексы',
        # https://ru.wikipedia.org/wiki/Точка_(тактический_ракетный_комплекс)
        'wpn_name_comment':'Мобильные комплексы для запуска баллистических ракет. Масса 15 тонн; дальность 120 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0003,
        'wpn_name_new':'Тактические ракетные комплексы новые',
        'wpn_name_mid':'Тактические ракетные комплексы устаревшие',
        'wpn_name_old':'Тактические ракетные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Баллистические ракеты',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Оперативно-тактические ракетные комплексы',
        # https://ru.wikipedia.org/wiki/Ока_(ОТРК)
        'wpn_name_comment':'Мобильные комплексы для запуска баллистических ракет. Масса 30 тонн; дальность 500 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':5000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0012,
        'wpn_name_new':'Оперативно-тактические ракетные комплексы новые',
        'wpn_name_mid':'Оперативно-тактические ракетные комплексы устаревшие',
        'wpn_name_old':'Оперативно-тактические ракетные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Баллистические ракеты',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Станковые крупнокалиберные пулемёты',
        # https://ru.wikipedia.org/wiki/Крупнокалиберный_пулемёт_Владимирова
        'wpn_name_comment':'Пегасо-переносимый пулемёт калибра 15-мм. Масса: 100 кг (50 кг станок). Прицельная дальность: 1500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00005,
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
        # https://ru.wikipedia.org/wiki/АГС-17
        'wpn_name_comment':'Пегасо-переносимый АГС под гранаты калибра 30-мм. Масса: 50 кг. Прицельная дальность: 1500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00004,
        'wpn_name_new':'Станковые автоматические гранатомёты новые',
        'wpn_name_mid':'Станковые автоматические гранатомёты устаревшие',
        'wpn_name_old':'Станковые автоматические гранатомёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Выстрелы АГС',
        'wpn_ammo_1_capacity':90,
        'wpn_ammo_1_expense':540,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные противотанковые ракетные комплексы',
        # https://ru.wikipedia.org/wiki/Метис_(ПТРК)
        'wpn_name_comment':'Противотанковые управляемые ракеты. Станок, тепловизор, лазер наведения. Масса: 15 кг (с ракетой 22 кг)',
        'wpn_troops_type':'СВ',
        'wpn_cost':50000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Переносные ПТРК новые',
        'wpn_name_mid':'Переносные ПТРК устаревшие',
        'wpn_name_old':'Станковые безоткатные орудия под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Управляемые ракеты',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':8,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Электромагнитные снайперские пушки',
        # https://ru.wikipedia.org/wiki/Steyr_AMR_/_IWS_2000
        'wpn_name_comment':'Сверхпроводящий аккумулятор, соленоиды, охлаждение, метровый ствол. Вес: 20 кг. Прицельная дальность: 1000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':50000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00005,
        'wpn_name_new':'Электромагнитные снайперские пушки новые',
        'wpn_name_mid':'Электромагнитные снайперские пушки устаревшие',
        'wpn_name_old':'Крупнокалиберные снайперские пушки под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.001,
        'wpn_c':2,
        # 20 гр пули разгоняются до 1500 м/с, энергия выстрела 22.5 кДж.
        'wpn_ammo_1_name':'Стреловидные пули',
        'wpn_ammo_1_capacity':100,
        'wpn_ammo_1_expense':1000,
        # КПД около 55%, 40 кДж на выстрел.
        'wpn_ammo_2_name':'Спарк-батареи',
        'wpn_ammo_2_capacity':100,
        'wpn_ammo_2_expense':1000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Электролазерные пушки',
        'wpn_name_comment':'Лазер ионизирует воздух, молния идёт через электропроводящий канал. Вес: 20 кг. Прицельная дальность: 500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':50000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00004,
        'wpn_name_new':'Электролазерные пушки новые',
        'wpn_name_mid':'Электролазерные пушки устаревшие',
        'wpn_name_old':'Электролазерные пушки не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.001,
        'wpn_c':2,
        # Молния на 20 кДж, 50% КПД.
        'wpn_ammo_1_name':'Спарк-батареи',
        'wpn_ammo_1_capacity':100,
        'wpn_ammo_1_expense':1000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные реактивные гранатомёты',
        # https://ru.wikipedia.org/wiki/РПГ-29
        'wpn_name_comment':'Прицел, крепления, ствол. Для различных типов гранат. Масса: 6 кг (заряженный 9-12 кг) Дальность: 500 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':5000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Переносные реактивные гранатомёты новые',
        'wpn_name_mid':'Переносные реактивные гранатомёты устаревшие',
        'wpn_name_old':'Переносные реактивные гранатомёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Реактивные гранаты',
        'wpn_ammo_1_capacity':3,
        'wpn_ammo_1_expense':12,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стрелково-гранатомётные комплексы',
        'wpn_name_comment':'Индивидуальное оружие, сочетание пулемёта и 30-мм гранатомёта. Вес: 8 кг. Прицельная дальность: 1000 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':10000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0004,
        'wpn_name_new':'Стрелково-гранатомётные комплексы новые',
        'wpn_name_mid':'Стрелково-гранатомётные комплексы устаревшие',
        'wpn_name_old':'Стрелково-гранатомётные комплексы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        # Патронный короб и рукав плюс магазин гранатомёта — 12 кг.
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':450,
        'wpn_ammo_1_expense':5000,
        'wpn_ammo_2_name':'Выстрелы АГС',
        'wpn_ammo_2_capacity':10,
        'wpn_ammo_2_expense':200,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Единые пулемёты',
        'wpn_name_comment':'Пехотные пулемёты под унифицированный патрон 6x48. Вес: 6 кг. Прицельная дальность: 1000 м',
        'wpn_troops_type':'СВ',
        'wpn_cost':5000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Единые пулемёты новые',
        'wpn_name_mid':'Единые пулемёты устаревшие',
        'wpn_name_old':'Единые пулемёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Ресурс ствола около 15 000 выстрелов.
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':600,
        'wpn_ammo_1_expense':10000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Автоматические карабины',
        'wpn_name_comment':'Укороченные винтовки под унифицированный патрон 6x48. Вес: 5 кг. Прицельная дальность: 1000 м',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Автоматические карабины новые',
        'wpn_name_mid':'Автоматические карабины устаревшие',
        'wpn_name_old':'Автоматические карабины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Ресурс ствола около 10 000 выстрелов.
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':450,
        'wpn_ammo_1_expense':10000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Пистолеты-пулемёты',
        'wpn_name_comment':'Оружие тыловиков и экипажей боевых машин. Крепится на груди. Вес: 3 кг. Прицельная дальность: 50 м.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
        'wpn_name_new':'Пистолеты-пулемёты новые',
        'wpn_name_mid':'Пистолеты-пулемёты устаревшие',
        'wpn_name_old':'Пистолеты-пулемёты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        # Магазин на 50 патронов.
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':50,
        'wpn_ammo_1_expense':5000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевая экипировка',
        'wpn_name_comment':'Разгрузка, аптечка, ПНВ, связь. СИБЗ: шлем, защитный комбинезон, пластины, химкостюм. Вес: 21 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':20000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Боевая экипировка новая',
        'wpn_name_mid':'Боевая экипировка поношенная',
        'wpn_name_old':'Боевая экипировка под списание',
        'wpn_age_mid':6,
        'wpn_age_old':12,
        'wpn_a':0.03,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Повседневная экипировка',
        'wpn_name_comment':'Униформа, спальники и палатки; котелки и ножи; пехотные лопатки и фонарики; рации и рюкзаки. Вес: 22 кг.',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Повседневная экипировка новая',
        'wpn_name_mid':'Повседневная экипировка поношенная',
        'wpn_name_old':'Повседневная экипировка на хранении',
        'wpn_age_mid':3,
        'wpn_age_old':6,
        'wpn_a':0.03,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        # Сухие пайки на 14 дней боёв.
        'wpn_ammo_1_name':'Полевые рационы (суточные)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':14,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Силовая броня',
        'wpn_name_comment':'Для сил специальных операций. Экзоскелет, сервоприводы, штурмовой щит. Масса: 100 кг; автономность: 4 часа.',
        'wpn_troops_type':'СВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.008,
        'wpn_name_new':'Силовая броня современная',
        'wpn_name_mid':'Силовая броня устаревшая',
        'wpn_name_old':'Силовая броня не существующая',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.001,
        'wpn_c':2,
        # 10-кг супермаховик.
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':100,
        # 300 кг боец, бег 50 км/час, 10 ватт/кг, 50% КПД — 6 киловатт.
        # Маховика хватит на четыре часа бега, или дальность в 200 км.
        'wpn_fuel_consumption':0.5,
        'wpn_fuel_expense':5000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Переносные радиолокаторы',
        # ПСНР-5 "Кредо" (1РЛ133) - переносная станция наземной разведки
        # http://www.russianarms.ru/forum/index.php?topic=4581.0
        'wpn_name_comment':'Для войсковой разведки. Масса: 50 кг. Дальность обнаружения танка — 10 км; солдат — 5 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':100000,
        'wpn_maintenance':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0004,
        'wpn_name_new':'Переносные РЛС новые',
        'wpn_name_mid':'Переносные РЛС устаревшие',
        'wpn_name_old':'Переносные РЛС не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходные комплексы радиоразведки',
        # Р-381Т "Таран"
        # http://www.russianarms.ru/forum/index.php?topic=2664.0
        'wpn_name_comment':'Для войсковой разведки, радиопеленгаторы УКВ и КВ диапазонов. Масса — 15 тонн. Дальность — 40 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':2000000,
        'wpn_maintenance':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Самоходные комплексы РЭР новые',
        'wpn_name_mid':'Самоходные комплексы РЭР устаревшие',
        'wpn_name_old':'Самоходные комплексы РЭР не существующие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,        
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Самоходные комплексы радиоподавления',
        # Автоматизированные станции радиопомех Р-378Б
        # http://www.russianarms.ru/forum/index.php?topic=1393.0
        'wpn_name_comment':'Для рот РЭБ, станции обнаружения/подавления УКВ и КВ диапазонов. Масса — 15 тонн. Радиус — 20 км.',
        'wpn_troops_type':'СВ',
        'wpn_cost':3000000,
        'wpn_maintenance':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0008,
        'wpn_name_new':'Самоходные комплексы РЭБ новые',
        'wpn_name_mid':'Самоходные комплексы РЭБ устаревшие',
        'wpn_name_old':'Самоходные комплексы РЭБ не существующие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.03,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,        
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиолокаторы дальнего обнаружения',
        # https://ru.wikipedia.org/wiki/Дуга_(радиолокационная_станция)
        'wpn_name_comment':'Надгоризонтные и загоризонтные, стационарные и плавучие РЛС. Дальность 3000-6000 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':200000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0008,
        'wpn_name_new':'Дальние РЛС третьего поколения',
        'wpn_name_mid':'Дальние РЛС второго поколения',
        'wpn_name_old':'Дальние РЛС первого поколения',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиолокаторы ближнего обнаружения',
        # https://ru.wikipedia.org/wiki/П-18_(радиолокационная_станция)
        # https://ru.wikipedia.org/wiki/П-19
        'wpn_name_comment':'Мобильные РЛС сантиметрового, дециметрового и метрового диапазонов. Масса 30 тонн. Дальность 25-400 км.',
        'wpn_troops_type':'РВ',
        'wpn_cost':5000000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Ближние РЛС новые',
        'wpn_name_mid':'Ближние РЛС устаревшие',
        'wpn_name_old':'Ближние РЛС под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.03,
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
        'wpn_name_comment':'Сверхмощные электролазеры взрывного типа. Дистанционное управление, автомобильный прицеп. Масса 15 тонн.',
        'wpn_troops_type':'РВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Лазеры противоракетной обороны новые',
        'wpn_name_mid':'Лазеры противоракетной обороны устаревшие',
        'wpn_name_old':'Лазеры противоракетной обороны не существующие',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.01,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        # 50-кг сверхпроводящий аккумулятор, 10% КПД, 200 МДж в разряде:
        # Отдача в 250 кг тротилового эквивалента
        'wpn_ammo_1_name':'Спарк-батареи',
        'wpn_ammo_1_capacity':50000,
        'wpn_ammo_1_expense':50000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'ЗРК большой дальности',
        # https://ru.wikipedia.org/wiki/С-200
        'wpn_name_comment':'Пусковые установки комплекса зенитных ракет. Автомобильный прицеп, 6-тонная ракета.',
        'wpn_troops_type':'РВ',
        'wpn_cost':300000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00012,
        'wpn_name_new':'ЗРК большой дальности новые',
        'wpn_name_mid':'ЗРК большой дальности устаревшие',
        'wpn_name_old':'ЗРК большой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стратегические ракетные комплексы',
        'wpn_name_comment':'Мобильные комплексы для запуска 50-тонных баллистических ракет с ядерными боеголовками.',
        'wpn_troops_type':'РВ',
        'wpn_cost':8000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.001,
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
        'wpn_name_comment':'Крепости в живых облаках. 100 тысяч тонн грузоподъёмности, магнитная левитация, ядерный реактор.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':10000000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.007,
        'wpn_name_new':'Тандерхеды третьего поколения',
        'wpn_name_mid':'Тандерхеды второго поколения',
        'wpn_name_old':'Тандерхеды первого поколения',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        # 8 дивизионов дальних зенитных ракет:
        'wpn_ammo_1_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_1_capacity':192,
        'wpn_ammo_1_expense':192,
        # 64 пусковые установки тактических ракет:
        'wpn_ammo_2_name':'Крылатые ракеты',
        'wpn_ammo_2_capacity':64,
        'wpn_ammo_2_expense':64,
        # 16 пусковых комплексов стратегических ракет:
        'wpn_ammo_3_name':'Стратегические ядерные ракеты',
        'wpn_ammo_3_capacity':16,
        'wpn_ammo_3_expense':16,
        # 128 лазеров противоракетной обороны:
        'wpn_ammo_4_name':'Спарк-батареи',
        'wpn_ammo_4_capacity':6400000,
        'wpn_ammo_4_expense':6400000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Рапторы',
        'wpn_name_comment':'Малозаметные многоцелевые экранолёты. 500 тонн взлётного веса; 120 тонн груза; 900 км/ч скорость; атомная СУ.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':1000000000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Рапторы новые',
        'wpn_name_mid':'Рапторы устаревшие',
        'wpn_name_old':'Рапторы не существующие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0006,
        'wpn_c':1.4,
        # Спаренная автоматическая пушка:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':1000,
        'wpn_ammo_1_expense':5000,
        # Восемь электролазеров активной защиты:
        'wpn_ammo_2_name':'Спарк-батареи',
        'wpn_ammo_2_capacity':800,
        'wpn_ammo_2_expense':8000,
        # Может нести в грузовом отсеке 4x3 счетверённых контейнера крылатых ракет:
        'wpn_ammo_3_name':'Крылатые ракеты',
        'wpn_ammo_3_capacity':48,
        'wpn_ammo_3_expense':48,
        # Или 4x3 пусковых контейнеров дальних зенитных ракет:
        'wpn_ammo_4_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_4_capacity':12,
        'wpn_ammo_4_expense':12,
        # Или 4x3 пусковых контейнеров противокорабельных ракет:
        'wpn_ammo_5_name':'Противокорабельные ракеты',
        'wpn_ammo_5_capacity':12,
        'wpn_ammo_5_expense':12,
        # Или 60 противолодочных мин-торпед:
        'wpn_ammo_6_name':'Противолодочные мины-торпеды',
        'wpn_ammo_6_capacity':60,
        'wpn_ammo_6_expense':60,
        # Или 1000 авиабомб массой по 100 кг:
        'wpn_ammo_7_name':'Авиабомбы',
        'wpn_ammo_7_capacity':1000,
        'wpn_ammo_7_expense':60000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Транспортники',
        # https://ru.wikipedia.org/wiki/ЭКИП
        'wpn_name_comment':'Десантные и транспортные экранолёты. 500 тонн взлётного веса; 120 тонн груза; 900 км/ч скорость; атомная СУ.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':600000000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Транспортники новые',
        'wpn_name_mid':'Транспортники устаревшие',
        'wpn_name_old':'Транспортники под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.4,
        # Спаренная автоматическая пушка:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':1000,
        'wpn_ammo_1_expense':5000,
        # Восемь электролазеров активной защиты:
        'wpn_ammo_2_name':'Спарк-батареи',
        'wpn_ammo_2_capacity':800,
        'wpn_ammo_2_expense':8000,
        # Может нести 1000 авиабомб массой по 100 кг:
        'wpn_ammo_3_name':'Авиабомбы',
        'wpn_ammo_3_capacity':1000,
        'wpn_ammo_3_expense':60000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Многоцелевые истребители',
        # https://ru.wikipedia.org/wiki/МиГ-21
        'wpn_name_comment':'Фронтовые истребители и истребители-перехватчики. Масса: 5-10 тонн, 1-2 Маха скорость, боевой радиус 500 км.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':20000000,
        'wpn_maintenance':0.1,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.008,
        'wpn_name_new':'Истребители новые',
        'wpn_name_mid':'Истребители устаревшие',
        'wpn_name_old':'Истребители под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        # Встроенная пушка:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':200,
        'wpn_ammo_1_expense':2000,
        # Четыре точки подвески:
        'wpn_ammo_2_name':'Авиабомбы',
        'wpn_ammo_2_capacity':8,
        'wpn_ammo_2_expense':800,
        'wpn_ammo_3_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':40,
        'wpn_ammo_4_name':'Управляемые ракеты',
        'wpn_ammo_4_capacity':8,
        'wpn_ammo_4_expense':24,
        'wpn_ammo_5_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_5_capacity':4,
        'wpn_ammo_5_expense':12,
        'wpn_ammo_6_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_6_capacity':2,
        'wpn_ammo_6_expense':6,
        # Два электролазера активной защиты
        'wpn_ammo_7_name':'Спарк-батареи',
        'wpn_ammo_7_capacity':200,
        'wpn_ammo_7_expense':2000,
        'wpn_fuel_name':'Синтетическое топливо (литры)',
        # Дальность 1000 км с крейсерской скоростью в 1000 км/час.
        # На 120 вылетов в год.
        'wpn_fuel_capacity':3000,
        'wpn_fuel_consumption':3,
        'wpn_fuel_expense':360000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Боевые планеры',
        # http://www.aeros.com.ua/structure/al/al12_ru.php
        'wpn_name_comment':'Пегасо-носимая авиация с грузоподъёмностью в 200 кг. Масса: 50 кг; скорость до 200 км/час.',
        'wpn_troops_type':'ВВС',
        'wpn_cost':200000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Боевые планеры новые',
        'wpn_name_mid':'Боевые планеры потрёпанные',
        'wpn_name_old':'Боевые планеры под списание',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        # Курсовой пулемёт:
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':250,
        'wpn_ammo_1_expense':5000,
        # Пилон для 100-кг авиабомбы:
        'wpn_ammo_2_name':'Авиабомбы',
        'wpn_ammo_2_capacity':1,
        'wpn_ammo_2_expense':6,
        # Или пусковая установка реактивных гранат:
        'wpn_ammo_3_name':'Реактивные гранаты',
        'wpn_ammo_3_capacity':24,
        'wpn_ammo_3_expense':72,
        # Или управляемая ракета:
        'wpn_ammo_4_name':'Управляемые ракеты',
        'wpn_ammo_4_capacity':4,
        'wpn_ammo_4_expense':4,
        'wpn_ammo_5_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_5_capacity':1,
        'wpn_ammo_5_expense':1,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Подводные ракетоносцы',
        'wpn_name_comment':'Водоизмещение: 10 000 тонн. Атомная силовая установка. 16 пусковых шахт МБР, торпеды.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':3000000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Подводные ракетоносцы новые',
        'wpn_name_mid':'Подводные лодки устаревшие',
        'wpn_name_old':'Подводные лодки не существующие',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.00,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Два торпедных аппарата
        'wpn_ammo_1_name':'Торпеды большой дальности',
        'wpn_ammo_1_capacity':2,
        'wpn_ammo_1_expense':6,
        'wpn_ammo_2_name':'Противолодочные мины-торпеды',
        'wpn_ammo_2_capacity':4,
        'wpn_ammo_2_expense':12,
        # Шестнадцать шахт баллистических ракет
        'wpn_ammo_3_name':'Стратегические ядерные ракеты',
        'wpn_ammo_3_capacity':16,
        'wpn_ammo_3_expense':16,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ракетные крейсера',
        # https://en.wikipedia.org/wiki/Virginia-class_cruiser
        'wpn_name_comment':'Водоизмещение: 10 000 тонн. АСУ на 100 МВт — скорость до 35 узлов. Ракеты ПВО/ПРО.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':2000000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Ракетные крейсера новые',
        'wpn_name_mid':'Крейсера устаревшие',
        'wpn_name_old':'Дредноуты под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        # Шесть пятистовольных 30-мм пушек:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':15000,
        'wpn_ammo_1_expense':15000,
        # Две установки зенитных ракет малой дальности:
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':64,
        'wpn_ammo_2_expense':128,
        # Две артиллерийские 120-мм установки:
        'wpn_ammo_3_name':'Снаряды 120-мм',
        'wpn_ammo_3_capacity':1000,
        'wpn_ammo_3_expense':6000,
        # Два торпедных аппарата:
        'wpn_ammo_4_name':'Торпеды большой дальности',
        'wpn_ammo_4_capacity':2,
        'wpn_ammo_4_expense':12,
        'wpn_ammo_5_name':'Противолодочные мины-торпеды',
        'wpn_ammo_5_capacity':4,
        'wpn_ammo_5_expense':12,        
        # Два реактивных бомбомёта:
        'wpn_ammo_6_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_6_capacity':24,
        'wpn_ammo_6_expense':72,
        # Две пусковые установки зенитных ракет средней дальности:
        'wpn_ammo_7_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_7_capacity':64,
        'wpn_ammo_7_expense':128,
        # 4x4 пусковые установки дальних зенитных ракет:
        'wpn_ammo_8_name':'Зенитные ракеты большой дальности',
        'wpn_ammo_8_capacity':16,
        'wpn_ammo_8_expense':32,
        # 2x4 пусковые установки противокорабельных ракет:
        'wpn_ammo_9_name':'Противокорабельные ракеты',
        'wpn_ammo_9_capacity':8,
        'wpn_ammo_9_expense':16,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Сторожевые корабли',
        # https://ru.wikipedia.org/wiki/Сторожевые_корабли_проекта_1135
        'wpn_name_comment':'Водоизмещение: 3000 тонн. АСУ на 50 МВт — скорость до 35 узлов. Противолодочное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':800000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Сторожевые корабли новые',
        'wpn_name_mid':'Сторожевые корабли устаревшие',
        'wpn_name_old':'Фрегаты под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.02,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Две пятиствольные 30-мм пушки
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':10000,
        # Две установки зенитных ракет малой дальности:
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':64,
        'wpn_ammo_2_expense':128,
        # Артиллерийская 120-мм установка
        'wpn_ammo_3_name':'Снаряды 120-мм',
        'wpn_ammo_3_capacity':500,
        'wpn_ammo_3_expense':3000,
        # Два торпедных аппарата
        'wpn_ammo_4_name':'Торпеды большой дальности',
        'wpn_ammo_4_capacity':2,
        'wpn_ammo_4_expense':6,
        'wpn_ammo_5_name':'Противолодочные мины-торпеды',
        'wpn_ammo_5_capacity':4,
        'wpn_ammo_5_expense':12,        
        # Два реактивных бомбомёта
        'wpn_ammo_6_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_6_capacity':24,
        'wpn_ammo_6_expense':72,
        # Пусковая установка зенитных ракет средней дальности:
        'wpn_ammo_7_name':'Зенитные ракеты средней дальности',
        'wpn_ammo_7_capacity':32,
        'wpn_ammo_7_expense':64,
        # 2x4 пусковые установки противокорабельных ракет:
        'wpn_ammo_8_name':'Противокорабельные ракеты',
        'wpn_ammo_8_capacity':8,
        'wpn_ammo_8_expense':16,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Средние десантные корабли',
        'wpn_name_comment':'Водоизмещение: 3000 тонн. АСУ на 30 МВт — скорость до 25 узлов. Десант: 10 танков, 300 бойцов.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':200000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Десантные корабли новые',
        'wpn_name_mid':'Десантные корабли устаревшие',
        'wpn_name_old':'Десантные корабли под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.01,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        # Две пятиствольные 30-мм пушки
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':10000,
        # Две установки зенитных ракет
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':64,
        'wpn_ammo_2_expense':128,
        # Два реактивных бомбомёта/РСЗО
        'wpn_ammo_3_name':'Реактивные снаряды 210-мм',
        'wpn_ammo_3_capacity':24,
        'wpn_ammo_3_expense':72,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Вспомогательные суда',
        'wpn_name_comment':'Суда снабжения, базы подводных лодок, плавучие мастерские. До 20 000 тонн. АСУ-50 МВт, скорость 25 узлов.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':400000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0012,
        'wpn_name_new':'Десантные корабли новые',
        'wpn_name_mid':'Десантные корабли устаревшие',
        'wpn_name_old':'Десантные корабли под списание',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.01,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        # Две пятиствольные 30-мм пушки
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':5000,
        'wpn_ammo_1_expense':10000,
        # Две установки зенитных ракет
        'wpn_ammo_2_name':'Зенитные ракеты малой дальности',
        'wpn_ammo_2_capacity':64,
        'wpn_ammo_2_expense':128,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Многоцелевые катера',
        'wpn_name_comment':'Водоизмещение: 50 тонн. СУ — маховик. Скорость 30 узлов, дальность 700 км. Ракетное и пушечное вооружение.',
        'wpn_troops_type':'ВМФ',
        'wpn_cost':5000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0005,
        'wpn_name_new':'Многоцелевые катера новые',
        'wpn_name_mid':'Многоцелевые катера устаревшие',
        'wpn_name_old':'Многоцелевые катера под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.03,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        # Орудийный модуль от боевой машины пехоты:
        'wpn_ammo_1_name':'Снаряды 30x165',
        'wpn_ammo_1_capacity':500,
        'wpn_ammo_1_expense':2500,
        'wpn_ammo_2_name':'Патроны 6x48',
        'wpn_ammo_2_capacity':2000,
        'wpn_ammo_2_expense':10000,
        'wpn_ammo_3_name':'Управляемые ракеты',
        'wpn_ammo_3_capacity':4,
        'wpn_ammo_3_expense':12,
        'wpn_fuel_name':'Маховики (МДж)',
        # 14 часов автономного плавания, или 700 км дальность.
        'wpn_fuel_capacity':80000,
        'wpn_fuel_consumption':114,
        'wpn_fuel_expense':2000000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Предприятия ВПК',
        'wpn_name_comment':'Предприятия оборонной промышленности: заводы и конструкторские бюро.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':5000000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.05,
        'wpn_name_new':'Предприятия ВПК современные',
        'wpn_name_mid':'Предприятия ВПК старого типа',
        'wpn_name_old':'Предприятия ВПК устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Резервные склады',
        'wpn_name_comment':'Скрытые хранилища продовольствия, вооружения и станков. Помещения под 100 000 кубометров.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':60000000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Резервные склады современные',
        'wpn_name_mid':'Резервные склады ненадёжные',
        'wpn_name_old':'Довоенные хранилища резерва',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Убежища гражданской обороны',
        'wpn_name_comment':'Временные противоядерные/противохимические убежища. Третий класс защиты: 0.1 МПа ударной волны. 300 мест.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Убежища современные',
        'wpn_name_mid':'Убежища старого типа',
        'wpn_name_old':'Довоенные бомбоубежища',
        'wpn_age_mid':15,
        'wpn_age_old':30,
        'wpn_a':0.00,
        'wpn_b':0.0002,
        'wpn_c':1.3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Военные городки',
        'wpn_name_comment':'Для войсковых частей полк/бригада, 3000 солдат.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':500000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.04,
        'wpn_name_new':'Военные городки современные',
        'wpn_name_mid':'Военные городки старого типа',
        'wpn_name_old':'Военные городки устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.00,
        'wpn_b':0.0001,
        'wpn_c':1.2,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Полевые лагеря',
        'wpn_name_comment':'Для учений и подготовки резервистов. Батальонного типа, 500 солдат.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':10000000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Полевые лагеря новые',
        'wpn_name_mid':'Полевые лагеря потрёпанные',
        'wpn_name_old':'Полевые лагеря обветшалые',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.002,
        'wpn_b':0.0006,
        'wpn_c':1.8,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Мобильные атомные электростанции',
        'wpn_name_comment':'Прицеп для тяжёлого тягача. Масса 50 тонн, тепловая мощность 100 МВт, полезная энергия 50 МВт.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':100000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.005,
        'wpn_name_new':'Мобильные АЭС современные',
        'wpn_name_mid':'Мобильные АЭС старого типа',
        'wpn_name_old':'Мобильные АЭС на списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.002,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Инженерные машины',
        'wpn_name_comment':'Минные заградители и разградители, мостоукладчики и путепрокладчики, траншейные машины. Масса 30 тонн.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':1000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Инженерные машины новые',
        'wpn_name_mid':'Инженерные машины устаревшие',
        'wpn_name_old':'Инженерные машины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.005,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_ammo_1_name':'Патроны 6x48',
        'wpn_ammo_1_capacity':2000,
        'wpn_ammo_1_expense':10000,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':20000,
        'wpn_fuel_consumption':50,
        'wpn_fuel_expense':500000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Военные грузовики',
        # https://ru.wikipedia.org/wiki/КамАЗ-43118 
        'wpn_name_comment':'Рабочие лошадки большой войны. Масса шасси — 10 тонн. Груз (с прицепом) до 10 тонн.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':100000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.007,
        'wpn_name_new':'Военные грузовики современные',
        'wpn_name_mid':'Военные грузовики старого типа',
        'wpn_name_old':'Военные грузовики устаревшие',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        'wpn_fuel_name':'Маховики (МДж)',
        'wpn_fuel_capacity':10000,
        'wpn_fuel_consumption':25,
        'wpn_fuel_expense':250000,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Радиационно-защитные костюмы',
        'wpn_name_comment':'Скафандры: системы фильтров, охлаждение, огнеупорная ткань. Для войск РХБЗ. Масса 30 кг.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':100000,
        'wpn_maintenance':0.05,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Противотанковые мины новые',
        'wpn_name_mid':'Противотанковые мины устаревшие',
        'wpn_name_old':'Противотанковые мины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_cost':100,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0002,
        'wpn_name_new':'Противопехотные мины новые',
        'wpn_name_mid':'Противопехотные мины устаревшие',
        'wpn_name_old':'Противопехотные мины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.20,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ядерные фугасы',
        'wpn_name_comment':'Для минирования инженерных сооружений, дорог и мостов. Масса: 200 кг; мощность взрыва 1-25 килотонн.',
        'wpn_troops_type':'ИВ',
        'wpn_cost':500000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0001,
        'wpn_name_new':'Ядерные фугасы новые',
        'wpn_name_mid':'Ядерные фугасы устаревшие',
        'wpn_name_old':'Ядерные фугасы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Синтетическое топливо (литры)',
        'wpn_name_comment':'Дорогостоящее подобие керосина, синтезируют из угля. Теплота сгорания: 43 МДж/кг. Плотность: 0.8 кг/литр',
        'wpn_troops_type':'ВПК',
        'wpn_cost':3,
        'wpn_maintenance':0.5,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'Синтетическое топливо свежее.',
        'wpn_name_mid':'Синтетическое топливо старых запасов.',
        'wpn_name_old':'Синтетическое топливо просроченное.',
        'wpn_age_mid':1,
        'wpn_age_old':2,
        'wpn_a':0.1,
        'wpn_b':0.002,
        'wpn_c':3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Маховики (МДж)',
        'wpn_name_comment':'Сверхпрочные диски из углеродных нанотрубок, ёмкость 10 МДж/кг. Стоимость энергии бит/МДж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':0.01,
        'wpn_maintenance':0.2,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0006,
        'wpn_name_new':'Маховики предельно заряженные.',
        'wpn_name_mid':'Маховики с половиной энергии.',
        'wpn_name_old':'Маховики остановившиеся.',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Полевые рационы (суточные)',
        'wpn_name_comment':'Повседневные/боевые рационы питания, энергетическая ценность 3500 килокаллорий, вес в упаковке 2 кг.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Сухие пайки свежие.',
        'wpn_name_mid':'Сухие пайки старые.',
        'wpn_name_old':'Сухие пайки просроченные.',
        'wpn_age_mid':3,
        'wpn_age_old':6,
        'wpn_a':0.2,
        'wpn_b':0.002,
        'wpn_c':3,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Спарк-батареи',
        'wpn_name_comment':'Кристаллы сверхпроводящих фуллеренов, одноразовые. 1 грамм сверхпроводника — 40 000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Спарк-батареи предельно заряженные.',
        'wpn_name_mid':'Спарк-батареи с половиной энергии.',
        'wpn_name_old':'Спарк-батареи разрядившиеся.',
        'wpn_age_mid':5,
        'wpn_age_old':10,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стреловидные пули',
        'wpn_name_comment':'Для электромагнитных снайперских пушек. Пуля: 20 г; нач.скорость 1500 м/с; энергия 22 500 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.00005,
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
        'wpn_name':'Патроны 6x48',
        # http://sniper-weapon.ru/boepripasy/370-patron-6kh49-mm
        'wpn_name_comment':'Для лёгкого стрелкового оружия. Патрон: 15 г; пуля: 5 г; нач.скорость 1100 м/с; энергия 3000 Дж.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':0.5,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
        'wpn_name_new':'Патроны 6x48 новые',
        'wpn_name_mid':'Патроны 6x48 устаревшие',
        'wpn_name_old':'Патроны 6x48 под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'Патроны 15x120 новые',
        'wpn_name_mid':'Патроны 15x120 устаревшие',
        'wpn_name_old':'Патроны 15x120 под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0027,
        'wpn_name_new':'Снаряды 30x165 новые',
        'wpn_name_mid':'Снаряды 30x165 устаревшие',
        'wpn_name_old':'Снаряды 30x165 под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0024,
        'wpn_name_new':'Снаряды 120-мм новые',
        'wpn_name_mid':'Снаряды 120-мм устаревшие',
        'wpn_name_old':'Снаряды 120-мм под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0002,
        'wpn_c':1.4,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Снаряды 150-мм',
        'wpn_name_comment':'Для дивизионной артиллерии, различные боеприпасы. Масса 40-60 кг. Дальность огня: 20 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0035,
        'wpn_name_new':'Снаряды 150-мм новые',
        'wpn_name_mid':'Снаряды 150-мм устаревшие',
        'wpn_name_old':'Снаряды 150-мм под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'Выстрелы АГС новые',
        'wpn_name_mid':'Выстрелы АГС устаревшие',
        'wpn_name_old':'Выстрелы АГС под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0016,
        'wpn_name_new':'Миномётные мины 120-мм новые',
        'wpn_name_mid':'Миномётные мины 120-мм устаревшие',
        'wpn_name_old':'Миномётные мины 120-мм под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
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
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
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
        'wpn_name_comment':'Для реактивной артиллерии. Осколочные, кассетные. Масса 200 кг (70 кг БЧ) Дальность огня до 40 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':5000,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.006,
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
        'wpn_name':'Авиабомбы',
        # http://www.modernforces.ru/fab-100/
        'wpn_name_comment':'Фугасные и осколочно-фугасные массой в 100 килограмм (50 кг ВВ).',
        'wpn_troops_type':'ВПК',
        'wpn_cost':500,
        'wpn_maintenance':0.01,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.002,
        'wpn_name_new':'100-кг авиабомбы новые',
        'wpn_name_mid':'100-кг авиабомбы устаревшие',
        'wpn_name_old':'100-кг авиабомбы под списание',
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
        'wpn_name_comment':'Противотанковые ракеты управляемые с пусковой установки. Масса 6 кг. Дальность 2 км',
        'wpn_troops_type':'ВПК',
        'wpn_cost':25000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.009,
        'wpn_name_new':'Управляемые ракеты новые',
        'wpn_name_mid':'Управляемые ракеты устаревшие',
        'wpn_name_old':'Управляемые ракеты под списание',
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
        'wpn_name_comment':'Противовоздушные ракеты, тепловая ГСН. Масса 60 кг; высота: 5 км; дальность: 10 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':30000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0017,
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
        # https://ru.wikipedia.org/wiki/9М38
        'wpn_name_comment':'Противовоздушные ракеты среднего радиуса. Радиволновая ГСН. Масса 500 кг; высота: 20; дальность 30 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':500000,
        'wpn_maintenance':0.02,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0035,
        'wpn_name_new':'Зенитные ракеты средней дальности новые',
        'wpn_name_mid':'Зенитные ракеты средней дальности устаревшие',
        'wpn_name_old':'Зенитные ракеты средней дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.05,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Зенитные ракеты большой дальности',
        'wpn_name_comment':'Ракеты ПВО/ПРО дальнего радиуса. Активная РГСН. Масса 6000 кг (БЧ 200 кг). Высота: 40 км; дальность 250 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':3000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0045,
        'wpn_name_new':'Зенитные ракеты большой дальности новые',
        'wpn_name_mid':'Зенитные ракеты большой дальности устаревшие',
        'wpn_name_old':'Зенитные ракеты большой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':0.1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Противокорабельные ракеты',
        # https://ru.wikipedia.org/wiki/П-120
        'wpn_name_comment':'Крылатые ракеты, околозвуковая скорость, активная РГСН. Масса 6000 кг (БЧ 500 кг). Дальность 150 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':2000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0007,
        'wpn_name_new':'Противокорабельные ракеты новые',
        'wpn_name_mid':'Противокорабельные ракеты устаревшие',
        'wpn_name_old':'Противокорабельные ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Торпеды большой дальности',
        'wpn_name_comment':'Торпеды с ядерными боеголовками. Масса: 4000 кг (200 кг БЧ); скорость 50 узлов; дальность 50 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':3000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0003,
        'wpn_name_new':'Торпеды большой дальности новые',
        'wpn_name_mid':'Торпеды большой дальности устаревшие',
        'wpn_name_old':'Торпеды большой дальности под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Противолодочные мины-торпеды',
        # https://ru.wikipedia.org/wiki/Кэптор_(мина)
        'wpn_name_comment':'Масса торпеды 1000 тонн (50 кг БЧ). Скорость — 30 узлов. Обнаружение судов — 1.5 км, дальность 7 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':1000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0015,
        'wpn_name_new':'Противолодочные мины-торпеды новые',
        'wpn_name_mid':'Противолодочные мины устаревшие',
        'wpn_name_old':'Морские мины под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.1,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Баллистические ракеты',
        'wpn_name_comment':'Баллистические ракеты малого радиуса. Масса 2000 кг (БЧ 500 кг). Дальность 120 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':800000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.004,
        'wpn_name_new':'Баллистические ракеты новые',
        'wpn_name_mid':'Баллистические ракеты устаревшие',
        'wpn_name_old':'Баллистические ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':0.1,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Крылатые ракеты',
        'wpn_name_comment':'Дозвуковые низколетящие ракеты с наведением по карте высот. Масса 2000 кг. Дальность 2500 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':2000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.0012,
        'wpn_name_new':'Крылатые ракеты новые',
        'wpn_name_mid':'Крылатые ракеты устаревшие',
        'wpn_name_old':'Крылатые ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.02,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (25 килотонн)',
        'wpn_ammo_1_capacity':1,
        'wpn_ammo_1_expense':0.5,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Стратегические ядерные ракеты',
        'wpn_name_comment':'Баллистические ракеты с БЧ на шесть ядерных боеголовок. Масса 50 тонн. Дальность 10 000 км.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':20000000,
        'wpn_maintenance':0.05,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.003,
        'wpn_name_new':'Стратегические ядерные ракеты новые',
        'wpn_name_mid':'Стратегические ядерные ракеты устаревшие',
        'wpn_name_old':'Стратегические ядерные ракеты под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        'wpn_ammo_1_name':'Ядерные заряды (500 килотонн)',
        'wpn_ammo_1_capacity':6,
        'wpn_ammo_1_expense':6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ядерные заряды (25 килотонн)',
        'wpn_name_comment':'Заряды изменяемой мощности от 1 до 25 килотонн. Радиус поражения до 1.5 км. Масса: 100 кг.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':5000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.008,
        'wpn_name_new':'Тактические ядерные бомбы новые',
        'wpn_name_mid':'Тактические ядерные бомбы устаревшие',
        'wpn_name_old':'Тактические ядерные бомбы под списание',
        'wpn_age_mid':10,
        'wpn_age_old':20,
        'wpn_a':0.01,
        'wpn_b':0.0004,
        'wpn_c':1.6,
        }
metadict_wpn[dict_wpn_key] = dict_wpn

dict_wpn_key = dict_wpn_key + 1
dict_wpn = {
        'wpn_name':'Ядерные заряды (500 килотонн)',
        'wpn_name_comment':'Заряды изменяемой мощности от 1 до 500 килотонн. Радиус поражения до 3.5 км. Масса: 400 кг.',
        'wpn_troops_type':'ВПК',
        'wpn_cost':10000000,
        'wpn_maintenance':0.03,
        'wpn_cost_currency':'Эквестрийские биты',
        'wpn_budget':0.01,
        'wpn_name_new':'Стратегические ядерные бомбы новые',
        'wpn_name_mid':'Стратегические ядерные бомбы устаревшие',
        'wpn_name_old':'Стратегические ядерные бомбы под списание',
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
print('Военные потери: ', round(army_soldiers * prof_hazard),
        ' (', round(army_soldiers * prof_hazard / (POPULATION * COMPONENT_A) * 100),
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
# База данных стоимости обслуживания по видам войск:
# Создаётся рабочий словарь, обнуляются значения:
maintenance_troops_types = {}
maintenance_troops_types.update(dict_troops_types)
for troop_key in budget_troops_types:
    maintenance_troops_types[troop_key] = 0

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
    # Подсчитываем, сколько оружия создано за год:
    wpn_create = round(GDP_size(0) * GDP_ARMY * \
                metadict_wpn[wpn_key]['wpn_budget'] / metadict_wpn[wpn_key]['wpn_cost'])
    # Расходы на проект:
    print('        Расходы: ',
            round(metadict_wpn[wpn_key]['wpn_budget'] * 100, 3),'% бюджета ',
            '(', metadict_wpn[wpn_key]['wpn_cost'] * wpn_create / (10 ** 9),
            ' млрд ', metadict_wpn[wpn_key]['wpn_cost_currency'], ') ', sep='')
    # Подсчитываем потери (без учёта старения оружия):
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
    # Считаем расходы на обслуживание данного вида оружия:
    # Стоимость оружия * процент обслуживания * штук на складах
    # Если строка 'wpn_maintenance' не указана, тогда обслуживание бесплатно
    wpn_maintenance_all = metadict_wpn[wpn_key]['wpn_cost'] * \
            metadict_wpn.get(wpn_key, 0).get('wpn_maintenance', 0)  * \
            dict_equipment_all.get(metadict_wpn[wpn_key]['wpn_name'])
    # Теперь распределяем расходы на обслуживание по родам войск:
    for troop_key in maintenance_troops_types:
        if troop_key == metadict_wpn[wpn_key]['wpn_troops_type']:
            maintenance_troops_types[troop_key] = maintenance_troops_types[troop_key] + \
                    wpn_maintenance_all

# Сумма бюджета всех проектов из базы данных оружия:
print('Расходы военного бюджета на закупки и производство:')
for troop_key in sorted(budget_troops_types.keys()):
    print('    ', troop_key, ' (', round(dict_troops_types[troop_key] * 100), '%)',
            ' — ', round(budget_troops_types[troop_key], 2), '%', sep='')
print('Использовано ', round(budget_percent * 100, 2), '% бюджета армии',
        ' (или ', round(GDP_ARMY * budget_percent * 100, 2), '% ВВП страны)',
        sep='')
print('        ---')

# Расходы на обслуживание оружия по видам войск:
maintenance_percent_sum = 0
print('Расходы военного бюджета на техническое обслуживание:')
for troop_key in sorted(maintenance_troops_types.keys()):
    maintenance_percent = maintenance_troops_types[troop_key] / (GDP_size(0) * GDP_ARMY)
    maintenance_percent_sum = maintenance_percent_sum + maintenance_percent
    print('    ', troop_key, ' (', round(dict_troops_types[troop_key] * 100), '%)',
            ' — ', round(maintenance_percent * 100, 2), '%', sep='')
print('Использовано ', round(maintenance_percent_sum * 100, 2), '% бюджета армии',
        ' (или ', round(maintenance_percent_sum * GDP_ARMY * 100, 2), '% ВВП страны)',
        sep='')
print('        ---')

# Соотношение производства боеприпасов и потребности в них:
print('Боеприпасы на складах (на год войны):')
for ammo_key in sorted(ammunition_needs.keys()):
    # (ammo_key, 0) — значит, если нет ключа, брать ноль.
    print('   ', ammo_key, ' — ', dict_equipment_all.get(ammo_key, 0), ' (',
            round(dict_equipment_all.get(ammo_key, ammunition_needs[ammo_key]) / \
                    ammunition_needs[ammo_key] * 100), '%)', sep='')
