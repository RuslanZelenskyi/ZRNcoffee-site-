# -*- coding: utf-8 -*-
"""Інтерактивний калькулятор кави для ZRN Coffee.
Підключається з tools/build.py: CALC_CSS (у pages.css), CALC_JS (calc.js), widget_html(lang), page_body(lang), faq(lang)."""
import json

CALC_CSS = r"""
/* ===== калькулятор кави ===== */
.calc{margin:8px 0 28px;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:0 10px 30px -22px rgba(33,26,17,.55);color:var(--ink);font-size:1rem}
.calc *{box-sizing:border-box}
.calc button{font:inherit;cursor:pointer;color:inherit}
.calc-methods{display:flex;gap:8px;overflow-x:auto;padding:2px 2px 10px;margin:0 -2px;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
.calc-methods button{flex:0 0 auto;border:1px solid var(--line);background:var(--bg);border-radius:999px;padding:9px 15px;font-weight:600;font-size:.92rem;white-space:nowrap;transition:background .15s,color .15s,border-color .15s}
.calc-methods button[aria-pressed=true]{background:var(--dark);color:#f3ead9;border-color:var(--dark)}
.calc-grid{display:grid;gap:14px;grid-template-columns:1fr}
@media(min-width:760px){.calc-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:start}}
.calc-in,.calc-out{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:14px}
.calc-out{background:var(--dark);color:#f3ead9;border-color:var(--dark)}
.calc-sec{margin:0 0 14px}
.calc-sec:last-child{margin-bottom:0}
.calc-lab{display:block;font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--gold-soft);font-weight:600;margin:0 0 6px}
.calc-seg{display:flex;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--card)}
.calc-seg button{flex:1;border:0;background:transparent;padding:9px 6px;font-size:.86rem;font-weight:500;line-height:1.2;border-right:1px solid var(--line)}
.calc-seg button:last-child{border-right:0}
.calc-seg button[aria-pressed=true]{background:var(--gold-soft);color:#fff}
.calc-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.calc-num{display:flex;align-items:stretch;border:1px solid var(--line);border-radius:10px;background:#fff;overflow:hidden}
.calc-num button{border:0;background:var(--card);width:42px;font-size:1.25rem;line-height:1}
.calc-num input{border:0;width:74px;text-align:center;font:inherit;font-weight:600;background:#fff;color:var(--ink);padding:9px 4px;min-width:0}
.calc-num input:focus,.calc input[type=range]:focus-visible,.calc button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.calc-unit{color:var(--sub);font-size:.9rem}
.calc-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.calc-chips button{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:5px 11px;font-size:.84rem}
.calc-chips button[aria-pressed=true]{background:var(--gold-soft);color:#fff;border-color:var(--gold-soft)}
.calc input[type=range]{width:100%;accent-color:var(--gold-soft);margin:6px 0 2px}
.calc-rv{font-family:'Fraunces',serif;font-size:1.5rem;font-weight:500;color:var(--ink)}
.calc-meter{position:relative;height:14px;border-radius:7px;background:linear-gradient(90deg,#e9dcc0,#ddc9a0);margin:10px 0 4px;overflow:visible}
.calc-meter i{position:absolute;top:0;bottom:0;background:rgba(107,74,28,.35);border-radius:7px}
.calc-meter b{position:absolute;top:-4px;width:4px;height:22px;background:var(--dark);border-radius:2px;transform:translateX(-2px);transition:left .15s}
.calc-meter-l{display:flex;justify-content:space-between;font-size:.72rem;color:var(--sub)}
.calc-meter-n{font-size:.74rem;color:var(--sub);margin-top:2px}
.calc-check{display:flex;gap:9px;align-items:flex-start;font-size:.9rem;line-height:1.4;cursor:pointer}
.calc-check input{margin-top:3px;accent-color:var(--gold-soft);width:18px;height:18px;flex:0 0 auto}
.calc-check small{display:block;color:var(--sub);font-size:.78rem;margin-top:2px}
.calc-big{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.calc-big div{background:rgba(243,234,217,.08);border:1px solid rgba(243,234,217,.18);border-radius:12px;padding:10px 12px}
.calc-big span{display:block;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;opacity:.75}
.calc-big strong{display:block;font-family:'Fraunces',serif;font-weight:500;font-size:clamp(1.7rem,6vw,2.3rem);line-height:1.1;margin-top:2px}
.calc-big small{font-size:.5em;font-weight:500;opacity:.8;margin-left:3px}
.calc-wide{grid-column:1/-1}
.calc-bar{display:flex;height:22px;border-radius:11px;overflow:hidden;background:rgba(243,234,217,.15);margin:2px 0 12px;font-size:.7rem;font-weight:600}
.calc-bar i{display:flex;align-items:center;justify-content:center;font-style:normal;min-width:30px;white-space:nowrap}
.calc-bar i:first-child{background:#c9954a;color:#211a11}
.calc-bar i:last-child{flex:1;color:#f3ead9}
.calc-facts{list-style:none;margin:0 0 10px!important;padding:0!important;display:grid;gap:5px}
.calc-facts li{display:flex;justify-content:space-between;gap:12px;font-size:.9rem!important;border-bottom:1px dashed rgba(243,234,217,.18);padding:0 0 5px!important;margin:0!important;color:#f3ead9!important;line-height:1.4!important}
.calc-facts li:last-child{border-bottom:0}
.calc-facts b{font-weight:600;text-align:right}
.calc-note{font-size:.84rem!important;line-height:1.45!important;border-radius:10px;padding:9px 11px;margin:0 0 10px!important;background:rgba(243,234,217,.1)}
.calc-note.warn{background:rgba(201,149,74,.22)}
.calc-note.ok{background:rgba(120,170,110,.2)}
.calc-out .calc-note,.calc-out p{color:#f3ead9!important}
.calc-act{display:flex;gap:8px;flex-wrap:wrap}
.calc-act button{flex:1 1 140px;border:1px solid rgba(243,234,217,.35);background:transparent;color:#f3ead9;border-radius:10px;padding:10px 12px;font-weight:600;font-size:.88rem}
.calc-act button:hover{background:rgba(243,234,217,.12)}
.calc-act button:focus-visible{outline-color:#f3ead9}
.calc-toast{min-height:1.3em;font-size:.82rem;margin-top:8px;opacity:.9}
.calc-src{margin-top:12px;font-size:.84rem;color:var(--sub)}
.calc-src summary{cursor:pointer;font-weight:600;color:var(--gold-soft)}
.calc-src p,.calc-src li{font-size:.86rem!important;line-height:1.55!important;color:var(--sub)!important}
.calc [hidden]{display:none!important}
.calc-noscript{padding:12px;border:1px dashed var(--line);border-radius:10px;color:var(--sub)}
@media(max-width:420px){.calc-num button{width:34px}.calc-num input{width:52px}.calc{padding:12px}.calc-in,.calc-out{padding:12px}.calc-seg button{font-size:.8rem;padding:8px 3px}}
@media(prefers-reduced-motion:reduce){.calc *{transition:none!important}}
"""

TXT = {
 'uk': {
  'methods': {'filter': 'Фільтр / V60', 'press': 'Френч-прес', 'aero': 'Аеропрес', 'espresso': 'Еспресо', 'turka': 'Турка', 'moka': 'Гейзер', 'cold': 'Колд брю'},
  'aria_methods': 'Спосіб заварювання',
  'goals': {'drink': 'Хочу напою', 'dose': 'Маю кави', 'water': 'Наллю води', 'edose': 'Знаю дозу', 'yield': 'Хочу вихід'},
  'aria_goal': 'Що ви знаєте',
  'cups': 'Чашок', 'cupml': 'Обсяг чашки', 'ml': 'мл', 'g': 'г', 'dose': 'Кава', 'water': 'Вода', 'yield': 'Напій (вихід)',
  'servings': 'Порцій', 'per_serv': 'Води на порцію', 'pot': 'Розмір гейзера (чашок)', 'pot_note': 'Розмір «чашки» в гейзері умовний: це приблизно 40–50 мл концентрату. Дивіться маркування саме вашої кавоварки.',
  'ratio': 'Міцність (співвідношення кави до води)', 'strong': 'Міцніше', 'base': 'Базово', 'light': 'Легше', 'sca': 'SCA',
  'ret': 'Врахувати воду, яку вбирає гуща', 'ret_h': 'Близько 2 мл на 1 г кави у фільтрі й 3 мл в імерсії (Barista Hustle). Без цього в чашці буде менше, ніж налили.',
  'ret_est': 'Для цього способу утримання води — наша оцінка.',
  'prec': 'Ваги', 'prec1': 'точність 1 г', 'prec01': 'точність 0,1 г',
  'tds_h': 'Для профі: TDS і вихід екстракції', 'tds_lab': 'TDS напою, % (за рефрактометром)', 'tds_hint': 'Необов’язково. EY = TDS × вага напою ÷ вага кави.',
  'ey': 'Вихід екстракції (EY)', 'tds': 'Міцність (TDS)',
  'ey_under': 'Недоекстраговано: смак кислий і пустий. Мельніть дрібніше, збільште час або температуру.',
  'ey_ok': 'У «золотому» вікні 18–22%.',
  'ey_over': 'Переекстраговано: гіркота й сухість. Мельніть грубіше, скоротіть час.',
  'tds_range_f': 'Типовий TDS фільтра: 1,15–1,45%.', 'tds_range_e': 'Типовий TDS еспресо: 8–12%.',
  'out_dose': 'Кава', 'out_water': 'Вода', 'out_drink': 'Вийде напою', 'out_conc': 'Вийде концентрату', 'out_yield': 'Вихід напою',
  'f_ratio': 'Співвідношення', 'f_perl': 'Кави на літр води', 'f_spoon': 'Ложки (без ваг)', 'f_temp': 'Температура води', 'f_time': 'Час', 'f_grind': 'Помел', 'f_out': 'Вийде в чашках',
  'spoon_val': '≈ {a}–{b} ст. ложок', 'spoon_h': 'Ложка — ненадійна міра: вага залежить від обсмаження й помелу (5–8 г на ст. ложку за одним із джерел). Краще зважувати.',
  'bar_c': 'кава', 'bar_w': 'вода',
  'v_low': 'Дуже міцно: це вже концентрат', 'v_strong': 'Міцніше за еталон SCA (55 г/л ±10%). Поширений вибір', 'v_sca': 'У межах еталона SCA: 55 г на літр ±10%', 'v_weak': 'Легше за еталон SCA',
  'sca_lab': 'Затінена зона: еталон SCA (55 г/л ±10%)', 'sca_cap': ['1:10','1:22'],
  'copy': 'Скопіювати рецепт', 'share': 'Поділитись посиланням', 'copied': 'Рецепт скопійовано', 'shared': 'Посилання скопійовано', 'copy_fail': 'Не вдалося скопіювати — виділіть текст вручну',
  'conc_to': 'Розбавити до співвідношення', 'conc_add': 'Додати води після настоювання', 'conc_v': 'Концентрат', 'rtd_v': 'Готовий напій', 'cold_var': 'Вид колд брю',
  'cold_time': '12–16 год у холодильнику, не більше 24 год', 'cold_grind': 'Грубий, як для френч-преса',
  'esp_note': 'Еспресо рахують за вагою напою в чашці, а не води.', 'esp_dose_warn': 'Для подвійного кошика зазвичай 16–18 г. Перевірте місткість вашого кошика.',
  'esp_style': ['Ристретто', 'Нормале', 'Нормале+', 'Лунго'],
  'turka_note': 'Нагрівайте повільно й зніміть, коли підніметься піна. Не кип’ятіть.', 'turka_water': 'холодна вода',
  'moka_note': 'Заповніть кошик вщерть без трамбування, воду налийте до клапана. Не недосипайте кошик: слабшу каву краще розбавити водою.',
  'moka_ratio': 'Співвідношення (за вагою)', 'moka_out': 'Вийде концентрату',
  'src_sum': 'Звідки ці цифри', 'src_html': '<p>Співвідношення й стандарти: еталон «Золотої чашки» SCA — 55 г кави на літр води (≈1:18, допуск ±10%, тобто приблизно 1:16,5–1:20), міцність напою 1,15–1,35%, екстракція 18–22%. Рецепти для фільтра (1:16, 92–96 °C, 2:30–3:30), френч-преса (1:15, ≈93 °C, 4 хв), турки (≈7 г на 70 мл) й еспресо (18 г → 36 г за 25–30 с, 92–94 °C) — з гайда ZRN Coffee.</p><p>Аеропрес: 18 г на 210 г води, ≈96 °C, ≈2 хв (Counter Culture Coffee). Гейзер: від 1:7 до 1:10, таблиця розмірів — Complete Home Barista. Колд брю: готовий напій від 1:10 до 1:13, концентрат від 1:8, 12–16 год (Kaffeemacher). Еспресо: стилі ристретто, нормале, лунго — Seattle Coffee Gear.</p><p>Утримання води гущею: близько 2 мл/г у фільтрі, 3 мл/г в імерсії (Barista Hustle); для аеропреса (2,5) і колд брю (3) це наша оцінка. Калькулятор — орієнтир, а не стандарт: підлаштовуйте смак помелом і часом.</p>',
  'err_ratio': 'Це співвідношення надто концентроване для обраного способу',
  'link_hash': 'calc', 'noscript': 'Калькулятор потребує JavaScript. Таблиця з готовими значеннями — нижче на сторінці.',
  'meter_aria': 'Положення на шкалі міцності', 'gram_tip': 'Для точності зважуйте і каву, і воду.',
  'goal_hint_drink': 'Скільки напою має бути в чашках', 'copy_head': 'ZRN Coffee · калькулятор кави',
 },
 'ru': {
  'methods': {'filter': 'Фильтр / V60', 'press': 'Френч-пресс', 'aero': 'Аэропресс', 'espresso': 'Эспрессо', 'turka': 'Турка', 'moka': 'Гейзер', 'cold': 'Колд брю'},
  'aria_methods': 'Способ заваривания',
  'goals': {'drink': 'Хочу напитка', 'dose': 'Есть кофе', 'water': 'Налью воды', 'edose': 'Знаю дозу', 'yield': 'Хочу выход'},
  'aria_goal': 'Что вы знаете',
  'cups': 'Чашек', 'cupml': 'Объём чашки', 'ml': 'мл', 'g': 'г', 'dose': 'Кофе', 'water': 'Вода', 'yield': 'Напиток (выход)',
  'servings': 'Порций', 'per_serv': 'Воды на порцию', 'pot': 'Размер гейзера (чашек)', 'pot_note': 'Размер «чашки» в гейзере условный: это примерно 40–50 мл концентрата. Смотрите маркировку именно вашей кофеварки.',
  'ratio': 'Крепость (соотношение кофе к воде)', 'strong': 'Крепче', 'base': 'Базово', 'light': 'Легче', 'sca': 'SCA',
  'ret': 'Учесть воду, которую впитывает гуща', 'ret_h': 'Около 2 мл на 1 г кофе в фильтре и 3 мл в иммерсии (Barista Hustle). Без этого в чашке будет меньше, чем налили.',
  'ret_est': 'Для этого способа удержание воды — наша оценка.',
  'prec': 'Весы', 'prec1': 'точность 1 г', 'prec01': 'точность 0,1 г',
  'tds_h': 'Для профи: TDS и выход экстракции', 'tds_lab': 'TDS напитка, % (по рефрактометру)', 'tds_hint': 'Необязательно. EY = TDS × вес напитка ÷ вес кофе.',
  'ey': 'Выход экстракции (EY)', 'tds': 'Крепость (TDS)',
  'ey_under': 'Недоэкстрагировано: вкус кислый и пустой. Мелите мельче, увеличьте время или температуру.',
  'ey_ok': 'В «золотом» окне 18–22%.',
  'ey_over': 'Переэкстрагировано: горечь и сухость. Мелите крупнее, сократите время.',
  'tds_range_f': 'Типичный TDS фильтра: 1,15–1,45%.', 'tds_range_e': 'Типичный TDS эспрессо: 8–12%.',
  'out_dose': 'Кофе', 'out_water': 'Вода', 'out_drink': 'Получится напитка', 'out_conc': 'Получится концентрата', 'out_yield': 'Выход напитка',
  'f_ratio': 'Соотношение', 'f_perl': 'Кофе на литр воды', 'f_spoon': 'Ложки (без весов)', 'f_temp': 'Температура воды', 'f_time': 'Время', 'f_grind': 'Помол', 'f_out': 'Получится в чашках',
  'spoon_val': '≈ {a}–{b} ст. ложек', 'spoon_h': 'Ложка — ненадёжная мера: вес зависит от обжарки и помола (5–8 г на ст. ложку по одному из источников). Лучше взвешивать.',
  'bar_c': 'кофе', 'bar_w': 'вода',
  'v_low': 'Очень крепко: это уже концентрат', 'v_strong': 'Крепче эталона SCA (55 г/л ±10%). Распространённый выбор', 'v_sca': 'В пределах эталона SCA: 55 г на литр ±10%', 'v_weak': 'Легче эталона SCA',
  'sca_lab': 'Затенённая зона: эталон SCA (55 г/л ±10%)', 'sca_cap': ['1:10','1:22'],
  'copy': 'Скопировать рецепт', 'share': 'Поделиться ссылкой', 'copied': 'Рецепт скопирован', 'shared': 'Ссылка скопирована', 'copy_fail': 'Не удалось скопировать — выделите текст вручную',
  'conc_to': 'Разбавить до соотношения', 'conc_add': 'Добавить воды после настаивания', 'conc_v': 'Концентрат', 'rtd_v': 'Готовый напиток', 'cold_var': 'Вид колд брю',
  'cold_time': '12–16 ч в холодильнике, не более 24 ч', 'cold_grind': 'Крупный, как для френч-пресса',
  'esp_note': 'Эспрессо считают по весу напитка в чашке, а не воды.', 'esp_dose_warn': 'Для двойной корзины обычно 16–18 г. Проверьте вместимость вашей корзины.',
  'esp_style': ['Ристретто', 'Нормале', 'Нормале+', 'Лунго'],
  'turka_note': 'Нагревайте медленно и снимите, когда поднимется пена. Не кипятите.', 'turka_water': 'холодная вода',
  'moka_note': 'Заполните корзину вровень с краем без трамбовки, воду налейте до клапана. Не недосыпайте корзину: более слабый кофе лучше разбавить водой.',
  'moka_ratio': 'Соотношение (по весу)', 'moka_out': 'Получится концентрата',
  'src_sum': 'Откуда эти цифры', 'src_html': '<p>Соотношения и стандарты: эталон «Золотой чашки» SCA — 55 г кофе на литр воды (≈1:18, допуск ±10%, то есть примерно 1:16,5–1:20), крепость напитка 1,15–1,35%, экстракция 18–22%. Рецепты для фильтра (1:16, 92–96 °C, 2:30–3:30), френч-пресса (1:15, ≈93 °C, 4 мин), турки (≈7 г на 70 мл) и эспрессо (18 г → 36 г за 25–30 с, 92–94 °C) — из гайда ZRN Coffee.</p><p>Аэропресс: 18 г на 210 г воды, ≈96 °C, ≈2 мин (Counter Culture Coffee). Гейзер: от 1:7 до 1:10, таблица размеров — Complete Home Barista. Колд брю: готовый напиток от 1:10 до 1:13, концентрат от 1:8, 12–16 ч (Kaffeemacher). Эспрессо: стили ристретто, нормале, лунго — Seattle Coffee Gear.</p><p>Удержание воды гущей: около 2 мл/г в фильтре, 3 мл/г в иммерсии (Barista Hustle); для аэропресса (2,5) и колд брю (3) это наша оценка. Калькулятор — ориентир, а не стандарт: подстраивайте вкус помолом и временем.</p>',
  'err_ratio': 'Это соотношение слишком концентрированное для выбранного способа',
  'link_hash': 'calc', 'noscript': 'Калькулятору нужен JavaScript. Таблица с готовыми значениями — ниже на странице.',
  'meter_aria': 'Положение на шкале крепости', 'gram_tip': 'Для точности взвешивайте и кофе, и воду.',
  'goal_hint_drink': 'Сколько напитка должно быть в чашках', 'copy_head': 'ZRN Coffee · калькулятор кофе',
 },
}

CALC_JS = r"""
(function () {
  'use strict';
  var root = document.querySelector('[data-calc]');
  if (!root) return;
  var LANG = root.getAttribute('data-lang') === 'ru' ? 'ru' : 'uk';
  var TX = __TX__;
  var T = TX[LANG];

  var METHODS = {
    filter:   { r: 16,   min: 12, max: 20, k: 2,   cupMl: 250, cups: 1, temp: '92–96 °C', time: '2:30–3:30', est: false, sca: true,
                chips: [[15, 'strong'], [16, 'base'], [17, 'light'], [18.18, 'sca']] },
    press:    { r: 15,   min: 10, max: 20, k: 3,   cupMl: 250, cups: 1, temp: '≈93 °C', time: LANG === 'ru' ? '4 мин' : '4 хв', est: false,
                chips: [[14, 'strong'], [15, 'base'], [16, 'light']] },
    aero:     { r: 11.7, min: 8,  max: 18, k: 2.5, cupMl: 200, cups: 1, temp: '≈96 °C', time: '≈2:00', est: true,
                chips: [[10, 'strong'], [11.7, 'base'], [14, 'light']] },
    espresso: { r: 2,    min: 1,  max: 4,  dose: 18, temp: '92–94 °C', time: LANG === 'ru' ? '25–30 с' : '25–30 с' },
    turka:    { r: 10,   min: 8,  max: 12, serv: 1, per: 70, temp: null, time: null,
                chips: [[9, 'strong'], [10, 'base'], [11, 'light']] },
    moka:     { pots: { 1: [7, 60, '40–50'], 2: [14, 130, '90–100'], 3: [17, 180, '130–150'], 6: [35, 350, '250–280'] }, pot: 2 },
    cold:     { r: 10,   min: 8,  max: 14, k: 3,   cupMl: 250, cups: 1, est: true, variant: 'rtd', to: 12,
                chips: [[10, 'base'], [13, 'light']] }
  };
  var ORDER = ['filter', 'press', 'aero', 'espresso', 'turka', 'moka', 'cold'];

  var S = { m: 'filter', g: 'drink', cups: 1, cupMl: 250, dose: 18, water: 288, r: 16, ret: true, prec: 1,
            edose: 18, er: 2, tds: 0, pot: 2, serv: 1, per: 70, variant: 'rtd', to: 12 };

  function $(sel, el) { return (el || root).querySelector(sel); }
  function $$(sel, el) { return [].slice.call((el || root).querySelectorAll(sel)); }
  function clamp(x, a, b) { return Math.min(b, Math.max(a, x)); }
  function num(v) { var n = parseFloat(String(v).replace(',', '.').replace(/[^\d.\-]/g, '')); return isFinite(n) ? n : NaN; }
  function fmt(n, d) { var s = (Math.round(n * Math.pow(10, d)) / Math.pow(10, d)).toFixed(d); return s.replace('.', ','); }
  function fmtAuto(n) { return Math.abs(n - Math.round(n)) < 0.05 ? fmt(n, 0) : fmt(n, 1); }
  function ratioStr(r) { return '1:' + (Math.abs(r - Math.round(r)) < 0.005 ? fmt(r, 0) : (Math.abs(r * 10 - Math.round(r * 10)) < 0.01 ? fmt(r, 1) : fmt(r, 2))); }
  function ratio1(r) { return '1:' + fmtAuto(r); }
  function round(n, step) { return Math.round(n / step) * step; }

  // ---------- каркас ----------
  function build() {
    var h = '';
    h += '<div class="calc-methods" role="group" aria-label="' + T.aria_methods + '">';
    ORDER.forEach(function (k) { h += '<button type="button" data-m="' + k + '" aria-pressed="false">' + T.methods[k] + '</button>'; });
    h += '</div><div class="calc-grid"><div class="calc-in">';
    h += '<div class="calc-sec" data-sec="goal"><span class="calc-lab">' + T.aria_goal + '</span><div class="calc-seg" role="group" aria-label="' + T.aria_goal + '" data-goalseg></div></div>';
    h += '<div class="calc-sec" data-sec="variant"><span class="calc-lab">' + T.cold_var + '</span><div class="calc-seg" role="group" data-varseg>' +
         '<button type="button" data-v="rtd" aria-pressed="true">' + T.rtd_v + '</button><button type="button" data-v="conc" aria-pressed="false">' + T.conc_v + '</button></div></div>';
    h += '<div class="calc-sec" data-sec="cups"><span class="calc-lab">' + T.cups + ' × ' + T.cupml + '</span><div class="calc-row">' +
         numBox('cups', 1, '') + '<span class="calc-unit">×</span>' + numBox('cupMl', 10, T.ml) + '</div>' +
         '<div class="calc-chips" data-chips="cupMl"></div></div>';
    h += '<div class="calc-sec" data-sec="dose"><label class="calc-lab" for="c-dose">' + T.dose + '</label><div class="calc-row">' + numBox('dose', 1, T.g, 'c-dose') + '</div></div>';
    h += '<div class="calc-sec" data-sec="water"><label class="calc-lab" for="c-water">' + T.water + '</label><div class="calc-row">' + numBox('water', 10, T.ml, 'c-water') + '</div></div>';
    h += '<div class="calc-sec" data-sec="serv"><span class="calc-lab">' + T.servings + ' × ' + T.per_serv + '</span><div class="calc-row">' +
         numBox('serv', 1, '') + '<span class="calc-unit">×</span>' + numBox('per', 10, T.ml) + '</div></div>';
    h += '<div class="calc-sec" data-sec="pot"><span class="calc-lab">' + T.pot + '</span><div class="calc-chips" data-chips="pot"></div><p class="calc-unit" style="margin:8px 0 0;font-size:.8rem">' + T.pot_note + '</p></div>';
    h += '<div class="calc-sec" data-sec="ratio"><span class="calc-lab">' + T.ratio + '</span><div class="calc-rv" data-rv></div>' +
         '<input type="range" data-range aria-label="' + T.ratio + '">' +
         '<div class="calc-chips" data-chips="ratio"></div>' +
         '<div data-meterwrap><div class="calc-meter" role="img" aria-label="' + T.meter_aria + '"><i data-sca></i><b data-pos></b></div><div class="calc-meter-l"><span>' + T.sca_cap[0] + '</span><span>' + T.sca_cap[1] + '</span></div><div class="calc-meter-n">' + T.sca_lab + '</div></div></div>';
    h += '<div class="calc-sec" data-sec="conc"><span class="calc-lab">' + T.conc_to + '</span><div class="calc-rv" data-tv></div><input type="range" data-torange min="10" max="13" step="0.5" aria-label="' + T.conc_to + '"></div>';
    h += '<div class="calc-sec" data-sec="opts"><label class="calc-check" data-retwrap><input type="checkbox" data-ret checked><span>' + T.ret + '<small data-reth>' + T.ret_h + '</small></span></label>' +
         '<div style="margin-top:12px"><span class="calc-lab">' + T.prec + '</span><div class="calc-seg" role="group" aria-label="' + T.prec + '" data-precseg>' +
         '<button type="button" data-p="1" aria-pressed="true">' + T.prec1 + '</button><button type="button" data-p="0.1" aria-pressed="false">' + T.prec01 + '</button></div></div></div>';
    h += '<div class="calc-sec" data-sec="tds"><label class="calc-lab" for="c-tds">' + T.tds_h + '</label><div class="calc-row"><div class="calc-num"><input type="text" inputmode="decimal" autocomplete="off" id="c-tds" data-tds placeholder="1,35" aria-label="' + T.tds_lab + '"></div><span class="calc-unit">% TDS</span></div><p class="calc-unit" style="margin:8px 0 0;font-size:.8rem">' + T.tds_hint + '</p></div>';
    h += '</div><div class="calc-out" aria-live="polite" data-out></div></div>';
    h += '<details class="calc-src"><summary>' + T.src_sum + '</summary>' + T.src_html + '</details>';
    root.innerHTML = h;
  }
  function numBox(key, step, unit, id) {
    var lab = { cups: T.cups, cupMl: T.cupml, dose: T.dose, water: T.water, serv: T.servings, per: T.per_serv }[key] || key;
    return '<div class="calc-num"><button type="button" data-dec="' + key + '" aria-label="− ' + lab + '">−</button>' +
           '<input type="text" inputmode="decimal" autocomplete="off" data-in="' + key + '"' + (id ? ' id="' + id + '"' : '') + ' aria-label="' + lab + '">' +
           '<button type="button" data-inc="' + key + '" aria-label="+ ' + lab + '">+</button></div>' + (unit ? '<span class="calc-unit">' + unit + '</span>' : '');
  }

  // ---------- розрахунок ----------
  function calc() {
    var m = S.m, c = METHODS[m], o = { warn: [], facts: [], notes: [] };
    var step = S.prec;
    function rd(n) { return Math.max(0, round(n, step)); }
    if (m === 'espresso') {
      var dose, yld, r = S.er;
      if (S.g === 'yield') { yld = S.edose; dose = Math.max(step, rd(yld / r)); }
      else { dose = Math.max(step, rd(S.edose)); yld = dose * r; }
      o.dose = dose; o.water = null; o.yield = yld; o.ratio = yld / dose; o.mode = 'espresso';
      if (dose < 14 || dose > 22) o.warn.push(T.esp_dose_warn);
      return o;
    }
    if (m === 'moka') {
      var p = c.pots[S.pot]; o.dose = p[0]; o.water = p[1]; o.yield = p[2]; o.ratio = p[1] / p[0]; o.mode = 'moka'; return o;
    }
    if (m === 'turka') {
      var water = S.serv * S.per; var d = rd(water / S.r);
      o.dose = d; o.water = water; o.ratio = water / Math.max(d, 0.0001); o.mode = 'turka'; return o;
    }
    // фільтр, прес, аеропрес, колд брю
    var k = S.ret ? c.k : 0, r2 = S.r, dose2, water2;
    if (r2 - k < 1.2) { o.error = T.err_ratio; r2 = k + 1.2; }
    if (S.g === 'drink') {
      var drink = S.cups * S.cupMl;
      dose2 = rd(drink / (r2 - k)); if (dose2 <= 0) dose2 = step;
      water2 = Math.round(dose2 * r2);
    } else if (S.g === 'dose') {
      dose2 = rd(S.dose); if (dose2 <= 0) dose2 = step; water2 = Math.round(dose2 * r2);
    } else {
      water2 = Math.round(S.water); dose2 = rd(water2 / r2); if (dose2 <= 0) dose2 = step;
    }
    o.dose = dose2; o.water = water2; o.ratio = water2 / dose2; o.k = k;
    o.drink = Math.max(0, water2 - k * dose2); o.mode = 'brew';
    return o;
  }

  // ---------- вивід ----------
  function verdict(r) {
    if (r < 12) return ['warn', T.v_low];
    if (r < 16.5) return ['', T.v_strong];
    if (r <= 20.2) return ['ok', T.v_sca];
    return ['', T.v_weak];
  }
  function render() {
    var m = S.m, c = METHODS[m], o = calc(), h = '';
    var brew = (o.mode === 'brew');
    // стан контролів
    $$('[data-m]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-m') === m)); });
    var isEsp = m === 'espresso', isMoka = m === 'moka', isTurka = m === 'turka', isCold = m === 'cold';
    show('goal', !isMoka && !isTurka);
    show('variant', isCold);
    show('cups', brew && S.g === 'drink');
    show('dose', (brew && S.g === 'dose') || isEsp);
    show('water', brew && S.g === 'water');
    show('serv', isTurka); show('pot', isMoka);
    show('ratio', !isMoka);
    show('conc', isCold && S.variant === 'conc');
    show('opts', brew || isEsp || isTurka);
    show('tds', (brew && !isCold) || isEsp);
    var retw = $('[data-retwrap]'); retw.hidden = !brew;
    $('[data-reth]').textContent = T.ret_h + (c.est ? ' ' + T.ret_est : '');
    // сегмент цілей
    var gs = $('[data-goalseg]'), gl = isEsp ? ['edose', 'yield'] : ['drink', 'dose', 'water'];
    var gmap = { edose: 'dose', yield: 'yield' };
    gs.innerHTML = gl.map(function (g) { var val = gmap[g] || g; return '<button type="button" data-g="' + val + '" aria-pressed="' + (S.g === val) + '">' + T.goals[g] + '</button>'; }).join('');
    $$('[data-varseg] button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === S.variant)); });
    $$('[data-precseg] button').forEach(function (b) { b.setAttribute('aria-pressed', String(parseFloat(b.getAttribute('data-p')) === S.prec)); });
    $('[data-ret]').checked = S.ret;
    // поля
    setIn('cups', S.cups); setIn('cupMl', S.cupMl); setIn('serv', S.serv); setIn('per', S.per);
    setIn('dose', isEsp ? S.edose : S.dose);
    setIn('water', S.water);
    var ti = $('[data-tds]'); if (ti && document.activeElement !== ti) ti.value = S.tds > 0 ? fmt(S.tds, 2) : '';
    var doseLab = $('label[for="c-dose"]'); doseLab.textContent = isEsp ? (S.g === 'yield' ? T.yield + ', ' + T.g : T.dose + ', ' + T.g) : T.dose + ', ' + T.g;
    var wl = $('label[for="c-water"]'); wl.textContent = T.water + ', ' + T.ml;
    $('[data-chips=cupMl]').innerHTML = [150, 200, 250, 300, 350, 500].map(function (v) { return '<button type="button" data-cup="' + v + '" aria-pressed="' + (S.cupMl === v) + '">' + v + '</button>'; }).join('');
    $('[data-chips=pot]').innerHTML = [1, 2, 3, 6].map(function (v) { return '<button type="button" data-pot="' + v + '" aria-pressed="' + (S.pot === v) + '">' + v + '</button>'; }).join('');
    // співвідношення
    var rng = $('[data-range]'), rv = $('[data-rv]'), curR = isEsp ? S.er : S.r;
    if (isEsp) { rng.min = 1; rng.max = 4; rng.step = 0.05; } else if (isCold && S.variant === 'conc') { rng.min = 4; rng.max = 10; rng.step = 0.1; } else { rng.min = c.min || 8; rng.max = c.max || 20; rng.step = 0.1; }
    rng.value = curR; rv.textContent = isEsp ? ratioStr(curR) : ratioStr(curR);
    var chips = isEsp ? [[1.5, 0], [2, 1], [2.5, 2], [3, 3]] : (isCold && S.variant === 'conc' ? [[8, 'base']] : (c.chips || []));
    $('[data-chips=ratio]').innerHTML = chips.map(function (ch) {
      var label = isEsp ? T.esp_style[ch[1]] : T[ch[1]];
      return '<button type="button" data-rc="' + ch[0] + '" aria-pressed="' + (Math.abs(ch[0] - curR) < 0.03) + '">' + label + ' ' + ratioStr(ch[0] === 18.18 ? 18 : ch[0]) + '</button>';
    }).join('');
    var mw = $('[data-meterwrap]'); mw.hidden = !(m === 'filter');
    if (m === 'filter') {
      var lo = 10, hi = 22; function pos(x) { return clamp((x - lo) / (hi - lo), 0, 1) * 100; }
      var sca = $('[data-sca]'); sca.style.left = pos(16.5) + '%'; sca.style.width = (pos(20.2) - pos(16.5)) + '%';
      $('[data-pos]').style.left = pos(S.r) + '%';
    }
    if (isCold) { $('[data-torange]').value = S.to; $('[data-tv]').textContent = ratioStr(S.to); }
    // результати
    if (o.mode === 'espresso') {
      h += '<div class="calc-big"><div><span>' + T.out_dose + '</span><strong>' + fmtAuto(o.dose) + '<small>' + T.g + '</small></strong></div>' +
           '<div><span>' + T.out_yield + '</span><strong>' + fmtAuto(o.yield) + '<small>' + T.g + '</small></strong></div></div>';
      h += barHtml(o.dose, o.yield, true);
      h += '<ul class="calc-facts"><li><span>' + T.f_ratio + '</span><b>' + ratioStr(o.yield / o.dose) + '</b></li>' +
           '<li><span>' + T.f_temp + '</span><b>' + c.temp + '</b></li><li><span>' + T.f_time + '</span><b>' + c.time + '</b></li></ul>';
      h += '<p class="calc-note">' + T.esp_note + '</p>';
    } else if (o.mode === 'moka') {
      h += '<div class="calc-big"><div><span>' + T.out_dose + '</span><strong>' + o.dose + '<small>' + T.g + '</small></strong></div>' +
           '<div><span>' + T.out_water + '</span><strong>' + o.water + '<small>' + T.ml + '</small></strong></div>' +
           '<div class="calc-wide"><span>' + T.moka_out + '</span><strong>' + o.yield + '<small>' + T.ml + '</small></strong></div></div>';
      h += '<ul class="calc-facts"><li><span>' + T.moka_ratio + '</span><b>' + ratioStr(o.ratio) + '</b></li></ul><p class="calc-note">' + T.moka_note + '</p>';
    } else if (o.mode === 'turka') {
      h += '<div class="calc-big"><div><span>' + T.out_dose + '</span><strong>' + fmtAuto(o.dose) + '<small>' + T.g + '</small></strong></div>' +
           '<div><span>' + T.out_water + '</span><strong>' + o.water + '<small>' + T.ml + '</small></strong></div></div>';
      h += barHtml(o.dose, o.water, false);
      h += '<ul class="calc-facts"><li><span>' + T.f_ratio + '</span><b>' + ratioStr(o.ratio) + '</b></li><li><span>' + T.f_spoon + '</span><b>' + spoon(o.dose) + '</b></li></ul>';
      h += '<p class="calc-note">' + T.turka_note + ' (' + T.turka_water + ')</p>';
    } else {
      if (o.error) h += '<p class="calc-note warn">' + o.error + '</p>';
      h += '<div class="calc-big"><div><span>' + T.out_dose + '</span><strong>' + fmtAuto(o.dose) + '<small>' + T.g + '</small></strong></div>' +
           '<div><span>' + T.out_water + '</span><strong>' + o.water + '<small>' + T.ml + '</small></strong></div>' +
           '<div class="calc-wide"><span>' + ((isCold && S.variant === 'conc') ? T.out_conc : T.out_drink) + '</span><strong>≈ ' + Math.round(o.drink) + '<small>' + T.ml + '</small></strong></div></div>';
      h += barHtml(o.dose, o.water, false);
      h += '<ul class="calc-facts"><li><span>' + T.f_ratio + '</span><b>' + ratio1(o.ratio) + '</b></li>' +
           '<li><span>' + T.f_perl + '</span><b>' + fmt(1000 / o.ratio, 1) + ' ' + T.g + '</b></li>';
      if (S.g === 'drink' && S.cups > 1) h += '<li><span>' + T.f_out + '</span><b>' + S.cups + ' × ' + S.cupMl + ' ' + T.ml + '</b></li>';
      h += '<li><span>' + T.f_spoon + '</span><b>' + spoon(o.dose) + '</b></li>';
      if (c.temp) h += '<li><span>' + T.f_temp + '</span><b>' + c.temp + '</b></li><li><span>' + T.f_time + '</span><b>' + c.time + '</b></li>';
      if (isCold) h += '<li><span>' + T.f_time + '</span><b>' + T.cold_time + '</b></li><li><span>' + T.f_grind + '</span><b>' + T.cold_grind + '</b></li>';
      h += '</ul>';
      if (m === 'filter') { var v = verdict(o.ratio); h += '<p class="calc-note ' + v[0] + '">' + v[1] + '</p>'; }
      if (isCold && S.variant === 'conc') {
        var add = Math.max(0, Math.round(o.dose * (S.to - o.ratio)));
        var fin = Math.round(Math.max(0, o.dose * S.to - (S.ret ? c.k : 0) * o.dose));
        h += '<p class="calc-note ok"><b>' + T.conc_add + ': ' + add + ' ' + T.ml + '</b> (' + ratioStr(S.to) + ' → ≈ ' + fin + ' ' + T.ml + ')</p>';
      }
    }
    if (S.tds > 0 && (isEsp || (brew && !isCold))) {
      var bev = isEsp ? o.yield : o.drink, ey = S.tds * bev / o.dose, vc = (ey >= 18 && ey <= 22) ? 'ok' : '', vt = ey < 18 ? T.ey_under : (ey <= 22 ? T.ey_ok : T.ey_over);
      h += '<ul class="calc-facts"><li><span>' + T.tds + '</span><b>' + fmt(S.tds, 2) + '%</b></li><li><span>' + T.ey + '</span><b>' + fmt(ey, 1) + '%</b></li></ul>';
      h += '<p class="calc-note ' + vc + '">' + vt + ' ' + (isEsp ? T.tds_range_e : T.tds_range_f) + '</p>';
    }
    (o.warn || []).forEach(function (w) { h += '<p class="calc-note warn">' + w + '</p>'; });
    h += '<div class="calc-act"><button type="button" data-copy>' + T.copy + '</button><button type="button" data-share>' + T.share + '</button></div><div class="calc-toast" data-toast></div>';
    $('[data-out]').innerHTML = h;
    root._o = o;
    saveState();
  }
  function barHtml(a, b, esp) {
    var tot = a + b, w = clamp(a / tot * 100, 8, 50);
    return '<div class="calc-bar" aria-hidden="true"><i style="width:' + w + '%">' + T.bar_c + '</i><i>' + (esp ? T.out_yield.toLowerCase() : T.bar_w) + '</i></div>';
  }
  function spoon(d) { return T.spoon_val.replace('{a}', fmtAuto(Math.max(0.5, d / 8))).replace('{b}', fmtAuto(Math.max(0.5, d / 5))); }
  function show(sec, on) { var e = $('[data-sec="' + sec + '"]'); if (e) e.hidden = !on; }
  function setIn(key, val) {
    var i = $('[data-in="' + key + '"]'); if (!i || document.activeElement === i) return;
    i.value = fmtAuto(val);
  }

  // ---------- стан ----------
  var LIM = { cups: [1, 24], cupMl: [30, 1000], dose: [1, 300], water: [30, 5000], serv: [1, 12], per: [30, 200] };
  function setVal(key, v, fromInput) {
    if (key === 'dose' && S.m === 'espresso') { S.edose = clamp(v, 5, 60); return; }
    var l = LIM[key]; if (!l) return; S[key] = clamp(v, l[0], l[1]);
  }
  function applyMethod(m) {
    var c = METHODS[m], prev = S.m; S.m = m; if ((prev === 'espresso') !== (m === 'espresso')) S.tds = 0;
    if (m === 'espresso') { if (S.g !== 'yield') S.g = 'dose'; if (S.er < 1 || S.er > 4) S.er = c.r; }
    else if (m === 'moka') { S.g = 'drink'; }
    else if (m === 'turka') { S.g = 'drink'; if (prev !== 'turka' || S.r < c.min || S.r > c.max) S.r = c.r; }
    else {
      if (S.g === 'yield') S.g = 'drink';
      S.r = c.r; S.ret = true; S.variant = 'rtd';
      if (!S.cupMlTouched) S.cupMl = c.cupMl;
    }
  }
  function saveState() { try { localStorage.setItem('zrn-calc', JSON.stringify({ m: S.m, prec: S.prec, cupMl: S.cupMl })); } catch (e) {} }
  function loadState() {
    try {
      var s = JSON.parse(localStorage.getItem('zrn-calc') || 'null');
      if (s) { if (METHODS[s.m]) { applyMethod(s.m); } if (s.prec === 0.1) S.prec = 0.1; if (s.cupMl >= 30 && s.cupMl <= 1000) { S.cupMl = s.cupMl; S.cupMlTouched = true; } }
    } catch (e) {}
    var h = location.hash || '';
    if (h.indexOf('#calc=') === 0) {
      var p = {}; h.slice(6).split(',').forEach(function (kv) { var a = kv.split(':'); p[a[0]] = a[1]; });
      if (METHODS[p.m]) { applyMethod(p.m); }
      if (p.g && /^(drink|dose|water|yield)$/.test(p.g)) S.g = p.g;
      if (p.c) S.cups = clamp(parseInt(p.c, 10) || 1, 1, 24);
      if (p.s) { S.cupMl = clamp(num(p.s) || 250, 30, 1000); S.cupMlTouched = true; }
      if (p.d) { var dv = num(p.d); if (isFinite(dv)) { if (S.m === 'espresso') S.edose = clamp(dv, 5, 60); else S.dose = clamp(dv, 1, 300); } }
      if (p.w) { var wv = num(p.w); if (isFinite(wv)) S.water = clamp(wv, 30, 5000); }
      if (p.r) { var rv = num(p.r); if (isFinite(rv)) { if (S.m === 'espresso') S.er = clamp(rv, 1, 4); else S.r = clamp(rv, 4, 25); } }
      if (p.p === '0.1') S.prec = 0.1;
      if (p.v === 'conc') S.variant = 'conc';
      if (p.x) S.pot = METHODS.moka.pots[p.x] ? parseInt(p.x, 10) : 2;
      if (p.t) S.serv = clamp(parseInt(p.t, 10) || 1, 1, 12);
      if (p.e) S.per = clamp(num(p.e) || 70, 30, 200);
      if (p.n === '0') S.ret = false;
      if (p.z) { var zv = num(p.z); if (isFinite(zv) && zv > 0) S.tds = clamp(zv, 0.05, 15); }
      setTimeout(function () { try { root.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) {} }, 300);
    }
  }
  function hashState() {
    var a = ['m:' + S.m];
    if (S.m === 'espresso') { a.push('g:' + S.g, 'd:' + S.edose, 'r:' + S.er); }
    else if (S.m === 'moka') { a.push('x:' + S.pot); }
    else if (S.m === 'turka') { a.push('t:' + S.serv, 'e:' + S.per, 'r:' + S.r); }
    else { a.push('g:' + S.g, 'r:' + S.r); if (S.g === 'drink') a.push('c:' + S.cups, 's:' + S.cupMl); if (S.g === 'dose') a.push('d:' + S.dose); if (S.g === 'water') a.push('w:' + S.water); if (!S.ret) a.push('n:0'); if (S.m === 'cold' && S.variant === 'conc') a.push('v:conc'); }
    if (S.prec === 0.1) a.push('p:0.1');
    if (S.tds > 0) a.push('z:' + S.tds);
    return '#calc=' + a.join(',');
  }
  function recipeText() {
    var o = root._o, c = METHODS[S.m], t = T.copy_head + ' — ' + T.methods[S.m] + '\n';
    if (o.mode === 'espresso') t += T.out_dose + ': ' + fmtAuto(o.dose) + ' ' + T.g + ' → ' + T.out_yield.toLowerCase() + ': ' + fmtAuto(o.yield) + ' ' + T.g + ' (' + ratioStr(o.yield / o.dose) + ')\n';
    else if (o.mode === 'moka') t += T.out_dose + ': ' + o.dose + ' ' + T.g + ', ' + T.out_water.toLowerCase() + ': ' + o.water + ' ' + T.ml + ' (' + ratioStr(o.ratio) + ')\n';
    else { t += T.out_dose + ': ' + fmtAuto(o.dose) + ' ' + T.g + ' + ' + T.out_water.toLowerCase() + ': ' + o.water + ' ' + T.ml + ' (' + ratioStr(o.ratio) + ')\n'; if (o.drink != null && o.mode === 'brew') t += T.out_drink + ' ≈ ' + Math.round(o.drink) + ' ' + T.ml + '\n'; }
    if (c && c.temp) t += T.f_temp + ': ' + c.temp + (c.time ? ', ' + T.f_time.toLowerCase() + ': ' + c.time : '') + '\n';
    return t.trim();
  }
  function copy(text, okMsg) {
    var toast = $('[data-toast]');
    function done(ok) { if (toast) toast.textContent = ok ? okMsg : T.copy_fail; }
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(); }); } else fallback();
    function fallback() {
      try { var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); var ok = document.execCommand('copy'); document.body.removeChild(ta); done(ok); } catch (e) { done(false); }
    }
  }

  // ---------- події ----------
  root.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('button') : null; if (!b || !root.contains(b)) return;
    if (b.hasAttribute('data-m')) { applyMethod(b.getAttribute('data-m')); }
    else if (b.hasAttribute('data-g')) { S.g = b.getAttribute('data-g'); if (S.g === 'dose' && S.m !== 'espresso') S.dose = (root._o && root._o.dose) ? root._o.dose : S.dose; if (S.g === 'water' && root._o && root._o.water) S.water = root._o.water; }
    else if (b.hasAttribute('data-v')) { S.variant = b.getAttribute('data-v'); S.r = S.variant === 'conc' ? 8 : 10; }
    else if (b.hasAttribute('data-p')) { S.prec = parseFloat(b.getAttribute('data-p')); }
    else if (b.hasAttribute('data-cup')) { S.cupMl = parseInt(b.getAttribute('data-cup'), 10); S.cupMlTouched = true; }
    else if (b.hasAttribute('data-pot')) { S.pot = parseInt(b.getAttribute('data-pot'), 10); }
    else if (b.hasAttribute('data-rc')) { var v = parseFloat(b.getAttribute('data-rc')); if (S.m === 'espresso') S.er = v; else S.r = v; }
    else if (b.hasAttribute('data-inc') || b.hasAttribute('data-dec')) {
      var key = b.getAttribute('data-inc') || b.getAttribute('data-dec'), sign = b.hasAttribute('data-inc') ? 1 : -1;
      var st = { cups: 1, cupMl: 10, dose: S.prec, water: 10, serv: 1, per: 10 }[key] || 1;
      var cur = (key === 'dose' && S.m === 'espresso') ? S.edose : S[key]; if (key === 'cupMl') S.cupMlTouched = true;
      setVal(key, Math.round((cur + sign * st) * 10) / 10);
    }
    else if (b.hasAttribute('data-copy')) { copy(recipeText() + '\n' + location.href.split('#')[0] + hashState(), T.copied); return; }
    else if (b.hasAttribute('data-share')) { var url = location.href.split('#')[0] + hashState(); try { history.replaceState(null, '', hashState()); } catch (e2) {} copy(url, T.shared); return; }
    else return;
    render();
  });
  root.addEventListener('input', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-range')) { var v = parseFloat(t.value); if (S.m === 'espresso') S.er = Math.round(v * 20) / 20; else S.r = Math.round(v * 10) / 10; render(); return; }
    if (t.hasAttribute('data-torange')) { S.to = parseFloat(t.value); render(); return; }
    if (t.hasAttribute('data-ret')) { S.ret = t.checked; render(); return; }
    if (t.hasAttribute('data-tds')) { var tv = num(t.value); S.tds = (isFinite(tv) && tv > 0) ? clamp(tv, 0.05, 15) : 0; render(); return; }
    if (t.hasAttribute('data-in')) { var key = t.getAttribute('data-in'), n = num(t.value); if (isFinite(n) && n > 0) { if (key === 'cupMl') S.cupMlTouched = true; setVal(key, n); render(); } }
  });
  root.addEventListener('focusout', function (e) { var t = e.target; if (t.hasAttribute && t.hasAttribute('data-in')) setTimeout(function () { render(); var k = t.getAttribute('data-in'); setIn(k, (k === 'dose' && S.m === 'espresso') ? S.edose : S[k]); }, 0); });

  build(); loadState(); render();
})();
"""

def widget_html(lang):
    t = TXT[lang]
    return ('<div class="calc" data-calc data-lang="%s" id="calc-widget"><p class="calc-noscript">%s</p></div>\n'
            '<script src="/calc.js" defer></script>\n' % (lang, t['noscript']))

def js():
    return CALC_JS.replace('__TX__', json.dumps(TXT, ensure_ascii=False))


# ===================== окрема сторінка /calculator/ =====================
CPAGE = {
 'uk': {
  'title': 'Калькулятор кави онлайн: скільки грамів кави на воду | ZRN Coffee',
  'desc': 'Безкоштовний калькулятор кави: оберіть спосіб (фільтр, френч-прес, еспресо, турка, гейзер, колд брю) і обсяг чашки, отримайте грами кави й води.',
  'kicker': 'Інструмент', 'h1': 'Калькулятор кави: скільки грамів кави на воду',
  'lead': 'Оберіть спосіб заварювання, обсяг чашки й бажану міцність: калькулятор покаже, скільки грамів кави й води взяти. Він враховує воду, яку вбирає гуща, тож у чашці вийде стільки напою, скільки ви планували.',
  'h_use': 'Як користуватися калькулятором',
  'steps': ['Оберіть спосіб: фільтр, френч-прес, аеропрес, еспресо, турка, гейзер або колд брю.',
            'Скажіть, що вам відомо: скільки напою хочете, скільки кави маєте або скільки води наллєте.',
            'Підберіть міцність: базове співвідношення вже виставлено, а кнопки (наприклад, 1:15, 1:16, 1:17) змінюють її на крок.',
            'Скопіюйте рецепт або посилання зі своїми налаштуваннями, щоб повторити його завтра.'],
  'h_how': 'Як працює розрахунок',
  'how': ['Основа — співвідношення кави до води за вагою: **кава (г) = вода (г) ÷ співвідношення**. Оскільки 1 мл води при кімнатній температурі важить приблизно 1 г, воду можна рахувати і в мілілітрах.',
          'Мелена кава вбирає воду, тому в чашку потрапляє менше, ніж ви налили. За Barista Hustle, це близько 2 мл на 1 г кави у фільтрі й близько 3 мл в імерсії (френч-прес). Коли ви вказуєте, скільки напою хочете, калькулятор рахує так: **кава = напій ÷ (співвідношення − утримання)**. Приклад: 250 мл у фільтрі при 1:16 дають 250 ÷ 14 ≈ 18 г кави й 288 г води.',
          'Еспресо рахують за вагою напою: 18 г кави → 36 г напою означає 1:2. Для гейзера дозу задає кошик, тому калькулятор бере табличні значення за розміром кавоварки.'],
  'h_tbl': 'Базові пропорції за способом',
  'tbl_head': ['Спосіб', 'Співвідношення', 'Приклад', 'Звідки'],
  'tbl': [['Еспресо', '1:2 (за вагою напою)', '18 г → 36 г за 25–30 с, 92–94 °C', 'Гайд ZRN'],
          ['Фільтр, V60', '1:16', '15 г на 240 мл, 2:30–3:30', 'Гайд ZRN'],
          ['Френч-прес', '1:15', '4 хв, ≈93 °C', 'Гайд ZRN'],
          ['Турка', 'приблизно 1:10', '7 г на 70 мл холодної води', 'Гайд ZRN'],
          ['Аеропрес', 'приблизно 1:12', '18 г на 210 г води, ≈2 хв', 'Counter Culture Coffee'],
          ['Гейзер', 'від 1:7 до 1:10', 'кошик вщерть, без трамбування', 'Complete Home Barista'],
          ['Колд брю', 'від 1:10 до 1:13 (концентрат від 1:8)', '12–16 год', 'Kaffeemacher']],
  'h_more': 'Читайте також',
  'more': [('/blog/skilky-kavy-na-chashku/', 'Скільки кави на чашку: пропорції, таблиця грамів і розрахунок за способом'),
           ('/blog/yak-pravylno-molotty-kavu/', 'Як правильно молоти каву'),
           ('/blog/espreso-kyslo-chy-hirko/', 'Як налаштувати еспресо: кисло чи гірко')],
  'h_faq': 'Часті запитання',
  'faq': [('Скільки грамів кави на 250 мл води?', 'При співвідношенні 1:16 це близько 15,6 г кави. Якщо вам потрібно саме 250 мл напою в чашці, води треба більше, бо гуща вбирає близько 2 мл на 1 г кави у фільтрі: це приблизно 18 г кави й 288 г води.'),
          ('Яке співвідношення кави й води найкраще?', 'Універсального немає. Для фільтра базове в нашому гайді — 1:16; еталон «Золотої чашки» SCA — 55 г на літр (≈1:18) з допуском ±10%. Еспресо рахують за вагою напою (1:2), турку — приблизно 1:10.'),
          ('Чому в чашці менше води, ніж я налив?', 'Мелена кава вбирає воду: близько 2 мл на 1 г кави у фільтрі й близько 3 мл в імерсії (Barista Hustle). Калькулятор може врахувати це, і тоді води більше, ніж потрібно напою.'),
          ('Чи можна відмірювати каву ложками?', 'Це ненадійно: вага ложки залежить від обсмаження й помелу, за одним із джерел від 5 до 8 г на столову ложку. Калькулятор показує ложки лише як орієнтир; краще зважувати.'),
          ('Як порахувати каву для гейзерної кавоварки?', 'Оберіть «Гейзер» і розмір вашої кавоварки: калькулятор покаже дозу, воду й орієнтовний вихід за таблицею. Кошик заповнюють вщерть без трамбування, а воду наливають до клапана.')],
  'related_label': 'Статті на цю тему',
  'app_name': 'Калькулятор кави ZRN Coffee', 'bread': 'Калькулятор кави',
 },
 'ru': {
  'title': 'Калькулятор кофе онлайн: сколько граммов кофе на воду | ZRN Coffee',
  'desc': 'Бесплатный калькулятор кофе: выберите способ (фильтр, френч-пресс, эспрессо, турка, гейзер, колд брю) и объём чашки, получите граммы кофе и воды.',
  'kicker': 'Инструмент', 'h1': 'Калькулятор кофе: сколько граммов кофе на воду',
  'lead': 'Выберите способ заваривания, объём чашки и желаемую крепость: калькулятор покажет, сколько граммов кофе и воды взять. Он учитывает воду, которую впитывает гуща, поэтому в чашке получится столько напитка, сколько вы планировали.',
  'h_use': 'Как пользоваться калькулятором',
  'steps': ['Выберите способ: фильтр, френч-пресс, аэропресс, эспрессо, турка, гейзер или колд брю.',
            'Скажите, что вам известно: сколько напитка хотите, сколько кофе есть или сколько воды нальёте.',
            'Подберите крепость: базовое соотношение уже выставлено, а кнопки (например, 1:15, 1:16, 1:17) меняют его на шаг.',
            'Скопируйте рецепт или ссылку со своими настройками, чтобы повторить его завтра.'],
  'h_how': 'Как работает расчёт',
  'how': ['Основа — соотношение кофе к воде по весу: **кофе (г) = вода (г) ÷ соотношение**. Поскольку 1 мл воды при комнатной температуре весит примерно 1 г, воду можно считать и в миллилитрах.',
          'Молотый кофе впитывает воду, поэтому в чашку попадает меньше, чем вы налили. По Barista Hustle, это около 2 мл на 1 г кофе в фильтре и около 3 мл в иммерсии (френч-пресс). Когда вы указываете, сколько напитка хотите, калькулятор считает так: **кофе = напиток ÷ (соотношение − удержание)**. Пример: 250 мл в фильтре при 1:16 дают 250 ÷ 14 ≈ 18 г кофе и 288 г воды.',
          'Эспрессо считают по весу напитка: 18 г кофе → 36 г напитка означает 1:2. Для гейзера дозу задаёт корзина, поэтому калькулятор берёт табличные значения по размеру кофеварки.'],
  'h_tbl': 'Базовые пропорции по способу',
  'tbl_head': ['Способ', 'Соотношение', 'Пример', 'Откуда'],
  'tbl': [['Эспрессо', '1:2 (по весу напитка)', '18 г → 36 г за 25–30 с, 92–94 °C', 'Гайд ZRN'],
          ['Фильтр, V60', '1:16', '15 г на 240 мл, 2:30–3:30', 'Гайд ZRN'],
          ['Френч-пресс', '1:15', '4 мин, ≈93 °C', 'Гайд ZRN'],
          ['Турка', 'примерно 1:10', '7 г на 70 мл холодной воды', 'Гайд ZRN'],
          ['Аэропресс', 'примерно 1:12', '18 г на 210 г воды, ≈2 мин', 'Counter Culture Coffee'],
          ['Гейзер', 'от 1:7 до 1:10', 'корзина вровень с краем, без трамбовки', 'Complete Home Barista'],
          ['Колд брю', 'от 1:10 до 1:13 (концентрат от 1:8)', '12–16 ч', 'Kaffeemacher']],
  'h_more': 'Читайте также',
  'more': [('/ru/blog/skilky-kavy-na-chashku/', 'Сколько кофе на чашку: пропорции, таблица граммов и расчёт по способу'),
           ('/ru/blog/yak-pravylno-molotty-kavu/', 'Как правильно молоть кофе'),
           ('/ru/blog/espreso-kyslo-chy-hirko/', 'Как настроить эспрессо: кисло или горько')],
  'h_faq': 'Частые вопросы',
  'faq': [('Сколько граммов кофе на 250 мл воды?', 'При соотношении 1:16 это около 15,6 г кофе. Если вам нужно именно 250 мл напитка в чашке, воды нужно больше, потому что гуща впитывает около 2 мл на 1 г кофе в фильтре: это примерно 18 г кофе и 288 г воды.'),
          ('Какое соотношение кофе и воды лучшее?', 'Универсального нет. Для фильтра базовое в нашем гайде — 1:16; эталон «Золотой чашки» SCA — 55 г на литр (≈1:18) с допуском ±10%. Эспрессо считают по весу напитка (1:2), турку — примерно 1:10.'),
          ('Почему в чашке меньше воды, чем я налил?', 'Молотый кофе впитывает воду: около 2 мл на 1 г кофе в фильтре и около 3 мл в иммерсии (Barista Hustle). Калькулятор может учесть это, и тогда воды больше, чем нужно напитку.'),
          ('Можно ли отмерять кофе ложками?', 'Это ненадёжно: вес ложки зависит от обжарки и помола, по одному из источников от 5 до 8 г на столовую ложку. Калькулятор показывает ложки только как ориентир; лучше взвешивать.'),
          ('Как посчитать кофе для гейзерной кофеварки?', 'Выберите «Гейзер» и размер вашей кофеварки: калькулятор покажет дозу, воду и ориентировочный выход по таблице. Корзину заполняют вровень с краем без трамбовки, а воду наливают до клапана.')],
  'related_label': 'Статьи по теме',
  'app_name': 'Калькулятор кофе ZRN Coffee', 'bread': 'Калькулятор кофе',
 },
}

def _md(t):
    import re
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)

def page_html(lang):
    P = CPAGE[lang]
    h = '<div class="tldr"><b>%s</b><p>%s</p></div>\n' % ('Коротко', P['lead'])
    h += widget_html(lang)
    h += '<h2 id="use">%s</h2><ol>%s</ol>\n' % (P['h_use'], ''.join('<li>%s</li>' % x for x in P['steps']))
    h += '<h2 id="how">%s</h2>%s\n' % (P['h_how'], ''.join('<p>%s</p>' % _md(x) for x in P['how']))
    head = ''.join('<th scope="col">%s</th>' % c for c in P['tbl_head'])
    rows = ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>' for r in P['tbl'])
    h += '<h2 id="table">%s</h2><div class="tbl"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>\n' % (P['h_tbl'], head, rows)
    h += '<h2 id="more">%s</h2><ul>%s</ul>\n' % (P['h_more'], ''.join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in P['more']))
    det = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in P['faq'])
    h += '<h2 id="faq">%s</h2><div class="faq">%s</div>\n' % (P['h_faq'], det)
    return h

def page_faq_ld(lang):
    return {'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in CPAGE[lang]['faq']]}
