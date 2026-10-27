"""Build self-contained animated SVG profile art. Daily run needs only Python."""
import argparse, json, re
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
USER='Walaa2S'
class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.cells={}; self.tips={}; self.target=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'data-date' in a and 'data-level' in a:
            self.cells[a['id']]={'date':a['data-date'],'level':int(a['data-level'])}
        if tag=='tool-tip': self.target=a.get('for')
    def handle_data(self, data):
        if self.target: self.tips[self.target]=self.tips.get(self.target,'')+data
    def handle_endtag(self, tag):
        if tag=='tool-tip': self.target=None

def svg(w,h,title,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.reveal{{animation:appear .5s both}}@keyframes appear{{from{{opacity:0;transform:translateY(-5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.reveal{{animation:none}}}}</style><rect width="{w}" height="{h}" rx="12" fill="#0D0714"/><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="none" stroke="#35234D"/>{body}</svg>'''

def text(x,y,s,color='#EDE9FE',size=13,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(s)}</text>'

def heatmap(source=None):
    if source: html=Path(source).read_text()
    else:
        req=Request(f'https://github.com/users/{USER}/contributions',headers={'User-Agent':'Walaa2S-profile-art'})
        with urlopen(req,timeout=30) as r: html=r.read().decode()
    p=Calendar();p.feed(html)
    days=[]
    for ident,d in p.cells.items():
        tip=p.tips.get(ident,'').strip()
        m=re.match(r'([\d,]+) contributions?\b',tip)
        if m: d['count']=int(m[1].replace(',',''))
        elif tip.startswith('No contributions'): d['count']=0
        else: raise ValueError('Contribution count missing; keeping previous artwork')
        if not 0<=d['level']<=4: raise ValueError('Unexpected level')
        days.append(d)
    days.sort(key=lambda d:d['date'])
    if len(days)<350: raise ValueError('Incomplete calendar; keeping previous artwork')
    start=date.fromisoformat(days[0]['date']);start-=timedelta(days=(start.weekday()+1)%7)
    palette=['#1C122B','#3B1D5C','#6D28D9','#8B5CF6','#C4B5FD']
    body=text(26,32,'Walaa2S / contribution activity','#B5A6CD',13)
    lastmonth=None
    for d in days:
        dt=date.fromisoformat(d['date']);offset=(dt-start).days;col,row=divmod(offset,7)
        x,y=40+col*14.6,74+row*17
        if dt.month!=lastmonth and row==0:
            body+=text(x,60,dt.strftime('%b'),'#B5A6CD',10);lastmonth=dt.month
        body+=f'<rect class="reveal" style="animation-delay:{(col+row)*.025:.3f}s" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{palette[d["level"]]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
    total=sum(d['count'] for d in days)
    body+=text(26,218,f'{total:,} contributions in the displayed year','#F5F0FF',13)
    body+=text(690,218,'Less','#B5A6CD',10)
    for i,c in enumerate(palette): body+=f'<rect x="{722+i*15}" y="208" width="11" height="11" rx="2" fill="{c}"/>'
    body+=text(803,218,'More','#B5A6CD',10)
    body+=text(26,246,f'Updated {days[-1]["date"]}  /  github.com/{USER}','#B5A6CD',10)
    (ROOT/'data/contributions.json').write_text(json.dumps({'username':USER,'days':days,'total':total},indent=2)+'\n')
    (ROOT/'contrib-heatmap.svg').write_text(svg(860,266,'Walaa2S GitHub contributions',body))

def card():
    body=text(24,32,'walaa@github:~','#C4B5FD',16)+text(24,60,'────────────────────────────────','#35234D')
    rows=[('Name','Walaa Salah'),('Role','Front-End Developer / UI/UX'),('Study','Informatics Engineering'),('University','University of Technology Bahrain'),('Location','Bahrain'),('',''),('Build','University experiences'),('Explore','AI / Computer Vision / Robotics'),('Stack','React / Next.js / TypeScript'),('Design','Figma / Prototyping / Design Systems'),('Code','Python / Node.js / Flutter'),('',''),('Highlights','Huawei Student Ambassador'),('Lead','UTB Photography Club President')]
    for i,(k,v) in enumerate(rows):
        body+=f'<g class="reveal" style="animation-delay:{i*.09}s">'+text(24,88+i*22,k,'#C4B5FD',12)+text(112,88+i*22,v,size=11.5)+'</g>'
    body+=text(24,422,'Design with purpose. Build with clarity.','#B5A6CD',11)
    (ROOT/'info-card.svg').write_text(svg(490,450,'Walaa Salah profile and skills',body))

def portrait(path):
    from PIL import Image, ImageOps, ImageEnhance
    im=Image.open(path).convert('L'); im=ImageOps.autocontrast(im,cutoff=1)
    im=ImageEnhance.Contrast(im).enhance(1.2).resize((80,45))
    ramp=' .`:-=+*cs#%@';body=text(20,30,'./portrait --ascii','#B5A6CD',12)
    # Existing avatar has a black background: dark pixels become spaces.
    for y in range(im.height):
        line=''.join(ramp[round(im.getpixel((x,y))/255*(len(ramp)-1))] for x in range(im.width))
        body+=f'<defs><clipPath id="r{y}"><rect x="18" y="{58+y*7.7}" width="334" height="9"><animate attributeName="width" from="0" to="334" dur=".18s" begin="{y*.045}s" fill="freeze"/></rect></clipPath></defs>'
        body+=text(18,65+y*7.7,line,'#EDE9FE',6.8,f'clip-path="url(#r{y})" xml:space="preserve" textLength="334" lengthAdjust="spacingAndGlyphs" class="reveal" style="animation-delay:{y*.045}s"')
    body+=text(20,430,'WALAA / DESIGN · CODE · CREATE','#B5A6CD',10)
    (ROOT/'walaa-ascii.svg').write_text(svg(370,450,'ASCII portrait of Walaa from her GitHub avatar',body))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--html');a.add_argument('--portrait');a.add_argument('--card',action='store_true');args=a.parse_args()
    heatmap(args.html)
    if args.card:card()
    if args.portrait:portrait(args.portrait)
