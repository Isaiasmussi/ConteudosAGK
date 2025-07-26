import streamlit as st
import datetime
from calendar import monthcalendar

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

    /* Estilo para o container de cada dia no calendário */
    .calendar-day {
        border: 1px solid #444; /* Borda para criar a grade */
        border-radius: 8px;
        padding: 10px;
        height: 150px; /* Altura fixa para cada célula */
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
        overflow-y: auto; /* Adiciona scroll se o conteúdo passar da altura */
    }

    /* Estilo para os dias que não pertencem ao mês atual */
    .other-month {
        background-color: #2a2a2a;
    }
    .other-month .day-number {
        color: #666; /* Cor cinza para o número do dia */
    }

    /* Estilo para o número do dia */
    .day-number {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
        padding: 4px 8px;
        border-radius: 50%;
        line-height: 1;
    }

    /* Estilo para destacar o dia atual */
    .today .day-number {
        background-color: #1a73e8; /* Azul do Google */
        color: white;
    }

    /* Estilo para os cards de evento */
    .event-card {
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 5px;
        width: 100%;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do Estado da Sessão ---
if 'events' not in st.session_state:
    st.session_state.events = []

if 'content_types' not in st.session_state:
    st.session_state.content_types = ["Notícia", "Post Instagram", "Publi", "Reels", "Artigo Blog"]

# Guarda o mês e ano que estão sendo visualizados
if 'current_view_date' not in st.session_state:
    # Começa em Agosto do ano atual
    st.session_state.current_view_date = datetime.date(datetime.date.today().year, 8, 1)

# --- Funções Auxiliares ---
def get_color_for_type(content_type):
    """Gera uma cor consistente para cada tipo de conteúdo."""
    hash_val = hash(content_type)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    return f"#{r:02x}{g:02x}{b:02x}"

def change_month(delta):
    """Navega para o mês anterior ou seguinte."""
    current_date = st.session_state.current_view_date
    new_month = current_date.month + delta
    new_year = current_date.year
    if new_month > 12:
        new_month = 1
        new_year += 1
    elif new_month < 1:
        new_month = 12
        new_year -= 1
    st.session_state.current_view_date = datetime.date(new_year, new_month, 1)

def go_to_today():
    """Volta para o mês atual."""
    st.session_state.current_view_date = datetime.date.today()


# --- Barra Lateral (Sidebar) ---
logo_url = "https://www.agrolink.com.br/images/logos/agrolink-logo-v2.png"
st.sidebar.image(logo_url, use_column_width=True)
st.sidebar.title("Agendador")

# Formulário para Adicionar Novo Conteúdo
with st.sidebar.form("new_event_form", clear_on_submit=True):
    st.subheader("Agendar Conteúdo")
    event_title = st.text_input("Título do Conteúdo:")
    event_date = st.date_input("Data:", value=datetime.date.today())
    event_type = st.selectbox(
        "Formato do Conteúdo:",
        options=st.session_state.content_types
    )
    submitted = st.form_submit_button("Salvar Agendamento", use_container_width=True)

    if submitted and event_title:
        st.session_state.events.append({
            "title": event_title,
            "date": event_date,
            "type": event_type
        })
        st.sidebar.success("Conteúdo agendado!")
    elif submitted:
        st.sidebar.error("Por favor, adicione um título.")

# Expander para Gerenciar Tipos de Conteúdo
with st.sidebar.expander("Gerenciar Formatos de Conteúdo"):
    with st.form("new_type_form", clear_on_submit=True):
        new_type_name = st.text_input("Nome do Novo Formato:")
        add_type_submitted = st.form_submit_button("Adicionar Formato", use_container_width=True)

        if add_type_submitted and new_type_name:
            if new_type_name not in st.session_state.content_types:
                st.session_state.content_types.append(new_type_name)
                st.success(f"Formato '{new_type_name}' adicionado!")
                st.experimental_rerun()
            else:
                st.warning(f"O formato '{new_type_name}' já existe.")

    st.write("Formatos existentes:")
    for content_type in st.session_state.content_types:
        color = get_color_for_type(content_type)
        st.markdown(f"<span style='color:{color}; font-weight: bold;'>●</span> {content_type}", unsafe_allow_html=True)


# --- Calendário Principal ---

# Cabeçalho de navegação do calendário
month_names_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
view_date = st.session_state.current_view_date

header_cols = st.columns([1, 2, 1, 4, 1, 1])
with header_cols[0]:
    st.title("Agenda")
with header_cols[1]:
    if st.button("Hoje", on_click=go_to_today):
        pass
with header_cols[2]:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-start; align-items: center; height: 100%;">
            <button onclick="document.getElementById('prev-month').click()" style="background:none; border:none; cursor:pointer;">&lt;</button>
            <button onclick="document.getElementById('next-month').click()" style="background:none; border:none; cursor:pointer;">&gt;</button>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Botões invisíveis para o Streamlit manipular o estado
    if st.button(" ", key="prev-month", on_click=change_month, args=(-1,)):
        pass
    if st.button(" ", key="next-month", on_click=change_month, args=(1,)):
        pass

with header_cols[3]:
    st.subheader(f"{month_names_pt[view_date.month]} de {view_date.year}")


# Cabeçalho com os dias da semana (abreviado)
week_headers = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
cols = st.columns(7)
for col, header in zip(cols, week_headers):
    col.markdown(f"<div style='text-align: center; font-weight: bold;'>{header}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)


# Gera o calendário do mês
cal = monthcalendar(view_date.year, view_date.month)
today = datetime.date.today()

for week in cal:
    cols = st.columns(7)
    for day_index, day in enumerate(week):
        with cols[day_index]:
            # Define as classes CSS para o dia
            day_class = "calendar-day"
            day_number_html = ""

            if day == 0:
                day_class += " other-month" # Dia de outro mês (célula vazia)
            else:
                current_date = datetime.date(view_date.year, view_date.month, day)
                if current_date == today:
                    day_class += " today" # Dia atual

                day_number_html = f"<div class='day-number'>{day}</div>"

                # Filtra os eventos para o dia atual
                events_for_day = sorted(
                    [event for event in st.session_state.events if event["date"] == current_date],
                    key=lambda x: x['title']
                )

                # Exibe os eventos agendados
                for event in events_for_day:
                    event_color = get_color_for_type(event['type'])
                    day_number_html += f"""
                    <div class="event-card" style="background-color: {event_color}40; border-left: 5px solid {event_color};">
                        <small style="color: {event_color}; font-weight: bold;">{event['type']}</small><br>
                        {event['title']}
                    </div>
                    """

            st.markdown(f"<div class='{day_class}'>{day_number_html}</div>", unsafe_allow_html=True)
