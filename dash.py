import streamlit as st
import datetime
from calendar import monthcalendar
from dateutil.relativedelta import relativedelta

# --- Configurações da Página ---
st.set_page_config(
    page_title="Agendador de Conteúdo - Agrolink",
    page_icon="https://www.agrolink.com.br/images/icons/favicon-32x32-24-v3.png",
    layout="wide"
)

# --- CSS Customizado para replicar o estilo do Google Agenda ---
st.markdown("""
<style>
    /* Esconde o menu hamburger e o footer do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
    }

    /* Estilo para o container de cada dia no calendário */
    .calendar-day {
        border-right: 1px solid #444;
        border-bottom: 1px solid #444;
        border-radius: 0;
        padding: 8px;
        height: 140px; /* Altura fixa para cada célula */
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
        overflow-y: auto; /* Adiciona scroll se o conteúdo passar da altura */
    }

    /* Primeiro dia da semana (Domingo) */
    .calendar-day-first {
        border-left: 1px solid #444;
    }
    /* Primeira semana do mes */
     .calendar-week-first .calendar-day {
        border-top: 1px solid #444;
    }

    /* Estilo para os dias que não pertencem ao mês atual */
    .other-month .day-number {
        color: #666; /* Cor cinza para o número do dia */
    }

    /* Estilo para o número do dia */
    .day-number {
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 8px;
        padding: 4px 8px;
        border-radius: 50%;
        line-height: 1;
        text-align: center;
        min-width: 28px;
    }

    /* Estilo para destacar o dia atual */
    .today .day-number {
        background-color: #1a73e8; /* Azul do Google */
        color: white;
    }

    /* Estilo para os cards de evento */
    .event-card {
        padding: 2px 5px;
        border-radius: 4px;
        margin-bottom: 4px;
        width: 100%;
        font-size: 0.85em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do Estado da Sessão ---
if 'events' not in st.session_state:
    st.session_state.events = []

if 'content_types' not in st.session_state:
    st.session_state.content_types = ["Notícia", "Post Instagram", "Publi", "Reels", "Artigo Blog"]

if 'current_view_date' not in st.session_state:
    # Começa em Agosto do ano atual
    st.session_state.current_view_date = datetime.date(datetime.date.today().year, 8, 1)

# --- Funções Auxiliares ---
def get_color_for_type(content_type):
    hash_val = hash(content_type)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    return f"#{r:02x}{g:02x}{b:02x}"

def change_month(delta):
    st.session_state.current_view_date += relativedelta(months=delta)

def go_to_today():
    st.session_state.current_view_date = datetime.date.today()


# --- Barra Lateral (Sidebar) ---
logo_url = "https://www.agrolink.com.br/images/logos/agrolink-logo-v2.png"
st.sidebar.image(logo_url, use_column_width=True)
st.sidebar.title("Agendador")

with st.sidebar.form("new_event_form", clear_on_submit=True):
    st.subheader("Agendar Conteúdo")
    event_title = st.text_input("Título do Conteúdo:")
    event_date = st.date_input("Data:", value=datetime.date.today())
    event_type = st.selectbox("Formato do Conteúdo:", options=st.session_state.content_types)
    submitted = st.form_submit_button("Salvar Agendamento", use_container_width=True)

    if submitted and event_title:
        st.session_state.events.append({"title": event_title, "date": event_date, "type": event_type})
        st.sidebar.success("Conteúdo agendado!")
    elif submitted:
        st.sidebar.error("Por favor, adicione um título.")

with st.sidebar.expander("Gerenciar Formatos de Conteúdo"):
    with st.form("new_type_form", clear_on_submit=True):
        new_type_name = st.text_input("Nome do Novo Formato:")
        add_type_submitted = st.form_submit_button("Adicionar Formato", use_container_width=True)
        if add_type_submitted and new_type_name and new_type_name not in st.session_state.content_types:
            st.session_state.content_types.append(new_type_name)
            st.success(f"Formato '{new_type_name}' adicionado!")
            st.experimental_rerun()
        elif add_type_submitted:
            st.warning("Formato inválido ou já existente.")

    st.write("Formatos existentes:")
    for content_type in st.session_state.content_types:
        color = get_color_for_type(content_type)
        st.markdown(f"<span style='color:{color}; font-weight: bold;'>●</span> {content_type}", unsafe_allow_html=True)


# --- Calendário Principal ---
month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
view_date = st.session_state.current_view_date

# Cabeçalho de navegação
header_cols = st.columns([1.5, 0.8, 0.4, 0.4, 4])
with header_cols[0]:
    st.title("Agenda")
with header_cols[1]:
    st.button("Hoje", on_click=go_to_today, use_container_width=True)
with header_cols[2]:
    st.button("<", on_click=change_month, args=(-1,), use_container_width=True)
with header_cols[3]:
    st.button(">", on_click=change_month, args=(1,), use_container_width=True)
with header_cols[4]:
    st.subheader(f"{month_names_pt[view_date.month]} de {view_date.year}")

# Dias da semana
week_headers = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
cols = st.columns(7)
for col, header in zip(cols, week_headers):
    col.markdown(f"<div style='text-align: center; font-weight: bold; color: #aaa; margin: 10px 0;'>{header}</div>", unsafe_allow_html=True)

# --- Lógica de Geração da Grade do Calendário ---
today = datetime.date.today()
first_day_of_month = view_date.replace(day=1)
# O calendário do Google começa no Domingo (weekday() == 6).
# Se o primeiro dia do mês não for domingo, voltamos para o último domingo.
start_date = first_day_of_month - datetime.timedelta(days=(first_day_of_month.weekday() + 1) % 7)

# Desenha 6 semanas
for week_num in range(6):
    is_first_week_class = "calendar-week-first" if week_num == 0 else ""
    st.markdown(f"<div class='{is_first_week_class}'>", unsafe_allow_html=True)
    cols = st.columns(7)
    for day_num in range(7):
        current_date = start_date + datetime.timedelta(days=(week_num * 7 + day_num))
        
        with cols[day_num]:
            day_class = "calendar-day"
            if day_num == 0:
                day_class += " calendar-day-first" # Adiciona borda esquerda no domingo
            
            if current_date.month != view_date.month:
                day_class += " other-month"
            
            if current_date == today:
                day_class += " today"

            day_number_html = f"<div class='day-number'>{current_date.day}</div>"
            
            # Busca e exibe eventos para o dia
            events_for_day = sorted([e for e in st.session_state.events if e["date"] == current_date], key=lambda x: x['title'])
            for event in events_for_day:
                event_color = get_color_for_type(event['type'])
                day_number_html += f"""
                <div class="event-card" style="background-color: {event_color}40; border-left: 3px solid {event_color};" title="{event['type']}: {event['title']}">
                    {event['title']}
                </div>
                """
            
            st.markdown(f"<div class='{day_class}'>{day_number_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

