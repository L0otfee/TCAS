# -*- coding: utf-8 -*-
import dash
from dash import dcc, html, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# อ่านข้อมูลจากไฟล์ CSV
df = pd.read_csv('/Users/lutfeesalaeh/year4-1/code/AJ.Boat/TCAS/output final.csv')

# สร้าง Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Custom CSS สำหรับสไตล์ Apple-like
app.index_string = '''
<!DOCTYPE html>

<html>
    <head>

        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #e9f4ff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                
                background-image: url('/assets/bg.webp');
                background-repeat: no-repeat;
                background-position: right top;
                background-size: 920px auto;
                background-attachment: fixed;

                margin: 0;
                padding: 0;
            }

            .apple-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .apple-gradient {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.85); /* Slightly transparent */
                backdrop-filter: blur(15px);
                border: none;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }
            .program-card {
                background: rgba(255, 255, 255, 0.85); /* Slightly transparent */
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .program-card:hover {
                transform: translateY(-10px);  /* Increased hover effect */
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);  /* Enhanced shadow */
            }
            .filter-card {
                background: rgba(255, 255, 255, 0.85); /* Slightly transparent */
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 18px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                position: relative;
                z-index: 1;
            }

            /* Fix dropdown z-index */
            .filter-card .dropdown {
                z-index: 9999;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dbc.Container([
        html.Div([
            html.Img(
                src='/assets/logo.svg', 
                style={
                    'width': '230px',
                    'height': '230px',
                    'objectFit': 'contain',
                    'marginRight': '10px'
                }
            ),
          html.Div([
    html.H1(
        'University Guide 2025',
        style={
            'fontSize': '3rem',
            'fontWeight': '700',
            'background': 'linear-gradient(135deg, #1a477f, #764ba2)',
            'backgroundClip': 'text',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'letterSpacing': '-2px',
            'textAlign': 'left',
            'marginTop': '10px',
            'marginBottom': '4px'  # 👈 ลดระยะห่างล่างของ H1
        }
    ),
    html.H4(
        'ค้นหาหลักสูตรในฝันของคุณ | Find Your Dream Program',
        style={
            'fontSize': '1.3rem',
            'color': "#1a477f",
            'fontWeight': '300',
            'marginTop': '0px'  # 👈 ไม่ต้องดันขึ้นอีก
        }
    )
],      
        style={'padding': '30px 0'})  # 👈 padding ด้านบน/ล่างโดยรวม
        ], style={

            'display': 'flex',
            'alignItems': 'center',
            'gap': '20px',
            'backgroundSize': '200px auto'
        }),
        html.Div([
            html.Div(id='quick-stats')
        ], className="mb-5"),
        html.Div([
            html.Div([
                html.H5("🔍 ค้นหาหลักสูตรที่เหมาะกับคุณ", 
                       style={
                           'color': '#1D1D1F',
                           'fontWeight': '600',
                           'fontSize': '1.5rem',
                           'marginBottom': '20px'
                       }),
                dbc.Row([
                    dbc.Col([
                        html.Label('เลือกมหาวิทยาลัย:', 
                                 style={'fontWeight': '500', 'color': '#1D1D1F', 'marginBottom': '8px'}),
                        dcc.Dropdown(
                            id='university-filter',
                            options=[{'label': 'ทั้งหมด', 'value': ''}] + [{'label': u, 'value': u} for u in sorted(df['university_name'].unique())],
                            value=None,
                            placeholder="เลือกมหาวิทยาลัยที่สนใจ",
                            style={
                                'marginBottom': '20px',
                                'fontSize': '1rem',
                                'borderRadius': '5px'
                            }
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label('เลือกสาขา:', 
                                 style={'fontWeight': '500', 'color': '#1D1D1F', 'marginBottom': '8px'}),
                        dcc.Dropdown(
                            id='field-filter',
                            options=[{'label': 'ทั้งหมด', 'value': ''}] + [{'label': f, 'value': f} for f in sorted(df['field'].unique())],
                            value=None,
                            placeholder="เลือกสาขาวิชา",
                            style={'marginBottom': '20px'}
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label('เลือกวิทยาเขต:', 
                                 style={'fontWeight': '500', 'color': '#1D1D1F', 'marginBottom': '8px'}),
                        dcc.Dropdown(
                            id='campus-filter',
                            options=[{'label': 'ทั้งหมด', 'value': ''}] + [{'label': c, 'value': c} for c in sorted(df['วิทยาเขต'].unique()) if pd.notna(c)],
                            value=None,
                            placeholder="เลือกวิทยาเขตที่สนใจ",
                            style={'marginBottom': '20px'}
                        )
                    ], width=4),
                ])
            ], className='filter-card', style={'padding': '30px'})
        ], className='mb-5'),
        html.Div(id='stats-cards'),
        html.Div(id='charts-row'),
        html.H2('ข้อมูลหลักสูตรที่กรองแล้ว', 
               style={
                   'textAlign': 'center',
                   'color': '#1a477f',
                   'fontWeight': '600',
                   'fontSize': '2rem',
                   'marginTop': '50px',
                   'marginBottom': '30px'
               }),
        html.Div(id='program-cards', className='mb-5'),
        # DataTable removed as per user request
    ], style={'padding': '0 20px', 'maxWidth': '1400px', 'margin': '0 auto'})
], style={'minHeight': '100vh'})

def prepare_data_for_display(df_data):
    display_data = df_data.copy()
    if 'university_logo' in display_data.columns:
        def format_logo(x):
            if pd.notna(x) and str(x).strip() != "":
                return "![logo](" + str(x) + ")"
            else:
                return ""
        display_data['university_logo'] = display_data['university_logo'].apply(format_logo)
    return display_data.to_dict('records')

def create_program_cards(filtered_df):
    """สร้าง cards แสดงรายละเอียดโปรแกรม (6 อันแรก) และแต่ละ card คลิกได้"""
    if len(filtered_df) == 0:
        return [dbc.Alert("ไม่พบข้อมูลโปรแกรมที่ตรงกับเงื่อนไขที่เลือก", color="warning")]

    card_count = len(filtered_df.head(64))
    sample_programs = filtered_df.head(64)  # Show first 64 programs for better performance

    cards = [
        dbc.Alert(
            f"พบข้อมูลหลักสูตรที่ตรงกับเงื่อนไขจำนวน {card_count} รายการ",
            className="mb-3",
            style={
                "fontWeight": "500",
                "fontSize": "1.1rem",
                "padding": "10px 16px",
                "borderRadius": "0.5rem",
                "backgroundColor": "rgba(255, 182, 1, 0.08)",  # สี #ffb601 แบบโปร่งใส ~92%
                "color": "#7a5a00",
                "backdropFilter": "blur(8px)",
                "WebkitBackdropFilter": "blur(8px)",  # รองรับ Safari
                "border": "1px solid rgba(255, 182, 1, 0.3)"
            }
        )
    ]

    for idx, program in sample_programs.iterrows():
        tuition_info = str(program.get('ค่าใช้จ่าย', 'ไม่ระบุ'))
        portfolio = str(program.get('รอบ 1 Portfolio', '0'))
        quota = str(program.get('รอบ 2 Quota', '0'))
        admission = str(program.get('รอบ 3 Admission', '0'))
        direct = str(program.get('รอบ 4 Direct Admission', '0'))
        university_name = program.get('university_name', 'ไม่ระบุ')
        course_name = program.get('ชื่อหลักสูตร', 'ไม่ระบุ')
        campus = program.get('วิทยาเขต', 'ไม่ระบุ')
        university_logo = program.get('university_logo', '')
        url = program.get('url', '#')
        card = html.A([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            html.Img(
                                src=university_logo, 
                                style={'width': '80px', 'height': '80px', 'objectFit': 'contain'},
                                className="me-2"
                            ) if university_logo and university_logo.strip() != '' else html.Div(),
                        ], width="auto"),
                        dbc.Col([
                            html.H3(university_name, className="mb-0 text-dark"),

                        ])
                    ], align="center")
                ]),
                dbc.CardBody([
                    html.Div([
                       html.H6("รายละเอียด", className="text-secondary mb-2"),
                    html.Div([
                        html.P([
                            html.Strong("ชื่อหลักสูตร: "), 
                            program.get('ชื่อหลักสูตร', 'ไม่ระบุ')
                        ], className="mb-1"),
                        html.P([
                            html.Strong("ชื่อหลักสูตรภาษาอังกฤษ: "), 
                            program.get('ชื่อหลักสูตรภาษาอังกฤษ', 'ไม่ระบุ')
                        ], className="mb-1"),
                        html.P([
                            html.Strong("ประเภทหลักสูตร: "), 
                            program.get('ประเภทหลักสูตร', 'ไม่ระบุ')
                        ], className="mb-1"),
                        html.P([
                            html.Strong("วิทยาเขต: "), 
                            program.get('วิทยาเขต', 'ไม่ระบุ')
                        ], className="mb-1"),
                    ])
                    ]),
                    html.Div([
                        html.H6("ค่าใช้จ่าย", className="text-secondary mb-2"),
                        html.P(tuition_info, className="text-success font-weight-bold mb-3")
                    ]),
                    html.Div([
                        html.H6("จำนวนรับแต่ละรอบ", className="text-secondary mb-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Small("รอบ 1", className="text-muted d-block"),
                                html.Strong(portfolio, className="text-info")
                            ], width=3),
                            dbc.Col([
                                html.Small("รอบ 2", className="text-muted d-block"),
                                html.Strong(quota, className="text-warning")
                            ], width=3),
                            dbc.Col([
                                html.Small("รอบ 3", className="text-muted d-block"),
                                html.Strong(admission, className="text-success")
                            ], width=3),
                            dbc.Col([
                                html.Small("รอบ 4", className="text-muted d-block"),
                                html.Strong(direct, className="text-danger")
                            ], width=3)
                        ], className="g-2")
                    ])
                ])
            ], className="h-100 shadow-sm program-card", style={
                'background': 'rgba(255,255,255,0.92)',
                'backdropFilter': 'blur(5px)',
                'border': '1px solid rgba(255,255,255,0.15)'
            })
        ], href=url, target="_blank", style={'textDecoration': 'none', 'display': 'block', 'height': '100%'})
        cards.append(dbc.Row([dbc.Col(card, width=12)], className="g-0", style={'marginBottom': '16px'}))
    return cards

# Callback functions
@callback(
    [Output('quick-stats', 'children'),
     Output('stats-cards', 'children'),
     Output('charts-row', 'children'),
     Output('program-cards', 'children'),
     Output('field-filter', 'options'),
     Output('campus-filter', 'options'),
     Output('university-filter', 'options')],
    [Input('field-filter', 'value'),
     Input('university-filter', 'value'),
     Input('campus-filter', 'value')]
)
def update_dashboard(selected_field, selected_university, selected_campus):
    # Filter data based on selections
    filtered_df = df.copy()

    if selected_university and selected_university != '':
        filtered_df = filtered_df[filtered_df['university_name'] == selected_university]

    if selected_field and selected_field != '':
        filtered_df = filtered_df[filtered_df['field'] == selected_field]

    if selected_campus and selected_campus != '':
        filtered_df = filtered_df[filtered_df['วิทยาเขต'] == selected_campus]

    # Update dropdown options based on filtered data
    field_options = [{'label': 'ทั้งหมด', 'value': ''}] + [{'label': f, 'value': f} for f in sorted(filtered_df['field'].unique())]
    campus_options = [{'label': 'ทั้งหมด', 'value': ''}] + [{'label': c, 'value': c} for c in sorted(filtered_df['วิทยาเขต'].unique()) if pd.notna(c)]
    university_options = [{'label': 'ทั้งหมด', 'value': ''}] + [{'label': u, 'value': u} for u in sorted(filtered_df['university_name'].unique())]

    # Calculate filtered statistics
    filtered_total_programs = len(filtered_df)
    filtered_total_universities = filtered_df['university_name'].nunique()

    # Calculate filtered tuition
    try:
        tuition_data = filtered_df['ค่าใช้จ่าย'].str.extract(r'(\d+,\d+)').iloc[:,0].str.replace(',','')
        tuition_numeric = pd.to_numeric(tuition_data, errors='coerce')
        filtered_avg_tuition = tuition_numeric.mean()
        filtered_max_tuition = tuition_numeric.max()
        filtered_min_tuition = tuition_numeric.min()
        if pd.isna(filtered_avg_tuition):
            filtered_avg_tuition = 0
        if pd.isna(filtered_max_tuition):
            filtered_max_tuition = 0
        if pd.isna(filtered_min_tuition):
            filtered_min_tuition = 0
    except:
        filtered_avg_tuition = 0
        filtered_max_tuition = 0
        filtered_min_tuition = 0

    # Calculate filtered quota
    try:
        portfolio_data = pd.to_numeric(filtered_df['รอบ 1 Portfolio'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        quota_data = pd.to_numeric(filtered_df['รอบ 2 Quota'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        admission_data = pd.to_numeric(filtered_df['รอบ 3 Admission'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        direct_data = pd.to_numeric(filtered_df['รอบ 4 Direct Admission'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)

        filtered_total_quota = portfolio_data.sum() + quota_data.sum() + admission_data.sum() + direct_data.sum()

        if pd.isna(filtered_total_quota):
            filtered_total_quota = 0
    except:
        filtered_total_quota = 0

    # Calculate filtered campuses
    filtered_total_campuses = filtered_df['วิทยาเขต'].nunique()

    quick_stats_content = [
        html.Div([
            html.H3(
                "แดชบอร์ดเส้นทางมหาวิทยาลัยของคุณ",
                className="text-center mb-3",
                style={'color': '#2c3e50', 'fontWeight': 'bold'}
            ),
            html.P(
                "การตัดสินใจที่ดีเริ่มต้นจากข้อมูลที่ชัดเจน",
                className="text-center text-muted mb-4"
            ),
            dbc.Row([
                dbc.Col([
                    html.H6(
                        f"฿{filtered_avg_tuition:,.0f}",
                        className="text-warning mb-0",
                        style={'fontSize': '2.3rem', 'fontWeight': 'bold'}
                    ),
                    html.Small("ค่าเล่าเรียนเฉลี่ยต่อภาค", className="text-muted")
                ], width=3, className="text-center"),

                dbc.Col([
                    html.H6(
                        f"฿{filtered_max_tuition:,.0f}",
                        className="text-danger mb-0",
                        style={'fontSize': '2.3rem', 'fontWeight': 'bold'}
                    ),
                    html.Small("ค่าเล่าเรียนสูงสุด", className="text-muted")
                ], width=3, className="text-center"),

                dbc.Col([
                    html.H6(
                        f"฿{filtered_min_tuition:,.0f}",
                        className="text-success mb-0",
                        style={'fontSize': '2.3rem', 'fontWeight': 'bold'}
                    ),
                    html.Small("ค่าเล่าเรียนต่ำสุด", className="text-muted")
                ], width=3, className="text-center"),

                dbc.Col([
                    html.H6(
                        f"{filtered_total_programs:,}",
                        className="text-primary mb-0",
                        style={'fontSize': '2.3rem', 'fontWeight': 'bold'}
                    ),
                    html.Small("หลักสูตรที่สามารถเลือกได้", className="text-muted")
                ], width=3, className="text-center"),
            ], className="g-0")
    ],
    className="p-4",
    style={
        'background': 'rgba(255, 255, 255, 0.7)',     # สีขาวโปร่งใส
        'borderRadius': '15px',
        'color': 'black',
        'marginBottom': '1px',
        'backdropFilter': 'blur(10px)',               # เอฟเฟกต์โปร่งเบลอ
        'WebkitBackdropFilter': 'blur(10px)'          # รองรับ Safari
    })
    ]



    # Adjust card spacing
    stats_cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                html.H4(f"{filtered_total_universities:,d}", className="text-primary"),
                html.P("จำนวนมหาวิทยาลัยทั้งหมด", className="text-muted")
            ], body=True, className="text-center", style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '8px'  # Reduced spacing
            }),
            width=3, style={'paddingLeft': '8px', 'paddingRight': '8px'}
        ),
        dbc.Col(
            dbc.Card([
                html.H4(f"{filtered_df['field'].nunique():,d}", className="text-warning"),
                html.P("สาขาทั้งหมด", className="text-muted")
            ], body=True, className="text-center", style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '8px'  # Reduced spacing
            }),
            width=3, style={'paddingLeft': '8px', 'paddingRight': '8px'}
        ),
        dbc.Col(
            dbc.Card([
                html.H4(f"{filtered_total_campuses:,d}", className="text-success"),
                html.P("วิทยาเขตทั้งหมด", className="text-muted")
            ], body=True, className="text-center", style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '8px'  # Reduced spacing
            }),
            width=3, style={'paddingLeft': '8px', 'paddingRight': '8px'}
        ), dbc.Col(
            dbc.Card([
                html.H4(f"{int(filtered_total_quota):,d}", className="text-info"),
                html.P("จำนวนที่นั่งทั้งหมดที่เปิดรับ", className="text-muted")
            ], body=True, className="text-center", style={
                'background': 'rgba(255,255,255,0.85)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '8px'  # Reduced spacing
            }),
            width=3, style={'paddingLeft': '8px', 'paddingRight': '8px'}
        ),
    ], className="g-2", style={'marginLeft': '0', 'marginRight': '0'})

    # Create filtered charts
    try:
        portfolio_data = pd.to_numeric(filtered_df['รอบ 1 Portfolio'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        quota_data = pd.to_numeric(filtered_df['รอบ 2 Quota'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        admission_data = pd.to_numeric(filtered_df['รอบ 3 Admission'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)
        direct_data = pd.to_numeric(filtered_df['รอบ 4 Direct Admission'].str.extract(r'(\d+)').iloc[:,0], errors='coerce').fillna(0)

        df_admission = pd.DataFrame({
            'รอบ': ['Portfolio', 'Quota', 'Admission', 'Direct'],
            'จำนวนรับ': [
                portfolio_data.sum(),
                quota_data.sum(),
                admission_data.sum(),
                direct_data.sum()
            ]
        })
    except:
        df_admission = pd.DataFrame({
            'รอบ': ['Portfolio', 'Quota', 'Admission', 'Direct'],
            'จำนวนรับ': [0, 0, 0, 0]
        })

    fig_admission = px.bar(
        df_admission, 
        x='รอบ', 
        y='จำนวนรับ', 
        title='จำนวนนักศึกษาที่รับรวมในแต่ละรอบ',
        labels={'จำนวนรับ': 'จำนวนที่รับ (คน)'},
        color_discrete_sequence=['#667eea']
    )
    fig_admission.update_layout(
        title_font=dict(size=20, family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F'),
        xaxis_title_font=dict(size=16, family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F'),
        yaxis_title_font=dict(size=16, family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F')
    )

    if len(filtered_df) > 0:
        university_counts = filtered_df['university_name'].value_counts()
        fig_university = px.pie(
            values=university_counts.values, 
            names=university_counts.index,
            title='สัดส่วนมหาลัยที่เปิดรับ',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
    else:
        fig_university = px.pie(
            values=[1], 
            names=['ไม่มีข้อมูล'], 
            title='สัดส่วนมหาลัยที่เปิดรับ',
            color_discrete_sequence=px.colors.sequential.Plasma
        )

    fig_university.update_layout(
        title_font=dict(size=20, family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif', color='#1D1D1F')
    )
    fig_university.update_traces(marker=dict(colors=['#1E90FF', '#4682B4', '#5F9EA0', '#87CEEB', '#00BFFF', '#6495ED']))

    charts_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_admission)
                ])
            ], style={
                'background': 'rgba(255,255,255,0.65)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '16px'
            })
        ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'}),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_university)
                ])
            ], style={
                'background': 'rgba(255,255,255,0.65)',
                'backdropFilter': 'blur(10px)',
                'border': '1px solid rgba(255,255,255,0.15)',
                'marginBottom': '16px'
            })
        ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'})
    ], className='g-2', style={'marginLeft': '0', 'marginRight': '0'})

    # Create program detail cards
    if selected_field or selected_university or selected_campus:
        program_cards = create_program_cards(filtered_df)
    else:
        program_cards = html.Div()  # Hide program cards if no filter is applied

    # Show charts only if at least one filter is applied
    if selected_field or selected_university or selected_campus:
        charts_row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_admission)
                    ])
                ], style={
                    'background': 'rgba(255,255,255,0.65)',
                    'backdropFilter': 'blur(10px)',
                    'border': '1px solid rgba(255,255,255,0.15)',
                    'marginBottom': '16px'
                })
            ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'}),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_university)
                    ])
                ], style={
                    'background': 'rgba(255,255,255,0.65)',
                    'backdropFilter': 'blur(10px)',
                    'border': '1px solid rgba(255,255,255,0.15)',
                    'marginBottom': '16px'
                })
            ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'})
        ], className='g-2', style={'marginLeft': '0', 'marginRight': '0'})
    else:
        charts_row = html.Div([
            html.P("กรุณาเลือกตัวกรองเพื่อดูข้อมูล", className="text-center text-muted", style={
                'fontSize': '1.2rem',
                'marginTop': '20px'
            })
        ])  # Hide charts if no filter is applied

    # Ensure charts and program cards are displayed when 'ทั้งหมด' is selected in all dropdowns.
    if selected_field == '' and selected_university == '' and selected_campus == '':
        charts_row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_admission)
                    ])
                ], style={
                    'background': 'rgba(255,255,255,0.65)',
                    'backdropFilter': 'blur(10px)',
                    'border': '1px solid rgba(255,255,255,0.15)',
                    'marginBottom': '16px'
                })
            ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'}),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_university)
                    ])
                ], style={
                    'background': 'rgba(255,255,255,0.65)',
                    'backdropFilter': 'blur(10px)',
                    'border': '1px solid rgba(255,255,255,0.15)',
                    'marginBottom': '16px'
                })
            ], width=6, style={'paddingLeft': '8px', 'paddingRight': '8px'})
        ], className='g-2', style={'marginLeft': '0', 'marginRight': '0'})

        program_cards = create_program_cards(filtered_df)

    return quick_stats_content, stats_cards, charts_row, program_cards, field_options, campus_options, university_options

if __name__ == '__main__':
    app.run(debug=True)
