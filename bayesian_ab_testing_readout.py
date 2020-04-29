import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from scipy.stats import beta

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        className="title",
        children=["Bayesian AB Testing Calculator"]
    ),
    html.Div(
        className="main",
        children=[
            html.Div(
                className="input",
                children=[
                    html.H2("Enter your inputs here"),
                    html.Div(
                        className="input-container",
                        children=[
                            html.Label('Control sample size'),
                            dcc.Input(id ='ctl_sample',
                                      type ='number',
                                      value=0,
                                      min=0,
                                      debounce=True)
                        ]
                    ),
                    html.Div(
                        className="input-container",
                        children=[
                            html.Label('Control success #'),
                            dcc.Input(id ='ctl_success',
                                      type ='number',
                                      value=0,
                                      min=0,
                                      debounce=True)
                        ]
                    ),
                    html.Div(
                        className="input-container",
                        children=[
                            html.Label('Experiment sample size'),
                            dcc.Input(id ='exp_sample',
                                      type ='number',
                                      value=0,
                                      min=0,
                                      debounce=True)
                        ]
                    ),
                    html.Div(
                        className="input-container",
                        children=[
                            html.Label('Experiment success #'),
                            dcc.Input(id ='exp_success',
                                      type ='number',
                                      value=0,
                                      min=0,
                                      debounce=True)
                        ]
                    ),
                    html.Div(
                        className="input-container",
                        children=[
                            html.Label('Minimum % lift'),
                            dcc.Input(id ='lift',
                                      type ='number',
                                      value=0,
                                      min=-1,
                                      max=1,
                                      debounce=True)
                        ]
                    )
            ]),
            html.Div(
                className='plot',
                children=[
                    dcc.Graph(id='graph'),
                    dcc.Graph(id='graph2')
                ]
            ),
            html.Div(className="conclude",
                children=[
                    html.Div(id="conclude"),
                    html.Div(className="notes",
                        children =["* This calculator assumes uninformative prior beta distribution with α=β=1.",
                            " It uses percent lift as the decision rule.",
                            " In order for either group to declare as winner, the group's percent lift needs to have at least 95% probability of exceeding minimum %lift.",
                            " Although the calculator may suggest a winner before the estimated sample size is collected,",
                            " please understand that there's still risk of terminating the experiment early. Read ",
                            html.A("this",href='http://varianceexplained.org/r/bayesian-ab-testing/'),
                            " article for details."
                        ]
                    )


                ]
                )
        ]
    )
])

@app.callback(Output(component_id='graph',component_property='figure'),
              [Input(component_id='ctl_sample',component_property='value'),
               Input(component_id='ctl_success',component_property='value'),
               Input(component_id='exp_sample',component_property='value'),
               Input(component_id='exp_success',component_property='value')
               ])

def update_beta(ctl_sample,ctl_success,exp_sample,exp_success):
    # make figure
    fig_dict = {
        "data": [],
        "layout":{}
        }
    # control group posterior distri
    a_ctl = ctl_success+1 #prior beta parameter is a=b=1
    b_ctl = ctl_sample - ctl_success + 1
    rv_ctl = beta(a_ctl,b_ctl)
    # generate evenly spaced numbers between 0 and 1, 10 times of the maximum of and b
    x_ctl = np.linspace(0,1,num=10*max(a_ctl,b_ctl))
    y_ctl = rv_ctl.pdf(x_ctl)
    data_ctl = {
        "x":x_ctl,
        "y":y_ctl,
        "fill":'tozerox',
        "mode":"lines",
        "marker":dict(color='FC766A'),
        "name": "Control"
        }
    # experiment group posterior distri
    a_exp = exp_success + 1  # prior beta parameter is a=b=1
    b_exp = exp_sample - exp_success + 1
    rv_exp = beta(a_exp,b_exp)
    # generate evenly spaced numbers between 0 and 1, 10 times of the maximum of and b
    x_exp = np.linspace(0,1,num=10*max(a_exp,b_exp))
    y_exp = rv_exp.pdf(x_exp)
    data_exp = {
        "x":x_exp,
        "y":y_exp,
        "fill":'tozerox',
        "mode":"lines",
        "marker":dict(color='34558b'),
        "name": "Experiment"
        }

    fig_dict["data"]=[data_ctl,data_exp]
    fig_dict["layout"]= dict(
                                title='Posterior pdf of control and experiment\'s binomial parameter p',
                                xaxis=dict(title='p'),
                                yaxis=dict(title='pdf'),
                                hovermode='closest',
                                font=dict(family="Goergia, serif",size=14),
                            )
    return fig_dict

@app.callback([Output(component_id='graph2',component_property='figure'),
               Output(component_id='conclude',component_property='children')],
             [Input(component_id='ctl_sample',component_property='value'),
              Input(component_id='ctl_success',component_property='value'),
              Input(component_id='exp_sample',component_property='value'),
              Input(component_id='exp_success',component_property='value'),
              Input(component_id='lift',component_property='value')
             ]
    )
def update_lift(ctl_sample,ctl_success,exp_sample,exp_success,threshold):
    # control group posterior 100k random variables genration
    a_ctl = ctl_success+1  #prior beta parameter is a=b=1
    b_ctl = ctl_sample-ctl_success+1
    x_ctl = beta.rvs(a=a_ctl, b=b_ctl, size=100000, random_state=1)
    # experiment group posterior 100k random variables generation
    a_exp = exp_success+1  # prior beta parameter is a=b=1
    b_exp = exp_sample-exp_success+1
    x_exp = beta.rvs(a=a_exp, b=b_exp, size=100000, random_state=2)

    x_lift = (x_exp - x_ctl)/x_ctl  ## % lift
    prob = len(x_lift[x_lift> threshold])/len(x_lift) ## prob of %lift exceeding threshold

    distplot = ff.create_distplot([x_lift],
                             ['lift pdf'],
                             bin_size=0.005,
                             show_hist=False,
                             show_rug=False)

    x=list(distplot.data[0]['x']) # tuple to list
    y=distplot.data[0]['y']  # np array

    data = [go.Scatter(x=x,
            y=y,
            mode="lines",
            fill="tozerox",
            line=dict(color='#5F4B8B',shape='spline',smoothing=1.3)
            )]
    layout = go.Layout(title='Probability that lift exceeds '+ str(threshold*100) + '% is ' + str(prob*100)+'%',
                xaxis=dict(title='%lift'),
                yaxis=dict(title='pdf'),
                hovermode='closest',
                font=dict(family="Georgia, serif",size=14),
                template='plotly_white'
                )
    fig = go.Figure(data=data,layout=layout)
    fig.add_shape(
        type='line',
        x0=threshold,
        y0=0,
        x1=threshold,
        y1=y.max()*1.2, # customize vertival line's height
        line=dict(color='black',
              dash="dot"
              )
    )
    fig.add_annotation(
        x=threshold,
        y=y.max()*1.1,
        text="minimum %lift"
        )

    if prob >=0.95:
        conclusion = html.H2([
            html.Span(id="experiment_group", children=["Experiment group"]),
            " is the winner!"
        ])
    elif prob <= 0.05:
        conclusion = html.H2([
            html.Span(id="control_group", children=["Control group"]),
            " is the winner!"
        ])
    else:
        conclusion=html.H2(["The result is inconclusive. Keep running to get more data."])

    return fig, conclusion

# Add the server clause:

if __name__=='__main__':
    app.run_server()
