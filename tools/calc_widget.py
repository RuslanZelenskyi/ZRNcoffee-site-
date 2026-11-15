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
.calc-pre{margin:0 0 14px}
.calc-prebtn{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid var(--gold-soft);background:linear-gradient(135deg,#2a1d12,#4a3320);color:#f3ead9;border-radius:16px;padding:14px 16px;font-size:1rem;font-weight:600;text-align:left;box-shadow:0 6px 18px rgba(42,29,18,.18)}
.calc-prebtn span:first-child{display:flex;flex-direction:column;gap:2px}
.calc-prebtn small{font-weight:400;font-size:.78rem;color:rgba(243,234,217,.75)}
.calc-prebtn i{font-style:normal;transition:transform .2s}
.calc-prebtn[aria-expanded=true] i{transform:rotate(180deg)}
.calc-prelist{margin-top:10px;display:grid;gap:12px}
.calc-prelist[hidden]{display:none}
.calc-prelist h4{margin:0 0 6px!important;font-size:.78rem!important;letter-spacing:.06em;text-transform:uppercase;color:var(--sub)!important;font-weight:600}
.calc-prelist .calc-pc{display:grid;gap:6px}
.calc-prelist button.calc-card{text-align:left;border:1px solid var(--line);background:var(--card);border-radius:12px;padding:10px 12px;display:flex;flex-direction:column;gap:2px;font-size:.95rem;font-weight:600}
.calc-prelist button.calc-card small{font-weight:400;font-size:.78rem;color:var(--sub)}
.calc-prelist button.calc-card[aria-pressed=true]{background:var(--gold-soft);border-color:var(--gold-soft);color:#fff}
.calc-prelist button.calc-card[aria-pressed=true] small{color:rgba(255,255,255,.85)}
.calc-steps{margin:10px 0 0;font-size:.9rem;color:#f3ead9}
.calc-steps summary{cursor:pointer;font-weight:600;color:var(--gold-soft)}
.calc-steps ol{margin:8px 0 0!important;padding:0 0 0 1.2em!important;display:grid;gap:7px}
.calc-steps li{font-size:.88rem!important;line-height:1.5!important;color:#f3ead9!important;margin:0!important}
.calc-steps li b{color:var(--gold-soft);font-weight:600;margin-right:4px}
.calc-steps p{font-size:.8rem!important;margin:8px 0 0!important;color:rgba(243,234,217,.7)!important}
.calc-steps a{color:var(--gold-soft)}
.calc-saved{margin-top:12px}
.calc-saved h4{margin:0 0 6px!important;font-size:.82rem!important;letter-spacing:.06em;text-transform:uppercase;color:rgba(243,234,217,.7)!important;font-weight:600}
.calc-saved ul{list-style:none;margin:0!important;padding:0!important;display:grid;gap:6px}
.calc-saved li{display:flex;gap:6px;margin:0!important}
.calc-saved li button:first-child{flex:1;text-align:left}
.calc-saved button,.calc-act button.calc-save{border:1px solid rgba(243,234,217,.25);background:transparent;color:#f3ead9;border-radius:10px;padding:8px 12px;font-size:.86rem}
.calc-tm{margin-top:12px;background:#2a1d12;color:#f3ead9;border-radius:16px;padding:16px}
.calc-tm[hidden]{display:none}
.calc-tm h4{margin:0 0 6px!important;font-size:.82rem!important;letter-spacing:.06em;text-transform:uppercase;color:rgba(243,234,217,.7)!important;font-weight:600}
.calc-tm-time{font-size:2.6rem;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.1}
.calc-tm-cur{margin:8px 0 0!important;font-size:.95rem!important;line-height:1.5!important;color:#f3ead9!important}
.calc-tm-nxt{margin:6px 0 0!important;font-size:.82rem!important;color:rgba(243,234,217,.7)!important}
.calc-tm-btn{display:flex;gap:8px;margin-top:12px}
.calc-tm-btn button{flex:1;border:1px solid rgba(243,234,217,.3);background:transparent;color:#f3ead9;border-radius:12px;padding:12px;font-size:1rem}
.calc-tm-btn button[data-tm=go]{background:var(--gold-soft);border-color:var(--gold-soft);color:#fff;font-weight:600}
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
  'ratio': 'Міцність (співвідношення кави до води)', 'strong': 'Міцніше', 'base': 'Базово', 'light': 'Легше', 'lighter': 'Ще легше', 'tea': 'Як чай', 'sca': 'SCA',
  'ret': 'Врахувати воду, яку вбирає гуща', 'ret_h': 'Близько 2 мл на 1 г кави у фільтрі й 3 мл в імерсії (Barista Hustle). Без цього в чашці буде менше, ніж налили.',
  'ret_est': 'Для цього способу утримання води — наша оцінка.',
  'presets_h': 'Відомі рецепти', 'presets_sub': 'Рецепти чемпіонів і відомих бариста: {n}', 'steps_h': 'Покроково', 'src_lbl': 'Джерело',
  'pre': {
    'v60h': {'n': 'Hoffmann V60', 'by': 'Джеймс Гоффман · 1:16,7 · 3:30', 'g': 'Середньо-дрібний', 'temp': 'якомога гарячіша, щойно з кипіння', 'time': 'до 3:30',
      'steps': ['Змочіть фільтр окропом, насипте каву, зробіть лунку. Блюм: влийте {a} г (2× кава), закрутіть воронку, щоб гуща змокла рівно. Чекайте до 0:45.',
                'Влийте воду до {c} г на вазі (ще {a} г), приблизно за 30 с. Тримайте воронку повною.',
                'Долийте до {c} г (ще {a} г) повільніше й м’якше.',
                'Один раз помішайте за годинниковою стрілкою й один проти, дайте стекти, злегка закрутіть воронку. Стік має завершитися приблизно до 3:30.'],
      'src': ['https://www.hario-usa.com/blogs/recipes-and-more-from-friends/james-hoffmann-uitimate-v60-technique', 'Hario USA, Джеймс Гоффман']},
    'k46': {'n': '4:6 (Tetsu Kasuya)', 'by': 'Тецу Касуя, чемпіон світу 2016 · 1:15 · 3:30', 'g': 'Грубий, як для френч-преса', 'temp': '93 °C світле, 88 °C середнє, 83 °C темне обсмаження', 'time': 'до 3:30',
      'steps': ['Перша порція: {a} г повільно по колу (на вазі {c} г).', 'Друга порція: {a} г (на вазі {c} г).', 'Третя порція: {a} г (на вазі {c} г).', 'Четверта порція: {a} г (на вазі {c} г).', 'П’ята порція: {a} г (на вазі {c} г). Дайте стекти до 3:30.'],
      'note': 'Перші дві порції (40% води) керують смаком: більша перша порція дає більше кислотності, більша друга — більше солодкості. Останні три (60%) керують міцністю: дві порції по 90 г дадуть слабше, чотири по 45 г міцніше.',
      'src': ['https://pullandpourcoffee.com/v60-4-to-6-method-pour-over/amp/', 'Pull & Pour']},
    'hedrick': {'n': 'Lance Hedrick V60', 'by': 'Ленс Гедрік · 1:15 · 2:45–3:00', 'g': 'Середньо-дрібний, як цукровий пісок', 'temp': '93–96 °C (світле обсмаження ближче до 96, темне 91–93)', 'time': '2:45–3:00',
      'steps': ['Промийте фільтр гарячою водою й злийте її, насипте каву, струсіть воронку, щоб вирівняти шар, зробіть лунку й обнуліть ваги. Блюм: влийте {a} г по колу, 3–5 разів помішайте, злегка закрутіть.',
                'Влийте до {c} г (ще {a} г) спіраллю від центру до країв і назад до центру. Злегка закрутіть.',
                'Коли шар видно, але він не сухий, влийте до {c} г (ще {a} г) такою ж спіраллю. Це найбільша порція. Злегка закрутіть.',
                'Коли шар знову видно, влийте до {c} г (ще {a} г) у центр, не торкаючись стінок. Один раз злегка закрутіть.',
                'Дайте каві стекти повністю. Шар має лягти рівно, на стінках мало осаду.'],
      'src': ['https://secure.lamose.com/blogs/recipes/lance-hedricks-pour-over-masterclass-v60-technique', 'LAMOSE, Ленс Гедрік']},
    'aerohh': {'n': 'Hoffmann, аеропрес', 'by': 'Джеймс Гоффман · 1:18 · ≈2:30', 'g': 'Дрібний або середньо-дрібний', 'temp': 'щойно з кипіння', 'time': '≈2:30–3:00',
      'steps': ['Вставте фільтр у кошик, поставте аеропрес на чашку, насипте каву й налийте всю воду ({c} г). Вставте поршень.',
                'Обережно покрутіть аеропрес.',
                'Повільно й м’яко притисніть до кінця.'],
      'src': ['https://www.fluentincoffee.com/wprm_print/james-hoffmanns-aeropress', 'Fluent in Coffee, Джеймс Гоффман']},
    'rao': {'n': 'Scott Rao V60', 'by': 'Скотт Рао · 1:16,5 · 4:00–4:30', 'g': 'Підберіть так, щоб злив завершився за 4:00–4:30', 'temp': '97 °C', 'time': '4:00–4:30',
      'steps': ['Пластикова воронка V60. Насипте каву й зробіть пальцем «пташине гніздо».',
                'Блюм: влийте {a} г і одразу енергійно закрутіть воронку.',
                'Через 40 с влийте до {c} г.',
                'Дуже ніжно закрутіть воронку, менше секунди, щоб заповнити рифлення.',
                'Коли шар злито приблизно на 70%, долийте до {c} г і ще раз дуже ніжно закрутіть.',
                'Лийте низько рівним струменем на постійній висоті, переміщуючи чайник так, щоб увесь шар екстрагувався рівномірно.'],
      'note': 'За словами автора, екстракція зазвичай виходить у межах 22–24,5% залежно від кавомолки, сорту й обсмаження. Точних часів, крім 40 с, автор не дає, тому таймера для цього рецепта немає.',
      'src': ['https://www.hario.co.uk/blogs/hario-ambassadors/hario-v60-recipe-interview-with-hario-ambassador-scott-rao', 'Hario UK, Скотт Рао']},
    'chemex': {'n': 'Hoffmann Chemex', 'by': 'Джеймс Гоффман · 1:16,7 · ≈4:15', 'g': 'Середній', 'temp': 'щойно з кипіння (100 °C)', 'time': '≈4:15',
      'steps': ['Вставте фільтр так, щоб трисловий бік дивився на носик. Промийте гарячою водою, злийте її. Насипте каву, струсіть, зробіть лунку, обнуліть ваги.',
                'Блюм: влийте {a} г ніжно по колу (≈10 с). Почекайте до 0:45.',
                'Влийте по колу до {c} г (ще {a} г) приблизно за 30 с.',
                'Влийте по колу до {c} г (ще {a} г) приблизно за 30 с.',
                'Один раз помішайте за годинниковою стрілкою й один проти, зачекайте ≈10 с і злегка струсіть.',
                'Дайте стекти приблизно до 4:10, зніміть фільтр і збовтайте каву.'],
      'note': 'Якщо стік закінчується надто швидко, мельніть дрібніше, а якщо надто повільно, грубіше. Часи в джерелі наближені, тому таймера для цього рецепта немає.',
      'src': ['https://honestcoffeeguide.com/brew-recipes/james-hoffmann-chemex-recipe/', 'Honest Coffee Guide, Джеймс Гоффман']},
    'wac24': {'n': 'WAC 2024: George Stanica', 'by': 'Чемпіон світу · перевернутий · 18 г / 100 г', 'g': 'Підібраний під конкретну каву: Comandante C40 Mk4 Red Clix, 58 кліків (≈870 мкм)', 'temp': '96 °C, вода ≈85–90 ppm', 'time': '≈2:10 і розбавлення',
      'steps': ['Перевернутий аеропрес (близько позначки 4). Насипте каву й влийте {a} г (5–6 с).',
                'Після блюму приблизно 30 с влийте ще {a} г (на вазі {c} г) і 10 с помішуйте «північ-південь-схід-захід».',
                'Накрийте змоченим фільтром і обережно видавіть повітря (≈10 с).',
                'Злегка закрутіть, поставте на сервер і почніть повільно тиснути.',
                'Тисніть 30–40 с, поки вага напою не досягне ≈76–79 г (для 18 г кави). Розбавте теплою водою до 130–135 г, потім додайте 20–30 г води кімнатної температури з нульовою мінералізацією.'],
      'note': 'Чемпіон зазначає, що метод підібраний під конкретну каву й обсмаження, тому підлаштуйте його під свій смак. Автор дає точні часи лише для 1:20 й 1:35, решта часів приблизні. Наведені в «Вийде напою» ≈157 г це кінцевий об’єм після розбавлення.',
      'src': ['https://worldaeropresschampionship.com/pages/1st-george-stanica-romania-2024', 'World AeroPress Championship']},
    'wac25': {'n': 'WAC 2025: Némo Pop', 'by': 'Чемпіон світу · вертикальний · 18 г / 100 г', 'g': 'Спеціальний: Comandante Trailmaster, 31 клік, відсіяно через 200 мкм', 'temp': '84 °C, вода ≈125 ppm; додаткова вода 50 °C', 'time': '≈1:10',
      'steps': ['Заздалегідь налийте {x} г води 50 °C у карафу. Поставте аеропрес вертикально на карафу з фільтр-кришкою Flow Control і двома паперовими фільтрами, насипте каву. Влийте {c} г води 84 °C, щоб змокла вся кава.',
                'Через 25 с помішайте за схемою «NSNS-WEWE» (північ-південь двічі, схід-захід двічі).',
                'Через 50 с почніть повільно тиснути, приблизно 20 с. Подавайте.'],
      'note': 'Цей змагальний рецепт потребує спеціальної води й помелу з відсіюванням дрібної фракції, тому вдома результат буде трохи іншим. Кінцевий об’єм ≈125 г включає додаткову воду.',
      'src': ['https://worldaeropresschampionship.com/pages/1st-nemo-pop-australia-2025', 'World AeroPress Championship']},
    'pressh': {'n': 'Hoffmann, френч-прес', 'by': 'Джеймс Гоффман · 1:16,7 · 9–12 хв', 'g': 'Середньо-грубий, як морська сіль', 'temp': '≈96 °C, щойно з кипіння', 'time': '9–12 хв',
      'steps': ['Насипте каву, влийте всю воду ({c} г) так, щоб уся гуща змокла. Не мішайте.',
                'Через 4 хв розбийте кірку ложкою й акуратно помішайте 2–3 рази.',
                'Двома ложками зніміть піну й гущу, що плаває.',
                'Зачекайте ще 5–8 хв, щоб гуща осіла.',
                'Опустіть поршень приблизно на 2,5 см під поверхню, як кришку, не притискайте до кінця. Наливайте повільно, останні 30–50 мл з осадом залиште.'],
      'src': ['https://secure.lamose.com/blogs/recipes/james-hoffmanns-french-press-method-the-better-way', 'LAMOSE, Джеймс Гоффман']}
  },
  'mi': {
    'filter': {'g': 'Середньо-дрібний (дрібніший за френч-прес, грубший за еспресо)', 'steps': ['Змочіть паперовий фільтр окропом, злийте воду.', 'Блюм: залийте кави вдвічі більше води за вагою й почекайте 30–45 с.', 'Доливайте колами до повної ваги води.', 'Стік має завершитися приблизно за 2:30–3:30. Якщо швидше, мельніть дрібніше, якщо довше, грубіше.']},
    'press': {'g': 'Грубий', 'steps': ['Залийте каву водою й накрийте кришкою без притискання.', 'Чекайте 4 хв, розбийте кірку й зніміть піну.', 'Повільно притисніть поршень і одразу перелийте каву, щоб не перетримати.']},
    'aero': {'g': 'Середній, між фільтром і еспресо', 'steps': ['Змочіть фільтр, налийте воду, насипте каву.', 'Залийте водою, перемішайте, вставте поршень.', 'Через ≈2 хв повільно тисніть 30 с, зупиніться на шипінні.']},
    'espresso': {'g': 'Дуже дрібний; підлаштуйте так, щоб вихід вийшов за 25–30 с', 'steps': ['Зважте дозу в кошику, рівно розподіліть, притрамбуйте.', 'Поставте чашку на вагу й запустіть екстракцію.', 'Зупиніть, коли вага напою досягне розрахованого. Якщо швидше за 25 с, мельніть дрібніше, якщо довше за 30 с, грубіше.']},
    'turka': {'g': 'Дуже дрібний, як пудра', 'steps': ['Всипте каву в холодну воду, не мішайте до нагрівання.', 'Нагрівайте на малому вогні, не кип’ятіть.', 'Зніміть, коли підніметься піна, дайте гущі осісти 1–2 хв.']},
    'moka': {'g': 'Середньо-дрібний, грубший за еспресо', 'steps': ['Налийте воду до клапана, насипте каву вщерть без трамбування.', 'Поставте на малий вогонь із відкритою кришкою.', 'Зніміть, щойно кава почне хрипіти, охолодіть дно під холодною водою.']},
    'cold': {'g': 'Грубий', 'steps': ['Змішайте каву з холодною водою, перемішайте, щоб усе змокло.', 'Настоюйте 12–16 год у холодильнику.', 'Процідіть через фільтр і розбавте водою або льодом до смаку.']}
  },
  'save': 'Зберегти рецепт', 'saved_h': 'Мої рецепти', 'saved_ok': 'Рецепт збережено в цьому браузері', 'saved_fail': 'Не вдалося зберегти (браузер забороняє сховище)', 'del': 'Видалити', 'saved_full': 'Збережено до 10 рецептів, найстарші видаляються',
  'tm_h': 'Таймер', 'tm_start': 'Старт', 'tm_pause': 'Пауза', 'tm_resume': 'Продовжити', 'tm_reset': 'Скинути', 'tm_ready': 'Натисніть «Старт», коли почнете наливати воду.', 'tm_next': 'Далі через', 'tm_step': 'Крок', 'tm_done': 'Готово. Смачної кави!', 'tm_after': 'Потім',
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
  'v_low': 'Дуже міцно: це вже концентрат', 'v_strong': 'Міцніше за еталон SCA (55 г/л ±10%). Поширений вибір', 'v_sca': 'У межах еталона SCA: 55 г на літр ±10%', 'v_vweak': 'Дуже легко, ледь не чайний смак. Щоб кава не стала водянистою, мельніть дрібніше й вливайте воду гарячішою', 'v_weak': 'Легше за еталон SCA. М’який, прозорий смак',
  'sca_lab': 'Затінена зона: еталон SCA (55 г/л ±10%)', 'sca_cap': ['1:10','1:30'],
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
  'ratio': 'Крепость (соотношение кофе к воде)', 'strong': 'Крепче', 'base': 'Базово', 'light': 'Легче', 'lighter': 'Ещё легче', 'tea': 'Как чай', 'sca': 'SCA',
  'ret': 'Учесть воду, которую впитывает гуща', 'ret_h': 'Около 2 мл на 1 г кофе в фильтре и 3 мл в иммерсии (Barista Hustle). Без этого в чашке будет меньше, чем налили.',
  'ret_est': 'Для этого способа удержание воды — наша оценка.',
  'presets_h': 'Известные рецепты', 'presets_sub': 'Рецепты чемпионов и известных бариста: {n}', 'steps_h': 'По шагам', 'src_lbl': 'Источник',
  'pre': {
    'v60h': {'n': 'Hoffmann V60', 'by': 'Джеймс Хоффман · 1:16,7 · 3:30', 'g': 'Средне-мелкий', 'temp': 'как можно горячее, только с кипения', 'time': 'до 3:30',
      'steps': ['Смочите фильтр кипятком, насыпьте кофе, сделайте лунку. Блюм: влейте {a} г (2× кофе), закрутите воронку, чтобы гуща смочилась ровно. Ждите до 0:45.',
                'Влейте воду до {c} г на весах (ещё {a} г), примерно за 30 с. Держите воронку полной.',
                'Долейте до {c} г (ещё {a} г) медленнее и мягче.',
                'Один раз помешайте по часовой стрелке и один против, дайте стечь, слегка закрутите воронку. Стекание должно завершиться примерно к 3:30.'],
      'src': ['https://www.hario-usa.com/blogs/recipes-and-more-from-friends/james-hoffmann-uitimate-v60-technique', 'Hario USA, Джеймс Хоффман']},
    'k46': {'n': '4:6 (Tetsu Kasuya)', 'by': 'Тэцу Касуя, чемпион мира 2016 · 1:15 · 3:30', 'g': 'Крупный, как для френч-пресса', 'temp': '93 °C светлая, 88 °C средняя, 83 °C тёмная обжарка', 'time': 'до 3:30',
      'steps': ['Первая порция: {a} г медленно по кругу (на весах {c} г).', 'Вторая порция: {a} г (на весах {c} г).', 'Третья порция: {a} г (на весах {c} г).', 'Четвёртая порция: {a} г (на весах {c} г).', 'Пятая порция: {a} г (на весах {c} г). Дайте стечь до 3:30.'],
      'note': 'Первые две порции (40% воды) управляют вкусом: большая первая порция даёт больше кислотности, большая вторая — больше сладости. Последние три (60%) управляют крепостью: две порции по 90 г дадут слабее, четыре по 45 г крепче.',
      'src': ['https://pullandpourcoffee.com/v60-4-to-6-method-pour-over/amp/', 'Pull & Pour']},
    'hedrick': {'n': 'Lance Hedrick V60', 'by': 'Ленс Хедрик · 1:15 · 2:45–3:00', 'g': 'Средне-мелкий, как сахарный песок', 'temp': '93–96 °C (светлая обжарка ближе к 96, тёмная 91–93)', 'time': '2:45–3:00',
      'steps': ['Промойте фильтр горячей водой и слейте её, насыпьте кофе, встряхните воронку, чтобы выровнять слой, сделайте лунку и обнулите весы. Блюм: влейте {a} г по кругу, 3–5 раз помешайте, слегка закрутите.',
                'Влейте до {c} г (ещё {a} г) спиралью от центра к краям и обратно к центру. Слегка закрутите.',
                'Когда слой виден, но не сухой, влейте до {c} г (ещё {a} г) такой же спиралью. Это самая большая порция. Слегка закрутите.',
                'Когда слой снова виден, влейте до {c} г (ещё {a} г) в центр, не касаясь стенок. Один раз слегка закрутите.',
                'Дайте кофе стечь полностью. Слой должен лечь ровно, на стенках мало осадка.'],
      'src': ['https://secure.lamose.com/blogs/recipes/lance-hedricks-pour-over-masterclass-v60-technique', 'LAMOSE, Ленс Хедрик']},
    'aerohh': {'n': 'Hoffmann, аэропресс', 'by': 'Джеймс Хоффман · 1:18 · ≈2:30', 'g': 'Мелкий или средне-мелкий', 'temp': 'только с кипения', 'time': '≈2:30–3:00',
      'steps': ['Вставьте фильтр в корзину, поставьте аэропресс на чашку, насыпьте кофе и налейте всю воду ({c} г). Вставьте поршень.',
                'Осторожно покрутите аэропресс.',
                'Медленно и мягко прижмите до конца.'],
      'src': ['https://www.fluentincoffee.com/wprm_print/james-hoffmanns-aeropress', 'Fluent in Coffee, Джеймс Хоффман']},
    'rao': {'n': 'Scott Rao V60', 'by': 'Скотт Рао · 1:16,5 · 4:00–4:30', 'g': 'Подберите так, чтобы слив завершился за 4:00–4:30', 'temp': '97 °C', 'time': '4:00–4:30',
      'steps': ['Пластиковая воронка V60. Насыпьте кофе и сделайте пальцем «птичье гнездо».',
                'Блюм: влейте {a} г и сразу энергично закрутите воронку.',
                'Через 40 с влейте до {c} г.',
                'Очень нежно закрутите воронку, меньше секунды, чтобы заполнить рифление.',
                'Когда слой слит примерно на 70%, долейте до {c} г и ещё раз очень нежно закрутите.',
                'Лейте низко ровной струёй на постоянной высоте, перемещая чайник так, чтобы весь слой экстрагировался равномерно.'],
      'note': 'По словам автора, экстракция обычно получается в пределах 22–24,5% в зависимости от кофемолки, сорта и обжарки. Точных времён, кроме 40 с, автор не даёт, поэтому таймера для этого рецепта нет.',
      'src': ['https://www.hario.co.uk/blogs/hario-ambassadors/hario-v60-recipe-interview-with-hario-ambassador-scott-rao', 'Hario UK, Скотт Рао']},
    'chemex': {'n': 'Hoffmann Chemex', 'by': 'Джеймс Хоффман · 1:16,7 · ≈4:15', 'g': 'Средний', 'temp': 'только с кипения (100 °C)', 'time': '≈4:15',
      'steps': ['Вставьте фильтр так, чтобы трёхслойная сторона смотрела на носик. Промойте горячей водой, слейте её. Насыпьте кофе, встряхните, сделайте лунку, обнулите весы.',
                'Блюм: влейте {a} г нежно по кругу (≈10 с). Подождите до 0:45.',
                'Влейте по кругу до {c} г (ещё {a} г) примерно за 30 с.',
                'Влейте по кругу до {c} г (ещё {a} г) примерно за 30 с.',
                'Один раз помешайте по часовой стрелке и один против, подождите ≈10 с и слегка встряхните.',
                'Дайте стечь примерно до 4:10, снимите фильтр и взболтайте кофе.'],
      'note': 'Если стекание заканчивается слишком быстро, мелите мельче, а если слишком медленно, крупнее. Времена в источнике приблизительные, поэтому таймера для этого рецепта нет.',
      'src': ['https://honestcoffeeguide.com/brew-recipes/james-hoffmann-chemex-recipe/', 'Honest Coffee Guide, Джеймс Хоффман']},
    'wac24': {'n': 'WAC 2024: George Stanica', 'by': 'Чемпион мира · перевёрнутый · 18 г / 100 г', 'g': 'Подобран под конкретный кофе: Comandante C40 Mk4 Red Clix, 58 щелчков (≈870 мкм)', 'temp': '96 °C, вода ≈85–90 ppm', 'time': '≈2:10 и разбавление',
      'steps': ['Перевёрнутый аэропресс (около отметки 4). Насыпьте кофе и влейте {a} г (5–6 с).',
                'После блюма примерно 30 с влейте ещё {a} г (на весах {c} г) и 10 с помешивайте «север-юг-восток-запад».',
                'Накройте смоченным фильтром и осторожно выдавите воздух (≈10 с).',
                'Слегка покрутите, поставьте на сервер и начните медленно давить.',
                'Давите 30–40 с, пока вес напитка не достигнет ≈76–79 г (для 18 г кофе). Разбавьте тёплой водой до 130–135 г, затем добавьте 20–30 г воды комнатной температуры с нулевой минерализацией.'],
      'note': 'Чемпион отмечает, что метод подобран под конкретный кофе и обжарку, поэтому подстройте его под свой вкус. Автор даёт точные времена только для 1:20 и 1:35, остальные времена приблизительные. Указанные в «Получится напитка» ≈157 г это конечный объём после разбавления.',
      'src': ['https://worldaeropresschampionship.com/pages/1st-george-stanica-romania-2024', 'World AeroPress Championship']},
    'wac25': {'n': 'WAC 2025: Némo Pop', 'by': 'Чемпион мира · вертикальный · 18 г / 100 г', 'g': 'Специальный: Comandante Trailmaster, 31 щелчок, отсеяно через 200 мкм', 'temp': '84 °C, вода ≈125 ppm; дополнительная вода 50 °C', 'time': '≈1:10',
      'steps': ['Заранее налейте {x} г воды 50 °C в карафу. Поставьте аэропресс вертикально на карафу с фильтр-крышкой Flow Control и двумя бумажными фильтрами, насыпьте кофе. Влейте {c} г воды 84 °C, чтобы смочился весь кофе.',
                'Через 25 с помешайте по схеме «NSNS-WEWE» (север-юг дважды, восток-запад дважды).',
                'Через 50 с начните медленно давить, примерно 20 с. Подавайте.'],
      'note': 'Этот соревновательный рецепт требует специальной воды и помола с отсевом мелкой фракции, поэтому дома результат будет немного другим. Конечный объём ≈125 г включает дополнительную воду.',
      'src': ['https://worldaeropresschampionship.com/pages/1st-nemo-pop-australia-2025', 'World AeroPress Championship']},
    'pressh': {'n': 'Hoffmann, френч-пресс', 'by': 'Джеймс Хоффман · 1:16,7 · 9–12 мин', 'g': 'Средне-крупный, как морская соль', 'temp': '≈96 °C, только с кипения', 'time': '9–12 мин',
      'steps': ['Насыпьте кофе, влейте всю воду ({c} г), чтобы вся гуща смочилась. Не мешайте.',
                'Через 4 мин разбейте корку ложкой и аккуратно помешайте 2–3 раза.',
                'Двумя ложками снимите пену и плавающую гущу.',
                'Подождите ещё 5–8 мин, чтобы гуща осела.',
                'Опустите поршень примерно на 2,5 см под поверхность, как крышку, не прижимайте до конца. Наливайте медленно, последние 30–50 мл с осадком оставьте.'],
      'src': ['https://secure.lamose.com/blogs/recipes/james-hoffmanns-french-press-method-the-better-way', 'LAMOSE, Джеймс Хоффман']}
  },
  'mi': {
    'filter': {'g': 'Средне-мелкий (мельче френч-пресса, крупнее эспрессо)', 'steps': ['Смочите бумажный фильтр кипятком, слейте воду.', 'Блюм: залейте кофе вдвое больше воды по весу и подождите 30–45 с.', 'Доливайте кругами до полного веса воды.', 'Стекание должно завершиться примерно за 2:30–3:30. Если быстрее, мелите мельче, если дольше, крупнее.']},
    'press': {'g': 'Крупный', 'steps': ['Залейте кофе водой и накройте крышкой без прижима.', 'Подождите 4 мин, разбейте корку и снимите пену.', 'Медленно прижмите поршень и сразу перелейте кофе, чтобы не перестоял.']},
    'aero': {'g': 'Средний, между фильтром и эспрессо', 'steps': ['Смочите фильтр, налейте воду, насыпьте кофе.', 'Залейте водой, перемешайте, вставьте поршень.', 'Через ≈2 мин медленно давите 30 с, остановитесь на шипении.']},
    'espresso': {'g': 'Очень мелкий; подстройте так, чтобы выход получился за 25–30 с', 'steps': ['Взвесьте дозу в корзине, ровно распределите, притрамбуйте.', 'Поставьте чашку на весы и запустите экстракцию.', 'Остановите, когда вес напитка достигнет расчётного. Если быстрее 25 с, мелите мельче, если дольше 30 с, крупнее.']},
    'turka': {'g': 'Очень мелкий, как пудра', 'steps': ['Всыпьте кофе в холодную воду, не мешайте до нагрева.', 'Нагревайте на малом огне, не кипятите.', 'Снимите, когда поднимется пена, дайте гуще осесть 1–2 мин.']},
    'moka': {'g': 'Средне-мелкий, крупнее эспрессо', 'steps': ['Налейте воду до клапана, насыпьте кофе вровень без трамбовки.', 'Поставьте на малый огонь с открытой крышкой.', 'Снимите, как только кофе начнёт хрипеть, охладите дно под холодной водой.']},
    'cold': {'g': 'Крупный', 'steps': ['Смешайте кофе с холодной водой, перемешайте, чтобы всё смочилось.', 'Настаивайте 12–16 ч в холодильнике.', 'Процедите через фильтр и разбавьте водой или льдом по вкусу.']}
  },
  'save': 'Сохранить рецепт', 'saved_h': 'Мои рецепты', 'saved_ok': 'Рецепт сохранён в этом браузере', 'saved_fail': 'Не удалось сохранить (браузер запрещает хранилище)', 'del': 'Удалить', 'saved_full': 'Сохраняется до 10 рецептов, самые старые удаляются',
  'tm_h': 'Таймер', 'tm_start': 'Старт', 'tm_pause': 'Пауза', 'tm_resume': 'Продолжить', 'tm_reset': 'Сбросить', 'tm_ready': 'Нажмите «Старт», когда начнёте наливать воду.', 'tm_next': 'Дальше через', 'tm_step': 'Шаг', 'tm_done': 'Готово. Приятного кофе!', 'tm_after': 'Потом',
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
  'v_low': 'Очень крепко: это уже концентрат', 'v_strong': 'Крепче эталона SCA (55 г/л ±10%). Распространённый выбор', 'v_sca': 'В пределах эталона SCA: 55 г на литр ±10%', 'v_vweak': 'Очень легко, почти чайный вкус. Чтобы кофе не стал водянистым, мелите мельче и берите воду погорячее', 'v_weak': 'Легче эталона SCA. Мягкий, прозрачный вкус',
  'sca_lab': 'Затенённая зона: эталон SCA (55 г/л ±10%)', 'sca_cap': ['1:10','1:30'],
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
    filter:   { r: 16,   min: 10, max: 30, k: 2,   cupMl: 250, cups: 1, temp: '92–96 °C', time: '2:30–3:30', est: false, sca: true,
                chips: [[15, 'strong'], [16, 'base'], [17, 'light'], [18.18, 'sca'], [20, 'lighter'], [24, 'tea']] },
    press:    { r: 15,   min: 10, max: 26, k: 3,   cupMl: 250, cups: 1, temp: '≈93 °C', time: LANG === 'ru' ? '4 мин' : '4 хв', est: false,
                chips: [[14, 'strong'], [15, 'base'], [16, 'light'], [18, 'lighter']] },
    aero:     { r: 11.7, min: 5,  max: 24, k: 2.5, cupMl: 200, cups: 1, temp: '≈96 °C', time: '≈2:00', est: true,
                chips: [[10, 'strong'], [11.7, 'base'], [14, 'light'], [18, 'lighter']] },
    espresso: { r: 2,    min: 1,  max: 4,  dose: 18, temp: '92–94 °C', time: LANG === 'ru' ? '25–30 с' : '25–30 с' },
    turka:    { r: 10,   min: 8,  max: 14, serv: 1, per: 70, temp: null, time: null,
                chips: [[9, 'strong'], [10, 'base'], [11, 'light'], [12.5, 'lighter']] },
    moka:     { pots: { 1: [7, 60, '40–50'], 2: [14, 130, '90–100'], 3: [17, 180, '130–150'], 6: [35, 350, '250–280'] }, pot: 2 },
    cold:     { r: 10,   min: 8,  max: 18, k: 3,   cupMl: 250, cups: 1, est: true, variant: 'rtd', to: 12,
                chips: [[10, 'base'], [13, 'light'], [16, 'lighter']] }
  };
  var PRESETS = {
    v60h:   { m: 'filter', dose: 30, r: 500 / 30, t: ['0:00', '0:45', '1:15', '1:45'], at: [0, 45, 75, 105], end: 210,
              cum: function (d, w) { return [2 * d, 0.6 * w, w, null]; } },
    k46:    { m: 'filter', dose: 20, r: 15, t: ['0:00', '0:40', '1:20', '2:00', '2:30'], at: [0, 40, 80, 120, 150], end: 210,
              cum: function (d, w) { return [0.2 * w, 0.4 * w, 0.6 * w, 0.8 * w, w]; } },
    hedrick:{ m: 'filter', dose: 20, r: 15, t: ['0:00', '0:45', '1:15', '2:00', '2:15'], at: [0, 45, 75, 120, 135], end: 180,
              cum: function (d, w) { return [w * 40 / 300, w * 120 / 300, w * 260 / 300, w, null]; } },
    aerohh: { m: 'aero', dose: 11, r: 200 / 11, t: ['0:00', '2:00', '2:30'], at: [0, 120, 150], end: 180,
              cum: function (d, w) { return [w, null, null]; } },
    rao:    { m: 'filter', dose: 20, r: 16.5, t: ['', '0:00', '0:40', '', '≈70%', ''],
              cum: function (d, w) { return [null, 3 * d, w * 200 / 330, null, w, null]; } },
    chemex: { m: 'filter', dose: 30, r: 500 / 30, t: ['', '0:00', '0:45', '1:15', '1:45', 'до 4:10'],
              cum: function (d, w) { return [null, w * 80 / 500, w * 0.6, w, null, null]; } },
    wac24:  { m: 'aero', dose: 18, r: 100 / 18, t: ['0:00', '≈0:35', '1:20', '1:35', '≈2:10'], at: [0, 35, 80, 95, 130], end: 170,
              cum: function (d, w) { return [w / 2, w, null, null, null]; },
              drinkT: function (d) { return 157 * d / 18; } },
    wac25:  { m: 'aero', dose: 18, r: 100 / 18, t: ['0:00', '0:25', '0:50'], at: [0, 25, 50], end: 75,
              cum: function (d, w) { return [w, null, null]; }, x: function (d) { return 70 * d / 18; },
              drinkT: function (d) { return 125 * d / 18; } },
    pressh: { m: 'press', dose: 30, r: 500 / 30, t: ['0:00', '4:00', '4:00', '4:00+', '9–12'],
              cum: function (d, w) { return [w, null, null, null, null]; } }
  };
  var PORDER = ['v60h', 'k46', 'hedrick', 'rao', 'chemex', 'pressh', 'aerohh', 'wac24', 'wac25'];
  var ORDER = ['filter', 'press', 'aero', 'espresso', 'turka', 'moka', 'cold'];

  var S = { m: 'filter', g: 'drink', cups: 1, cupMl: 250, dose: 18, water: 288, r: 16, ret: true, prec: 1,
            edose: 18, er: 2, tds: 0, preset: '', preOpen: false, pot: 2, serv: 1, per: 70, variant: 'rtd', to: 12 };

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
    h += '<div class="calc-pre"><button type="button" class="calc-prebtn" data-prepanel aria-expanded="false"><span data-prelabel></span><i aria-hidden="true">▾</i></button><div class="calc-prelist" data-prelist hidden></div></div>';
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
    h += '</div><div class="calc-out" aria-live="polite" data-out></div><div class="calc-tm" data-timer hidden></div></div>';
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
    if (S.preset && PRESETS[S.preset] && PRESETS[S.preset].drinkT) o.drink = PRESETS[S.preset].drinkT(dose2);
    return o;
  }

  // ---------- вивід ----------
  function verdict(r) {
    if (r < 12) return ['warn', T.v_low];
    if (r < 16.5) return ['', T.v_strong];
    if (r <= 20.2) return ['ok', T.v_sca];
    if (r <= 24) return ['', T.v_weak];
    return ['warn', T.v_vweak];
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
    var pbtn = $('[data-prepanel]'), plist = $('[data-prelist]');
    pbtn.setAttribute('aria-expanded', String(!!S.preOpen)); plist.hidden = !S.preOpen;
    $('[data-prelabel]').innerHTML = '★ ' + T.presets_h + '<small>' + (S.preset ? T.pre[S.preset].n : T.presets_sub.replace('{n}', PORDER.length)) + '</small>';
    if (S.preOpen) {
      var gr = {}, gh = '';
      PORDER.forEach(function (id) { (gr[PRESETS[id].m] = gr[PRESETS[id].m] || []).push(id); });
      ['filter', 'press', 'aero'].forEach(function (mm) {
        if (!gr[mm]) return;
        gh += '<div><h4>' + T.methods[mm] + '</h4><div class="calc-pc">' + gr[mm].map(function (id) { return '<button type="button" class="calc-card" data-preset="' + id + '" aria-pressed="' + (S.preset === id) + '">' + T.pre[id].n + '<small>' + T.pre[id].by + '</small></button>'; }).join('') + '</div></div>';
      });
      plist.innerHTML = gh;
    }
    var PI = S.preset ? T.pre[S.preset] : null, tempV = PI ? PI.temp : c.temp, timeV = PI ? PI.time : c.time;
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
      var lo = 10, hi = 30; function pos(x) { return clamp((x - lo) / (hi - lo), 0, 1) * 100; }
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
      if (tempV) h += '<li><span>' + T.f_temp + '</span><b>' + tempV + '</b></li><li><span>' + T.f_time + '</span><b>' + timeV + '</b></li>';
      if (isCold) h += '<li><span>' + T.f_time + '</span><b>' + T.cold_time + '</b></li><li><span>' + T.f_grind + '</span><b>' + T.cold_grind + '</b></li>';
      h += '</ul>';
      if (m === 'filter') { var v = verdict(o.ratio); h += '<p class="calc-note ' + v[0] + '">' + v[1] + '</p>'; }
      if (isCold && S.variant === 'conc') {
        var add = Math.max(0, Math.round(o.dose * (S.to - o.ratio)));
        var fin = Math.round(Math.max(0, o.dose * S.to - (S.ret ? c.k : 0) * o.dose));
        h += '<p class="calc-note ok"><b>' + T.conc_add + ': ' + add + ' ' + T.ml + '</b> (' + ratioStr(S.to) + ' → ≈ ' + fin + ' ' + T.ml + ')</p>';
      }
    }
    h += stepsHtml(o);
    if (S.tds > 0 && (isEsp || (brew && !isCold))) {
      var bev = isEsp ? o.yield : o.drink, ey = S.tds * bev / o.dose, vc = (ey >= 18 && ey <= 22) ? 'ok' : '', vt = ey < 18 ? T.ey_under : (ey <= 22 ? T.ey_ok : T.ey_over);
      h += '<ul class="calc-facts"><li><span>' + T.tds + '</span><b>' + fmt(S.tds, 2) + '%</b></li><li><span>' + T.ey + '</span><b>' + fmt(ey, 1) + '%</b></li></ul>';
      h += '<p class="calc-note ' + vc + '">' + vt + ' ' + (isEsp ? T.tds_range_e : T.tds_range_f) + '</p>';
    }
    (o.warn || []).forEach(function (w) { h += '<p class="calc-note warn">' + w + '</p>'; });
    h += '<div class="calc-act"><button type="button" data-copy>' + T.copy + '</button><button type="button" data-share>' + T.share + '</button><button type="button" class="calc-save" data-save>' + T.save + '</button></div><div class="calc-toast" data-toast></div>' + savedHtml();
    $('[data-out]').innerHTML = h;
    root._o = o;
    saveState();
    tmSync();
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
    var c = METHODS[m], prev = S.m; S.m = m; S.preset = ''; if ((prev === 'espresso') !== (m === 'espresso')) S.tds = 0;
    if (m === 'espresso') { if (S.g !== 'yield') S.g = 'dose'; if (S.er < 1 || S.er > 4) S.er = c.r; }
    else if (m === 'moka') { S.g = 'drink'; }
    else if (m === 'turka') { S.g = 'drink'; if (prev !== 'turka' || S.r < c.min || S.r > c.max) S.r = c.r; }
    else {
      if (S.g === 'yield') S.g = 'drink';
      S.r = c.r; S.ret = true; S.variant = 'rtd';
      if (!S.cupMlTouched) S.cupMl = c.cupMl;
    }
  }
  function applyPreset(id) {
    var P = PRESETS[id]; if (!P) return;
    applyMethod(P.m); S.g = 'dose'; S.dose = P.dose; S.r = P.r; S.ret = true; S.preset = id;
  }
  function presetSteps(o) {
    var P = PRESETS[S.preset], PI = T.pre[S.preset], cum = P.cum(o.dose, o.water), prev = 0;
    return PI.steps.map(function (tx, i) {
      var c = cum[i], a = '';
      if (c != null) { a = Math.round(c - prev); prev = c; }
      return { t: P.t[i], at: P.at ? P.at[i] : null, text: tx.replace('{a}', a).replace('{c}', c != null ? Math.round(c) : '').replace('{x}', P.x ? Math.round(P.x(o.dose)) : '') };
    });
  }
  // ---------- таймер ----------
  var TM = { run: false, acc: 0, t0: 0, iv: 0, id: '', last: -1, lock: null, ac: null };
  function fmtT(sec) { sec = Math.max(0, Math.floor(sec)); return Math.floor(sec / 60) + ':' + ('0' + (sec % 60)).slice(-2); }
  function tmBeep() {
    try { if (navigator.vibrate) navigator.vibrate([120, 60, 120]); } catch (e) {}
    try { if (TM.ac) { var o = TM.ac.createOscillator(), g = TM.ac.createGain(); o.frequency.value = 880; g.gain.value = 0.08; o.connect(g); g.connect(TM.ac.destination); o.start(); o.stop(TM.ac.currentTime + 0.18); } } catch (e) {}
  }
  function tmSecs() { return (TM.run ? Date.now() - TM.t0 : TM.acc) / 1000; }
  function tmDraw() {
    var box = $('[data-timer]'), o = root._o; if (!box || box.hidden || !o || !S.preset || !PRESETS[S.preset].at) return;
    var P = PRESETS[S.preset], steps = presetSteps(o), sec = tmSecs(), idx = -1, i;
    for (i = 0; i < steps.length; i++) if (steps[i].at <= sec) idx = i;
    var done = sec >= P.end, started = TM.run || TM.acc > 0;
    var cur = done ? T.tm_done : (idx < 0 || !started ? T.tm_ready : T.tm_step + ' ' + (idx + 1) + '/' + steps.length + ': ' + steps[idx].text);
    var nxt = '';
    if (started && !done) { var nx = steps[idx + 1]; nxt = nx ? T.tm_next + ' ' + fmtT(nx.at - sec + 0.999) + ' · ' + T.tm_after + ': ' + nx.text : T.tm_next + ' ' + fmtT(P.end - sec + 0.999) + ' · ' + T.tm_done; }
    if (idx !== TM.last) { if (TM.last !== -2 && TM.run && idx >= 0) tmBeep(); TM.last = idx; }
    if (done && TM.run) { tmBeep(); tmStop(false); }
    box.querySelector('[data-tm-time]').textContent = fmtT(sec);
    box.querySelector('[data-tm-cur]').textContent = cur;
    box.querySelector('[data-tm-nxt]').textContent = nxt;
    var go = box.querySelector('[data-tm=go]'); go.textContent = TM.run ? T.tm_pause : (TM.acc > 0 && !done ? T.tm_resume : T.tm_start);
  }
  function tmStop(keepAcc) {
    if (TM.run) TM.acc = Date.now() - TM.t0;
    TM.run = false; clearInterval(TM.iv); TM.iv = 0;
    try { if (TM.lock) { TM.lock.release(); TM.lock = null; } } catch (e) {}
    if (keepAcc === false) { /* залишаємо час, щоб показати результат */ }
  }
  function tmReset() { tmStop(true); TM.acc = 0; TM.last = -1; tmDraw(); }
  function tmToggle() {
    if (TM.run) { tmStop(true); tmDraw(); return; }
    var P = PRESETS[S.preset]; if (TM.acc / 1000 >= P.end) TM.acc = 0;
    try { if (!TM.ac && (window.AudioContext || window.webkitAudioContext)) TM.ac = new (window.AudioContext || window.webkitAudioContext)(); if (TM.ac && TM.ac.resume) TM.ac.resume(); } catch (e) {}
    try { if (navigator.wakeLock) navigator.wakeLock.request('screen').then(function (l) { TM.lock = l; }, function () {}); } catch (e) {}
    TM.run = true; TM.t0 = Date.now() - TM.acc; TM.last = -2; TM.iv = setInterval(tmDraw, 250); tmDraw();
  }
  function tmSync() {
    var box = $('[data-timer]'); if (!box) return;
    var on = !!(S.preset && PRESETS[S.preset].at);
    if (TM.id !== (on ? S.preset : '')) { tmReset(); TM.id = on ? S.preset : ''; }
    if (on && !box.firstChild) box.innerHTML = '<h4>' + T.tm_h + '</h4><div class="calc-tm-time" data-tm-time>0:00</div><p class="calc-tm-cur" data-tm-cur></p><p class="calc-tm-nxt" data-tm-nxt></p><div class="calc-tm-btn"><button type="button" data-tm="go"></button><button type="button" data-tm="reset">' + T.tm_reset + '</button></div>';
    box.hidden = !on; tmDraw();
  }
  // ---------- збережені рецепти ----------
  function getSaved() { try { var a = JSON.parse(localStorage.getItem('zrn-calc-recipes') || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
  function putSaved(a) { try { localStorage.setItem('zrn-calc-recipes', JSON.stringify(a)); return true; } catch (e) { return false; } }
  function recipeName(o) {
    var PI = S.preset ? T.pre[S.preset] : null, n = PI ? PI.n : T.methods[S.m];
    return n + ' · ' + fmtAuto(o.dose) + ' ' + T.g + (o.water ? ' / ' + Math.round(o.water) + ' ' + T.ml : o.yield ? ' → ' + fmtAuto(o.yield) + ' ' + T.g : '');
  }
  function savedHtml() {
    var a = getSaved(); if (!a.length) return '';
    return '<div class="calc-saved"><h4>' + T.saved_h + '</h4><ul>' + a.map(function (r, i) {
      return '<li><button type="button" data-load="' + i + '">' + E(r.n) + '</button><button type="button" data-del="' + i + '" aria-label="' + T.del + '" title="' + T.del + '">×</button></li>';
    }).join('') + '</ul></div>';
  }
  function E(x) { return String(x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function stepsHtml(o) {
    var PI = S.preset ? T.pre[S.preset] : null, P = S.preset ? PRESETS[S.preset] : null, h = '';
    if (!(o.mode === 'brew' || o.mode === 'espresso' || o.mode === 'turka' || o.mode === 'moka')) return h;
    var info = T.mi[S.m]; if (!info && !PI) return h;
    var grind = PI ? PI.g : info.g;
    if (grind && S.m !== 'cold') h += '<ul class="calc-facts"><li><span>' + T.f_grind + '</span><b>' + grind + '</b></li></ul>';
    var items = '';
    if (PI && P) {
      items = presetSteps(o).map(function (st) { return '<li><b>' + st.t + '</b>' + st.text + '</li>'; }).join('');
    } else if (info) {
      items = info.steps.map(function (tx) { return '<li>' + tx + '</li>'; }).join('');
    }
    if (items) {
      h += '<details class="calc-steps"' + (PI ? ' open' : '') + '><summary>' + T.steps_h + (PI ? ': ' + PI.n : '') + '</summary><ol>' + items + '</ol>';
      if (PI && PI.note) h += '<p>' + PI.note + '</p>';
      if (PI) h += '<p>' + T.src_lbl + ': <a href="' + PI.src[0] + '" target="_blank" rel="noopener">' + PI.src[1] + '</a></p>';
      h += '</details>';
    }
    return h;
  }
  function saveState() { try { localStorage.setItem('zrn-calc', JSON.stringify({ m: S.m, prec: S.prec, cupMl: S.cupMl })); } catch (e) {} }
  function loadState() {
    try {
      var s = JSON.parse(localStorage.getItem('zrn-calc') || 'null');
      if (s) { if (METHODS[s.m]) { applyMethod(s.m); } if (s.prec === 0.1) S.prec = 0.1; if (s.cupMl >= 30 && s.cupMl <= 1000) { S.cupMl = s.cupMl; S.cupMlTouched = true; } }
    } catch (e) {}
    var h = location.hash || '';
    if (h.indexOf('#calc=') === 0) {
      applyParams(h);
      setTimeout(function () { try { root.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) {} }, 300);
    }
  }
  function applyParams(h) {
    {
      var p = {}; h.slice(6).split(',').forEach(function (kv) { var a = kv.split(':'); p[a[0]] = a[1]; });
      if (METHODS[p.m]) { applyMethod(p.m); }
      if (p.g && /^(drink|dose|water|yield)$/.test(p.g)) S.g = p.g;
      if (p.c) S.cups = clamp(parseInt(p.c, 10) || 1, 1, 24);
      if (p.s) { S.cupMl = clamp(num(p.s) || 250, 30, 1000); S.cupMlTouched = true; }
      if (p.d) { var dv = num(p.d); if (isFinite(dv)) { if (S.m === 'espresso') S.edose = clamp(dv, 5, 60); else S.dose = clamp(dv, 1, 300); } }
      if (p.w) { var wv = num(p.w); if (isFinite(wv)) S.water = clamp(wv, 30, 5000); }
      if (p.r) { var rv = num(p.r); if (isFinite(rv)) { if (S.m === 'espresso') S.er = clamp(rv, 1, 4); else S.r = clamp(rv, 4, 30); } }
      if (p.p === '0.1') S.prec = 0.1;
      if (p.v === 'conc') S.variant = 'conc';
      if (p.x) S.pot = METHODS.moka.pots[p.x] ? parseInt(p.x, 10) : 2;
      if (p.t) S.serv = clamp(parseInt(p.t, 10) || 1, 1, 12);
      if (p.e) S.per = clamp(num(p.e) || 70, 30, 200);
      if (p.n === '0') S.ret = false;
      if (p.k && PRESETS[p.k] && PRESETS[p.k].m === S.m) S.preset = p.k;
      if (p.z) { var zv = num(p.z); if (isFinite(zv) && zv > 0) S.tds = clamp(zv, 0.05, 15); }
    }
  }
  function hashState() {
    var a = ['m:' + S.m];
    if (S.m === 'espresso') { a.push('g:' + S.g, 'd:' + S.edose, 'r:' + S.er); }
    else if (S.m === 'moka') { a.push('x:' + S.pot); }
    else if (S.m === 'turka') { a.push('t:' + S.serv, 'e:' + S.per, 'r:' + S.r); }
    else { a.push('g:' + S.g, 'r:' + S.r); if (S.g === 'drink') a.push('c:' + S.cups, 's:' + S.cupMl); if (S.g === 'dose') a.push('d:' + S.dose); if (S.g === 'water') a.push('w:' + S.water); if (!S.ret) a.push('n:0'); if (S.m === 'cold' && S.variant === 'conc') a.push('v:conc'); }
    if (S.prec === 0.1) a.push('p:0.1');
    if (S.preset) a.push('k:' + S.preset);
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
    if (b.hasAttribute('data-tm')) { if (b.getAttribute('data-tm') === 'go') tmToggle(); else tmReset(); return; }
    if (b.hasAttribute('data-prepanel')) { S.preOpen = !S.preOpen; }
    else if (b.hasAttribute('data-preset')) { S.preOpen = false; applyPreset(b.getAttribute('data-preset')); }
    else if (b.hasAttribute('data-m')) { applyMethod(b.getAttribute('data-m')); }
    else if (b.hasAttribute('data-g')) { S.g = b.getAttribute('data-g'); if (S.g === 'dose' && S.m !== 'espresso') S.dose = (root._o && root._o.dose) ? root._o.dose : S.dose; if (S.g === 'water' && root._o && root._o.water) S.water = root._o.water; }
    else if (b.hasAttribute('data-v')) { S.variant = b.getAttribute('data-v'); S.r = S.variant === 'conc' ? 8 : 10; }
    else if (b.hasAttribute('data-p')) { S.prec = parseFloat(b.getAttribute('data-p')); }
    else if (b.hasAttribute('data-cup')) { S.cupMl = parseInt(b.getAttribute('data-cup'), 10); S.cupMlTouched = true; }
    else if (b.hasAttribute('data-pot')) { S.pot = parseInt(b.getAttribute('data-pot'), 10); }
    else if (b.hasAttribute('data-rc')) { S.preset = ''; var v = parseFloat(b.getAttribute('data-rc')); if (S.m === 'espresso') S.er = v; else S.r = v; }
    else if (b.hasAttribute('data-inc') || b.hasAttribute('data-dec')) {
      var key = b.getAttribute('data-inc') || b.getAttribute('data-dec'), sign = b.hasAttribute('data-inc') ? 1 : -1;
      var st = { cups: 1, cupMl: 10, dose: S.prec, water: 10, serv: 1, per: 10 }[key] || 1;
      var cur = (key === 'dose' && S.m === 'espresso') ? S.edose : S[key]; if (key === 'cupMl') S.cupMlTouched = true;
      setVal(key, Math.round((cur + sign * st) * 10) / 10);
    }
    else if (b.hasAttribute('data-copy')) { copy(recipeText() + '\n' + location.href.split('#')[0] + hashState(), T.copied); return; }
    else if (b.hasAttribute('data-save')) {
      var sv = getSaved(), hs = hashState(), nm = recipeName(root._o);
      sv = sv.filter(function (r) { return r.h !== hs; }); sv.unshift({ n: nm, h: hs, t: Date.now() }); if (sv.length > 10) sv.length = 10;
      pendingToast = putSaved(sv) ? T.saved_ok : T.saved_fail;
    }
    else if (b.hasAttribute('data-load')) {
      var ld = getSaved()[parseInt(b.getAttribute('data-load'), 10)];
      if (ld && ld.h) { var keep = { prec: S.prec, cupMl: S.cupMl, cupMlTouched: S.cupMlTouched }; var fresh = JSON.parse(S0); for (var kk in fresh) S[kk] = fresh[kk]; applyParams(ld.h); }
    }
    else if (b.hasAttribute('data-del')) { var dl = getSaved(); dl.splice(parseInt(b.getAttribute('data-del'), 10), 1); putSaved(dl); }
    else if (b.hasAttribute('data-share')) { var url = location.href.split('#')[0] + hashState(); try { history.replaceState(null, '', hashState()); } catch (e2) {} copy(url, T.shared); return; }
    else return;
    render();
    if (pendingToast) { var tt = $('[data-toast]'); if (tt) tt.textContent = pendingToast; pendingToast = ''; }
  });
  var pendingToast = '';
  root.addEventListener('input', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-range')) { S.preset = ''; var v = parseFloat(t.value); if (S.m === 'espresso') S.er = Math.round(v * 20) / 20; else S.r = Math.round(v * 10) / 10; render(); return; }
    if (t.hasAttribute('data-torange')) { S.to = parseFloat(t.value); render(); return; }
    if (t.hasAttribute('data-ret')) { S.ret = t.checked; render(); return; }
    if (t.hasAttribute('data-tds')) { var tv = num(t.value); S.tds = (isFinite(tv) && tv > 0) ? clamp(tv, 0.05, 15) : 0; render(); return; }
    if (t.hasAttribute('data-in')) { var key = t.getAttribute('data-in'), n = num(t.value); if (isFinite(n) && n > 0) { if (key === 'cupMl') S.cupMlTouched = true; setVal(key, n); render(); } }
  });
  root.addEventListener('focusout', function (e) { var t = e.target; if (t.hasAttribute && t.hasAttribute('data-in')) setTimeout(function () { render(); var k = t.getAttribute('data-in'); setIn(k, (k === 'dose' && S.m === 'espresso') ? S.edose : S[k]); }, 0); });

  var S0 = JSON.stringify(S);
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
    h += '<p class="calc-a2hs"><small>%s</small></p>\n' % {
        'uk': 'Порада: додайте сайт на головний екран телефона (меню браузера, «Додати на головний екран»), і калькулятор буде під рукою на кухні. На Android довгий дотик до значка ZRN Coffee відкриває пункт «Калькулятор кави».',
        'ru': 'Совет: добавьте сайт на главный экран телефона (меню браузера, «Добавить на главный экран»), и калькулятор будет под рукой на кухне. На Android долгое нажатие на значок ZRN Coffee открывает пункт «Калькулятор кофе».'}[lang]
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
