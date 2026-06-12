import streamlit as st
import requests
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse

# ─── CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="Krylastore · Pechinchas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

ETIQUETA_ML = "krylastore"

CATEGORIAS = {
    "📱 Celulares":       "MLB1051",
    "💻 Computação":      "MLB1648",
    "🎧 Áudio":           "MLB1144",
    "⚡ Eletrônicos":     "MLB1000",
    "🏠 Eletrodomésticos":"MLB1574",
    "🎮 Games":           "MLB1246",
    "🛋️ Casa":            "MLB5726",
}

# ─── ESTILO ────────────────────────────────────────────────
st.markdown("""
<style>
  /* fundo geral */
  .stApp { background: #0f0f0f; }
  [data-testid="stSidebar"] { background: #161616; border-right: 1px solid #222; }

  /* cabeçalho */
  .header-box {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .header-title { font-size: 26px; font-weight: 700; color: #fff; margin: 0; }
  .header-sub   { font-size: 13px; color: #888; margin: 4px 0 0; }

  /* card de produto */
  .deal-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    transition: border-color .2s;
  }
  .deal-card:hover { border-color: #444; }

  /* badges */
  .badge-hot  { background:#3d0f0f; color:#ff6b6b; border:1px solid #5a1a1a;
                padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
  .badge-good { background:#0f2a0f; color:#6bcb77; border:1px solid #1a4a1a;
                padding:3px 10px; border-radius:20px; font-size:12px; }
  .badge-ok   { background:#1a1a0f; color:#ffd166; border:1px solid #3a3a1a;
                padding:3px 10px; border-radius:20px; font-size:12px; }

  /* preços */
  .price-now  { font-size:24px; font-weight:700; color:#6bcb77; }
  .price-was  { font-size:14px; color:#555; text-decoration:line-through; }
  .discount   { background:#ff4444; color:#fff; padding:2px 9px;
                border-radius:20px; font-size:13px; font-weight:700; }

  /* link afiliado */
  .aff-link {
    background:#111;
    border:1px solid #2a2a2a;
    border-radius:8px;
    padding:10px 14px;
    font-family:monospace;
    font-size:11px;
    color:#888;
    word-break:break-all;
    margin-top:10px;
  }
  .aff-link span { color:#6bcb77; }

  /* stat cards */
  .stat-card {
    background:#1a1a1a;
    border:1px solid #2a2a2a;
    border-radius:10px;
    padding:16px 20px;
    text-align:center;
  }
  .stat-num   { font-size:28px; font-weight:700; color:#fff; }
  .stat-label { font-size:12px; color:#666; margin-top:4px; }

  /* botão copiar */
  .stButton button {
    background:#1f3a1f !important;
    color:#6bcb77 !important;
    border:1px solid #2a4a2a !important;
    border-radius:8px !important;
    font-size:12px !important;
    padding:4px 14px !important;
  }
  .stButton button:hover { background:#2a4a2a !important; }

  /* esconde elementos padrão streamlit */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ─── FUNÇÕES ───────────────────────────────────────────────
def gerar_link_afiliado(url: str) -> str:
    parsed = urlparse(url)
    params = {"matt_tool": "aff_id", "matt_word": ETIQUETA_ML}
    return urlunparse(parsed._replace(query=urlencode(params)))


def buscar_ml(categoria_id: str, desconto_min: int, limite: int = 48) -> list:
    try:
        resp = requests.get(
            "https://api.mercadolibre.com/sites/MLB/search",
            params={"category": categoria_id, "sort": "price_asc",
                    "limit": limite, "condition": "new"},
            timeout=12,
        )
        resp.raise_for_status()
        items = resp.json().get("results", [])
    except Exception as e:
        st.sidebar.error(f"Erro API ML: {e}")
        return []

    resultado = []
    for item in items:
        preco     = item.get("price", 0)
        original  = item.get("original_price") or preco
        if original <= preco or preco == 0:
            continue
        desc = round((1 - preco / original) * 100)
        if desc < desconto_min:
            continue

        link_orig = item.get("permalink", "")
        resultado.append({
            "id":        item.get("id", ""),
            "titulo":    item.get("title", ""),
            "preco":     preco,
            "original":  original,
            "desconto":  desc,
            "economia":  round(original - preco, 2),
            "link_orig": link_orig,
            "link_aff":  gerar_link_afiliado(link_orig),
            "thumb":     item.get("thumbnail", "").replace("I.jpg", "O.jpg"),
            "vendedor":  item.get("seller", {}).get("nickname", ""),
            "achado_em": datetime.now().strftime("%H:%M:%S"),
        })
    return resultado


def nivel(desc: int):
    if desc >= 50: return "🔥 Queima total", "badge-hot"
    if desc >= 35: return "⚡ Oferta forte", "badge-good"
    return "💰 Boa oferta", "badge-ok"


# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")

    cats_sel = st.multiselect(
        "Categorias",
        list(CATEGORIAS.keys()),
        default=["📱 Celulares", "🎧 Áudio", "🎮 Games"],
    )

    desc_min = st.slider("Desconto mínimo", 10, 70, 30, step=5,
                         format="%d%%")

    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-varredura", value=False)
    if auto_refresh:
        intervalo = st.select_slider("Intervalo", [1, 2, 5, 10, 15, 30],
                                     value=5, format_func=lambda x: f"{x} min")

    st.markdown("---")
    st.markdown(f"**Etiqueta:** `{ETIQUETA_ML}`")
    st.caption("Links gerados automaticamente com sua etiqueta krylastore")


# ─── HEADER ────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <div style="font-size:36px">🔥</div>
  <div>
    <p class="header-title">Krylastore · Caçador de Pechinchas</p>
    <p class="header-sub">Mercado Livre · Links de afiliado gerados automaticamente</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── ESTADO ────────────────────────────────────────────────
if "deals"       not in st.session_state: st.session_state.deals = []
if "ultima_scan" not in st.session_state: st.session_state.ultima_scan = None
if "total_scan"  not in st.session_state: st.session_state.total_scan = 0


# ─── BOTÃO BUSCAR ──────────────────────────────────────────
col_btn, col_status = st.columns([2, 5])
with col_btn:
    buscar = st.button("🔍 Buscar pechinchas agora", use_container_width=True)

with col_status:
    if st.session_state.ultima_scan:
        st.caption(f"Última varredura: {st.session_state.ultima_scan} · "
                   f"{len(st.session_state.deals)} pechinchas encontradas")


# ─── BUSCA ─────────────────────────────────────────────────
if buscar or (auto_refresh and st.session_state.ultima_scan is None):
    if not cats_sel:
        st.warning("Selecione ao menos uma categoria.")
    else:
        novos = []
        prog  = st.progress(0, text="Iniciando varredura...")
        ids_existentes = {d["id"] for d in st.session_state.deals}

        for i, nome_cat in enumerate(cats_sel):
            cat_id = CATEGORIAS[nome_cat]
            prog.progress((i) / len(cats_sel),
                          text=f"Varrendo {nome_cat}...")
            encontrados = buscar_ml(cat_id, desc_min)
            for d in encontrados:
                if d["id"] not in ids_existentes:
                    novos.append(d)
                    ids_existentes.add(d["id"])

        prog.progress(1.0, text="Concluído!")
        time.sleep(0.5)
        prog.empty()

        st.session_state.deals      = novos + st.session_state.deals
        st.session_state.ultima_scan = datetime.now().strftime("%H:%M:%S")
        st.session_state.total_scan += len(novos)

        if novos:
            st.success(f"✅ {len(novos)} pechinchas novas encontradas!")
        else:
            st.info("Nenhuma pechincha nova neste momento. Tente em alguns minutos.")


# ─── STATS ─────────────────────────────────────────────────
deals = st.session_state.deals
if deals:
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    economia_total = sum(d["economia"] for d in deals)
    queimas        = sum(1 for d in deals if d["desconto"] >= 50)

    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(deals)}</div>'
                    f'<div class="stat-label">Pechinchas hoje</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#ff6b6b">'
                    f'{queimas}</div><div class="stat-label">Queimas totais</div></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#6bcb77">'
                    f'R${economia_total:,.0f}</div>'
                    f'<div class="stat-label">Economia potencial</div></div>',
                    unsafe_allow_html=True)
    with c4:
        maior = max(deals, key=lambda d: d["desconto"])
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#ffd166">'
                    f'-{maior["desconto"]}%</div>'
                    f'<div class="stat-label">Maior desconto</div></div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    # ─── FILTROS ───────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        filtro_nivel = st.selectbox("Filtrar por nível",
            ["Todos", "🔥 Queima total (50%+)",
             "⚡ Oferta forte (35%+)", "💰 Boa oferta"])
    with fc2:
        ordenar = st.selectbox("Ordenar por",
            ["Maior desconto", "Menor preço", "Maior economia", "Mais recente"])
    with fc3:
        busca_texto = st.text_input("🔎 Buscar produto", placeholder="Ex: fone, celular...")

    # aplica filtros
    exibir = deals.copy()
    if filtro_nivel == "🔥 Queima total (50%+)":
        exibir = [d for d in exibir if d["desconto"] >= 50]
    elif filtro_nivel == "⚡ Oferta forte (35%+)":
        exibir = [d for d in exibir if d["desconto"] >= 35]
    if busca_texto:
        exibir = [d for d in exibir
                  if busca_texto.lower() in d["titulo"].lower()]
    if ordenar == "Maior desconto":
        exibir.sort(key=lambda d: d["desconto"], reverse=True)
    elif ordenar == "Menor preço":
        exibir.sort(key=lambda d: d["preco"])
    elif ordenar == "Maior economia":
        exibir.sort(key=lambda d: d["economia"], reverse=True)

    st.caption(f"Mostrando {len(exibir)} de {len(deals)} pechinchas")

    # ─── CARDS ─────────────────────────────────────────────
    for d in exibir:
        rotulo, classe = nivel(d["desconto"])
        economia_fmt   = f"R$ {d['economia']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        preco_fmt      = f"R$ {d['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        orig_fmt       = f"R$ {d['original']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        col_img, col_info = st.columns([1, 4])

        with col_img:
            if d["thumb"]:
                try:
                    st.image(d["thumb"], width=100)
                except:
                    st.markdown("🖼️")

        with col_info:
            st.markdown(
                f'<span class="{classe}">{rotulo}</span> '
                f'&nbsp;<span class="discount">-{d["desconto"]}%</span> '
                f'<span style="font-size:11px;color:#555;margin-left:8px">'
                f'⏱ {d["achado_em"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**{d['titulo']}**")
            st.markdown(
                f'<span class="price-now">{preco_fmt}</span> '
                f'&nbsp;<span class="price-was">{orig_fmt}</span> '
                f'&nbsp;<span style="color:#888;font-size:13px">'
                f'economia de {economia_fmt}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"🏪 {d['vendedor']}")

            st.markdown(
                f'<div class="aff-link">🔗 Seu link: '
                f'<span>{d["link_aff"]}</span></div>',
                unsafe_allow_html=True,
            )

            cb1, cb2 = st.columns([1, 1])
            with cb1:
                st.link_button("🛒 Ver no ML", d["link_aff"],
                               use_container_width=True)
            with cb2:
                if st.button("📋 Copiar link",
                             key=f"cp_{d['id']}",
                             use_container_width=True):
                    st.write(f"`{d['link_aff']}`")

        st.markdown('<hr style="border-color:#222;margin:8px 0">', unsafe_allow_html=True)

    # ─── EXPORTAR ──────────────────────────────────────────
    if exibir:
        st.markdown("---")
        linhas = []
        for d in exibir:
            linhas.append(
                f"{d['titulo']} | R${d['preco']} (-{d['desconto']}%) | {d['link_aff']}"
            )
        st.download_button(
            "⬇️ Exportar lista (TXT)",
            data="\n".join(linhas),
            file_name=f"pechinchas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )

else:
    # estado vazio
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#444">
      <div style="font-size:64px;margin-bottom:16px">🔍</div>
      <div style="font-size:18px;color:#666">Nenhuma pechincha ainda</div>
      <div style="font-size:14px;margin-top:8px">
        Selecione as categorias e clique em <b style="color:#6bcb77">Buscar pechinchas agora</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── AUTO REFRESH ──────────────────────────────────────────
if auto_refresh and st.session_state.ultima_scan:
    time.sleep(intervalo * 60)
    st.rerun()
