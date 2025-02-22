# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 11:26:04 2019

@author: Nicolas
"""
from operator import attrgetter
import hltvRankingAnalysis as hl
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

b = hl.HLTVTopsList.getObjectFromFile("data.json")
b.fromFile("data.json")
#b.update()
#b.save("data.json")
(s,e) = b.getDate()
listTPC = {'Teams':b.getTeams(),'Players':b.getPlayers(),'Countries':b.getCountries()}


app = dash.Dash(__name__)
app.title = "HLTV Ranking Stats"
server = app.server


app.layout = html.Div(children=[
    html.Div(["Hide menu"],id="menuArrow",n_clicks=0),
    html.Div([
        html.Div('?',
                        id='help'),
        dcc.Input(
                id="nbPlayerCountries",
        value=1,
        type="number",
        min = 1,
        step = 1,
        max = 5,
        disabled = True),
        dcc.RadioItems(
                id = 'radioTrack',
                className = 'radioTrack',
                options=[
                    {'label': 'Teams', 'value': 'Teams'},
                    {'label': 'Players', 'value': 'Players'},
                    {'label': 'Countries', 'value': 'Countries'}
                ],
                value='Teams',
                labelClassName='labelR'),
        dcc.Dropdown(
                id = 'dropdown',
                options=[],
                value=['Astralis'],
                multi=True),
            
    ],id = 'menuSelector'),
     html.Div([html.P("You can select between 3 filters : Teams, Players, or Countries."),
                          html.P("Teams : Displays the team's ranking"),
                           html.P("Players : Displays the ranking of the player's team"),
                           html.P("Countries : Displays the ranking of the best team in the country. You can filter the teams by the minimum number of players from the same country.")],id='toolTipHelp'),
    html.Div(["Show info"],id="detailArrow",n_clicks=0),
    html.Div([html.Div([html.P("Date"),html.P("Team"),html.P("Rank"),html.P("Points"),html.P("HLTV Link"),html.Div([html.P("Players")],className="playerList")],className="Column1"),
             html.Div([html.P(id="date"), html.P(id="team"),html.P(id="pos"),html.P(id="points"),html.P(id="link"),html.Div([html.P(id="player1"),html.P(id="player2"),html.P(id="player3"),html.P(id="player4"),html.P(id="player5")],className="playerList")],className="Column2")
               
     ],id='graphDetail'),
    html.Div([
    dcc.Graph(
        id='graph1',
        config={'displaylogo': False}
    )]),
    html.Div([
    dcc.Graph(
        id='graph2',
        config={'displaylogo': False}
    )]),
          
 html.Div([html.P(str(len(b.tops)) + " ranking (last "+ e + ")")],id='toolDetail')
],id="app-body")
     
@app.callback(
    [Output('dropdown', 'options'),Output('dropdown', 'value'),Output('dropdown', 'placeholder'),Output('nbPlayerCountries', 'disabled'),Output('nbPlayerCountries', 'style'),Output('app-body', 'style')],
    [Input('radioTrack', 'value')])
def show_type_dropdown(name):
    if(name == "Teams"):
        placeholder = "Select teams"
        value = "Astralis"
        disabled = True
        style = {"font-weight":"100"}
    elif(name == "Players"):
        placeholder = "Select players"
        value = "s1mple"
        disabled = True
        style = {"font-weight":"100"}
    elif(name == "Countries"):
        placeholder = "Select countries"
        value = "France"
        disabled = False
        style = {"font-weight":"bold"}
     
    return [{'label': i, 'value': i} for i in listTPC[name]],[value],placeholder,disabled,style,{'opacity':1}

@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown', 'value'),Input('radioTrack', 'value'),Input('nbPlayerCountries', 'value')])
def update_figure(selected,name,nbPCountries):
    trace = []
    if name == "Players":
        for i in selected:
            dataBrut = b.trackPlayer(i)
            x = [x[0] for x in dataBrut]
            y = [x[1].pos if x[1] is not None else x[1] for x in dataBrut]
            point = [x[1].points if x[1] is not None else x[1] for x in dataBrut]
            team = [x[1].team.name  if x[1] is not None else x[1] for x in dataBrut]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'mode' :'lines+markers',
                          'marker' : {'opacity':0},
                          'selected':{'marker': {'opacity':1,'size':12}},
                          'text': ['<br><b>Point </b>: {}<br><b>Team </b>: {}'.format(i,j) for (i,j) in zip(point,team)],
                          'hovertemplate' :    '<br><b>Rank </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                                             
        
                        'showlegend':True})

    elif name == "Teams":
        for i in selected:
            dataBrut = b.trackTeam(i)
            x = [x[0] for x in dataBrut]
            y = [x[1].pos if x[1] is not None else x[1] for x in dataBrut]
            point = [x[1].points if x[1] is not None else x[1] for x in dataBrut]
            team = [x[1].team.name  if x[1] is not None else x[1] for x in dataBrut]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'mode' :'lines+markers',
                           'marker' : {'opacity':0},
                           'selected':{'marker': {'opacity':1,'size':12}},
                          'text': ['<br><b>Point </b>: {}<br><b>Team </b>: {}'.format(i,j) for (i,j) in zip(point,team)],
                          'hovertemplate' :    '<br><b>Rank </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                        'showlegend':True})
    elif name == "Countries":
        for i in selected: 
            dataBrut = b.trackCountry(i,nbPCountries)
            x = [x[0] for x in dataBrut]
            y = [min(d, key=attrgetter('pos')).pos if d is not None else d for d in [x[1] for x in dataBrut]]
            point = [min(d, key=attrgetter('pos')).points if d is not None else d for d in [x[1] for x in dataBrut]]
            team = [min(d, key=attrgetter('pos')).team.name if d is not None else d for d in [x[1] for x in dataBrut]]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'mode' :'lines+markers',
                           'marker' : {'opacity':0},
                           'selected':{'marker': {'opacity':1,'size':12}},
                          'text': ['<br><b>Point </b>: {}<br><b>Team </b>: {}'.format(i,j) for (i,j) in zip(point,team)],
                          'hovertemplate' :    '<br><b>Rank </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                        'showlegend':True})
            
        
    return {"data": trace,
            'layout': {
                    'clickmode': 'event+select',
                    'height':600,
                   'paper_bgcolor' : 'rgba(0,0,0,0)',
                    'plot_bgcolor':'rgba(0,0,0,0)',
                    'font': {'size':14,'color':'#ffffff'},
                    'title':'Team Ranking versus Time',
                     'automargin':True,
                 'yaxis': {'range' : [30,0], 'title': 'Rank', 'tickmode' : 'array','tickvals' : [1, 5, 10, 15, 20, 25,30]},
                 'xaxis': {'rangeselector': { 'buttons':[
                                                  {'count':3,
                                                  'label':'3m',
                                                  'step':'month',
                                                  'stepmode':'backward',
                                                  },
                                                  {'count':6,
                                                  'label':'6m',
                                                  'step':'month',
                                                  'stepmode':'backward'},
                                                   {'count':12,
                                                  'label':'12m',
                                                  'step':'month',
                                                  'stepmode':'backward'},
                                                   {'step':'all'}],'y':1.05},
                            'rangeslider':{
                                'visible': True
                            },
                                     'showgrid':False,
                            'type':'date',
                            'tickformatstops': [{
                                    'enabled':'true',
                                    'dtickrange': [0, 864000000.0],
                                    'value': '%b %d'
                                }
                            ]
                },
                'legend':{'orientation':'h', 'x':0,'y':-0.5},
              
                            
            }}

@app.callback(
    Output('graph2', 'figure'),
    [Input('dropdown', 'value'),Input('radioTrack', 'value'),Input('nbPlayerCountries', 'value')])
def update_figure2(selected,name,nbPCountries):
    trace = []
    if name == "Players":
        for i in selected:
            dataBrut = b.trackPlayer(i)
            x = [x[0] for x in dataBrut]
            rank = [x[1].pos if x[1] is not None else x[1] for x in dataBrut]
            point = [x[1].points if x[1] is not None else 0 for x in dataBrut]
            y = [sum(list(map(int, filter(None,point[0:x])))) for x in range(1,len(point))]
            team = [x[1].team.name  if x[1] is not None else None for x in dataBrut]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'fill':'tozeroy',
                          'mode' :'lines+markers',
                          'marker' : {'opacity':0},
                          'selected':{'marker': {'opacity':1,'size':12}},
                           'text': ['<br><b>Point </b>: + {} (#{})<br><b>Team </b>: {}'.format(i,j,k) for (i,j,k) in zip(point,rank,team)],
                          'hovertemplate' :    '<br><b>Total points </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                        'showlegend':True})

    elif name == "Teams":
        for i in selected:
            dataBrut = b.trackTeam(i)
            x = [x[0] for x in dataBrut]
            rank = [x[1].pos if x[1] is not None else x[1] for x in dataBrut]
            point = [x[1].points if x[1] is not None else 0 for x in dataBrut]
            y = [sum(list(map(int, filter(None,point[0:x])))) for x in range(1,len(point))]
            team = [x[1].team.name  if x[1] is not None else None for x in dataBrut]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'fill':'tozeroy',
                          'mode' :'lines+markers',
                          'marker' : {'opacity':0},
                          'selected':{'marker': {'opacity':1,'size':12}},
                          'text': ['<br><b>Point </b>: + {} (#{})<br><b>Team </b>: {}'.format(i,j,k) for (i,j,k) in zip(point,rank,team)],
                          'hovertemplate' :    '<br><b>Total points </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                        'showlegend':True})
                                
    elif name == "Countries":
        for i in selected: 
            dataBrut = b.trackCountry(i,nbPCountries)
            x = [x[0] for x in dataBrut]
            rank = [min(d, key=attrgetter('pos')).pos if d is not None else d for d in [x[1] for x in dataBrut]]
            point = [min(d, key=attrgetter('pos')).points if d is not None else None for d in [x[1] for x in dataBrut]]
            y = [sum(list(map(int, filter(None,point[0:x])))) for x in range(1,len(point))]
            team = [min(d, key=attrgetter('pos')).team.name if d is not None else None for d in [x[1] for x in dataBrut]]
            trace.append({'x':x, 
                          'y':y,
                          'name': i,
                          'fill':'tozeroy',
                          'mode' :'lines+markers',
                          'marker' : {'opacity':0},
                          'selected':{'marker': {'opacity':1,'size':12}},
                           'text': ['<br><b>Point </b>: + {} (#{})<br><b>Team </b>: {}'.format(i,j,k) for (i,j,k) in zip(point,rank,team)],
                          'hovertemplate' :    '<br><b>Total points </b>: %{y}'
                                              '%{text}<br>Click to show more<extra></extra>',
                        'showlegend':True})
            
        
    return {"data": trace,
            'layout': {
                     'clickmode': 'event+select',
                    'height':600,
                   'paper_bgcolor' : 'rgba(0,0,0,0)',
                    'plot_bgcolor':'rgba(0,0,0,0)',
                    'font': {'size':14,'color':'#ffffff'},
                    'title':'Cumulated Points versus Time',
                     'automargin':True,
                 'yaxis': {'title': 'Cumulated points'},
                 'xaxis': {'rangeselector': { 'buttons':[
                                                  {'count':3,
                                                  'label':'3m',
                                                  'step':'month',
                                                  'stepmode':'backward',
                                                  },
                                                  {'count':6,
                                                  'label':'6m',
                                                  'step':'month',
                                                  'stepmode':'backward'},
                                                   {'count':12,
                                                  'label':'12m',
                                                  'step':'month',
                                                  'stepmode':'backward'},
                                                   {'step':'all'}],'y':1.05},
                            'rangeslider':{
                                'visible': True
                            },
                                     'showgrid':False,
                            'type':'date',
                            'tickformatstops': [{
                                    'enabled':'true',
                                    'dtickrange': [0, 864000000.0],
                                    'value': '%b %d'
                                }
                            ]
                },
                'legend':{'orientation':'h', 'x':0,'y':-0.5},
              
                            
            }}





@app.callback(
    [Output('menuSelector', 'style'),Output('menuArrow', 'style'),Output('menuArrow', 'children')],[Input('menuArrow', 'n_clicks')])
def menu_toggle(n_clicks):
    if  n_clicks is not None and n_clicks % 2 == 1:
        return {'transform': 'translateY(-100%)'},{'top': '0'},"Show menu"
    else:
        return {'transform': 'translateY(0%)'},{'top': '130px'},"Hide menu"
    
    
@app.callback(
    [Output('toolTipHelp', 'style'),Output('help', 'style')],[Input('help', 'n_clicks')])
def help_toggle(n_clicks):
    if  n_clicks is not None and n_clicks % 2 == 1:
        return {'transform': 'translateY(0%)'},{'color': '#ed213a','border-color':'#ed213a'}
    else:
        return {'transform': 'translateX(150%)'},{'color': 'white','border-color':'white'}

@app.callback(
    [Output('graphDetail', 'style'),Output('detailArrow', 'style'),Output('detailArrow', 'children')],
    [Input('detailArrow', 'n_clicks')])
def detail_toggle(n_clicks):
    if n_clicks % 2 == 1:
        style1 = {'transform':'translateX(100%)'}
        style2 = {'right':0}
        text = "Show info"
    else:
        style1 = {'transform':'translateX(0%)'}
        style2 = {'right':'20%'}
        text = "Hide info"
    return style1,style2,text

@app.callback(
    [Output('date', 'children'),Output('team', 'children'),Output('pos', 'children'),Output('points', 'children'),Output('link', 'children'),Output('player1', 'children'),Output('player2', 'children'),Output('player3', 'children'),Output('player4', 'children'),Output('player5', 'children')],
    [Input('graph1', 'selectedData'),Input('graph2', 'selectedData')])
def display_click_data(selectedData,selectedData2):
    print(selectedData)
    if selectedData is not None :
        date = selectedData["points"][0]["x"]
        pos = selectedData["points"][0]["y"]
        top = b.tops[selectedData["points"][0]["pointIndex"]]
        teamScore = top.findByPos(pos)
        teamName = teamScore.team.name
        points = teamScore.points
        teamPlayer = ["{} ({})".format(x.name,x.country) for x in teamScore.team.playerList]
        link = html.A("HLTV", href=top.url,target="_blank")
        teamPlayer = teamPlayer + ["None"]*(5 - len(teamPlayer))
    
        return date,teamName,pos,points,link,(*teamPlayer)
    
    elif selectedData2 is not None :
        print(selectedData2)
        date = selectedData2["points"][0]["x"]
        pos = selectedData2["points"][0]["text"]
        pos = pos[pos.index("#")+1] + pos[pos.index("#")+2]
        if pos[1].isdigit():
            pos = int(pos)
        else:
            pos = int(pos[0])
        top = b.tops[selectedData2["points"][0]["pointIndex"]]
        teamScore = top.findByPos(pos)
        teamName = teamScore.team.name
        points = teamScore.points
        teamPlayer = ["{} ({})".format(x.name,x.country) for x in teamScore.team.playerList]
        link = html.A("HLTV", href=top.url,target="_blank")
        teamPlayer = teamPlayer + ["None"]*(5 - len(teamPlayer))
        
        return date,teamName,pos,points,link,(*teamPlayer)
        
    else:
        return "None","None","None","None","None","None","None","None","None","None"


@app.callback(
    [Output('graph1', 'selectedData')],
    [Input('graph2', 'selectedData')])
def deselectGraph1(selectedData2):
    if selectedData2 is not None:
        return [None]
    return [None]

if __name__ == '__main__':
    app.run_server(debug=True)
