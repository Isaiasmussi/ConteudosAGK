import streamlit as st
import datetime
from calendar import month_name, monthcalendar

# --- Configurações da Página ---
st.set_page_config(
    page_title="Agendador de Conteúdo - Agrolink",
    page_icon="📅",
    layout="wide" # Usar layout 'wide' é melhor para calendários
)

# --- Título e Descrição ---
st.title("📅 Agendador de Conteúdo da Agrolink")
st.markdown("Use este painel para planejar e visualizar o calendário de publicações.")

# --- Inicialização do Estado da Sessão ---
# Usamos o st.session_state para guardar os dados enquanto o app está rodando.
# Isso evita que os dados se percam a cada interação do usuário.

# Inicializa a lista de eventos se ela não existir
if 'events' not in st.session_state:
    st.session_state.events = []

# Inicializa os tipos de conteúdo com alguns exemplos
if 'content_types' not in st.session_state:
    st.session_state.content_types = ["Notícia", "Post Instagram", "Publi", "Reels", "Artigo Blog"]

# --- Funções Auxiliares ---

def get_color_for_type(content_type):
    """Gera uma cor única (mas consistente) para cada tipo de conteúdo para fácil visualização."""
    # Gera um hash do tipo de conteúdo para ter uma cor consistente
    hash_val = hash(content_type)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    return f"#{r:02x}{g:02x}{b:02x}"


# --- Barra Lateral (Sidebar) para Ações ---
st.sidebar.header("🗓️ Ações")

# --- Formulário para Adicionar Novo Conteúdo ---
st.sidebar.subheader("Agendar Novo Conteúdo")
with st.sidebar.form("new_event_form", clear_on_submit=True):
    event_title = st.text_input("Título do Conteúdo:")
    event_date = st.date_input("Data:")
    event_type = st.selectbox(
        "Formato do Conteúdo:",
        options=st.session_state.content_types
    )
    submitted = st.form_submit_button("✅ Salvar Agendamento")

    if submitted:
        if event_title:
            # Adiciona o novo evento à lista no session_state
            st.session_state.events.append({
                "title": event_title,
                "date": event_date,
                "type": event_type
            })
            st.sidebar.success("Conteúdo agendado com sucesso!")
        else:
            st.sidebar.error("Por favor, adicione um título ao conteúdo.")

# --- Formulário para Gerenciar Tipos de Conteúdo ---
st.sidebar.subheader("Gerenciar Formatos")
with st.sidebar.form("new_type_form", clear_on_submit=True):
    new_type_name = st.text_input("Nome do Novo Formato (ex: Vídeo TikTok):")
    add_type_submitted = st.form_submit_button("➕ Adicionar Formato")

    if add_type_submitted:
        if new_type_name and new_type_name not in st.session_state.content_types:
            st.session_state.content_types.append(new_type_name)
            st.sidebar.success(f"Formato '{new_type_name}' adicionado!")
            # Força um rerun para o selectbox de agendamento ser atualizado
            st.experimental_rerun()
        elif not new_type_name:
            st.sidebar.warning("Digite um nome para o novo formato.")
        else:
            st.sidebar.warning(f"O formato '{new_type_name}' já existe.")

# Exibe os tipos de conteúdo atuais
st.sidebar.write("Formatos existentes:")
for content_type in st.session_state.content_types:
    color = get_color_for_type(content_type)
    st.sidebar.markdown(f"<span style='color:{color}; font-weight: bold;'>●</span> {content_type}", unsafe_allow_html=True)


# --- Calendário Principal ---
current_year = datetime.datetime.now().year

# Gera abas para os meses a partir de Agosto até Dezembro
# `month_name` é uma lista do módulo `calendar`, onde o índice 1 é Janeiro, 2 é Fevereiro, etc.
# Usamos `pt_BR` para os nomes dos meses em português.
month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
# Começamos em Agosto (mês 8)
tabs = st.tabs([month_names_pt[i] for i in range(8, 13)])

# Itera sobre os meses de Agosto (8) a Dezembro (12)
for i, month_index in enumerate(range(8, 13)):
    with tabs[i]:
        st.subheader(f"{month_names_pt[month_index]} de {current_year}")

        # Cabeçalho com os dias da semana
        week_headers = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        cols = st.columns(7)
        for col, header in zip(cols, week_headers):
            col.markdown(f"**{header}**")

        # Pega o calendário do mês como uma matriz (semanas x dias)
        cal = monthcalendar(current_year, month_index)

        for week in cal:
            cols = st.columns(7)
            for day_index, day in enumerate(week):
                with cols[day_index]:
                    # Dias que não pertencem ao mês são representados por 0
                    if day == 0:
                        st.write("") # Deixa o espaço em branco
                    else:
                        current_date = datetime.date(current_year, month_index, day)
                        # Escreve o número do dia
                        st.markdown(f"**{day}**")

                        # Filtra os eventos para o dia atual
                        events_for_day = [
                            event for event in st.session_state.events
                            if event["date"] == current_date
                        ]

                        # Exibe os eventos agendados para este dia
                        for event in events_for_day:
                            event_color = get_color_for_type(event['type'])
                            st.markdown(
                                f"""
                                <div style="background-color: {event_color}22; border-left: 5px solid {event_color}; padding: 5px; border-radius: 5px; margin-bottom: 5px;">
                                    <small style="color: {event_color}; font-weight: bold;">{event['type']}</small><br>
                                    {event['title']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


