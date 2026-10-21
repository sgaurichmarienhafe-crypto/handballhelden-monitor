import json,urllib.request,datetime
from pathlib import Path
from html.parser import HTMLParser
from lxml import html
URL='https://handball-engagiert.de/unsere-handballhelden'
req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 (compatible; HandballheldenMonitor/1.0)'})
with urllib.request.urlopen(req,timeout=45) as resp: content=resp.read()
root=html.fromstring(content.decode('utf-8'))
rows=[]
for card in root.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," hbe-card ")]'):
 b=card.xpath('.//button[@data-hbe-vote-nid]')
 if not b:continue
 def txt(xpath):
  a=card.xpath(xpath);return ' '.join(''.join(a[0].itertext()).split()) if a else ''
 facts={}
 for f in card.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," hbe-card__fact ")]'):
  k=f.xpath('.//dt');v=f.xpath('.//dd')
  if k and v:facts[''.join(k[0].itertext()).strip(' :')]=''.join(v[0].itertext()).strip()
 n=b[0].xpath('.//*[@data-hbe-vote-num]')
 if not n:continue
 raw=''.join(n[0].itertext()).strip().replace('.','').replace(' ','')
 if not raw.isdigit():continue
 rows.append({'id':b[0].get('data-hbe-vote-nid'),'name':txt('.//*[contains(concat(" ",normalize-space(@class)," ")," hbe-card__name ")]'),'votes':int(raw),'verband':facts.get('Landesverband',''),'kategorie':facts.get('Kategorie',''),'geschlecht':'Nicht angegeben'})
if len(rows)<700:raise RuntimeError(f'Nur {len(rows)} Einträge gefunden. Alte Daten bleiben unverändert.')
if len({x['id'] for x in rows})!=len(rows):raise RuntimeError('Doppelte IDs, keine Aktualisierung')
Path('daten.json').write_text(json.dumps({'stand':datetime.datetime.now(datetime.timezone.utc).strftime('%d.%m.%Y %H:%M UTC'),'personen':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('Aktualisiert:',len(rows))
