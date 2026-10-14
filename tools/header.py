import re,glob,os,sys
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','public')
MARK='<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="fvmark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2bc4a8"/><stop offset="1" stop-color="#0f766e"/></linearGradient></defs><rect width="40" height="40" rx="11" fill="url(#fvmark)"/><path d="M10.5 21.5l6.5 6.5L30 13.5" fill="none" stroke="#fff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
DOWN='<svg class="ic-down" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
BURGER='<svg class="ic-burger" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

AT_MAIN=[('at/kreditkarten/','Kreditkarten'),('at/kreditkarten/bestenlisten/','Bestenlisten'),('at/ratgeber/','Ratgeber'),('at/kreditkarten/anbieter/','Anbieter'),('at/rechner/','Rechner')]
AT_MORE=[('at/kreditkarten/business/','Business-Kreditkarten'),('at/kreditkarten/methodik/','So bewerten wir'),('at/','Übersicht Österreich')]
DE_MAIN=[('de/kreditkarten/','Kreditkarten'),('de/kreditkarten/bestenlisten/','Bestenlisten'),('de/ratgeber/','Ratgeber'),('de/kreditkarten/anbieter/','Anbieter'),('de/rechner/','Rechner')]
DE_MORE=[('de/kreditkarten/business/','Business-Kreditkarten'),('de/kreditkarten/methodik/','So bewerten wir'),('de/','Übersicht Deutschland')]
INFO=[('ueber-uns/','Über uns'),('so-verdienen-wir-geld/','So verdienen wir Geld')]

def active(rel, items):
    # longest matching prefix wins; card pages fall under Kreditkarten
    best=None
    for h,_ in items:
        h=h.split('?')[0]
        if rel==h or (rel.startswith(h) and h not in ('at/','de/')):
            if best is None or len(h)>len(best): best=h
    return best

FA='<svg class="flag" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#c8102e"/><rect y="6.67" width="30" height="6.67" fill="#fff"/></svg>'
FD='<svg class="flag" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="6.67" fill="#000"/><rect y="6.67" width="30" height="6.67" fill="#dd0000"/><rect y="13.33" width="30" height="6.67" fill="#ffce00"/></svg>'
def build(rel, P, land):
    land=land.replace('title="Österreich">AT</a>','title="Österreich">'+FA+'AT</a>').replace('title="Deutschland">DE</a>','title="Deutschland">'+FD+'DE</a>')
    de = rel.startswith('de/')
    main, more = (DE_MAIN, DE_MORE) if de else (AT_MAIN, AT_MORE)
    cur = active(rel, main+more+INFO)
    def a(h,t,cls=''):
        ac=' aria-current="page"' if h.split('?')[0]==cur else ''
        c=f' class="{cls}"' if cls else ''
        return f'<a{c} href="{P}{h}"{ac}>{t}</a>'
    nav=''.join(a(h,t) for h,t in main)
    pop=''.join(a(h,t,'m-main') for h,t in main)+''.join(a(h,t) for h,t in more)
    pop+='<span class="lbl">Finvallo</span>'+''.join(a(h,t) for h,t in INFO)
    return (f'<a class="skip" href="#app">Zum Inhalt springen</a><header class="hdr"><div class="wrap">\n'
            f'<a class="brand" href="{P or "./"}" aria-label="finvallo – zur Startseite">{MARK}<b>fin<span>vallo</span></b></a>\n'
            f'<nav class="nav" aria-label="Hauptmenü">{nav}</nav>\n{land}\n'
            f'<details class="menu"><summary aria-label="Menü öffnen"><span class="m-more">Mehr</span>{DOWN}{BURGER}</summary>'
            f'<nav class="menu-pop" aria-label="Menü">{pop}</nav></details></div></header>')

def land_default(P):
    return (f'<div class="land" role="group" aria-label="Land wählen"><a href="{P}at/" hreflang="de-AT" aria-current="false" title="Österreich">AT</a>'
            f'<a href="{P}de/" hreflang="de-DE" aria-current="false" title="Deutschland">DE</a></div>')

def run():
  for f in sorted(glob.glob(ROOT+'/**/*.html',recursive=True)):
      relf=os.path.relpath(f,ROOT)
      s=open(f).read()
      if relf=='404.html': rel='404/'; P='/'
      else:
          rel=os.path.dirname(relf); rel=rel+'/' if rel else ''
          P='../'*rel.count('/')
      m=re.search(r'<a class="skip".*?</header>',s,re.S)
      if m:
          lm=re.search(r'<div class="land".*?</div>',m.group(0),re.S)
          land=lm.group(0) if lm else land_default(P)
          s=s[:m.start()]+build(rel,P,land)+s[m.end():]
      else:
          s=s.replace('<body>\n','<body>\n'+build(rel,P,land_default(P))+'\n',1)
      open(f,'w').write(s)
      print('ok',relf)

if __name__=='__main__': run()
