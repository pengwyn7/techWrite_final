from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

MAX_ROWS = 100
PAGE_BG = "#fefcff"
CARD_BG = "#ffffff"
ACCENT_COLOR = "#1B1F3B"  # Bold Midnight Blue
SECONDARY_COLOR = "#FF0054"  # Vivid Magenta
TEXT_COLOR = "#1F1D2B"
PALETTE_BUSH = "#FF9F1C"  # Vibrant Mango
PALETTE_COOL_GRAY = "#2EC4B6"  # Tropical Teal
PALETTE_CLAY = "#FDEADE"  # Soft highlight
PALETTE_VIOLET = "#9D4EDD"  # Electric Violet
COLOR_SEQUENCE = [ACCENT_COLOR, SECONDARY_COLOR, PALETTE_BUSH, PALETTE_COOL_GRAY, PALETTE_VIOLET]
CONTINUOUS_SCALE = [ACCENT_COLOR, SECONDARY_COLOR, PALETTE_BUSH]
BASE_CARD_STYLE = {
    "backgroundColor": CARD_BG,
    "borderRadius": "16px",
    "padding": "28px",
    "boxShadow": "0 12px 28px rgba(19, 59, 69, 0.18)",
}
CHART_CARD_STYLE = dict(BASE_CARD_STYLE, padding="24px")


def theme_figure(fig):
    fig.update_layout(
        template="simple_white",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_COLOR),
        title_font=dict(color=TEXT_COLOR, size=20, family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif"),
        colorway=COLOR_SEQUENCE,
    )
    return fig

# =========================================
# LOAD DATA (FIRST 100 ROWS TO KEEP IT LIGHT)
DATA_PATH = Path(__file__).resolve().parent / "enhanced_student_habits_performance_dataset.csv"

# =========================================
df = pd.read_csv(DATA_PATH).head(MAX_ROWS)

# Create simpler attendance ranges
df['attendance_bucket'] = pd.cut(
    df['attendance_percentage'],
    bins=[0, 70, 85, 95, 100],
    labels=['<70%', '70-85%', '85-95%', '>95%']
)

app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "STUDENT HABITS AND ACADEMIC PERFORMANCE",
                    style={
                        "textAlign": "center",
                        "color": ACCENT_COLOR,
                        "fontSize": "44px",
                        "fontWeight": "800",
                        "letterSpacing": "2px",
                        "marginBottom": "16px",
                    },
                ),
                html.Div(style={"height": "8px"}),
                html.Div(
                    [
                        html.Span(
                            style={
                                "display": "block",
                                "fontWeight": "600",
                                "color": SECONDARY_COLOR,
                                "marginBottom": "12px",
                                "fontSize": "18px",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Gender", style={"color": TEXT_COLOR, "fontWeight": "500"}),
                                        dcc.Dropdown(
                                            id="gender_filter",
                                            options=[{"label": g, "value": g} for g in df["gender"].dropna().unique()],
                                            placeholder="All genders",
                                            clearable=True,
                                            style={"width": "100%"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    [
                                        html.Label("Major", style={"color": TEXT_COLOR, "fontWeight": "500"}),
                                        dcc.Dropdown(
                                            id="major_filter",
                                            options=[{"label": g, "value": g} for g in df["major"].dropna().unique()],
                                            placeholder="All majors",
                                            clearable=True,
                                            style={"width": "100%"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    [
                                        html.Label("Semester", style={"color": TEXT_COLOR, "fontWeight": "500"}),
                                        dcc.Dropdown(
                                            id="semester_filter",
                                            options=[{"label": g, "value": g} for g in df["semester"].dropna().unique()],
                                            placeholder="All semesters",
                                            clearable=True,
                                            style={"width": "100%"},
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "display": "grid",
                                "gap": "16px",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                            },
                        ),
                    ],
                    style=dict(BASE_CARD_STYLE, marginBottom="28px"),
                ),
                html.Div(
                    id="kpi_row",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                        "gap": "28px",
                    },
                ),
                html.Div(
                    [
                        html.Div(dcc.Graph(id="gender_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="attendance_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="study_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="support_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="sleep_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="dropout_chart"), style=CHART_CARD_STYLE),
                        html.Div(dcc.Graph(id="stress_chart"), style=CHART_CARD_STYLE),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
                        "gap": "28px",
                        "marginTop": "36px",
                    },
                ),
            ],
            style={"maxWidth": "1120px", "margin": "0 auto", "padding": "40px 32px"},
        )
    ],
    style={
        "backgroundColor": PAGE_BG,
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "color": TEXT_COLOR,
    },
)


# =========================================
# CALLBACK – UPDATE EVERYTHING
# =========================================
@app.callback(
    [
        Output("kpi_row", "children"),
        Output("gender_chart", "figure"),
        Output("attendance_chart", "figure"),
        Output("study_chart", "figure"),
        Output("support_chart", "figure"),
        Output("sleep_chart", "figure"),
        Output("dropout_chart", "figure"),
        Output("stress_chart", "figure"),
    ],
    [
        Input("gender_filter", "value"),
        Input("major_filter", "value"),
        Input("semester_filter", "value"),
    ]
)
def update_dashboard(gender, major, semester):
    dff = df.copy()

    if gender:
        dff = dff[dff["gender"] == gender]

    if major:
        dff = dff[dff["major"] == major]

    if semester:
        dff = dff[dff["semester"] == semester]

    # =========================================
    # KPIs
    # =========================================
    avg_score = round(dff["exam_score"].mean(), 1)
    avg_study = round(dff["study_hours_per_day"].mean(), 1)
    avg_attendance = round(dff["attendance_percentage"].mean(), 1)
    dropout_rate = round(
        (dff["dropout_risk"].value_counts(normalize=True).get("Yes", 0) * 100), 1
    )

    kpi_cards = [
        html.Div(
            style=dict(BASE_CARD_STYLE, backgroundColor=ACCENT_COLOR, textAlign="center"),
            children=[
                html.Div("Avg Exam Score", style={"fontWeight": "600", "color": PALETTE_CLAY}),
                html.H3(f"{avg_score}", style={"margin": "8px 0 0", "color": "#f7f7ff"}),
            ],
        ),
        html.Div(
            style=dict(BASE_CARD_STYLE, backgroundColor=SECONDARY_COLOR, textAlign="center"),
            children=[
                html.Div("Study Hrs / Day", style={"fontWeight": "600", "color": PALETTE_CLAY}),
                html.H3(f"{avg_study}", style={"margin": "8px 0 0", "color": "#fff"}),
            ],
        ),
        html.Div(
            style=dict(BASE_CARD_STYLE, backgroundColor=PALETTE_BUSH, textAlign="center"),
            children=[
                html.Div("Attendance %", style={"fontWeight": "600", "color": ACCENT_COLOR}),
                html.H3(f"{avg_attendance}%", style={"margin": "8px 0 0", "color": ACCENT_COLOR}),
            ],
        ),
        html.Div(
            style=dict(BASE_CARD_STYLE, backgroundColor=PALETTE_COOL_GRAY, textAlign="center"),
            children=[
                html.Div("Dropout Risk", style={"fontWeight": "600", "color": ACCENT_COLOR}),
                html.H3(f"{dropout_rate}%", style={"margin": "8px 0 0", "color": "#06373a"}),
            ],
        ),
    ]

    # =========================================
    # CHARTS
    # =========================================

    # Gender
    fig_gender = px.pie(
        dff,
        names="gender",
        hole=0.3,
        title="Gender mix of students",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig_gender.update_traces(textinfo="percent+label")
    theme_figure(fig_gender)

    # Attendance
    att = dff.groupby("attendance_bucket")["exam_score"].mean().reset_index()
    fig_attendance = px.bar(
        att,
        x="attendance_bucket",
        y="exam_score",
        title="Attendance vs average exam score",
        text="exam_score"
    )
    fig_attendance.update_traces(marker_color=SECONDARY_COLOR, texttemplate="%{text:.1f}")
    theme_figure(fig_attendance)

    # Study Hours vs Grades
    gender_values = dff["gender"].dropna().unique()
    gender_colors = {
        gender: COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)] for idx, gender in enumerate(gender_values)
    }
    fig_study = px.scatter(
        dff,
        x="study_hours_per_day",
        y="exam_score",
        trendline="ols",
        title="Study time and exam score",
        color="gender",
        color_discrete_map=gender_colors,
    )
    theme_figure(fig_study)

    # Parental Support
    ps = dff.groupby("parental_support_level")["exam_score"].mean().reset_index()
    fig_support = px.bar(
        ps,
        x="parental_support_level",
        y="exam_score",
        title="Family support and exam score",
        text="exam_score",
    )
    fig_support.update_traces(marker_color=PALETTE_BUSH, texttemplate="%{text:.1f}")
    fig_support.update_layout(showlegend=False)
    theme_figure(fig_support)

    # NEW – Sleep vs Score
    fig_sleep = px.scatter(
        dff,
        x="sleep_hours",
        y="exam_score",
        trendline="ols",
        title="Sleep hours and exam score",
        color="stress_level",
        color_continuous_scale=CONTINUOUS_SCALE,
    )
    theme_figure(fig_sleep)

    # NEW – Dropout Risk vs Score
    risk_values = dff["dropout_risk"].dropna().unique()
    risk_colors = {
        risk: COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)] for idx, risk in enumerate(risk_values)
    }
    fig_dropout = px.box(
        dff,
        x="dropout_risk",
        y="exam_score",
        title="Exam score by dropout risk",
        color="dropout_risk",
        color_discrete_map=risk_colors,
    )
    theme_figure(fig_dropout)

    # NEW – Stress Level Impact
    fig_stress = px.scatter(
        dff,
        x="stress_level",
        y="exam_score",
        trendline="ols",
        title="Stress level and exam score",
        color="sleep_hours",
        color_continuous_scale=CONTINUOUS_SCALE,
    )
    theme_figure(fig_stress)

    return (
        kpi_cards,
        fig_gender,
        fig_attendance,
        fig_study,
        fig_support,
        fig_sleep,
        fig_dropout,
        fig_stress
    )


if __name__ == "__main__":
    app.run(debug=True)
