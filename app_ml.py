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

def get_logo_b64():
    p = Path(__file__).parent / "KRYLA1.png"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

logo_b64 = get_logo_b64()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; font-family: 'Inter', sans-serif !important; }

/* ── página ── */
.stApp { background: #f5f5f7 !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── navbar ── */
.navbar {
  background: #1a1a2e;
  padding: 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 999;
  border-bottom: 3px solid #ff6b1a;
}
.nav-logo { height: 36px; object-fit: contain; }
.nav-logo-text { font-size: 22px; font-weight: 900; color: #fff; letter-spacing: -1px; }
.nav-logo-text span { color: #ff6b1a; }
.nav-badge {
  background: #ff6b1a;
  color: #fff;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

/* ── hero banner ── */
.hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #2d1b00 100%);
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hero-title { font-size: 28px; font-weight: 900; color: #fff; margin: 0; }
.hero-title span { color: #ff6b1a; }
.hero-sub { font-size: 14px; color: #aaa; margin-top: 6px; }
.hero-stats { display: flex; gap: 24px; }
.hero-stat-num   { font-size: 26px; font-weight: 800; color: #fff; text-align: center; }
.hero-stat-label { font-size: 11px; color: #888; text-align: center; margin-top: 2px; }

/* ── filtros ── */
.filters {
  background: #fff;
  padding: 14px 32px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  position: sticky;
  top: 64px;
  z-index: 998;
  box-shadow: 0 2px 8px #0001;
}
.filter-chip {
  padding: 7px 18px;
  border-radius: 999px;
  border: 1.5px solid #e0e0e0;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #444;
  cursor: pointer;
  transition: all .15s;
  white-space: nowrap;
}
.filter-chip:hover  { border-color: #ff6b1a; color: #ff6b1a; }
.filter-chip.active { background: #ff6b1a; color: #fff; border-color: #ff6b1a; }

/* ── grid de cards ── */
.deals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  padding: 24px 32px;
}

/* ── card individual ── */
.deal-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #ebebeb;
  transition: transform .15s, box-shadow .15s;
  cursor: pointer;
  position: relative;
}
.deal-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px #0000001a;
}

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
.card-img-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52px;
}

.card-discount {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #ff6b1a;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
  z-index: 2;
}
.card-hot {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff3ed;
  color: #ff6b1a;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #ff6b1a44;
  z-index: 2;
}

.card-body { padding: 14px; }
.card-title {
  font-size: 13px;
  font-weight: 600;
  color: #222;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
  min-height: 36px;
}
.card-price-now { font-size: 20px; font-weight: 800; color: #1a7d3a; }
.card-price-was { font-size: 12px; color: #bbb; text-decoration: line-through; }
.card-economy   { font-size: 11px; color: #1a7d3a; font-weight: 600; margin-top: 2px; }
.card-store     { font-size: 11px; color: #999; margin-top: 8px; }

.card-btn {
  display: block;
  margin: 12px 14px 14px;
  background: #ff6b1a;
  color: #fff !important;
  text-align: center;
  padding: 9px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none !important;
}
.card-btn:hover { background: #e55a0a; }

.card-link-box {
  margin: 0 14px 14px;
  background: #fff8f4;
  border: 1px solid #ffe0cc;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 10px;
  color: #ff6b1a;
  font-family: monospace !important;
  word-break: break-all;
}

/* ── empty state ── */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #bbb;
}
.empty-state .icon { font-size: 72px; margin-bottom: 16px; }
.empty-state .msg  { font-size: 18px; font-weight: 700; color: #555; }
.empty-state .sub  { font-size: 14px; margin-top: 8px; }

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
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_token():
    try:
        r = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={"grant_type":"client_credentials",
                  "client_id":ML_CLIENT_ID,
                  "client_secret":ML_CLIENT_SECRET},
            timeout=10)
        r.raise_for_status()
        return r.json().get("access_token")
    except:
        return None

def gerar_link(url):
    p = urlparse(url)
    return urlunparse(p._replace(query=urlencode({"matt_tool":"aff_id","matt_word":ETIQUETA_ML})))

def buscar_ml(cat_id, desconto_min, token):
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
        desc = round((1 - preco/orig)*100)
        if desc < desconto_min: continue
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
        })
    return out

def fmt(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


# ─── ESTADO ────────────────────────────────────────────────
if "deals"    not in st.session_state: st.session_state.deals = []
if "scan"     not in st.session_state: st.session_state.scan  = None
if "cat_ativa" not in st.session_state: st.session_state.cat_ativa = "Todos"
if "desc_min" not in st.session_state: st.session_state.desc_min = 30


# ─── NAVBAR ────────────────────────────────────────────────
if logo_b64:
    st.markdown(f"""
    <div class="navbar">
      <img src="data:image/png;base64,{logo_b64}" class="nav-logo">
      <span class="nav-badge">🔥 {len(st.session_state.deals)} pechinchas</span>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="navbar">
      <span class="nav-logo-text">KRYLA<span>STORE</span></span>
      <span class="nav-badge">🔥 {len(st.session_state.deals)} pechinchas</span>
    </div>""", unsafe_allow_html=True)


# ─── HERO ──────────────────────────────────────────────────
deals = st.session_state.deals
queimas = sum(1 for d in deals if d["desconto"]>=50)
eco     = sum(d["economia"] for d in deals)

st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">Caçador de <span>Pechinchas</span></div>
    <div class="hero-sub">Links de afiliado <b style="color:#ff6b1a">krylastore</b> gerados automaticamente · Mercado Livre</div>
  </div>
  <div class="hero-stats">
    <div>
      <div class="hero-stat-num">{len(deals)}</div>
      <div class="hero-stat-label">Pechinchas</div>
    </div>
    <div>
      <div class="hero-stat-num" style="color:#ff6b1a">{queimas}</div>
      <div class="hero-stat-label">Queimas</div>
    </div>
    <div>
      <div class="hero-stat-num" style="color:#4edd6a">R${eco:,.0f}</div>
      <div class="hero-stat-label">Economia</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ─── CONTROLES ─────────────────────────────────────────────
col_buscar, col_desc = st.columns([2, 2])
with col_buscar:
    buscar = st.button("🔍  Buscar pechinchas agora")
with col_desc:
    desc_min = st.slider("Desconto mínimo", 10, 70,
                         st.session_state.desc_min, step=5, format="%d%%",
                         label_visibility="collapsed")
    st.session_state.desc_min = desc_min


# ─── FILTROS POR CATEGORIA (chips) ─────────────────────────
chips_html = '<div class="filters">'
for nome in CATEGORIAS:
    ativo = "active" if nome == st.session_state.cat_ativa else ""
    chips_html += f'<span class="filter-chip {ativo}" onclick="">{nome}</span>'
chips_html += "</div>"
st.markdown(chips_html, unsafe_allow_html=True)

# selectbox invisível para filtrar (workaround streamlit)
cat_sel = st.selectbox("cat", list(CATEGORIAS.keys()),
                       index=list(CATEGORIAS.keys()).index(st.session_state.cat_ativa),
                       label_visibility="collapsed")
st.session_state.cat_ativa = cat_sel


# ─── BUSCA ─────────────────────────────────────────────────
if buscar:
    token = get_token()
    novos = []
    cats_buscar = {k:v for k,v in CATEGORIAS.items() if k!="Todos" and v}
    prog  = st.progress(0, text="Buscando pechinchas...")
    ids   = {d["id"] for d in st.session_state.deals}
    for i,(nome,cat_id) in enumerate(cats_buscar.items()):
        prog.progress(i/len(cats_buscar), text=f"Varrendo {nome}...")
        for d in buscar_ml(cat_id, desc_min, token):
            if d["id"] not in ids:
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


# ─── GRID DE CARDS ─────────────────────────────────────────
deals = st.session_state.deals

# filtra por categoria
if st.session_state.cat_ativa != "Todos":
    exibir = [d for d in deals if d.get("cat") == st.session_state.cat_ativa]
else:
    exibir = deals

if not exibir and not deals:
    st.markdown("""
    <div class="empty-state">
      <div class="icon">🔥</div>
      <div class="msg">Nenhuma pechincha ainda</div>
      <div class="sub">Clique em <b style="color:#ff6b1a">Buscar pechinchas agora</b> para começar</div>
    </div>""", unsafe_allow_html=True)
else:
    # monta HTML do grid inteiro
    cards_html = '<div class="deals-grid">'
    for d in (exibir or deals):
        hot_badge = '<span class="card-hot">🔥 QUEIMA</span>' if d["desconto"]>=50 else ""
        if d["thumb"]:
            img_html = f'<img src="{d["thumb"]}" onerror="this.style.display=\'none\'">'
        else:
            img_html = '<div class="card-img-placeholder">🛒</div>'

        economia_fmt = fmt(d["economia"])
        cards_html += f"""
        <div class="deal-card">
          <div class="card-img-wrap">
            {img_html}
            <span class="card-discount">-{d["desconto"]}%</span>
            {hot_badge}
          </div>
          <div class="card-body">
            <div class="card-title">{d["titulo"]}</div>
            <div class="card-price-now">{fmt(d["preco"])}</div>
            <div class="card-price-was">{fmt(d["original"])}</div>
            <div class="card-economy">Economia: {economia_fmt}</div>
            <div class="card-store">🏪 {d["vendedor"]} · ⏱ {d["hora"]}</div>
          </div>
          <a href="{d['link']}" target="_blank" class="card-btn">🛒 Ver oferta no ML</a>
          <div class="card-link-box">🔗 {d["link"]}</div>
        </div>"""
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    # exportar
    if deals:
        st.markdown("---")
        linhas = [f"{d['titulo']} | {fmt(d['preco'])} (-{d['desconto']}%) | {d['link']}" for d in deals]
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.download_button("⬇️ Exportar lista TXT", "\n".join(linhas),
                               f"kryla_{datetime.now().strftime('%Y%m%d_%H%M')}.txt","text/plain")
