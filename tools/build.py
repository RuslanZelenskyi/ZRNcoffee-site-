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
        o['price200'] = p['price200']
        o['price500'] = p['price500']
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
        return ''.join(f'\n      <li><a href="/coffee/{p["id"]}/">{E(p["name"])}</a> — 200 г: {p["price200"]} ₴, 500 г: {p["price500"]} ₴</li>'
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
    keys = ['trust.fact', 'ship.del2', 'ship.del3', 'ship.del4', 'ship.pay1', 'ck.guarantee']
    return {lang: {k: get(lang, k) for k in keys} for lang in LANGS}


# ------------------------------------------------------------------ сторінки
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
               blogIdx='Блог ZRN — про каву, помел і свіжість | ZRN Coffee', author='Руслан Зеленський'),
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
               blogIdx='Блог ZRN — о кофе, помоле и свежести | ZRN Coffee', author='Руслан Зеленский'),
}


class Site:
    def __init__(self, cat, index_src):
        self.cat = cat
        self.url = cat['site']['url'].rstrip('/')
        self.tg = cat['site']['telegram']
        self.email = cat['site']['email']
        self.prods = cat['products']
        self.posts = cat['posts']
        self.ui_txt = ui_texts(index_src)
        self.out = {}

    # --- адреси
    def p_url(self, lang, pid): return f"{self.url}{UI[lang]['pre']}/coffee/{pid}/"
    def b_url(self, lang, bid): return f"{self.url}{UI[lang]['pre']}/blog/{bid}/"
    def blog_idx(self, lang): return f"{self.url}{UI[lang]['pre']}/blog/"
    def main(self, lang): return self.url + '/' if lang == 'uk' else self.url + '/?lang=ru'

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
    def head(self, lang, title, desc, canonical, alts, og_type, image, ld):
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
<meta name="robots" content="index, follow, max-image-preview:large">
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23211a11'/%3E%3Ctext x='16' y='21' text-anchor='middle' font-size='9' font-weight='700' fill='%23c89640' font-family='Georgia,serif'%3EZRN%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pages.css">
{ld_tags}</head>
<body>
'''

    def header(self, lang, alt_href):
        u = UI[lang]
        home = '/' if lang == 'uk' else '/?lang=ru'
        return f'''<header class="site-head">
  <div class="wrap hd-in">
    <a class="hd-logo" href="{home}" aria-label="ZRN Craft Micro Roastery"><b>ZRN</b><span>{u['craft']}</span></a>
    <nav aria-label="{u['home']}">
      <a href="{home}#catalog">{u['catalog']}</a>
      <a href="{home}#blends">{u['blends']}</a>
      <a href="{u['pre']}/blog/">{u['blog']}</a>
    </nav>
    <a class="lang" href="{alt_href}" hreflang="{'ru' if lang == 'uk' else 'uk'}">{u['altcode']}</a>
  </div>
</header>
<main class="wrap">
'''

    def footer(self, lang):
        u = UI[lang]
        home = '/' if lang == 'uk' else '/?lang=ru'
        return f'''</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-brand"><b>ZRN</b> {u['foot']}</div>
    <div class="foot-links">
      <a href="{home}">ZRN Coffee</a>
      <a href="{u['pre']}/blog/">{u['blog']}</a>
      <a href="{self.tg}" rel="noopener">Telegram</a>
      <a href="mailto:{self.email}">{u['mail']}</a>
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
                desc = self.short(f"{u['h1']}{name}: {notes}. {p['region'][lang]}. {u['fresh']}. 200 {u['g']} — {p['price200']} ₴.", 158)
                img = f"{self.url}/{p['img']}"
                canonical = self.p_url(lang, p['id'])
                alts = {'uk': self.p_url('uk', p['id']), 'ru': self.p_url('ru', p['id']), 'x-default': self.p_url('uk', p['id'])}
                shop = '/' if lang == 'uk' else '/?lang=ru'
                buy_href = ('/?buy=' if lang == 'uk' else '/?lang=ru&amp;buy=') + p['id']
                sect = 'blends' if p['type'] == 'blend' else 'catalog'
                offers = [{'@type': 'Offer', 'name': f"{w} {u['g']}", 'priceCurrency': 'UAH', 'price': str(pr),
                           'availability': 'https://schema.org/InStock', 'itemCondition': 'https://schema.org/NewCondition', 'url': canonical,
                           'shippingDetails': {'@type': 'OfferShippingDetails',
                                               'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'UA'},
                                               'deliveryTime': {'@type': 'ShippingDeliveryTime',
                                                                'handlingTime': {'@type': 'QuantitativeValue', 'minValue': 0, 'maxValue': 1, 'unitCode': 'DAY'}}},
                           'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'UA',
                                                       'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow',
                                                       'merchantReturnDays': 14}}
                          for w, pr in ((200, p['price200']), (500, p['price500']))]
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
                            f'<span>{E(q["name"])}</span><small>{E(q["notes"][lang])}</small><em>{u["from_"]}{q["price200"]} ₴</em></a>')
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
        <div><b>200 {u['g']}</b><span>{p['price200']} ₴</span><small>{round(p['price200'] / 2)} ₴ {u['per100']}</small></div>
        <div><b>500 {u['g']}</b><span>{p['price500']} ₴</span><small>{round(p['price500'] / 5)} ₴ {u['per100']}</small></div>
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
            home = '/' if lang == 'uk' else '/?lang=ru'
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

    # --- sitemap
    def sitemap(self):
        def entry(loc, alts, prio, freq):
            x = f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n"
            for k, v in alts.items():
                x += f'    <xhtml:link rel="alternate" hreflang="{k}" href="{v}"/>\n'
            return x + '  </url>\n'
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        ma = {'uk': self.url + '/', 'ru': self.url + '/?lang=ru', 'x-default': self.url + '/'}
        sm += entry(self.url + '/', ma, '1.0', 'weekly') + entry(self.url + '/?lang=ru', ma, '0.8', 'weekly')
        for p in self.prods:
            a = {'uk': self.p_url('uk', p['id']), 'ru': self.p_url('ru', p['id']), 'x-default': self.p_url('uk', p['id'])}
            sm += entry(a['uk'], a, '0.9', 'weekly') + entry(a['ru'], a, '0.7', 'weekly')
        bi = {'uk': self.blog_idx('uk'), 'ru': self.blog_idx('ru'), 'x-default': self.blog_idx('uk')}
        sm += entry(bi['uk'], bi, '0.7', 'weekly') + entry(bi['ru'], bi, '0.5', 'weekly')
        for a_ in self.posts:
            a = {'uk': self.b_url('uk', a_['id']), 'ru': self.b_url('ru', a_['id']), 'x-default': self.b_url('uk', a_['id'])}
            sm += entry(a['uk'], a, '0.6', 'monthly') + entry(a['ru'], a, '0.5', 'monthly')
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
.foot-links{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:8px}
.foot-links a{display:inline-flex;align-items:center;min-height:44px;color:var(--sub)}
@media(max-width:560px){.hd-logo span{display:none}.site-head nav a{padding:0 7px;font-size:.85rem}.specs div{flex-direction:column;gap:2px}.specs dt{flex:none}.bar{grid-template-columns:96px 1fr}}
'''


def main():
    cat = load()
    index_src = build_index(cat)
    site = Site(cat, index_src)
    site.product_pages()
    site.blog_pages()
    site.sitemap()
    site.write('pages.css', CSS)
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
    print(f'Готово: сортів {len(cat["products"])}, статей {len(cat["posts"])}, файлів згенеровано {len(site.out)} + index.html')


if __name__ == '__main__':
    main()
