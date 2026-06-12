import streamlit as st
import requests
import time
import base64
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse
from pathlib import Path

st.set_page_config(
    page_title="Kryla Pechinchas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ML_CLIENT_ID     = "1059265064005867"
ML_CLIENT_SECRET = "0EICxKO8e82e7yIclw5tBscSDMP2UWUP"
ETIQUETA_ML      = "krylastore"

CATEGORIAS = {
    "Todos":               None,
    "📱 Celulares":        "MLB1051",
    "💻 Computação":       "MLB1648",
    "🎧 Áudio":            "MLB1144",
    "⚡ Eletrônicos":      "MLB1000",
    "🏠 Eletrodomésticos": "MLB1574",
    "🎮 Games":            "MLB1246",
    "🛋️ Casa":             "MLB5726",
}

def get_b64(filename):
    p = Path(__file__).parent / filename
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

logo_b64 = get_b64("kryla_store1.png")
asa_b64  = get_b64("asafogo.png")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*, *::before, *::after { box-sizing: border-box; font-family: 'Inter', sans-serif !important; }

.stApp { background: linear-gradient(160deg, #fff5ee 0%, #fff0e0 30%, #ffecd6 60%, #fff8f0 100%) !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── navbar ── */
.navbar {
  background: #1a1a2e;
  padding: 0 32px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 999;
  border-bottom: 3px solid #ff6b1a;
}
.nav-logo  { width: 600px; height: auto; object-fit: contain; }
.nav-badge {
  background: #ff6b1a;
  color: #fff;
  padding: 5px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
}

/* ── hero ── */
.hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #2d1500 100%);
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.hero-left { display: flex; align-items: center; gap: 20px; }
.hero-icon { height: 140px; object-fit: contain; filter: drop-shadow(0 0 24px #ff6b1aaa); }
.hero-title { font-size: 28px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -0.5px; }
.hero-title span { color: #ff6b1a; }
.hero-sub   { font-size: 13px; color: #888; margin-top: 5px; }
.hero-stats { display: flex; gap: 28px; }
.hs-num   { font-size: 26px; font-weight: 800; color: #fff; text-align: center; }
.hs-label { font-size: 11px; color: #666; text-align: center; margin-top: 2px; }

/* ── filtros ── */
.filters {
  background: #fff;
  padding: 12px 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  position: sticky;
  top: 64px;
  z-index: 998;
  box-shadow: 0 2px 8px #0001;
}
.fchip {
  padding: 7px 18px;
  border-radius: 999px;
  border: 1.5px solid #e0e0e0;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}
.fchip.active { background: #ff6b1a; color: #fff; border-color: #ff6b1a; }

/* ── grid ── */
.deals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  padding: 24px 32px;
}

/* ── card ── */
.deal-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #ebebeb;
  transition: transform .15s, box-shadow .15s;
  position: relative;
}
.deal-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px #0000001a; }

.card-img-wrap {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: #f9f9f9;
  overflow: hidden;
}
.card-img-wrap img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 12px;
}
.card-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}
.card-disc {
  position: absolute;
  top: 10px; left: 10px;
  background: #ff6b1a;
  color: #fff;
  font-size: 13px; font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
  z-index: 2;
}
.card-hot {
  position: absolute;
  top: 10px; right: 10px;
  background: #fff3ed;
  color: #ff6b1a;
  font-size: 10px; font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #ff6b1a55;
  z-index: 2;
}
.card-body  { padding: 14px; }
.card-title {
  font-size: 13px; font-weight: 600; color: #222;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 36px;
  margin-bottom: 10px;
}
.card-price-now { font-size: 20px; font-weight: 800; color: #1a7d3a; }
.card-price-was { font-size: 12px; color: #bbb; text-decoration: line-through; }
.card-economy   { font-size: 11px; color: #1a7d3a; font-weight: 600; margin-top: 2px; }
.card-store     { font-size: 11px; color: #aaa; margin-top: 8px; }
.card-btn {
  display: block;
  margin: 10px 14px 10px;
  background: #ff6b1a;
  color: #fff !important;
  text-align: center;
  padding: 9px;
  border-radius: 10px;
  font-size: 13px; font-weight: 700;
  text-decoration: none !important;
}
.card-btn:hover { background: #e55a0a; }
.card-link {
  margin: 0 14px 14px;
  background: #fff8f4;
  border: 1px solid #ffe0cc;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 10px;
  color: #ff6b1a;
  font-family: monospace !important;
  word-break: break-all;
}

/* ── empty ── */
.empty {
  text-align: center;
  padding: 80px 20px;
}
.empty .eicon { font-size: 80px; margin-bottom: 16px; }
.empty .emsg  { font-size: 20px; font-weight: 800; color: #444; }
.empty .esub  { font-size: 14px; color: #aaa; margin-top: 8px; }

/* ── streamlit overrides ── */
.stButton > button {
  background: #ff6b1a !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  padding: 10px 28px !important;
  width: 100%;
}
.stButton > button:hover { background: #e55a0a !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_token():
    try:
        r = requests.post("https://api.mercadolibre.com/oauth/token",
            data={"grant_type":"client_credentials",
                  "client_id":ML_CLIENT_ID,"client_secret":ML_CLIENT_SECRET},
            timeout=10)
        r.raise_for_status()
        return r.json().get("access_token")
    except:
        return None

def gerar_link(url):
    p = urlparse(url)
    return urlunparse(p._replace(query=urlencode({"matt_tool":"aff_id","matt_word":ETIQUETA_ML})))

def buscar_ml(cat_id, desc_min, token):
    headers = {"Authorization":f"Bearer {token}"} if token else {}
    try:
        r = requests.get("https://api.mercadolibre.com/sites/MLB/search",
            params={"category":cat_id,"sort":"price_asc","limit":50,"condition":"new"},
            headers=headers, timeout=12)
        r.raise_for_status()
        items = r.json().get("results",[])
    except:
        return []
    out = []
    for item in items:
        preco = item.get("price",0)
        orig  = item.get("original_price") or preco
        if orig <= preco or preco == 0: continue
        desc = round((1-preco/orig)*100)
        if desc < desc_min: continue
        out.append({
            "id":       item.get("id",""),
            "titulo":   item.get("title",""),
            "preco":    preco,
            "original": orig,
            "desconto": desc,
            "economia": round(orig-preco,2),
            "link":     gerar_link(item.get("permalink","")),
            "thumb":    item.get("thumbnail","").replace("I.jpg","O.jpg"),
            "vendedor": item.get("seller",{}).get("nickname",""),
            "hora":     datetime.now().strftime("%H:%M"),
            "cat_nome": "",
        })
    return out

def fmt(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


# ─── ESTADO ────────────────────────────────────────────────
if "deals"    not in st.session_state: st.session_state.deals = []
if "scan"     not in st.session_state: st.session_state.scan  = None
if "cat"      not in st.session_state: st.session_state.cat   = "Todos"
if "desc_min" not in st.session_state: st.session_state.desc_min = 30

deals   = st.session_state.deals
queimas = sum(1 for d in deals if d["desconto"]>=50)
eco     = sum(d["economia"] for d in deals)

# ─── NAVBAR ────────────────────────────────────────────────
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo">'
else:
    logo_html = '<span style="font-size:20px;font-weight:900;color:#fff">KRYLA<span style="color:#ff6b1a">STORE</span></span>'

st.markdown(f"""
<div class="navbar">
  {logo_html}
  <span class="nav-badge">🔥 {len(deals)} pechinchas hoje</span>
</div>""", unsafe_allow_html=True)

# ─── HERO ──────────────────────────────────────────────────
if asa_b64:
    icon_html = f'<img src="data:image/png;base64,{asa_b64}" class="hero-icon">'
else:
    icon_html = '<span style="font-size:64px">🔥</span>'

st.markdown(f"""
<div class="hero">
  <div class="hero-left">
    {icon_html}
    <div>
      <div class="hero-title">Caçador de <span>Pechinchas</span></div>
      <div class="hero-sub">Links <b style="color:#ff6b1a">krylastore</b> gerados automaticamente · Mercado Livre</div>
    </div>
  </div>
  <div class="hero-stats">
    <div><div class="hs-num">{len(deals)}</div><div class="hs-label">Pechinchas</div></div>
    <div><div class="hs-num" style="color:#ff6b1a">{queimas}</div><div class="hs-label">Queimas</div></div>
    <div><div class="hs-num" style="color:#4edd6a">R${eco:,.0f}</div><div class="hs-label">Economia</div></div>
  </div>
</div>""", unsafe_allow_html=True)

# ─── CONTROLES ─────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    buscar = st.button("🔍  Buscar pechinchas agora")
with c2:
    desc_min = st.slider("Desconto mínimo", 10, 70,
                         st.session_state.desc_min, step=5, format="%d%%",
                         label_visibility="collapsed")
    st.session_state.desc_min = desc_min
with c3:
    cat_sel = st.selectbox("Categoria", list(CATEGORIAS.keys()),
                           index=list(CATEGORIAS.keys()).index(st.session_state.cat),
                           label_visibility="collapsed")
    st.session_state.cat = cat_sel

# ─── CHIPS VISUAIS ─────────────────────────────────────────
chips = ""
for nome in CATEGORIAS:
    ativo = "active" if nome == st.session_state.cat else ""
    chips += f'<span class="fchip {ativo}">{nome}</span>'
st.markdown(f'<div class="filters">{chips}</div>', unsafe_allow_html=True)

# ─── BUSCA ─────────────────────────────────────────────────
if buscar:
    token = get_token()
    novos = []
    cats  = {k:v for k,v in CATEGORIAS.items() if k!="Todos" and v}
    prog  = st.progress(0, text="Buscando...")
    ids   = {d["id"] for d in st.session_state.deals}
    for i,(nome,cat_id) in enumerate(cats.items()):
        prog.progress(i/len(cats), text=f"Varrendo {nome}...")
        for d in buscar_ml(cat_id, desc_min, token):
            if d["id"] not in ids:
                d["cat_nome"] = nome
                novos.append(d)
                ids.add(d["id"])
    prog.progress(1.0, text="Concluído!")
    time.sleep(0.3)
    prog.empty()
    st.session_state.deals = novos + st.session_state.deals
    st.session_state.scan  = datetime.now().strftime("%H:%M:%S")
    if novos: st.success(f"✅ {len(novos)} pechinchas encontradas!")
    else:     st.info("Nenhuma pechincha nova agora. Tente em alguns minutos.")
    st.rerun()

# ─── GRID ──────────────────────────────────────────────────
deals = st.session_state.deals
exibir = deals if st.session_state.cat == "Todos" else \
         [d for d in deals if d.get("cat_nome") == st.session_state.cat]

if not deals:
    st.markdown(f"""
    <div class="empty">
      {icon_html.replace('class="hero-icon"','style="height:100px;filter:drop-shadow(0 0 20px #ff6b1a88)"') if asa_b64 else '<div class="eicon">🔥</div>'}
      <div class="emsg">Nenhuma pechincha ainda</div>
      <div class="esub">Clique em <b style="color:#ff6b1a">Buscar pechinchas agora</b> para começar</div>
    </div>""", unsafe_allow_html=True)
else:
    html = '<div class="deals-grid">'
    for d in exibir:
        hot   = '<span class="card-hot">🔥 QUEIMA</span>' if d["desconto"]>=50 else ""
        img   = f'<img src="{d["thumb"]}" onerror="this.style.display=\'none\'">' if d["thumb"] else '<div class="card-placeholder">🛒</div>'
        html += f"""
        <div class="deal-card">
          <div class="card-img-wrap">
            {img}
            <span class="card-disc">-{d["desconto"]}%</span>
            {hot}
          </div>
          <div class="card-body">
            <div class="card-title">{d["titulo"]}</div>
            <div class="card-price-now">{fmt(d["preco"])}</div>
            <div class="card-price-was">{fmt(d["original"])}</div>
            <div class="card-economy">Economia: {fmt(d["economia"])}</div>
            <div class="card-store">🏪 {d["vendedor"]} · ⏱ {d["hora"]}</div>
          </div>
          <a href="{d['link']}" target="_blank" class="card-btn">🛒 Ver oferta no ML</a>
          <div class="card-link">🔗 {d['link']}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    linhas = [f"{d['titulo']} | {fmt(d['preco'])} (-{d['desconto']}%) | {d['link']}" for d in deals]
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.download_button("⬇️ Exportar lista TXT", "\n".join(linhas),
                           f"kryla_{datetime.now().strftime('%Y%m%d_%H%M')}.txt","text/plain")
