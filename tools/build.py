#!/usr/bin/env python3
"""
ZRN Coffee — збірка сайту з catalog.json.

Що робить (запускати з кореня репозиторію:  python tools/build.py):
  1. Перевіряє catalog.json (зрозумілі помилки, якщо щось не так).
  2. Вставляє дані сортів і статей у index.html (між маркерами /*CATALOG:START*/ … /*CATALOG:END*/),
     оновлює список у <noscript> та посилання в підвалі.
  3. Генерує сторінки сортів (coffee/<id>/), блог (blog/…), російські версії (ru/…),
     pages.css та sitemap.xml.

index.html сам по собі нічого не втрачає: все, що поза маркерами, лишається як є.
"""
import datetime
import html
import json
import os
import re
import time
import urllib.request
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, 'catalog.json')
INDEX = os.path.join(ROOT, 'index.html')
E = html.escape
LANGS = ('uk', 'ru')
TODAY = datetime.date.today().isoformat()

BREW_RU = {'Фільтр': 'Фильтр', 'Еспресо': 'Эспрессо', 'Автомат': 'Автомат', 'Турка': 'Турка', 'Гейзер': 'Гейзер',
           'Гейзерна': 'Гейзер', 'Френч-прес': 'Френч-пресс', 'З молоком': 'С молоком'}


def fail(msg):
    sys.stderr.write('\nПОМИЛКА в catalog.json: ' + msg + '\n')
    sys.exit(1)


# ------------------------------------------------------------------ завантаження і перевірка
def load():
    try:
        cat = json.load(open(CATALOG, encoding='utf-8'))
    except json.JSONDecodeError as e:
        fail(f'файл не є коректним JSON — рядок {e.lineno}, позиція {e.colno}: {e.msg}. '
             'Найчастіше це зайва або загублена кома, лапка чи дужка поруч із цим місцем.')
    for key in ('site', 'products', 'posts', 'brewGuide', 'processInfo'):
        if key not in cat:
            fail(f'немає розділу "{key}"')
    ids = set()
    for i, p in enumerate(cat['products']):
        where = f'сорт №{i + 1} ({p.get("id", "?")})'
        for k in ('id', 'type', 'name', 'img', 'alt', 'accent', 'price200', 'price500', 'region', 'variety',
                  'processing', 'roastLevel', 'roastLabel', 'notes', 'info', 'story', 'brew', 'taste'):
            if k not in p:
                fail(f'{where}: немає поля "{k}"')
        if p['id'] in ids:
            fail(f'{where}: id повторюється')
        ids.add(p['id'])
        if not re.fullmatch(r'[a-z0-9-]+', p['id']):
            fail(f'{where}: id має складатися з латинських малих літер, цифр і дефіса')
        if p['type'] not in ('mono', 'blend'):
            fail(f'{where}: type має бути "mono" або "blend"')
        for k in ('price200', 'price500', 'roastLevel'):
            if not isinstance(p[k], int):
                fail(f'{where}: "{k}" має бути цілим числом без лапок')
        if not 1 <= p['roastLevel'] <= 5:
            fail(f'{where}: roastLevel від 1 до 5')
        for k in ('region', 'variety', 'roastLabel', 'notes', 'info', 'story') + (('ratio',) if 'ratio' in p else ()):
            for lang in LANGS:
                if lang not in p[k] or not p[k][lang]:
                    fail(f'{where}: у полі "{k}" немає тексту для "{lang}"')
        for k in ('acid', 'sweet', 'bitter', 'body'):
            if not isinstance(p['taste'].get(k), int) or not 1 <= p['taste'][k] <= 5:
                fail(f'{where}: taste.{k} має бути числом від 1 до 5')
        for b in p['brew']:
            if b not in cat['brewGuide']:
                fail(f'{where}: способу заварювання "{b}" немає в розділі brewGuide')
        if os.path.isdir(os.path.join(ROOT, 'img')) and not os.path.exists(os.path.join(ROOT, p['img'])):
            sys.stderr.write(f'Увага: файлу зображення немає в репозиторії: {p["img"]} ({p["id"]})\n')
    for i, a in enumerate(cat['posts']):
        for k in ('id', 'k', 'title', 'excerpt', 'body'):
            if k not in a:
                fail(f'стаття №{i + 1}: немає поля "{k}"')
        for k in ('k', 'title', 'excerpt', 'body'):
            for lang in LANGS:
                if not a[k].get(lang):
                    fail(f'стаття "{a["id"]}": у полі "{k}" немає тексту для "{lang}"')
    return cat


# ------------------------------------------------------------------ ціни, ваги і налаштування з Google Таблиці
SETTINGS = {'freeShip': 1400, 'heroW': 200, 'heroP': 260, 'sub': {'on': True}}   # заповнюється в apply_sheet()


def find_sheet_url():
    m = re.search(r"const ORDER_SHEET_URL\s*=\s*'([^']*)'", open(INDEX, encoding='utf-8').read())
    return (m.group(1) if m else '').strip()


def fetch_sheet(url):
    last = ''
    for attempt in range(3):
        try:
            req = urllib.request.Request(url + ('&' if '?' in url else '?') + 'prices=1', headers={'User-Agent': 'zrn-build'})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.loads(r.read().decode('utf-8'))
            if isinstance(data, dict) and data.get('ok') and isinstance(data.get('products'), list):
                return data
            last = 'таблиця відповіла без даних цін (оновіть Apps Script до нової версії і запустіть setupPrices)'
        except Exception as e:   # мережа, не JSON тощо
            last = str(e)
        time.sleep(2 + attempt * 3)
    return last


def posint(v):
    try:
        f = float(str(v).replace(',', '.').replace(' ', '').replace('\u00a0', ''))
    except ValueError:
        return None
    return int(round(f)) if f > 0 and abs(f - round(f)) < 1e-9 else None


def badge_from(v):
    """Текст із колонки «Плашка» → (текст українською для сайту, тип для стилю). Порожньо → (None, None)."""
    t = str(v or '').strip()
    if not t or t in ('-', '—', 'ні', 'Ні', 'нет', 'Нет'):
        return None, None
    k = t.lower().replace('ё', 'е')
    if k.startswith('популярн'):
        return 'Популярне', 'popular'
    if k.startswith('новинк'):
        return 'Новинка', 'new'
    if k.startswith('вибір') or k.startswith('выбор'):
        return 'Вибір роастмайстера', 'choice'
    return t[:30], 'choice'


def truthy(v):
    return str(v).strip().lower() not in ('ні', 'нет', 'no', 'false', '0', '-', 'hide', 'приховати')


def sets_from(sheet, cat):
    """Набори знайомства: з листа «Набори» (якщо він є), інакше з catalog.json → "sets". Показуємо лише коректні й увімкнені."""
    raw = sheet.get('sets') if isinstance(sheet, dict) and isinstance(sheet.get('sets'), list) else (cat.get('sets') or [])
    prods = {p['id']: p for p in cat['products']}
    out = []
    for idx, r in enumerate(raw):
        sid = str(r.get('id', '')).strip()
        if not sid or not truthy(r.get('show', 'Так')):
            continue
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sid):
            sys.stderr.write(f'Увага: набір «{sid}»: ID має бути латиницею/цифрами — пропущено.\n')
            continue
        name_uk = str(r.get('nameUk', '')).strip()
        price = posint(r.get('price'))
        defw = posint(r.get('defW'))
        items, bad = [], False
        for part in re.split(r'[,;\n]', str(r.get('items', ''))):
            part = part.strip()
            if not part:
                continue
            m = re.fullmatch(r'([A-Za-z0-9_-]+)\s*(?::\s*(\d+(?:[.,]\d+)?))?', part)
            if not m:
                bad = True
                break
            w = posint(m.group(2)) if m.group(2) else defw
            if m.group(1) not in prods or not w:
                sys.stderr.write(f'Увага: набір «{sid}»: сорт «{m.group(1)}» схований, відсутній у листі «Ціни» або без ваги — набір не показано.\n')
                bad = True
                break
            items.append({'id': m.group(1), 'w': w})
        if bad or len(items) < 2 or not name_uk or not price:
            if not bad:
                sys.stderr.write(f'Увага: набір «{sid}»: потрібні назва, ціна й щонайменше 2 сорти — не показано.\n')
            continue
        worth = int(round(sum(prods[i['id']]['price1'] / prods[i['id']]['w1'] * i['w'] for i in items)))
        o = posint(r.get('order'))
        name_ru = str(r.get('nameRu', '')).strip() or name_uk
        desc_uk = str(r.get('descUk', '')).strip()
        badge_uk = str(r.get('badgeUk', '')).strip()
        out.append(((o if o is not None else 1e9, idx), {
            'id': 'set-' + sid.lower(), 'name': name_uk, 'desc': desc_uk, 'badge': badge_uk,
            'price': price, 'worth': worth if worth > price else 0, 'items': items,
            'ru': {'name': name_ru, 'desc': str(r.get('descRu', '')).strip() or desc_uk, 'badge': str(r.get('badgeRu', '')).strip() or badge_uk}}))
    return [x[1] for x in sorted(out, key=lambda x: x[0])]


REVIEWS_DATA = None   # None = у таблиці немає даних про відгуки (старий Apps Script) → блок у index.html не чіпаємо


def reviews_from(sheet):
    out = []
    for r in (sheet or {}).get('reviews') or []:
        text = str(r.get('text', '')).strip()
        if len(text) < 5:
            continue
        try:
            rating = max(1, min(5, int(float(r.get('rating', 5)))))
        except ValueError:
            rating = 5
        out.append({'name': str(r.get('name', '')).strip()[:80], 'rating': rating, 'product': str(r.get('product', '')).strip()[:80], 'text': text[:1200]})
    return out[:12]


def apply_sheet(cat):
    """Накладає на catalog.json ціни/ваги/видимість/порядок із листа «Ціни» та налаштування з листа «Налаштування».
    Значення з catalog.json (price200/price500) — запасні: їх використовують, якщо сорту в таблиці немає."""
    for p in cat['products']:
        p['w1'], p['w2'], p['price1'], p['price2'] = 200, 500, p['price200'], p['price500']
    url = os.environ.get('ZRN_SHEET_URL') or find_sheet_url()
    off = os.environ.get('ZRN_OFFLINE') == '1' or cat['site'].get('pricesFromSheet') is False or not url
    sheet = None
    if off:
        sys.stderr.write('Увага: ціни беруться з catalog.json (таблицю не читаємо).\n')
    else:
        sheet = fetch_sheet(url)
        if isinstance(sheet, str):
            sys.stderr.write('\nПОМИЛКА: не вдалося прочитати ціни з Google Таблиці: ' + sheet + '\n'
                             'Збирання зупинено, щоб на сайті не з\'явилися застарілі ціни: попередня версія сайту лишається.\n'
                             'Що зробити: перевірте, що Apps Script оновлено й розгорнуто (Deploy → New version), потім запустіть збирання знову.\n')
            sys.exit(1)
    rows = {}
    if sheet:
        for r in sheet['products']:
            rows[str(r.get('id', '')).strip()] = r
        for rid in rows:
            if rid and rid not in {p['id'] for p in cat['products']}:
                sys.stderr.write(f'Увага: у листі «Ціни» є сорт «{rid}», якого немає в catalog.json — рядок пропущено.\n')
    shown = []
    for idx, p in enumerate(cat['products']):
        r = rows.get(p['id'])
        p['_ord'] = (1e9, idx)
        if r:
            if not truthy(r.get('show', 'Так')):
                continue
            w1, w2, p1, p2 = (posint(r.get(k)) for k in ('w1', 'w2', 'p1', 'p2'))
            if None in (w1, w2, p1, p2):
                sys.stderr.write(f'Увага: сорт «{p["id"]}»: у листі «Ціни» не всі значення є додатними числами — лишаємо значення з catalog.json.\n')
            else:
                if w1 > w2:
                    w1, w2, p1, p2 = w2, w1, p2, p1
                if w1 == w2:
                    sys.stderr.write(f'Увага: сорт «{p["id"]}»: однакові ваги — лишаємо значення з catalog.json.\n')
                else:
                    p['w1'], p['w2'], p['price1'], p['price2'] = w1, w2, p1, p2
            o = posint(r.get('order'))
            if o is not None:
                p['_ord'] = (o, idx)
            if 'badge' in r:   # колонка «Плашка» є в таблиці: порожньо = без плашки; немає колонки (старий скрипт) = як у catalog.json
                p['badge'], p['badgeType'] = badge_from(r.get('badge'))
        shown.append(p)
    if not shown:
        fail('усі сорти приховані в листі «Ціни» — на сайті має лишитися хоча б один.')
    cat['products'] = sorted(shown, key=lambda p: p['_ord'])
    for p in cat['products']:
        p.pop('_ord', None)
    cat['sets_out'] = sets_from(sheet, cat)
    global REVIEWS_DATA
    if sheet and isinstance(sheet.get('reviews'), list):
        REVIEWS_DATA = reviews_from(sheet)
    # налаштування: порожня клітинка → автоматично
    st = (sheet or {}).get('settings') or {}
    free = posint(st.get('freeShip')) or 1400
    hw = posint(st.get('heroW'))
    hp = posint(st.get('heroP'))
    if not hw:
        ws = [p['w1'] for p in cat['products']]
        hw = max(set(ws), key=lambda w: (ws.count(w), -w))
    if not hp:
        hp = min(p['price1'] for p in cat['products'] if p['w1'] == hw)
    # Клуб (підписка): на сайті лише перемикач «показувати блок» (Так/Ні); решта налаштувань потрібна лише скрипту таблиці
    off = str(st.get('subOn', '')).strip().lower() in ('ні', 'нет', 'no', 'off', 'false', '0')
    SETTINGS.update({'freeShip': free, 'heroW': hw, 'heroP': hp, 'sub': {'on': not off}})
    cat['settings'] = dict(SETTINGS)
    return cat


# ------------------------------------------------------------------ блок даних для index.html
def j(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace('</', '<\\/')


def js_block(cat):
    prods = cat['products']
    mono = [p for p in prods if p['type'] == 'mono']
    blend = [p for p in prods if p['type'] == 'blend']

    def base(p):
        o = {'id': p['id'], 'img': '/' + p['img'], 'alt': p['alt'], 'accent': p['accent']}
        if p.get('badge'):
            o['badge'] = p['badge']
            o['badgeType'] = p['badgeType']
        if p.get('kicker'):
            o['kicker'] = p['kicker']
        o['name'] = p['name']
        o['region'] = p['region']['uk']
        o['variety'] = p['variety']['uk']
        if 'ratio' in p:
            o['ratio'] = p['ratio']['uk']
        o['processing'] = p['processing']
        o['roastLevel'] = p['roastLevel']
        o['roastLabel'] = p['roastLabel']['uk']
        o['notes'] = p['notes']['uk']
        o['info'] = p['info']['uk']
        o['story'] = p['story']['uk']
        o['brew'] = p['brew']
        o['w1'] = p['w1']
        o['w2'] = p['w2']
        o['price1'] = p['price1']
        o['price2'] = p['price2']
        return o

    i18n = {}
    for p in prods:
        e = {}
        if 'ratio' in p:
            e['ratio'] = p['ratio']
        for k in ('notes', 'info', 'roastLabel', 'variety', 'story', 'region'):
            e[k] = p[k]
        i18n[p['id']] = e
    blog = [{'id': a['id'], 'k': a['k']['uk'], 'title': a['title']['uk'], 'excerpt': a['excerpt']['uk'], 'body': a['body']['uk']}
            for a in cat['posts']]
    blog_i18n = {a['id']: {'k': a['k'], 'title': a['title'], 'excerpt': a['excerpt'],
                           'body': {'uk': None, 'ru': a['body']['ru']}} for a in cat['posts']}
    taste = {p['id']: p['taste'] for p in prods}
    out = ['/*CATALOG:START — блок генерується tools/build.py з catalog.json. Не правте вручну: зміни вносьте в catalog.json*/']
    out.append('const PRODUCT_I18N = ' + j(i18n) + ';')
    out.append('const BLOG_I18N = ' + j(blog_i18n) + ';')
    out.append('const PRODUCTS = ' + j([base(p) for p in mono]) + ';')
    out.append('const BLENDS = ' + j([base(p) for p in blend]) + ';')
    sets = cat.get('sets_out') or []
    out.append('const SETS = ' + j([{k: v for k, v in x.items() if k != 'ru'} for x in sets]) + ';')
    out.append('const SET_I18N = ' + j({x['id']: x['ru'] for x in sets}) + ';')
    out.append('const BLOG = ' + j(blog) + ';')
    out.append('const TASTE_PROFILE = ' + j(taste) + ';')
    out.append('const BREW_GUIDE = ' + j(cat['brewGuide']) + ';')
    out.append('const PROCESS_INFO = ' + j(cat['processInfo']) + ';')
    out.append('/*CATALOG:END*/')
    return '\n'.join(out)


def replace_between(text, start, end, new, label):
    a = text.find(start)
    b = text.find(end)
    if a < 0 or b < 0 or b < a:
        fail(f'в index.html не знайдено маркери {label}. Не видаляйте рядки з "CATALOG" / "CAT:" в index.html.')
    return text[:a + len(start)] + new + text[b:]


def noscript_block(cat):
    def lis(lst):
        return ''.join(f'\n      <li><a href="/coffee/{p["id"]}/">{E(p["name"])}</a> — {p["w1"]} г: {p["price1"]} ₴, {p["w2"]} г: {p["price2"]} ₴</li>'
                       for p in lst)
    mono = [p for p in cat['products'] if p['type'] == 'mono']
    blend = [p for p in cat['products'] if p['type'] == 'blend']
    return (f'\n  <h3>Моносорти</h3>\n  <ul>{lis(mono)}\n  </ul>\n  <h3>Бленди</h3>\n  <ul>{lis(blend)}\n  </ul>\n  ')


def build_index(cat):
    s = open(INDEX, encoding='utf-8').read()
    s = replace_between(s, '/*CATALOG:START', '/*CATALOG:END*/', '', 'CATALOG')  # перевірка наявності
    a = s.index('/*CATALOG:START')
    b = s.index('/*CATALOG:END*/') + len('/*CATALOG:END*/')
    s = s[:a] + js_block(cat) + s[b:]
    s = replace_between(s, '<!--CAT:NOSCRIPT:START-->', '<!--CAT:NOSCRIPT:END-->', noscript_block(cat), 'CAT:NOSCRIPT')
    s = replace_between(s, '/*SETTINGS:START*/', '/*SETTINGS:END*/', 'const ZRN_SET = ' + json.dumps(SETTINGS) + ';', 'SETTINGS')
    s = replace_between(s, '<!--FAQ:LD:START-->', '<!--FAQ:LD:END-->', faq_ld_tag(s, 'uk'), 'FAQ:LD')
    # числа у статичному HTML (для пошуковиків і режиму без JS): <span data-v="free">1400</span>
    if REVIEWS_DATA is not None:
        rj = json.dumps(REVIEWS_DATA, ensure_ascii=False).replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        s = replace_between(s, '/*REVIEWS:START*/', '/*REVIEWS:END*/', 'const REVIEWS = ' + rj + ';', 'REVIEWS')
    s = re.sub(r'(<span data-v="(\w+)">)[^<]*(</span>)', lambda m: m.group(1) + str(SETTINGS.get(m.group(2), '')) + m.group(3), s)
    open(INDEX, 'w', encoding='utf-8').write(s)
    return s


# ------------------------------------------------------------------ тексти інтерфейсу з index.html
def ui_texts(index_src):
    """Дістає з словника ZRN_I18N у index.html тексти, які повторюються на сторінках (щоб не дублювати вручну)."""
    start = index_src.index('const ZRN_I18N = {')
    ru_at = index_src.index('\nru: {', start)
    parts = {'uk': index_src[start:ru_at], 'ru': index_src[ru_at:ru_at + 400000]}

    def get(lang, key):
        m = re.search(r"'" + re.escape(key) + r"':\s*'((?:[^'\\]|\\.)*)'", parts[lang])
        if not m:
            fail(f'в index.html не знайдено текст інтерфейсу "{key}" ({lang})')
        return m.group(1).replace("\\'", "'").replace('\\\\', '\\')
    keys = ['trust.fact', 'ship.del2', 'ship.del3', 'ship.del4', 'ship.pay1', 'ck.guarantee', 'meta.title', 'meta.desc']
    def tok(v):
        return v.replace('{free}', str(SETTINGS['freeShip'])).replace('{heroW}', str(SETTINGS['heroW'])).replace('{heroP}', str(SETTINGS['heroP']))
    return {lang: {k: tok(get(lang, k)) for k in keys} for lang in LANGS}


def faq_ld_tag(index_src, lang):
    """Статична розмітка FAQPage з тих самих текстів faq.q1..N / faq.a1..N, що показуються на сайті (для пошуковиків без JS)."""
    start = index_src.index('const ZRN_I18N = {')
    ru_at = index_src.index('\nru: {', start)
    part = index_src[start:ru_at] if lang == 'uk' else index_src[ru_at:ru_at + 400000]

    def get(key):
        m = re.search(r"'" + re.escape(key) + r"':\s*'((?:[^'\\]|\\.)*)'", part)
        if not m:
            return None
        v = m.group(1).replace("\\'", "'").replace('\\\\', '\\')
        return v.replace('{free}', str(SETTINGS['freeShip'])).replace('{heroW}', str(SETTINGS['heroW'])).replace('{heroP}', str(SETTINGS['heroP']))
    items = []
    for i in range(1, 31):
        q, a = get(f'faq.q{i}'), get(f'faq.a{i}')
        if not q or not a:
            break
        items.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    if not items:
        fail('не знайдено тексти FAQ (faq.q1/faq.a1) в index.html')
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': 'ru' if lang == 'ru' else 'uk', 'mainEntity': items}
    return '<script type="application/ld+json" id="ld-faq">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>'


# ------------------------------------------------------------------ сторінки
ICONS = '''<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script src="/analytics.js" defer></script>'''

UI = {
    'uk': dict(lang='uk', loc='uk_UA', catalog='Моносорти', blends='Бленди', blog='Блог', blogTitle='Блог ZRN', buy='Обрати вагу і замовити',
               g='г', about='Про цей сорт', specs='Характеристики', region='Регіон', alt_h='Висота вирощування', alt_u='м над рівнем моря',
               variety='Різновид', process='Обробка', roast='Обсмаження', comp='Склад', brew='Як заварювати', notes='Смак',
               taste_h='Смак', taste_note='Оцінка обсмажувальника за шкалою від 1 до 5.',
               acid='Кислотність', sweet='Солодкість', bitter='Гіркота', body='Тіло', light='світле', dark='темне',
               origin_h='Походження та обробка', ship_h='Доставка та гарантія', similar='Спробуйте також', allc='Усі сорти',
               from_='від ', more='Читайте також', toShop='До каталогу', read='Читати',
               fresh='Обсмажуємо після замовлення, доставка по Україні', foot='Мікроростерня ZRN · Обсмажуємо після замовлення',
               mail='Написати на пошту', craft='Craft Micro Roastery', h1='Кава ', tTitle=' — свіжообсмажена кава | ZRN Coffee',
               pre='', postSuf=' | Блог ZRN Coffee', home='Головна', altcode='RU', per100='/ 100 г',
               brewNote='Це стартові рецепти — підлаштуйте їх під свій смак: гірчить → грубіший помел, кисло → дрібніший.',
               blogDesc='Статті про каву від мікроростерні ZRN: помел, свіжість, зберігання та заварювання.',
               blogIdx='Блог ZRN — про каву, помел і свіжість | ZRN Coffee', author='Руслан Зеленський',
               offer='Публічна оферта', privacy='Політика конфіденційності'),
    'ru': dict(lang='ru', loc='ru_RU', catalog='Моносорты', blends='Бленды', blog='Блог', blogTitle='Блог ZRN', buy='Выбрать вес и заказать',
               g='г', about='Об этом сорте', specs='Характеристики', region='Регион', alt_h='Высота выращивания', alt_u='м над уровнем моря',
               variety='Разновидность', process='Обработка', roast='Обжарка', comp='Состав', brew='Как заваривать', notes='Вкус',
               taste_h='Вкус', taste_note='Оценка обжарщика по шкале от 1 до 5.',
               acid='Кислотность', sweet='Сладость', bitter='Горечь', body='Тело', light='светлая', dark='тёмная',
               origin_h='Происхождение и обработка', ship_h='Доставка и гарантия', similar='Попробуйте также', allc='Все сорта',
               from_='от ', more='Читайте также', toShop='В каталог', read='Читать',
               fresh='Обжариваем после заказа, доставка по Украине', foot='Микрообжарочная ZRN · Обжариваем после заказа',
               mail='Написать на почту', craft='Craft Micro Roastery', h1='Кофе ', tTitle=' — свежеобжаренный кофе | ZRN Coffee',
               pre='/ru', postSuf=' | Блог ZRN Coffee', home='Главная', altcode='UA', per100='/ 100 г',
               brewNote='Это стартовые рецепты — подстройте их под свой вкус: горчит → грубее помол, кисло → мельче.',
               blogDesc='Статьи о кофе от микрообжарочной ZRN: помол, свежесть, хранение и заваривание.',
               blogIdx='Блог ZRN — о кофе, помоле и свежести | ZRN Coffee', author='Руслан Зеленский',
               offer='Публичная оферта (укр.)', privacy='Политика конфиденциальности (укр.)'),
}



REV = {
    'uk': dict(title='Залишити відгук про каву | ZRN Coffee', desc='Розкажіть, як вам кава ZRN — відгук допоможе іншим обрати свій сорт.',
               h1='Ваш відгук про каву', lead='Розкажіть, як вам смакує кава ZRN. Це допомагає іншим обрати свій сорт, а нам — ставати кращими. Займе хвилину.',
               rating='Ваша оцінка*', rating_err='Поставте оцінку від 1 до 5.', product='Яку каву пробували', product_any='— не вказувати —',
               text='Ваш відгук*', text_ph='Який смак, аромат, як заварювали, що сподобалось…', text_err='Напишіть, будь ласка, хоча б кілька слів (від 10 символів).',
               name='Ваше ім’я*', name_ph='Як вас підписати на сайті', name_err='Вкажіть ім’я (можна лише ім’я).',
               order='Номер замовлення', order_hint='Він є в повідомленні про замовлення — так відгук буде позначено як перевірену покупку. Необов’язково.',
               consent='Погоджуюсь на публікацію мого відгуку та імені на сайті. <a href="/privacy/" target="_blank" rel="noopener">Політика конфіденційності</a>',
               consent_err='Підтвердіть згоду на публікацію відгуку.', submit='Надіслати відгук', sending='Надсилаємо…',
               ok_h='Дякуємо за відгук!', ok_p='Ми обов’язково його прочитаємо. Після перевірки відгук може з’явитися на сайті.', ok_btn='До каталогу',
               fail='Не вдалося надіслати відгук. Спробуйте ще раз або напишіть нам у Telegram: '),
    'ru': dict(title='Оставить отзыв о кофе | ZRN Coffee', desc='Расскажите, как вам кофе ZRN — отзыв поможет другим выбрать свой сорт.',
               h1='Ваш отзыв о кофе', lead='Расскажите, как вам вкус кофе ZRN. Это помогает другим выбрать свой сорт, а нам — становиться лучше. Займёт минуту.',
               rating='Ваша оценка*', rating_err='Поставьте оценку от 1 до 5.', product='Какой кофе пробовали', product_any='— не указывать —',
               text='Ваш отзыв*', text_ph='Какой вкус, аромат, как заваривали, что понравилось…', text_err='Напишите, пожалуйста, хотя бы несколько слов (от 10 символов).',
               name='Ваше имя*', name_ph='Как вас подписать на сайте', name_err='Укажите имя (можно только имя).',
               order='Номер заказа', order_hint='Он есть в сообщении о заказе — так отзыв будет отмечен как проверенная покупка. Необязательно.',
               consent='Согласен на публикацию моего отзыва и имени на сайте. <a href="/privacy/" target="_blank" rel="noopener">Политика конфиденциальности (укр.)</a>',
               consent_err='Подтвердите согласие на публикацию отзыва.', submit='Отправить отзыв', sending='Отправляем…',
               ok_h='Спасибо за отзыв!', ok_p='Мы обязательно его прочитаем. После проверки отзыв может появиться на сайте.', ok_btn='В каталог',
               fail='Не удалось отправить отзыв. Попробуйте ещё раз или напишите нам в Telegram: '),
}

NF = {
    'uk': dict(h='Сторінку не знайдено', p='Схоже, такої адреси немає: її могли змінити або видалити. Перейдіть до каталогу — там уся свіжообсмажена кава.',
               cat='До каталогу', blog='Блог', home='На головну'),
    'ru': dict(h='Страница не найдена', p='Похоже, такого адреса нет: его могли изменить или удалить. Перейдите в каталог — там весь свежеобжаренный кофе.',
               cat='В каталог', blog='Блог', home='На главную'),
}

REVIEW_HTML = """<nav class="crumbs" aria-label="breadcrumb"><a href="@@HOME@@">ZRN Coffee</a> › <span>@@H1@@</span></nav>
<h1>@@H1@@</h1>
<p class="lead">@@LEAD@@</p>
<form id="revForm" class="rev-form" novalidate>
  <fieldset class="rv-f"><legend>@@RATING@@</legend><div class="stars">@@STARS@@</div></fieldset>
  <div class="rv-f"><label for="revProduct">@@PRODUCT@@</label><select id="revProduct">@@OPTS@@</select></div>
  <div class="rv-f"><label for="revText">@@TEXT@@</label><textarea id="revText" rows="5" maxlength="2000" placeholder="@@TEXT_PH@@"></textarea></div>
  <div class="rv-f"><label for="revName">@@NAME@@</label><input type="text" id="revName" maxlength="80" autocomplete="given-name" placeholder="@@NAME_PH@@"></div>
  <div class="rv-f"><label for="revOrder">@@ORDER@@</label><input type="text" id="revOrder" maxlength="40" autocomplete="off" placeholder="ZRN-000000-000"><small>@@ORDER_HINT@@</small></div>
  <label class="rv-check" for="revConsent"><input type="checkbox" id="revConsent"><span>@@CONSENT@@</span></label>
  <div class="rv-hp" aria-hidden="true"><input type="checkbox" id="revBot" tabindex="-1" autocomplete="off"></div>
  <p id="revErr" class="rv-err" role="alert" hidden></p>
  <button type="submit" class="btn" id="revBtn">@@SUBMIT@@</button>
</form>
<div id="revThanks" class="rev-thanks" hidden>
  <h2>@@OK_H@@</h2>
  <p>@@OK_P@@</p>
  <p><a class="btn" href="@@HOME@@#catalog">@@OK_BTN@@</a></p>
</div>
<script>
(function(){
  var C = @@CFG@@;
  var f = document.getElementById('revForm'), err = document.getElementById('revErr'), btn = document.getElementById('revBtn');
  var q = new URLSearchParams(location.search);
  var o = (q.get('o') || '').replace(/[^A-Za-z0-9\\-]/g, '').slice(0, 40);
  if (o) document.getElementById('revOrder').value = o;
  var pid = q.get('p'); if (pid) document.getElementById('revProduct').value = pid;
  var lg = document.querySelector('.lang'); if (lg && location.search) lg.href += location.search;
  function fail(m){ err.textContent = m; err.hidden = false; }
  f.addEventListener('submit', function(e){
    e.preventDefault(); err.hidden = true;
    if (document.getElementById('revBot').checked) return;
    var rt = f.querySelector('input[name=rating]:checked');
    var text = document.getElementById('revText').value.trim();
    var name = document.getElementById('revName').value.trim();
    var sel = document.getElementById('revProduct'), prod = sel.value ? sel.options[sel.selectedIndex].getAttribute('data-name') : '';
    var order = document.getElementById('revOrder').value.trim();
    if (!rt) return fail(C.err.rating_err);
    if (text.length < 10) return fail(C.err.text_err);
    if (name.length < 2) return fail(C.err.name_err);
    if (!document.getElementById('revConsent').checked) return fail(C.err.consent_err);
    btn.disabled = true; btn.textContent = C.err.sending;
    var rating = Number(rt.value);
    var w3 = fetch('https://api.web3forms.com/submit', {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'},
      body: JSON.stringify({access_key:C.key, subject:'Новий відгук ' + rating + '/5 — ZRN Coffee', from_name:'ZRN Coffee — відгуки',
        name:name, rating:rating + '/5', product:prod || '—', order_number:order || '—', review:text, lang:C.lang,
        message:'Новий відгук ' + rating + '/5\\nСорт: ' + (prod || '—') + '\\nІм’я: ' + name + '\\nЗамовлення: ' + (order || '—') + '\\n\\n' + text, botcheck:false})})
      .then(function(r){return r.json();}).then(function(r){return !!(r && r.success);}).catch(function(){return false;});
    var sh = !C.sheet ? Promise.resolve(false) : fetch(C.sheet, {method:'POST', headers:{'Content-Type':'text/plain;charset=utf-8'},
      body: JSON.stringify({kind:'review', name:name, rating:rating, product:prod, text:text, orderNumber:order, lang:C.lang, consent:true})})
      .then(function(r){return r.json();}).then(function(r){return !!(r && r.ok);}).catch(function(){return false;});
    Promise.all([w3, sh]).then(function(r){
      btn.disabled = false; btn.textContent = C.err.submit;
      if (r[0] || r[1]) { f.hidden = true; document.getElementById('revThanks').hidden = false; window.scrollTo(0, 0); }
      else fail(C.err.fail + C.tg);
    });
  });
})();
</script>
"""

PAGE_404 = """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>404 — ZRN Coffee</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#f3ead9">
@@ICONS@@
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pages.css">
</head>
<body>
<header class="site-head"><div class="wrap hd-in"><a class="hd-logo" href="/" aria-label="ZRN Craft Micro Roastery"><b>ZRN</b><span>Craft Micro Roastery</span></a></div></header>
<main class="wrap nf-wrap">
<div class="nf-code" aria-hidden="true">404</div>
@@BLOCKS@@</main>
<script>
(function(){
  var l = 'uk';
  try { var q = new URLSearchParams(location.search).get('lang'); l = (q === 'ru' || q === 'uk') ? q : (localStorage.getItem('zrn_language') || (/^\\/ru(\\/|$)/.test(location.pathname) ? 'ru' : 'uk')); } catch (e) {}
  if (l !== 'ru') l = 'uk';
  document.documentElement.lang = l;
  document.querySelectorAll('.nf').forEach(function(s){ s.hidden = s.getAttribute('data-l') !== l; });
})();
</script>
</body>
</html>
"""

# Короткі адреси для соцмереж: zrncoffee.com.ua/ig → головна + запам'ятане джерело заказу
SHORT = {'ig': 'instagram', 'tg': 'telegram', 'viber': 'viber', 'qr': 'qr', 'fb': 'facebook',
         'tt': 'tiktok', 'yt': 'youtube', 'x': 'x (twitter)'}

SHORT_HTML = '''<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZRN Coffee</title>@@META@@<meta name="robots" content="noindex, follow"><link rel="canonical" href="@@URL@@/">
<script>
(function(){var to='/';try{
  var q=new URLSearchParams(location.search).get('to');
  if(q&&q.charAt(0)==='/'&&q.charAt(1)!=='/'&&q.length<120)to=q;
  localStorage.setItem('zrn_attr',JSON.stringify({s:@@SRC@@,l:to.split('?')[0],t:Date.now()}));
}catch(e){}
location.replace(to);})();
</script>
<meta http-equiv="refresh" content="1;url=/">
<style>body{margin:0;display:grid;place-items:center;min-height:100vh;background:#f3ead9;font:16px system-ui,sans-serif;color:#1f1912}a{color:#1f1912}</style>
</head><body><p><a href="/">ZRN Coffee →</a></p></body></html>
'''


ST = {
    'uk': dict(
        title='Статус замовлення | ZRN Coffee', desc='Дізнайтесь, на якому етапі ваше замовлення: обсмажування, пакування, доставка.',
        h1='Статус замовлення', lead='Введіть номер замовлення та останні 4 цифри телефону, який вказували в замовленні.',
        order='Номер замовлення', order_ph='ZRN-261022-001', last4='Останні 4 цифри телефону', last4_ph='1234',
        btn='Дізнатись статус', loading='Шукаємо…', refresh='Оновити', again='Інше замовлення', forget='Не ваш пристрій? Очистити збережене',
        err_fmt='Перевірте номер замовлення та 4 цифри телефону.',
        err_nf='Не знайшли замовлення. Перевірте номер і останні 4 цифри телефону — вони мають збігатися з тими, що в замовленні.',
        err_lock='Забагато невдалих спроб. Спробуйте за 15 хвилин або напишіть нам.',
        err_net='Не вдалося отримати статус. Спробуйте ще раз за хвилину або напишіть нам у Telegram: ',
        ordered='Замовлення від', steps=['Прийнято', 'Обсмажуємо', 'Пакуємо', 'Відправлено', 'Отримано'],
        cancelled='Замовлення скасовано', returned='Посилку повернено відправнику',
        track_created='Передано до відправлення', track_transit='Посилка в дорозі', track_arrived='Посилка прибула — можна забирати',
        track_received='Посилку отримано', track_returning='Посилка повертається відправнику',
        at='Відділення', eta='Очікувана доставка', pay_h='Оплата',
        pay=dict(cod='При отриманні (накладений платіж)', wait='Очікуємо оплату. Реквізити надішлемо після підтвердження замовлення.',
                 paid='Оплачено', codpaid='Оплачено при отриманні', refused='Посилку не забрали', refund='Кошти повернено'),
        del_h='Доставка', ttn_np='ТТН Нової Пошти', ttn_ukr='Трек-номер Укрпошти', copy='Копіювати', copied='Скопійовано', track_link='Відстежити на сайті перевізника',
        items_h='Склад замовлення', total='Разом', note_h='Повідомлення від нас', help='Є питання?', tg='Написати в Telegram',
        auto='Статус доставки оновлюється автоматично.'),
    'ru': dict(
        title='Статус заказа | ZRN Coffee', desc='Узнайте, на каком этапе ваш заказ: обжарка, упаковка, доставка.',
        h1='Статус заказа', lead='Введите номер заказа и последние 4 цифры телефона, который указывали в заказе.',
        order='Номер заказа', order_ph='ZRN-261022-001', last4='Последние 4 цифры телефона', last4_ph='1234',
        btn='Узнать статус', loading='Ищем…', refresh='Обновить', again='Другой заказ', forget='Не ваше устройство? Очистить сохранённое',
        err_fmt='Проверьте номер заказа и 4 цифры телефона.',
        err_nf='Не нашли заказ. Проверьте номер и последние 4 цифры телефона — они должны совпадать с указанными в заказе.',
        err_lock='Слишком много неудачных попыток. Попробуйте через 15 минут или напишите нам.',
        err_net='Не удалось получить статус. Попробуйте ещё раз через минуту или напишите нам в Telegram: ',
        ordered='Заказ от', steps=['Принят', 'Обжарка', 'Упаковка', 'Отправлен', 'Получен'],
        cancelled='Заказ отменён', returned='Посылка возвращена отправителю',
        track_created='Передано к отправке', track_transit='Посылка в пути', track_arrived='Посылка прибыла — можно забирать',
        track_received='Посылка получена', track_returning='Посылка возвращается отправителю',
        at='Отделение', eta='Ожидаемая доставка', pay_h='Оплата',
        pay=dict(cod='При получении (наложенный платёж)', wait='Ожидаем оплату. Реквизиты отправим после подтверждения заказа.',
                 paid='Оплачено', codpaid='Оплачено при получении', refused='Посылку не забрали', refund='Средства возвращены'),
        del_h='Доставка', ttn_np='ТТН Новой Почты', ttn_ukr='Трек-номер Укрпочты', copy='Копировать', copied='Скопировано', track_link='Отследить на сайте перевозчика',
        items_h='Состав заказа', total='Итого', note_h='Сообщение от нас', help='Есть вопросы?', tg='Написать в Telegram',
        auto='Статус доставки обновляется автоматически.'),
}

SB = {
 'uk': dict(
  title='Моя підписка | Клуб ZRN', desc='Керування підпискою Клубу ZRN: пауза, пропуск, зміна сорту.',
  h1='Моя підписка', lead='Введіть номер підписки та останні 4 цифри телефону, який вказували у заявці.',
  id='Номер підписки', id_ph='SUB-0001', last4='Останні 4 цифри телефону', last4_ph='1234', btn='Відкрити', loading='Шукаємо…',
  forget='Не ваш пристрій? Очистити збережене',
  err_fmt='Перевірте номер підписки та 4 цифри телефону.', err_nf='Не знайшли підписку. Перевірте номер і останні 4 цифри телефону.',
  err_lock='Забагато невдалих спроб. Спробуйте за 15 хвилин або напишіть нам.', err_net='Не вдалося з’єднатися. Спробуйте ще раз або напишіть нам: ',
  err_locked='Відправка вже в роботі — тут змінити не вийде. Напишіть нам, і ми щось придумаємо.', err_act='Не вдалося виконати дію. Спробуйте ще раз або напишіть нам.',
  st_new='Заявку отримано', st_new_p='Ми зв’яжемося з вами, підтвердимо умови та призначимо першу відправку. Поки нічого не оплачується.',
  st_act='Активна', st_pause='На паузі', st_cancel='Скасована', st_cancel_p='Підписку скасовано. Дякуємо, що були з нами. Двері завжди відчинені — оформити нову можна будь-коли.',
  plan_h='Ваш план', type='Тип', fmt='Формат', level='Рівень', sort='Сорт', freq='Періодичність', grind='Помел', club_h='Статус у клубі', ships='Відправок',
  freq_t={'10': 'Кожні 10 днів', '14': 'Кожні 2 тижні', '30': 'Щомісяця'},
  next_h='Наступна відправка', next_none='Дату призначимо після підтвердження.', next_sort='Сорт цієї відправки', next_sort_none='роастмайстер обере сам', skipped='Цю відправку пропущено за вашим проханням.',
  pause_until='Пауза до', locked_note='До обсмажки менше ніж {lead} дні — зміни вже не приймаємо тут. Напишіть нам.',
  a_skip='Пропустити наступну відправку', a_unskip='Не пропускати наступну відправку', a_pause='Поставити на паузу', a_pause_date='Пауза до (необов’язково)', a_resume='Відновити підписку',
  a_addr_h='Змінити відділення або адресу', a_addr_now='Зараз', a_addr_city='Місто', a_addr_branch='Відділення / поштомат / адреса', a_addr_save='Зберегти адресу', a_addr_note='Якщо відправка ще не пішла, оновимо адресу і в поточному замовленні.', ok_addr='Готово: адресу збережено.', del_np='Нова Пошта', del_ukr='Укрпошта',
  a_sort='Змінити сорт', a_sort_save='Зберегти сорт', a_comm_h='Як нам з вами спілкуватися', a_req_h='Особливий ритм, інший формат, окрема пропозиція', a_req_ph='Напишіть, що вам потрібно — відповімо особисто', a_req_btn='Надіслати',
  a_cancel='Скасувати підписку', a_cancel_sure='Точно скасувати? Натисніть ще раз', a_cancel_note='Без пояснень і без утримання.',
  comm={'Звичайна': 'Звичайно', 'Більше близькості': 'Хочу більше близькості', 'Менше повідомлень': 'Хочу менше повідомлень'},
  ok_skip='Готово: наступну відправку пропустимо.', ok_unskip='Готово: відправку повернуто в план.', ok_pause='Готово: підписка на паузі.', ok_resume='Готово: підписку відновлено.',
  ok_sort='Готово: сорт змінено.', ok_comm='Збережено.', ok_req='Дякуємо! Ми відповімо особисто.', ok_cancel='Підписку скасовано.',
  demo='Демо-режим: так клієнт бачить свою сторінку. Нічого не зберігається і нікуди не надсилається.', refresh='Оновити', again='Інша підписка', tg='Написати в Telegram', join='Оформити підписку', pay_h='Оплата',
  pay_t='За 1–2 дні до обсмажки надішлемо суму до сплати. Після підтвердження оплати обсмажуємо й відправляємо.'),
 'ru': dict(
  title='Моя подписка | Клуб ZRN', desc='Управление подпиской Клуба ZRN: пауза, пропуск, смена сорта.',
  h1='Моя подписка', lead='Введите номер подписки и последние 4 цифры телефона, который указывали в заявке.',
  id='Номер подписки', id_ph='SUB-0001', last4='Последние 4 цифры телефона', last4_ph='1234', btn='Открыть', loading='Ищем…',
  forget='Не ваше устройство? Очистить сохранённое',
  err_fmt='Проверьте номер подписки и 4 цифры телефона.', err_nf='Не нашли подписку. Проверьте номер и последние 4 цифры телефона.',
  err_lock='Слишком много неудачных попыток. Попробуйте через 15 минут или напишите нам.', err_net='Не удалось соединиться. Попробуйте ещё раз или напишите нам: ',
  err_locked='Отправка уже в работе — здесь изменить не получится. Напишите нам, и мы что-нибудь придумаем.', err_act='Не удалось выполнить действие. Попробуйте ещё раз или напишите нам.',
  st_new='Заявка получена', st_new_p='Мы свяжемся с вами, подтвердим условия и назначим первую отправку. Пока ничего не оплачивается.',
  st_act='Активна', st_pause='На паузе', st_cancel='Отменена', st_cancel_p='Подписка отменена. Спасибо, что были с нами. Двери всегда открыты — оформить новую можно в любой момент.',
  plan_h='Ваш план', type='Тип', fmt='Формат', level='Уровень', sort='Сорт', freq='Периодичность', grind='Помол', club_h='Статус в клубе', ships='Отправок',
  freq_t={'10': 'Каждые 10 дней', '14': 'Каждые 2 недели', '30': 'Каждый месяц'},
  next_h='Следующая отправка', next_none='Дату назначим после подтверждения.', next_sort='Сорт этой отправки', next_sort_none='роастмастер выберет сам', skipped='Эта отправка пропущена по вашей просьбе.',
  pause_until='Пауза до', locked_note='До обжарки меньше {lead} дней — изменения здесь уже не принимаем. Напишите нам.',
  a_skip='Пропустить следующую отправку', a_unskip='Не пропускать следующую отправку', a_pause='Поставить на паузу', a_pause_date='Пауза до (необязательно)', a_resume='Возобновить подписку',
  a_addr_h='Изменить отделение или адрес', a_addr_now='Сейчас', a_addr_city='Город', a_addr_branch='Отделение / почтомат / адрес', a_addr_save='Сохранить адрес', a_addr_note='Если отправка ещё не ушла, обновим адрес и в текущем заказе.', ok_addr='Готово: адрес сохранён.', del_np='Новая Почта', del_ukr='Укрпочта',
  a_sort='Сменить сорт', a_sort_save='Сохранить сорт', a_comm_h='Как нам с вами общаться', a_req_h='Особый ритм, другой формат, отдельное предложение', a_req_ph='Напишите, что вам нужно — ответим лично', a_req_btn='Отправить',
  a_cancel='Отменить подписку', a_cancel_sure='Точно отменить? Нажмите ещё раз', a_cancel_note='Без объяснений и без удержания.',
  comm={'Звичайна': 'Как обычно', 'Більше близькості': 'Хочу больше близости', 'Менше повідомлень': 'Хочу меньше сообщений'},
  ok_skip='Готово: следующую отправку пропустим.', ok_unskip='Готово: отправка возвращена в план.', ok_pause='Готово: подписка на паузе.', ok_resume='Готово: подписка возобновлена.',
  ok_sort='Готово: сорт изменён.', ok_comm='Сохранено.', ok_req='Спасибо! Мы ответим лично.', ok_cancel='Подписка отменена.',
  demo='Демо-режим: так клиент видит свою страницу. Ничего не сохраняется и никуда не отправляется.', refresh='Обновить', again='Другая подписка', tg='Написать в Telegram', join='Оформить подписку', pay_h='Оплата',
  pay_t='За 1–2 дня до обжарки пришлём сумму к оплате. После подтверждения оплаты обжариваем и отправляем.'),
}

SUB_HTML = """<nav class="crumbs" aria-label="breadcrumb"><a href="@@HOME@@">ZRN Coffee</a> › <span>@@H1@@</span></nav>
<h1>@@H1@@</h1>
<p class="lead" id="sbLead">@@LEAD@@</p>
<form id="sbForm" class="st-form" novalidate>
  <div class="rv-f"><label for="sbId">@@ID@@</label><input type="text" id="sbId" autocapitalize="characters" autocomplete="off" spellcheck="false" maxlength="16" placeholder="@@ID_PH@@"></div>
  <div class="rv-f"><label for="sbLast4">@@LAST4@@</label><input type="text" id="sbLast4" inputmode="numeric" autocomplete="off" maxlength="4" placeholder="@@LAST4_PH@@"></div>
  <p id="sbErr" class="rv-err" role="alert" hidden></p>
  <button type="submit" class="btn" id="sbBtn">@@BTN@@</button>
  <p class="st-forget"><a href="#" id="sbForget" hidden>@@FORGET@@</a></p>
</form>
<section id="sbRes" class="st-res" aria-live="polite" hidden></section>
<noscript><p>Для керування підпискою потрібен JavaScript. Напишіть нам: <a href="@@TG@@">Telegram</a></p></noscript>
<script>
(function(){
  var C = @@CFG@@, T = C.t;
  var $ = function(id){ return document.getElementById(id); };
  var form = $('sbForm'), err = $('sbErr'), btn = $('sbBtn'), res = $('sbRes'), forget = $('sbForget');
  var HINT = 'zrn_sub_hint', cur = null, flash = '', cancelArmed = false, demo = false;
  function el(tag, cls, txt){ var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined && txt !== null) e.textContent = txt; return e; }
  function readHint(){ try { var h = JSON.parse(localStorage.getItem(HINT)); return (h && h.s && h.p) ? h : null; } catch (e) { return null; } }
  function fail(m){ err.textContent = m; err.hidden = false; }
  function dmy(s){ var m = /^(\\d{4})-(\\d{2})-(\\d{2})/.exec(s || ''); return m ? m[3] + '.' + m[2] + '.' + m[1] : (s || ''); }
  function money(v){ return Number(v).toLocaleString(C.lang === 'ru' ? 'ru-RU' : 'uk-UA') + ' ₴'; }
  function row(box, k, v){ if (v === '' || v === null || v === undefined) return; var p = el('p'); p.appendChild(el('span', 'sb-k', k + ': ')); p.appendChild(el('b', '', v)); box.appendChild(p); }
  var DEMO = { id: 'SUB-0000', status: 'Активна', type: 'My Choice', weight: 500, format: 'Home', level: '—', sort: C.products[0] || '', grind: 'Зернова', freq: 14,
               next: '', nextSort: '', skip: '', pauseUntil: '', comm: 'Звичайна', club: 'Новачок клубу', count: 2, locked: false, lead: 3,
               delivery: 'Нова Пошта', city: 'Київ', branch: 'Відділення №15' };
  (function(){ var d = new Date(); d.setDate(d.getDate() + 9); DEMO.next = d.toISOString().slice(0, 10); })();
  function demoCall(p, cb){
    var v = p.value || '';
    if (p.action === 'skip') DEMO.skip = DEMO.skip ? '' : 'Так';
    if (p.action === 'pause') { DEMO.status = 'Пауза'; DEMO.pauseUntil = v; }
    if (p.action === 'resume') { DEMO.status = 'Активна'; DEMO.pauseUntil = ''; }
    if (p.action === 'sort') DEMO.sort = v;
    if (p.action === 'comm') DEMO.comm = v;
    if (p.action === 'cancel') DEMO.status = 'Скасована';
    if (p.action === 'address') { DEMO.delivery = p.delivery || DEMO.delivery; DEMO.city = p.city; DEMO.branch = p.branch; }
    setTimeout(function(){ cb({ ok: true, found: true, sub: JSON.parse(JSON.stringify(DEMO)) }); }, 150);
  }
  function call(payload, cb){
    if (demo) return demoCall(payload, cb);
    var b = { kind: payload.kind, id: cur.id, last4: cur.last4 };
    for (var k in payload) if (k !== 'kind') b[k] = payload[k];
    fetch(C.sheet, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(b) })
      .then(function(r){ return r.json(); }).then(cb).catch(function(){ cb(null); });
  }
  function act(action, value, okMsg, extra){
    flash = '';
    var pl = { kind: 'sub_action', action: action, value: value || '' };
    if (extra) for (var xk in extra) pl[xk] = extra[xk];
    call(pl, function(d){
      if (d && d.ok && d.found && d.sub) { cur.sub = d.sub; flash = okMsg; cancelArmed = false; render(); }
      else { flash = '!' + ((d && d.error === 'locked') ? T.err_locked : T.err_act); render(); }
    });
  }
  function render(){
    var s = cur.sub; res.textContent = '';
    var card = el('div', 'st-card');
    if (demo) card.appendChild(el('div', 'st-banner', T.demo));
    var head = el('div', 'st-head');
    head.appendChild(el('div', 'st-num', s.id));
    var stTxt = { 'Нова заявка': T.st_new, 'Активна': T.st_act, 'Пауза': T.st_pause, 'Скасована': T.st_cancel }[s.status] || s.status;
    head.appendChild(el('div', 'st-date', stTxt));
    card.appendChild(head);
    if (flash) card.appendChild(el('div', flash.charAt(0) === '!' ? 'st-banner st-bad' : 'st-banner', flash.replace(/^!/, '')));
    if (s.status === 'Нова заявка') { card.appendChild(el('div', 'st-banner', T.st_new_p)); }
    if (s.status === 'Скасована') { card.appendChild(el('div', 'st-banner st-bad', T.st_cancel_p)); }
    var g = el('div', 'st-grid');
    var plan = el('div', 'st-box'); plan.appendChild(el('h3', '', T.plan_h));
    row(plan, T.type, s.type === "Roaster's Choice" ? 'Roaster’s Choice' : 'My Choice');
    row(plan, T.fmt, s.format + ' · ' + s.weight + ' г');
    if (s.type === 'My Choice') row(plan, T.sort, s.sort); else row(plan, T.level, s.level);
    row(plan, T.freq, T.freq_t[String(s.freq)] || s.freq);
    row(plan, T.grind, s.grind);
    g.appendChild(plan);
    var nx = el('div', 'st-box'); nx.appendChild(el('h3', '', T.next_h));
    if (s.status === 'Пауза') { nx.appendChild(el('p', '', T.st_pause + (s.pauseUntil ? ' · ' + T.pause_until + ' ' + dmy(s.pauseUntil) : ''))); }
    else if (s.status === 'Скасована') { nx.appendChild(el('p', '', '—')); }
    else if (s.next) {
      nx.appendChild(el('p', '', dmy(s.next)));
      if (s.skip) nx.appendChild(el('p', 'sb-sub', T.skipped));
      else row(nx, T.next_sort, s.type === 'My Choice' ? s.sort : (s.nextSort || T.next_sort_none));
    } else nx.appendChild(el('p', '', T.next_none));
    if (s.club) row(nx, T.club_h, s.club);
    if (s.count) row(nx, T.ships, String(s.count));
    g.appendChild(nx);
    card.appendChild(g);
    var pb = el('div', 'st-box'); pb.appendChild(el('h3', '', T.pay_h)); pb.appendChild(el('p', '', T.pay_t)); card.appendChild(pb);

    var live = s.status === 'Активна' || s.status === 'Пауза';
    if (live) {
      var acts = el('div', 'st-act sb-act');
      if (s.locked && s.status === 'Активна') card.appendChild(el('p', 'st-auto', T.locked_note.replace('{lead}', s.lead)));
      if (s.status === 'Активна') {
        var sk = el('button', 'btn ghost', s.skip ? T.a_unskip : T.a_skip); sk.type = 'button'; sk.disabled = !!(s.locked && !s.skip);
        sk.onclick = function(){ act('skip', '', s.skip ? T.ok_unskip : T.ok_skip); }; acts.appendChild(sk);
        var pw = el('div', 'sb-pause');
        var di = el('input'); di.type = 'date'; di.id = 'sbPauseDate'; di.setAttribute('aria-label', T.a_pause_date);
        var pl = el('label', '', T.a_pause_date); pl.setAttribute('for', 'sbPauseDate');
        var pb2 = el('button', 'btn ghost', T.a_pause); pb2.type = 'button';
        pb2.onclick = function(){ act('pause', di.value, T.ok_pause); };
        pw.appendChild(pl); pw.appendChild(di); pw.appendChild(pb2); card.appendChild(acts); card.appendChild(pw);
      } else {
        var rs = el('button', 'btn', T.a_resume); rs.type = 'button'; rs.onclick = function(){ act('resume', '', T.ok_resume); }; acts.appendChild(rs); card.appendChild(acts);
      }
      if (s.type === 'My Choice' && s.status === 'Активна' && C.products.length) {
        var sb = el('div', 'st-box sb-blk'); sb.appendChild(el('h3', '', T.a_sort));
        var sel = el('select', 'sb-sel'); C.products.forEach(function(n){ var o = el('option', '', n); o.value = n; if (n === s.sort) o.selected = true; sel.appendChild(o); });
        var sv = el('button', 'btn ghost', T.a_sort_save); sv.type = 'button'; sv.disabled = !!s.locked;
        sv.onclick = function(){ act('sort', sel.value, T.ok_sort); };
        sb.appendChild(sel); sb.appendChild(sv); card.appendChild(sb);
      }
      var ab = el('div', 'st-box sb-blk'); ab.appendChild(el('h3', '', T.a_addr_h));
      ab.appendChild(el('p', 'sb-sub', T.a_addr_now + ': ' + [s.delivery, s.city, s.branch].filter(Boolean).join(', ')));
      var dsel = el('select', 'sb-sel');
      [['Нова Пошта', T.del_np], ['Укрпошта', T.del_ukr]].forEach(function(x){ var o = el('option', '', x[1]); o.value = x[0]; if (x[0] === s.delivery) o.selected = true; dsel.appendChild(o); });
      var ci = el('input', 'sb-in'); ci.type = 'text'; ci.placeholder = T.a_addr_city; ci.value = s.city || ''; ci.maxLength = 120; ci.setAttribute('aria-label', T.a_addr_city);
      var bi = el('input', 'sb-in'); bi.type = 'text'; bi.placeholder = T.a_addr_branch; bi.value = s.branch || ''; bi.maxLength = 200; bi.setAttribute('aria-label', T.a_addr_branch);
      var asv = el('button', 'btn ghost', T.a_addr_save); asv.type = 'button';
      asv.onclick = function(){ if (ci.value.trim().length < 2 || !bi.value.trim()) return; act('address', '', T.ok_addr, { delivery: dsel.value, city: ci.value.trim(), branch: bi.value.trim() }); };
      ab.appendChild(dsel); ab.appendChild(ci); ab.appendChild(bi); ab.appendChild(asv); ab.appendChild(el('p', 'sb-sub', T.a_addr_note)); card.appendChild(ab);
      var cb = el('div', 'st-box sb-blk'); cb.appendChild(el('h3', '', T.a_comm_h));
      Object.keys(T.comm).forEach(function(k){
        var lb = el('label', 'sb-radio'); var r = el('input'); r.type = 'radio'; r.name = 'sbComm'; r.value = k; r.checked = (s.comm || 'Звичайна') === k;
        r.onchange = function(){ act('comm', k, T.ok_comm); };
        lb.appendChild(r); lb.appendChild(el('span', '', ' ' + T.comm[k])); cb.appendChild(lb);
      });
      card.appendChild(cb);
      var rb = el('div', 'st-box sb-blk'); rb.appendChild(el('h3', '', T.a_req_h));
      var ta = el('textarea'); ta.rows = 3; ta.maxLength = 280; ta.placeholder = T.a_req_ph; ta.className = 'sb-ta';
      var rq = el('button', 'btn ghost', T.a_req_btn); rq.type = 'button';
      rq.onclick = function(){ if (ta.value.trim().length >= 3) act('request', ta.value.trim(), T.ok_req); };
      rb.appendChild(ta); rb.appendChild(rq); card.appendChild(rb);
      var cc = el('div', 'sb-cancel');
      var cn = el('button', 'sb-cancel-btn', cancelArmed ? T.a_cancel_sure : T.a_cancel); cn.type = 'button';
      cn.onclick = function(){ if (!cancelArmed) { cancelArmed = true; render(); } else act('cancel', '', T.ok_cancel); };
      cc.appendChild(cn); cc.appendChild(el('span', 'sb-sub', ' ' + T.a_cancel_note)); card.appendChild(cc);
    }
    var bot = el('div', 'st-act');
    var rf = el('button', 'btn ghost', T.refresh); rf.type = 'button'; rf.onclick = function(){ lookup(cur.id, cur.last4); };
    var ag = el('button', 'btn ghost', T.again); ag.type = 'button';
    ag.onclick = function(){ res.hidden = true; form.hidden = false; $('sbLead').hidden = false; $('sbId').value = ''; $('sbLast4').value = ''; $('sbId').focus(); };
    var tg = el('a', 'btn ghost', T.tg); tg.href = C.tg; tg.rel = 'noopener';
    bot.appendChild(rf); bot.appendChild(ag); bot.appendChild(tg); card.appendChild(bot);
    res.appendChild(card); res.hidden = false; form.hidden = true; $('sbLead').hidden = true;
    window.scrollTo(0, 0);
  }
  function lookup(id, last4){
    err.hidden = true; btn.disabled = true; btn.textContent = T.loading;
    cur = { id: id, last4: last4 };
    call({ kind: 'sub_status' }, function(d){
      btn.disabled = false; btn.textContent = T.btn;
      if (d && d.ok && d.found) {
        cur.sub = d.sub; cur.id = d.sub.id;
        try { localStorage.setItem(HINT, JSON.stringify({ s: d.sub.id, p: last4 })); } catch (e) {}
        flash = ''; render();
      } else if (d && d.ok) { form.hidden = false; res.hidden = true; $('sbLead').hidden = false; fail(d.locked ? T.err_lock : T.err_nf); }
      else { form.hidden = false; res.hidden = true; $('sbLead').hidden = false; fail(T.err_net + C.tgText); }
    });
  }
  form.addEventListener('submit', function(e){
    e.preventDefault();
    var i = $('sbId').value.trim().toUpperCase(), p = $('sbLast4').value.replace(/\\D/g, '');
    if (i.length < 4 || p.length !== 4) return fail(T.err_fmt);
    lookup(i, p);
  });
  $('sbLast4').addEventListener('input', function(){ this.value = this.value.replace(/\\D/g, '').slice(0, 4); });
  forget.addEventListener('click', function(e){ e.preventDefault(); try { localStorage.removeItem(HINT); } catch (x) {} forget.hidden = true; $('sbId').value = ''; $('sbLast4').value = ''; });
  var lg = document.querySelector('.lang'); if (lg && location.search) lg.href += location.search;
  if (new URLSearchParams(location.search).has('demo')) { demo = true; cur = { id: DEMO.id, last4: '0000', sub: JSON.parse(JSON.stringify(DEMO)) }; form.hidden = true; render(); return; }
  var q = new URLSearchParams(location.search).get('s'); q = q ? q.replace(/[^A-Za-z0-9\\-]/g, '').slice(0, 16).toUpperCase() : '';
  var h = readHint(); if (h) forget.hidden = false;
  if (q) $('sbId').value = q;
  if (h && (!q || q === String(h.s).toUpperCase())) { $('sbId').value = h.s; $('sbLast4').value = h.p; lookup(h.s, h.p); }
  else if (q) $('sbLast4').focus();
})();
</script>
"""

SB_CSS = """
.sb-k{color:var(--sub)}
.sb-sub{color:var(--sub);font-size:.84rem}
.sb-act{margin-top:16px}
.sb-pause{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:12px 0}
.sb-pause label{font-size:.84rem;color:var(--sub);width:100%}
.sb-pause input[type=date],.sb-sel,.sb-ta{padding:10px;border:1px solid var(--line);border-radius:8px;font:inherit;background:#fff;color:var(--ink)}
.sb-blk{margin-top:14px}
.sb-blk .btn{margin-top:8px}
.sb-sel{width:100%}
.sb-in{width:100%;margin-top:8px;padding:10px;border:1px solid var(--line);border-radius:8px;font:inherit;background:#fff;color:var(--ink)}
.sb-ta{width:100%;resize:vertical}
.sb-radio{display:block;padding:6px 0;cursor:pointer}
.sb-cancel{margin:22px 0 4px}
.sb-cancel-btn{background:none;border:0;color:var(--sub);text-decoration:underline;cursor:pointer;font:inherit;padding:0}
.sb-act .btn:disabled,.sb-blk .btn:disabled{opacity:.5;cursor:not-allowed}
.sb-act .btn,.sb-blk .btn,.sb-pause .btn{border:1px solid var(--line);cursor:pointer;font:inherit}
"""

STATUS_HTML = """<nav class="crumbs" aria-label="breadcrumb"><a href="@@HOME@@">ZRN Coffee</a> › <span>@@H1@@</span></nav>
<h1>@@H1@@</h1>
<p class="lead" id="stLead">@@LEAD@@</p>
<form id="stForm" class="st-form" novalidate>
  <div class="rv-f"><label for="stOrder">@@ORDER@@</label><input type="text" id="stOrder" inputmode="text" autocapitalize="characters" autocomplete="off" spellcheck="false" maxlength="24" placeholder="@@ORDER_PH@@"></div>
  <div class="rv-f"><label for="stLast4">@@LAST4@@</label><input type="text" id="stLast4" inputmode="numeric" autocomplete="off" maxlength="4" pattern="[0-9]{4}" placeholder="@@LAST4_PH@@"></div>
  <p id="stErr" class="rv-err" role="alert" hidden></p>
  <button type="submit" class="btn" id="stBtn">@@BTN@@</button>
  <p class="st-forget"><a href="#" id="stForget" hidden>@@FORGET@@</a></p>
</form>
<section id="stRes" class="st-res" aria-live="polite" hidden></section>
<noscript><p>Для перегляду статусу потрібен JavaScript. Напишіть нам: <a href="@@TG@@">Telegram</a></p></noscript>
<script>
(function(){
  var C = @@CFG@@, T = C.t;
  var $ = function(id){ return document.getElementById(id); };
  var form = $('stForm'), err = $('stErr'), btn = $('stBtn'), res = $('stRes'), forget = $('stForget');
  var HINT = 'zrn_status_hint';
  function el(tag, cls, txt){ var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined && txt !== null) e.textContent = txt; return e; }
  function readHint(){ try { var h = JSON.parse(localStorage.getItem(HINT)); return (h && h.o && h.p) ? h : null; } catch (e) { return null; } }
  function fail(m){ err.textContent = m; err.hidden = false; }
  function money(v){ return (isNaN(Number(v)) ? v : Number(v).toLocaleString(C.lang === 'ru' ? 'ru-RU' : 'uk-UA')) + ' ₴'; }
  function dateOnly(s){ return String(s || '').split(' ')[0]; }
  function etaFmt(s){ var m = /^(\\d{2})-(\\d{2})-(\\d{4})/.exec(s || ''); return m ? m[1] + '.' + m[2] + '.' + m[3] : (s || ''); }

  function render(d, order, last4){
    res.textContent = '';
    var tr = d.tracking, stage = d.status.stage;
    if (tr) {
      if (tr.stage === 'received') stage = 4;
      else if (tr.stage === 'returning') stage = -2;
      else if ((tr.stage === 'transit' || tr.stage === 'arrived' || tr.stage === 'created') && (stage === null || stage < 3)) stage = 3;
    }
    var card = el('div', 'st-card');
    var head = el('div', 'st-head');
    head.appendChild(el('div', 'st-num', d.number));
    head.appendChild(el('div', 'st-date', T.ordered + ' ' + dateOnly(d.date)));
    card.appendChild(head);

    if (stage === -1 || stage === -2) {
      card.appendChild(el('div', 'st-banner st-bad', stage === -1 ? T.cancelled : T.returned));
    } else if (stage === null) {
      card.appendChild(el('div', 'st-banner', d.status.raw));
    } else {
      var ol = el('ol', 'st-tl');
      T.steps.forEach(function(label, i){
        var li = el('li', i < stage ? 'done' : (i === stage ? 'cur' : ''));
        li.appendChild(el('span', 'st-dot', i < stage ? '✓' : String(i + 1)));
        li.appendChild(el('span', 'st-lb', label));
        ol.appendChild(li);
      });
      card.appendChild(ol);
    }
    if (tr && tr.stage !== 'notfound') {
      var tm = { created: T.track_created, transit: T.track_transit, arrived: T.track_arrived, received: T.track_received, returning: T.track_returning }[tr.stage];
      if (tm) {
        var b = el('div', 'st-track'); b.appendChild(el('b', '', tm));
        var sub = [];
        if (tr.stage === 'arrived' && tr.where) sub.push(tr.where);
        if ((tr.stage === 'transit' || tr.stage === 'created') && tr.eta) sub.push(T.eta + ': ' + etaFmt(tr.eta));
        if (sub.length) b.appendChild(el('div', 'st-sub', sub.join(' · ')));
        card.appendChild(b);
      }
    }
    if (d.note) { var n = el('div', 'st-note'); n.appendChild(el('b', '', T.note_h)); n.appendChild(el('div', '', d.note)); card.appendChild(n); }

    var g = el('div', 'st-grid');
    var pay = el('div', 'st-box'); pay.appendChild(el('h3', '', T.pay_h)); pay.appendChild(el('p', '', T.pay[d.pay] || '')); g.appendChild(pay);
    var dl = el('div', 'st-box'); dl.appendChild(el('h3', '', T.del_h));
    dl.appendChild(el('p', '', [d.delivery.label, d.delivery.city, d.delivery.branch].filter(Boolean).join(', ')));
    if (d.ttn) {
      var row = el('p', 'st-ttn'); row.appendChild(el('span', '', (d.delivery.carrier === 'ukr' ? T.ttn_ukr : T.ttn_np) + ': '));
      var code = el('b', '', d.ttn); row.appendChild(code);
      var cp = el('button', 'st-copy', T.copy); cp.type = 'button';
      cp.onclick = function(){ try { navigator.clipboard.writeText(d.ttn); cp.textContent = T.copied; setTimeout(function(){ cp.textContent = T.copy; }, 1500); } catch (e) {} };
      row.appendChild(cp); dl.appendChild(row);
      var url = d.delivery.carrier === 'ukr' ? 'https://track.ukrposhta.ua/tracking_UA.html?barcode=' + encodeURIComponent(d.ttn)
              : (d.delivery.carrier === 'np' ? 'https://novaposhta.ua/tracking/?cargo_number=' + encodeURIComponent(d.ttn) : '');
      if (url) { var a = el('a', 'st-link', T.track_link + ' →'); a.href = url; a.target = '_blank'; a.rel = 'noopener'; dl.appendChild(a); }
    }
    g.appendChild(dl);
    card.appendChild(g);

    var it = el('div', 'st-box st-items'); it.appendChild(el('h3', '', T.items_h));
    var ul = el('ul'); d.items.forEach(function(x){ ul.appendChild(el('li', '', x)); }); it.appendChild(ul);
    it.appendChild(el('p', 'st-total', T.total + ': ' + money(d.total)));
    card.appendChild(it);
    if (d.ttn && d.delivery.carrier === 'np') card.appendChild(el('p', 'st-auto', T.auto));

    var act = el('div', 'st-act');
    var rf = el('button', 'btn', T.refresh); rf.type = 'button'; rf.onclick = function(){ lookup(order, last4, true); };
    var ag = el('button', 'btn ghost', T.again); ag.type = 'button';
    ag.onclick = function(){ res.hidden = true; form.hidden = false; $('stLead').hidden = false; $('stOrder').value = ''; $('stLast4').value = ''; $('stOrder').focus(); };
    var tg = el('a', 'btn ghost', T.tg); tg.href = C.tg; tg.rel = 'noopener';
    act.appendChild(rf); act.appendChild(ag); act.appendChild(tg);
    card.appendChild(act);
    res.appendChild(card);
    res.hidden = false; form.hidden = true; $('stLead').hidden = true;
    window.scrollTo(0, 0);
  }

  function lookup(order, last4, keep){
    err.hidden = true;
    btn.disabled = true; btn.textContent = T.loading;
    fetch(C.sheet, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify({ kind: 'status', order: order, last4: last4 }) })
      .then(function(r){ return r.json(); })
      .then(function(d){
        btn.disabled = false; btn.textContent = T.btn;
        if (d && d.ok && d.found) {
          try { localStorage.setItem(HINT, JSON.stringify({ o: d.number, p: last4 })); } catch (e) {}
          render(d, order, last4);
        } else if (d && d.ok) { form.hidden = false; res.hidden = true; $('stLead').hidden = false; fail(d.locked ? T.err_lock : T.err_nf); }
        else throw new Error('bad');
      })
      .catch(function(){ btn.disabled = false; btn.textContent = T.btn; form.hidden = false; res.hidden = true; fail(T.err_net + C.tgText); });
  }

  form.addEventListener('submit', function(e){
    e.preventDefault();
    var o = $('stOrder').value.trim(), p = $('stLast4').value.replace(/\\D/g, '');
    if (o.length < 8 || p.length !== 4) return fail(T.err_fmt);
    lookup(o, p);
  });
  $('stLast4').addEventListener('input', function(){ this.value = this.value.replace(/\\D/g, '').slice(0, 4); });
  forget.addEventListener('click', function(e){ e.preventDefault(); try { localStorage.removeItem(HINT); } catch (x) {} forget.hidden = true; $('stOrder').value = ''; $('stLast4').value = ''; });

  var lg = document.querySelector('.lang'); if (lg && location.search) lg.href += location.search;
  var q = new URLSearchParams(location.search).get('o');
  q = q ? q.replace(/[^A-Za-z0-9\\-]/g, '').slice(0, 24) : '';
  var h = readHint();
  if (h) forget.hidden = false;
  if (q) $('stOrder').value = q;
  if (h && (!q || q.toUpperCase().replace(/[^A-Z0-9]/g, '').replace(/^ZRN/, '') === String(h.o).toUpperCase().replace(/[^A-Z0-9]/g, '').replace(/^ZRN/, ''))) {
    $('stOrder').value = h.o; $('stLast4').value = h.p; lookup(h.o, h.p);   // той самий пристрій, що й замовлення — одразу показуємо статус
  } else if (q) { $('stLast4').focus(); }
})();
</script>
"""


class Site:
    def __init__(self, cat, index_src):
        self.cat = cat
        self.url = cat['site']['url'].rstrip('/')
        self.tg = cat['site']['telegram']
        self.email = cat['site']['email']
        self.phones = cat['site'].get('phones', [])
        self.insta = cat['site'].get('instagram', '')
        self.city = cat['site'].get('city', {})
        self.prods = cat['products']
        self.posts = cat['posts']
        self.ui_txt = ui_texts(index_src)
        self.index_src = index_src
        m = re.search(r"WEB3FORMS_KEY = '([^']*)'", index_src)
        self.w3key = m.group(1) if m else ''
        m = re.search(r"ORDER_SHEET_URL = '([^']*)'", index_src)
        self.sheet_url = m.group(1) if m else ''
        self.out = {}

    # --- адреси
    def p_url(self, lang, pid): return f"{self.url}{UI[lang]['pre']}/coffee/{pid}/"
    def b_url(self, lang, bid): return f"{self.url}{UI[lang]['pre']}/blog/{bid}/"
    def blog_idx(self, lang): return f"{self.url}{UI[lang]['pre']}/blog/"
    def main(self, lang): return self.url + '/' if lang == 'uk' else self.url + '/ru/'

    @staticmethod
    def short(s, n):
        s = ' '.join(s.split())
        if len(s) <= n:
            return s
        return s[:n].rsplit(' ', 1)[0].rstrip(',;:—-') + '…'

    def similar(self, p):
        a = p['taste']

        def dist(q):
            b = q['taste']
            return sum((a[k] - b[k]) ** 2 for k in ('acid', 'sweet', 'bitter', 'body'))
        return sorted([q for q in self.prods if q['id'] != p['id']], key=dist)[:3]

    def process_text(self, p, lang):
        w = bool(re.search('washed', p['processing'], re.I))
        n = bool(re.search('natural', p['processing'], re.I))
        key = 'both' if (w and n) else 'natural' if n else 'washed' if w else None
        return self.cat['processInfo'][key][lang] if key else ''

    # --- каркас
    def head(self, lang, title, desc, canonical, alts, og_type, image, ld, robots='index, follow, max-image-preview:large'):
        u = UI[lang]
        alt_tags = ''.join(f'<link rel="alternate" hreflang="{k}" href="{v}">\n' for k, v in alts.items())
        ld_tags = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False).replace("</", "<\\/")}</script>\n' for x in ld)
        other = 'ru_RU' if lang == 'uk' else 'uk_UA'
        return f'''<!DOCTYPE html>
<html lang="{u['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#f3ead9">
<link rel="canonical" href="{canonical}">
{alt_tags}<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{u['loc']}">
<meta property="og:locale:alternate" content="{other}">
<meta property="og:site_name" content="ZRN Coffee">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{image}">
{ICONS}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pages.css">
{ld_tags}</head>
<body>
'''

    def header(self, lang, alt_href):
        u = UI[lang]
        home = '/' if lang == 'uk' else '/ru/'
        club_link = f'\n      <a href="{home}#club">Клуб</a>' if SETTINGS['sub']['on'] else ''
        return f'''<header class="site-head">
  <div class="wrap hd-in">
    <a class="hd-logo" href="{home}" aria-label="ZRN Craft Micro Roastery"><b>ZRN</b><span>{u['craft']}</span></a>
    <nav aria-label="{u['home']}">
      <a href="{home}#catalog">{u['catalog']}</a>
      <a href="{home}#blends">{u['blends']}</a>{club_link}
      <a href="{u['pre']}/blog/">{u['blog']}</a>
    </nav>
    <a class="lang" href="{alt_href}" hreflang="{'ru' if lang == 'uk' else 'uk'}">{u['altcode']}</a>
  </div>
</header>
<main class="wrap">
'''

    def footer(self, lang):
        u = UI[lang]
        home = '/' if lang == 'uk' else '/ru/'
        def fmt(ph):
            d = re.sub(r'\D', '', ph)
            return f'+{d[:2]} {d[2:5]} {d[5:8]} {d[8:10]} {d[10:12]}' if len(d) == 12 else ph
        phones_html = ' '.join(f'<a href="tel:{ph}">{fmt(ph)}</a>' for ph in self.phones)
        city_html = f'<div class="foot-city">{"м." if lang == "uk" else "г."} {self.city.get(lang, "")}{" · відправляємо по всій Україні" if lang == "uk" else " · отправляем по всей Украине"}</div>' if self.city.get(lang) else ''
        sub_foot = (f'<a href="{u["pre"]}/subscription/">{"Моя підписка" if lang == "uk" else "Моя подписка"}</a>') if SETTINGS['sub']['on'] else ''
        return f'''</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-brand"><b>ZRN</b> {u['foot']}</div>
    {city_html}
    <div class="foot-links">
      <a href="{home}">ZRN Coffee</a>
      <a href="{u['pre']}/blog/">{u['blog']}</a>
      <a href="{self.tg}" rel="noopener">Telegram</a>
      {f'<a href="{self.insta}" rel="noopener me">Instagram</a>' if self.insta else ''}
      <a href="mailto:{self.email}">{u['mail']}</a>
      {phones_html}
      <a href="/oferta/">{u['offer']}</a>
      <a href="/privacy/">{u['privacy']}</a>
      <a href="{u['pre']}/status/">{'Статус замовлення' if lang == 'uk' else 'Статус заказа'}</a>
      {sub_foot}
      <a href="#" data-cookie-settings>{'Налаштування cookie' if lang == 'uk' else 'Настройки cookie'}</a>
    </div>
  </div>
</footer>
</body>
</html>
'''

    @staticmethod
    def crumbs(items):
        return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': url} for i, (n, url) in enumerate(items)]}

    def write(self, path, content):
        self.out[path] = content

    # --- сорти
    def product_pages(self):
        for lang in LANGS:
            u = UI[lang]
            other = 'ru' if lang == 'uk' else 'uk'
            ut = self.ui_txt[lang]
            for p in self.prods:
                name = p['name']
                notes = p['notes'][lang]
                title = f"{u['h1']}{name}{u['tTitle']}"
                desc = self.short(f"{u['h1']}{name}: {notes}. {p['region'][lang]}. {u['fresh']}. {p['w1']} {u['g']} — {p['price1']} ₴.", 158)
                img = f"{self.url}/{p['img']}"
                canonical = self.p_url(lang, p['id'])
                alts = {'uk': self.p_url('uk', p['id']), 'ru': self.p_url('ru', p['id']), 'x-default': self.p_url('uk', p['id'])}
                shop = '/' if lang == 'uk' else '/ru/'
                buy_href = ('/?buy=' if lang == 'uk' else '/ru/?buy=') + p['id']
                sect = 'blends' if p['type'] == 'blend' else 'catalog'
                offers = [{'@type': 'Offer', 'name': f"{w} {u['g']}", 'priceCurrency': 'UAH', 'price': str(pr),
                           'availability': 'https://schema.org/InStock', 'itemCondition': 'https://schema.org/NewCondition', 'url': canonical,
                           'shippingDetails': {'@type': 'OfferShippingDetails',
                                               'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'UA'},
                                               'deliveryTime': {'@type': 'ShippingDeliveryTime',
                                                                'handlingTime': {'@type': 'QuantitativeValue', 'minValue': 0, 'maxValue': 1, 'unitCode': 'DAY'},
                                                                'transitTime': {'@type': 'QuantitativeValue', 'minValue': 1, 'maxValue': 3, 'unitCode': 'DAY'}}},
                           'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'UA',
                                                       'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow',
                                                       'merchantReturnDays': 14,
                                                       'returnMethod': 'https://schema.org/ReturnByMail',
                                                       'returnFees': 'https://schema.org/ReturnShippingFees'}}
                          for w, pr in ((p['w1'], p['price1']), (p['w2'], p['price2']))]
                ld_prod = {'@context': 'https://schema.org', '@type': 'Product', 'name': name, 'sku': p['id'], 'image': img,
                           'description': self.short(f"{notes}. {p['info'][lang]}", 300), 'category': 'Coffee', 'url': canonical,
                           'brand': {'@type': 'Brand', 'name': 'ZRN Coffee'}, 'offers': offers}
                ld_bc = self.crumbs([('ZRN Coffee', self.main(lang)),
                                     (u['blends'] if p['type'] == 'blend' else u['catalog'], self.main(lang) + '#' + sect), (name, canonical)])
                h = self.head(lang, title, desc, canonical, alts, 'product', img, [ld_prod, ld_bc])
                h += self.header(lang, self.p_url(other, p['id']).replace(self.url, ''))
                chips = ''.join(f'<span class="chip">{E(x.strip())}</span>' for x in notes.replace('，', ',').split(',') if x.strip())
                altm = re.search(r'(\d{3,4})\s*[–-]\s*(\d{3,4})\s*м', p['region']['uk'])
                specs = ''
                if 'ratio' in p:
                    specs += f"<div><dt>{u['comp']}</dt><dd>{E(p['ratio'][lang])}</dd></div>"
                specs += f"<div><dt>{u['region']}</dt><dd>{E(p['region'][lang])}</dd></div>"
                if altm:
                    specs += f"<div><dt>{u['alt_h']}</dt><dd>{altm.group(1)}–{altm.group(2)} {u['alt_u']}</dd></div>"
                specs += f"<div><dt>{u['variety']}</dt><dd>{E(p['variety'][lang])}</dd></div>"
                specs += f"<div><dt>{u['process']}</dt><dd>{E(p['processing'])}</dd></div>"
                dots = ''.join(f'<span class="{"on" if i <= p["roastLevel"] else ""}"></span>' for i in range(1, 6))
                specs += (f"<div><dt>{u['roast']}</dt><dd>{E(p['roastLabel'][lang])} <span class=\"dots\" aria-hidden=\"true\">{dots}</span>"
                          f"<small class=\"ends\"><i>{u['light']}</i><i>{u['dark']}</i></small></dd></div>")
                bars = ''.join(f'<div class="bar"><span>{u[k]}</span><div class="track"><div class="fill" style="width:{p["taste"][k] * 20}%"></div></div>'
                               f'<b class="sr">{p["taste"][k]}/5</b></div>' for k in ('acid', 'sweet', 'bitter', 'body'))
                brew = ''
                for b in p['brew']:
                    g = self.cat['brewGuide'][b]
                    bn = BREW_RU.get(b, b) if lang == 'ru' else b
                    brew += f'<div class="brewc"><b>{E(bn)}</b><p>{E(g[lang])}</p></div>'
                story = ''.join(f'<p>{E(s)}</p>' for s in p['story'][lang])
                proc = self.process_text(p, lang)
                ship = ''.join(f'<li>{E(x)}</li>' for x in (ut['trust.fact'], ut['ship.del2'] + ' ' + ut['ship.del3'], ut['ship.del4'],
                                                            ut['ship.pay1'], ut['ck.guarantee']))

                def mini(q):
                    return (f'<a class="mini" href="{u["pre"]}/coffee/{q["id"]}/"><img src="/{q["img"]}" alt="{E(q["alt"])}" width="120" height="120" loading="lazy">'
                            f'<span>{E(q["name"])}</span><small>{E(q["notes"][lang])}</small><em>{u["from_"]}{q["price1"]} ₴</em></a>')
                allc = ' · '.join(f'<a href="{u["pre"]}/coffee/{q["id"]}/">{E(q["name"])}</a>' for q in self.prods if q['id'] != p['id'])
                h += f'''<nav class="crumbs" aria-label="breadcrumb"><a href="{shop}">ZRN Coffee</a> › <a href="{shop}#{sect}">{u['blends'] if p['type'] == 'blend' else u['catalog']}</a> › <span>{E(name)}</span></nav>
<article class="product">
  <div class="p-grid">
    <img class="p-img" src="/{p['img']}" alt="{E(p['alt'])}" width="600" height="600" fetchpriority="high">
    <div class="p-main">
      {f'<div class="kicker">{E(p["kicker"])}</div>' if p.get('kicker') else ''}
      <h1>{u['h1']}{E(name)}</h1>
      <p class="origin">{E(p['region'][lang])}</p>
      <div class="chips" aria-label="{u['notes']}">{chips}</div>
      <div class="prices">
        <div><b>{p['w1']} {u['g']}</b><span>{p['price1']} ₴</span><small>{round(p['price1'] * 100 / p['w1'])} ₴ {u['per100']}</small></div>
        <div><b>{p['w2']} {u['g']}</b><span>{p['price2']} ₴</span><small>{round(p['price2'] * 100 / p['w2'])} ₴ {u['per100']}</small></div>
      </div>
      <a class="btn" href="{buy_href}" rel="nofollow">{u['buy']}</a>
      <p class="fresh">{u['fresh']}</p>
    </div>
  </div>
  <section>
    <h2>{u['about']}</h2>
    <p>{E(p['info'][lang])}</p>
  </section>
  <section>
    <h2>{u['taste_h']}</h2>
    <div class="bars">{bars}</div>
    <p class="note">{u['taste_note']}</p>
  </section>
  <section>
    <h2>{u['origin_h']}</h2>
    <dl class="specs">{specs}</dl>
    {f'<p class="note strong">{E(proc)}</p>' if proc else ''}
    {story}
  </section>
  <section>
    <h2>{u['brew']}</h2>
    {brew}
    <p class="note">{u['brewNote']}</p>
  </section>
  <section>
    <h2>{u['ship_h']}</h2>
    <ul class="ticks">{ship}</ul>
  </section>
  <section class="wide">
    <h2>{u['similar']}</h2>
    <div class="minis">{''.join(mini(q) for q in self.similar(p))}</div>
    <p class="allc">{u['allc']}: {allc}</p>
  </section>
</article>
'''
                h += self.footer(lang)
                self.write(f"{u['pre'].strip('/')}/coffee/{p['id']}/index.html".lstrip('/'), h)

    # --- блог
    def blog_pages(self):
        for lang in LANGS:
            u = UI[lang]
            other = 'ru' if lang == 'uk' else 'uk'
            home = '/' if lang == 'uk' else '/ru/'
            canonical = self.blog_idx(lang)
            alts = {'uk': self.blog_idx('uk'), 'ru': self.blog_idx('ru'), 'x-default': self.blog_idx('uk')}
            ld = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': u['blogTitle'], 'url': canonical,
                   'hasPart': [{'@type': 'Article', 'headline': a['title'][lang], 'url': self.b_url(lang, a['id'])} for a in self.posts]},
                  self.crumbs([('ZRN Coffee', self.main(lang)), (u['blogTitle'], canonical)])]
            h = self.head(lang, u['blogIdx'], u['blogDesc'], canonical, alts, 'website', f"{self.url}/img/og.jpg", ld)
            h += self.header(lang, f"{UI[other]['pre']}/blog/")
            h += (f'<nav class="crumbs" aria-label="breadcrumb"><a href="{home}">ZRN Coffee</a> › <span>{u["blogTitle"]}</span></nav>\n'
                  f'<h1>{u["blogTitle"]}</h1>\n<div class="posts">\n')
            h += ''.join(f'  <a class="post" href="{u["pre"]}/blog/{a["id"]}/"><small>{E(a["k"][lang])}</small><h2>{E(a["title"][lang])}</h2>'
                         f'<p>{E(a["excerpt"][lang])}</p><span>{u["read"]} →</span></a>\n' for a in self.posts) + '</div>\n'
            h += self.footer(lang)
            self.write(f"{u['pre'].strip('/')}/blog/index.html".lstrip('/'), h)
            for a in self.posts:
                title = a['title'][lang] + u['postSuf']
                desc = self.short(a['excerpt'][lang] + ' ' + a['body'][lang].replace('\n', ' '), 158)
                canonical = self.b_url(lang, a['id'])
                alts = {'uk': self.b_url('uk', a['id']), 'ru': self.b_url('ru', a['id']), 'x-default': self.b_url('uk', a['id'])}
                ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'][lang], 'description': a['excerpt'][lang],
                       'inLanguage': lang, 'mainEntityOfPage': canonical, 'image': f"{self.url}/img/og.jpg",
                       'author': {'@type': 'Person', 'name': u['author']},
                       'publisher': {'@type': 'Organization', 'name': 'ZRN Coffee', 'url': self.url + '/'}},
                      self.crumbs([('ZRN Coffee', self.main(lang)), (u['blogTitle'], self.blog_idx(lang)), (a['title'][lang], canonical)])]
                h = self.head(lang, title, desc, canonical, alts, 'article', f"{self.url}/img/og.jpg", ld)
                h += self.header(lang, self.b_url(other, a['id']).replace(self.url, ''))
                body = ''.join(f'<p>{E(par.strip())}</p>' for par in a['body'][lang].split('\n\n') if par.strip())
                rel = [y for y in self.posts if y['id'] != a['id']]
                h += (f'<nav class="crumbs" aria-label="breadcrumb"><a href="{home}">ZRN Coffee</a> › <a href="{u["pre"]}/blog/">{u["blogTitle"]}</a> › <span>{E(a["title"][lang])}</span></nav>\n'
                      f'<article class="article">\n  <small class="kicker">{E(a["k"][lang])}</small>\n  <h1>{E(a["title"][lang])}</h1>\n  {body}\n'
                      f'  <p><a class="btn" href="{home}#catalog">{u["toShop"]}</a></p>\n</article>\n'
                      f'<section class="more"><h2>{u["more"]}</h2><div class="posts">\n')
                h += ''.join(f'<a class="post" href="{u["pre"]}/blog/{y["id"]}/"><small>{E(y["k"][lang])}</small><h3>{E(y["title"][lang])}</h3>'
                             f'<p>{E(y["excerpt"][lang])}</p></a>' for y in rel) + '</div></section>\n'
                h += self.footer(lang)
                self.write(f"{u['pre'].strip('/')}/blog/{a['id']}/index.html".lstrip('/'), h)

    # --- сторінка статусу замовлення (/status/, /ru/status/)
    def status_pages(self):
        for lang in LANGS:
            u, r = UI[lang], ST[lang]
            other = 'ru' if lang == 'uk' else 'uk'
            canonical = f"{self.url}{u['pre']}/status/"
            alts = {'uk': f"{self.url}/status/", 'ru': f"{self.url}/ru/status/", 'x-default': f"{self.url}/status/"}
            home = '/' if lang == 'uk' else '/ru/'
            h = self.head(lang, r['title'], r['desc'], canonical, alts, 'website', f"{self.url}/img/og.jpg", [], robots='noindex, follow')
            h += self.header(lang, f"{UI[other]['pre']}/status/")
            cfg = json.dumps({'sheet': self.sheet_url, 'tg': self.tg, 'tgText': self.tg.replace('https://', ''), 'lang': lang,
                              't': {k: v for k, v in r.items() if k not in ('title', 'desc')}},
                             ensure_ascii=False).replace('</', '<\\/')
            tpl = STATUS_HTML
            for k, v in dict(HOME=home, H1=r['h1'], LEAD=r['lead'], ORDER=r['order'], ORDER_PH=r['order_ph'], LAST4=r['last4'],
                             LAST4_PH=r['last4_ph'], BTN=r['btn'], FORGET=r['forget'], TG=self.tg, CFG=cfg).items():
                tpl = tpl.replace('@@' + k + '@@', v)
            h += tpl
            h += self.footer(lang)
            self.write(f"{u['pre'].strip('/')}/status/index.html".lstrip('/'), h)

    # --- керування підпискою (/subscription/, /ru/subscription/)
    def subscription_pages(self):
        for lang in LANGS:
            u, r = UI[lang], SB[lang]
            other = 'ru' if lang == 'uk' else 'uk'
            canonical = f"{self.url}{u['pre']}/subscription/"
            alts = {'uk': f"{self.url}/subscription/", 'ru': f"{self.url}/ru/subscription/", 'x-default': f"{self.url}/subscription/"}
            home = '/' if lang == 'uk' else '/ru/'
            h = self.head(lang, r['title'], r['desc'], canonical, alts, 'website', f"{self.url}/img/og.jpg", [], robots='noindex, follow')
            h += self.header(lang, f"{UI[other]['pre']}/subscription/")
            tx = {k: v for k, v in r.items() if k not in ('title', 'desc')}
            cfg = json.dumps({'sheet': self.sheet_url, 'tg': self.tg, 'tgText': self.tg.replace('https://', ''), 'lang': lang,
                              'products': [p['name'] for p in self.prods], 't': tx}, ensure_ascii=False).replace('</', '<\\/')
            tpl = SUB_HTML
            for k, v in dict(HOME=home, H1=r['h1'], LEAD=r['lead'], ID=r['id'], ID_PH=r['id_ph'], LAST4=r['last4'], LAST4_PH=r['last4_ph'],
                             BTN=r['btn'], FORGET=r['forget'], TG=self.tg, CFG=cfg).items():
                tpl = tpl.replace('@@' + k + '@@', v)
            h += tpl
            h += self.footer(lang)
            self.write(f"{u['pre'].strip('/')}/subscription/index.html".lstrip('/'), h)

    # --- сторінка відгуку (/review/, /ru/review/)
    def review_pages(self):
        for lang in LANGS:
            u, r = UI[lang], REV[lang]
            other = 'ru' if lang == 'uk' else 'uk'
            canonical = f"{self.url}{u['pre']}/review/"
            alts = {'uk': f"{self.url}/review/", 'ru': f"{self.url}/ru/review/", 'x-default': f"{self.url}/review/"}
            home = '/' if lang == 'uk' else '/ru/'
            h = self.head(lang, r['title'], r['desc'], canonical, alts, 'website', f"{self.url}/img/og.jpg", [], robots='noindex, follow')
            h += self.header(lang, f"{UI[other]['pre']}/review/")
            stars = ''.join(f'<input type="radio" name="rating" id="st{i}" value="{i}"><label for="st{i}" title="{i}"><span aria-hidden="true">★</span><span class="sr">{i}</span></label>'
                            for i in (5, 4, 3, 2, 1))
            opts = f'<option value="">{r["product_any"]}</option>' + ''.join(
                f'<option value="{E(p["id"])}" data-name="{E(p["name"])}">{E(p["name"])}</option>' for p in self.prods)
            cfg = json.dumps({'key': self.w3key, 'sheet': self.sheet_url, 'tg': self.tg, 'lang': lang,
                              'err': {k: r[k] for k in ('rating_err', 'text_err', 'name_err', 'consent_err', 'submit', 'sending', 'fail')}},
                             ensure_ascii=False).replace('</', '<\\/')
            tpl = REVIEW_HTML
            for k, v in dict(HOME=home, H1=r['h1'], LEAD=r['lead'], RATING=r['rating'], STARS=stars, PRODUCT=r['product'], OPTS=opts,
                             TEXT=r['text'], TEXT_PH=E(r['text_ph']), NAME=r['name'], NAME_PH=E(r['name_ph']), ORDER=r['order'],
                             ORDER_HINT=r['order_hint'], CONSENT=r['consent'], SUBMIT=r['submit'], OK_H=r['ok_h'], OK_P=r['ok_p'],
                             OK_BTN=r['ok_btn'], CFG=cfg).items():
                tpl = tpl.replace('@@' + k + '@@', v)
            h += tpl
            h += self.footer(lang)
            self.write(f"{u['pre'].strip('/')}/review/index.html".lstrip('/'), h)

    # --- 404.html (GitHub Pages показує її для неіснуючих адрес)
    def page_404(self):
        blocks = ''
        for lg in LANGS:
            hm = '/' if lg == 'uk' else '/ru/'
            blocks += (f'<section class="nf" data-l="{lg}"{"" if lg == "uk" else " hidden"}><h1>{NF[lg]["h"]}</h1><p>{NF[lg]["p"]}</p>'
                       f'<p class="nf-btns"><a class="btn" href="{hm}#catalog">{NF[lg]["cat"]}</a> '
                       f'<a class="btn ghost" href="{UI[lg]["pre"]}/blog/">{NF[lg]["blog"]}</a> '
                       f'<a class="btn ghost" href="{hm}">{NF[lg]["home"]}</a></p></section>\n')
        self.write('404.html', PAGE_404.replace('@@ICONS@@', ICONS).replace('@@BLOCKS@@', blocks))

    # --- короткі посилання (/ig, /tg, ...)
    def short_links(self):
        # Превʼю в Viber/Telegram/Facebook бере Open Graph із самої сторінки (JS і редірект боти не виконують),
        # тому копіюємо їх з index.html — коротке посилання виглядає в чаті так само, як головна.
        head = open(INDEX, encoding='utf-8').read().split('</head>')[0]
        tags = re.findall(r'<meta (?:property="og:[^"]+"|name="twitter:[^"]+"|name="description")[^>]*>', head)
        meta = '\n'.join(tags) + '\n'
        for code, src in SHORT.items():
            self.write(f'{code}/index.html', SHORT_HTML.replace('@@META@@', meta).replace('@@URL@@', self.url).replace('@@SRC@@', json.dumps(src, ensure_ascii=False)))

    # --- фід товарів для Google Merchant Center (безкоштовні лістинги): /feed/merchant-uk.xml, /feed/merchant-ru.xml
    def merchant_feed(self):
        def x(v):
            return html.escape(str(v), quote=False)
        cat_path = 'Food, Beverages & Tobacco > Beverages > Coffee & Tea > Coffee'
        for lang in LANGS:
            u = UI[lang]
            title_site = 'ZRN Coffee'
            out = ['<?xml version="1.0" encoding="UTF-8"?>',
                   '<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">', '<channel>',
                   f'<title>{title_site}</title>', f'<link>{self.main(lang)}</link>',
                   f'<description>{x(self.ui_txt[lang]["meta.desc"])}</description>']
            for p in self.prods:
                link = self.p_url(lang, p['id'])
                img = f"{self.url}/{p['img']}"
                kind = ('Бленди' if lang == 'uk' else 'Бленды') if p['type'] == 'blend' else ('Моносорти' if lang == 'uk' else 'Моносорты')
                base_desc = self.short(f"{p['notes'][lang]}. {p['region'][lang]}. {p['info'][lang]}", 900)
                for w, pr in ((p['w1'], p['price1']), (p['w2'], p['price2'])):
                    out.append('<item>')
                    out.append(f'<g:id>{x(p["id"])}-{w}</g:id>')
                    out.append(f'<g:item_group_id>{x(p["id"])}</g:item_group_id>')
                    out.append(f'<title>{x(p["name"])} — {w} {u["g"]}</title>')
                    out.append(f'<description>{x(base_desc)}</description>')
                    out.append(f'<link>{x(link)}</link>')
                    out.append(f'<g:image_link>{x(img)}</g:image_link>')
                    out.append('<g:availability>in_stock</g:availability>')
                    out.append(f'<g:price>{pr}.00 UAH</g:price>')
                    out.append('<g:condition>new</g:condition>')
                    out.append('<g:brand>ZRN Coffee</g:brand>')
                    out.append('<g:identifier_exists>no</g:identifier_exists>')
                    out.append(f'<g:google_product_category>{x(cat_path)}</g:google_product_category>')
                    out.append(f'<g:product_type>{x("Кава > " + kind if lang == "uk" else "Кофе > " + kind)}</g:product_type>')
                    out.append(f'<g:product_weight>{w} g</g:product_weight>')
                    out.append(f'<g:shipping_weight>{w} g</g:shipping_weight>')
                    out.append('<g:ships_from_country>UA</g:ships_from_country>')
                    out.append('<g:min_handling_time>0</g:min_handling_time>')
                    out.append('<g:max_handling_time>1</g:max_handling_time>')
                    out.append(f'<g:custom_label_0>{"blend" if p["type"] == "blend" else "mono"}</g:custom_label_0>')
                    out.append('</item>')
            out += ['</channel>', '</rss>', '']
            self.write(f'feed/merchant-{lang}.xml', '\n'.join(out))

    # --- sitemap
    def home_ru(self):
        """Російська головна: /ru/index.html — той самий index.html, але з російськими <title>, описом, canonical, og.
        Мову сторінки вибирає JS за адресою /ru/ (див. initLanguage)."""
        h = self.index_src
        t = html.escape(self.ui_txt['ru']['meta.title'], quote=True)
        d = html.escape(self.ui_txt['ru']['meta.desc'], quote=True)
        def sub(pattern, repl):
            nonlocal h
            h, n = re.subn(pattern, lambda m: repl, h, count=1)
            if n != 1:
                fail(f'/ru/: не знайдено в index.html: {pattern}')
        sub(r'<html lang="uk">', '<html lang="ru">')
        sub(r'<title>[^<]*</title>', f'<title>{t}</title>')
        sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d}">')
        sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{self.url}/ru/">')
        sub(r'<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="ru_RU">')
        sub(r'<meta property="og:locale:alternate" content="ru_RU">', '<meta property="og:locale:alternate" content="uk_UA">')
        sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">')
        sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d}">')
        sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{self.url}/ru/">')
        sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{t}">')
        sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{d}">')
        h = replace_between(h, '<!--FAQ:LD:START-->', '<!--FAQ:LD:END-->', faq_ld_tag(self.index_src, 'ru'), 'FAQ:LD')
        self.write('ru/index.html', h)

    def sitemap(self):
        def entry(loc, alts, prio, freq):
            x = f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n"
            for k, v in alts.items():
                x += f'    <xhtml:link rel="alternate" hreflang="{k}" href="{v}"/>\n'
            return x + '  </url>\n'
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        ma = {'uk': self.url + '/', 'ru': self.url + '/ru/', 'x-default': self.url + '/'}
        sm += entry(self.url + '/', ma, '1.0', 'weekly') + entry(self.url + '/ru/', ma, '0.8', 'weekly')
        for p in self.prods:
            a = {'uk': self.p_url('uk', p['id']), 'ru': self.p_url('ru', p['id']), 'x-default': self.p_url('uk', p['id'])}
            sm += entry(a['uk'], a, '0.9', 'weekly') + entry(a['ru'], a, '0.7', 'weekly')
        bi = {'uk': self.blog_idx('uk'), 'ru': self.blog_idx('ru'), 'x-default': self.blog_idx('uk')}
        sm += entry(bi['uk'], bi, '0.7', 'weekly') + entry(bi['ru'], bi, '0.5', 'weekly')
        for a_ in self.posts:
            a = {'uk': self.b_url('uk', a_['id']), 'ru': self.b_url('ru', a_['id']), 'x-default': self.b_url('uk', a_['id'])}
            sm += entry(a['uk'], a, '0.6', 'monthly') + entry(a['ru'], a, '0.5', 'monthly')
        for path in ('oferta', 'privacy'):
            sm += entry(f'{self.url}/{path}/', {}, '0.3', 'yearly')
        self.write('sitemap.xml', sm + '</urlset>\n')


CSS = '''/* ZRN Coffee — стилі окремих сторінок сортів і блогу (генерується tools/build.py) */
:root{--bg:#f3ead9;--bg2:#ece0c7;--card:#fdf9f0;--ink:#2a2217;--sub:#6f6150;--gold:#8a6324;--gold-soft:#6b4a1c;--line:rgba(107,74,28,.28);--dark:#211a11;--accent:#a9792f}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{color:var(--ink);font-family:'Inter',system-ui,sans-serif;line-height:1.6;font-size:16px}
h1,h2,h3{font-family:'Fraunces',Georgia,serif;font-weight:500;letter-spacing:-.01em;line-height:1.2}
a{color:var(--gold-soft)}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px}
.site-head{position:sticky;top:0;z-index:10;background:rgba(243,234,217,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.hd-in{display:flex;align-items:center;gap:18px;min-height:60px}
.hd-logo{display:flex;flex-direction:column;text-decoration:none;color:var(--dark);line-height:1.1}
.hd-logo b{font-family:'Fraunces',Georgia,serif;font-size:1.25rem;letter-spacing:.08em}
.hd-logo span{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--sub)}
.site-head nav{display:flex;gap:4px;margin-left:auto;flex-wrap:wrap}
.site-head nav a,.lang{display:inline-flex;align-items:center;min-height:44px;padding:0 10px;text-decoration:none;color:var(--ink);font-size:.92rem;font-weight:500}
.site-head nav a:hover,.lang:hover{color:var(--gold)}
.lang{border:1px solid var(--line);border-radius:8px;min-width:44px;justify-content:center;font-size:.85rem}
main{padding-top:18px;padding-bottom:60px}
.crumbs{font-size:.85rem;color:var(--sub);margin:6px 0 18px}
.crumbs a{color:var(--sub)}
.p-grid{display:grid;grid-template-columns:1fr;gap:24px;margin-bottom:34px}
@media(min-width:760px){.p-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:start;gap:40px}}
.p-img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:12px;background:var(--dark);box-shadow:0 0 0 2px color-mix(in srgb,var(--accent) 55%,transparent)}
.kicker{font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--gold)}
h1{font-size:clamp(1.7rem,4.6vw,2.4rem);margin:4px 0 8px}
.origin{color:var(--sub);margin-bottom:14px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.chip{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.88rem}
.prices{display:flex;gap:28px;margin:6px 0 20px}
.prices div{display:flex;flex-direction:column}
.prices b{font-weight:500;color:var(--sub);font-size:.85rem}
.prices span{font-family:'Fraunces',Georgia,serif;font-size:1.6rem}
.prices small{color:var(--sub);font-size:.78rem}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 28px;background:var(--dark);color:#fff;border-radius:10px;text-decoration:none;font-weight:600}
.btn:hover{background:var(--gold-soft)}
.fresh{margin-top:12px;font-size:.88rem;color:var(--sub)}
section{margin:0 0 32px;max-width:70ch}
section.wide{max-width:none}
section h2,.more h2{font-size:1.4rem;margin-bottom:12px}
section p,.article p{margin-bottom:12px;color:var(--sub)}
.note{font-size:.85rem;color:var(--sub)}
.note.strong{color:var(--ink);background:rgba(169,121,47,.08);border-left:3px solid var(--gold);padding:8px 12px;border-radius:0 8px 8px 0;margin:12px 0}
.bars{display:grid;gap:10px;margin-bottom:8px}
.bar{display:grid;grid-template-columns:110px 1fr;gap:12px;align-items:center;font-size:.8rem;letter-spacing:.04em;text-transform:uppercase;color:var(--sub);font-weight:600}
.track{height:6px;background:rgba(42,34,23,.09);border-radius:99px;overflow:hidden}
.fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--gold-soft),#b8862f)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.specs{display:grid;grid-template-columns:1fr;gap:0;border:1px solid var(--line);border-radius:10px;background:var(--card);overflow:hidden;margin-bottom:14px}
.specs div{display:flex;gap:12px;padding:11px 16px;border-bottom:1px solid var(--line)}
.specs div:last-child{border-bottom:0}
.specs dt{flex:0 0 150px;color:var(--sub);font-size:.9rem}
.specs dd{font-weight:500}
.dots{display:inline-flex;gap:4px;margin-left:8px;vertical-align:middle}
.dots span{width:9px;height:9px;border-radius:50%;border:1px solid var(--gold);display:inline-block}
.dots span.on{background:var(--gold)}
.ends{display:flex;justify-content:space-between;max-width:150px;font-size:.72rem;color:var(--sub);font-weight:400}
.ends i{font-style:normal}
.brewc{padding:10px 0;border-bottom:1px dashed var(--line)}
.brewc:last-of-type{border-bottom:0}
.brewc p{margin:2px 0 0}
.ticks{list-style:none;display:grid;gap:8px;color:var(--sub)}
.ticks li{padding-left:20px;position:relative}
.ticks li::before{content:'✓';position:absolute;left:0;color:var(--gold-soft);font-weight:700}
.minis{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}
.mini{display:flex;flex-direction:column;gap:4px;text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px}
.mini:hover{border-color:var(--gold)}
.mini img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:6px;background:var(--dark)}
.mini span{font-weight:600;font-size:.95rem}
.mini small{color:var(--sub);font-size:.8rem;line-height:1.35}
.mini em{font-style:normal;color:var(--gold-soft);font-size:.82rem}
.allc{margin-top:16px;font-size:.88rem;color:var(--sub)}
.posts{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin:18px 0 34px}
.post{display:flex;flex-direction:column;gap:8px;text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px}
.post:hover{border-color:var(--gold)}
.post small{font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--gold-soft)}
.post h2,.post h3{font-size:1.1rem}
.post p{color:var(--sub);font-size:.9rem;margin:0}
.post span{color:var(--gold-soft);font-size:.9rem;margin-top:auto}
.article{max-width:66ch;margin-bottom:34px}
.article .kicker{display:block}
.article h1{margin-bottom:18px}
.article p{font-size:1rem;line-height:1.75}
.article .btn{margin-top:10px;color:#fff}
.site-foot{border-top:1px solid var(--line);background:var(--bg2);padding:26px 0;font-size:.9rem;color:var(--sub)}
.foot-city{font-size:.82rem;color:var(--sub);margin-top:4px}
.foot-links{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:8px}
.foot-links a{display:inline-flex;align-items:center;min-height:44px;color:var(--sub)}
.btn.ghost{background:transparent;color:var(--dark);border:1px solid var(--line)}
.btn.ghost:hover{background:var(--card);color:var(--dark)}
.nf-wrap{text-align:center;padding-top:56px}
.nf-code{font-family:'Fraunces',Georgia,serif;font-size:clamp(5rem,22vw,9rem);line-height:1;color:var(--gold);opacity:.85;margin-bottom:8px}
.nf h1{margin-bottom:12px}
.nf p{color:var(--sub);max-width:46ch;margin:0 auto 14px}
.nf-btns{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:22px}
.nf-btns .btn{min-width:150px}
.lead{color:var(--sub);max-width:62ch;margin-bottom:22px}
.rev-form{max-width:620px;margin-bottom:34px}
.rv-f{margin:0 0 16px;border:0;padding:0}
.rv-f label,.rv-f legend{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--sub);margin-bottom:7px;padding:0}
.rv-f input[type=text],.rv-f select,.rv-f textarea{width:100%;font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;min-height:48px}
.rv-f textarea{resize:vertical;min-height:120px;line-height:1.5}
.rv-f input:focus,.rv-f select:focus,.rv-f textarea:focus{outline:2px solid var(--gold);outline-offset:1px}
.rv-f small{display:block;margin-top:6px;font-size:.8rem;color:var(--sub);line-height:1.4}
.stars{display:inline-flex;flex-direction:row-reverse;justify-content:flex-end;gap:2px}
.stars input{position:absolute;opacity:0;width:1px;height:1px}
.stars label{margin:0;padding:0 3px;font-size:2.3rem;line-height:1;color:#cdbf9f;cursor:pointer;text-transform:none;letter-spacing:0;min-width:44px;min-height:48px;display:inline-flex;align-items:center;justify-content:center}
.stars input:checked~label,.stars label:hover,.stars label:hover~label{color:#c89640}
.stars input:focus-visible+label{outline:2px solid var(--gold);border-radius:6px}
.rv-check{display:flex;gap:10px;align-items:flex-start;font-size:.88rem;color:var(--sub);line-height:1.45;margin:4px 0 16px;cursor:pointer}
.rv-check input{width:20px;height:20px;flex:none;margin-top:1px;accent-color:var(--gold-soft)}
.rv-check a{color:var(--gold-soft);text-decoration:underline}
.rv-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.rv-err{background:rgba(193,67,42,.09);color:#9c3b26;border:1px solid rgba(193,67,42,.3);border-radius:8px;padding:10px 14px;font-size:.9rem;margin:0 0 14px}
.rev-form .btn{width:100%;border:0;cursor:pointer;font:inherit;font-weight:600}
.rev-form .btn:disabled{opacity:.6;cursor:wait}
.rev-thanks{max-width:560px;margin:10px 0 40px}
.rev-thanks h2{font-size:1.6rem;margin-bottom:10px}
.rev-thanks p{color:var(--sub);margin-bottom:14px}
.st-form{max-width:460px;margin-bottom:34px}
.st-form .btn{width:100%;border:0;cursor:pointer;font:inherit;font-weight:600}
.st-form .btn:disabled{opacity:.6;cursor:wait}
.st-form input{letter-spacing:.04em}
.st-forget{margin:14px 0 0;font-size:.82rem}
.st-forget a{color:var(--sub);text-decoration:underline}
.st-res{max-width:720px;margin:0 0 44px}
.st-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 18px}
.st-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 16px;align-items:baseline;margin-bottom:18px}
.st-num{font-family:'Fraunces',Georgia,serif;font-size:1.5rem;color:var(--dark)}
.st-date{color:var(--sub);font-size:.9rem}
.st-tl{list-style:none;margin:0 0 18px;padding:0;display:flex;gap:0;counter-reset:s}
.st-tl li{flex:1;position:relative;text-align:center;font-size:.78rem;color:var(--sub);padding-top:0}
.st-tl li::before{content:"";position:absolute;top:15px;left:-50%;width:100%;height:2px;background:var(--line);z-index:0}
.st-tl li:first-child::before{display:none}
.st-tl li.done::before,.st-tl li.cur::before{background:var(--gold)}
.st-dot{position:relative;z-index:1;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;background:var(--bg);border:2px solid var(--line);font-weight:600;font-size:.85rem;color:var(--sub)}
.st-tl li.done .st-dot{background:var(--gold);border-color:var(--gold);color:#fff}
.st-tl li.cur .st-dot{border-color:var(--gold);color:var(--dark);box-shadow:0 0 0 4px rgba(201,162,77,.22)}
.st-tl li.cur .st-lb{color:var(--dark);font-weight:600}
.st-lb{display:block;margin-top:6px;line-height:1.25}
.st-banner{background:rgba(201,162,77,.14);border-radius:10px;padding:14px 16px;font-weight:600;margin-bottom:16px;color:var(--dark)}
.st-banner.st-bad{background:rgba(193,67,42,.1);color:#9c3b26}
.st-track{background:rgba(201,162,77,.14);border-radius:10px;padding:12px 16px;margin-bottom:16px;color:var(--dark)}
.st-sub{color:var(--sub);font-size:.88rem;margin-top:3px}
.st-note{border-left:3px solid var(--gold);padding:4px 0 4px 14px;margin:0 0 16px;color:var(--dark)}
.st-note b{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--sub);margin-bottom:3px}
.st-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.st-box{border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.st-box h3{margin:0 0 6px;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--sub);font-weight:600}
.st-box p{margin:0 0 6px;font-size:.92rem;line-height:1.45}
.st-ttn{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.st-copy{font:inherit;font-size:.78rem;padding:3px 10px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--dark);cursor:pointer}
.st-link{display:inline-block;color:var(--gold-soft);text-decoration:underline;font-size:.88rem;margin-top:2px}
.st-items ul{margin:0 0 8px;padding-left:18px;font-size:.92rem}
.st-items li{margin:2px 0}
.st-total{font-weight:600}
.st-auto{color:var(--sub);font-size:.8rem;margin:12px 0 0}
.st-act{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.st-act .btn{flex:1 1 140px;text-align:center;border:0;cursor:pointer;font:inherit;font-weight:600}
.st-act .btn.ghost{border:1px solid var(--line)}
@media(max-width:560px){.st-grid{grid-template-columns:1fr}.st-tl li{font-size:.6rem;padding:0;letter-spacing:-.01em;overflow-wrap:normal;hyphens:none}.st-dot{width:28px;height:28px}.st-tl li::before{top:13px}.st-card{padding:18px 12px}}
@media(max-width:560px){.hd-logo span{display:none}.site-head nav a{padding:0 7px;font-size:.85rem}.specs div{flex-direction:column;gap:2px}.specs dt{flex:none}.bar{grid-template-columns:96px 1fr}}
'''


def main():
    cat = apply_sheet(load())
    index_src = build_index(cat)
    site = Site(cat, index_src)
    site.product_pages()
    site.blog_pages()
    site.review_pages()
    site.status_pages()
    site.subscription_pages()
    site.page_404()
    site.short_links()
    site.home_ru()
    site.merchant_feed()
    site.sitemap()
    site.write('pages.css', CSS + SB_CSS)
    # прибираємо застарілі сторінки сортів/статей, яких більше немає в catalog.json
    keep = set(site.out)
    for base in ('coffee', 'blog', 'ru/coffee', 'ru/blog'):
        root = os.path.join(ROOT, base)
        if not os.path.isdir(root):
            continue
        for d in os.listdir(root):
            f = os.path.join(root, d, 'index.html')
            rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
            if os.path.exists(f) and rel not in keep:
                os.remove(f)
                try:
                    os.rmdir(os.path.dirname(f))
                except OSError:
                    pass
    for rel, content in site.out.items():
        full = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, 'w', encoding='utf-8').write(content)
    print(f'Готово: ціни — {"з таблиці" if os.environ.get("ZRN_OFFLINE") != "1" else "з catalog.json"}; сортів {len(cat["products"])}, статей {len(cat["posts"])}, файлів згенеровано {len(site.out)} + index.html')


if __name__ == '__main__':
    main()
