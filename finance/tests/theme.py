import plotly.offline as pyo
import plotly.graph_objs as go
from plotly import tools

trace1 = go.Bar(
    x=[1, 2, 3],
    y=[10, 11, 12]
)
trace2 = go.Bar(
    x=[1, 2, 3],
    y=[100, 110, 120],
)
trace3 = go.Bar(
    x=[1, 2, 3],
    y=[1000, 1100, 1200],
)

fig = tools.make_subplots(rows=1, cols=3,
                          shared_xaxes=True, shared_yaxes=True,
                          vertical_spacing=0.001,
                          subplot_titles = ('first_title', 'second_title', 'third_title'))

fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 1, 1)
fig.append_trace(trace2, 1, 2)
fig.append_trace(trace3, 1, 3)

fig['layout'].update(height=600, width=600, title='main_title')

pyo.plot(fig, filename='file.html')















import plotly.offline as pyo
import plotly.graph_objs as go
from plotly import tools

trace1 = go.Bar(
    x=[1, 2, 3],
    y=[10, 11, 12]
)
trace2 = go.Bar(
    x=[1, 2, 3],
    y=[100, 110, 120],
)
trace3 = go.Bar(
    x=[1, 2, 3],
    y=[1000, 1100, 1200],
)

fig = tools.make_subplots(rows=1, cols=3,
                          shared_xaxes=True, shared_yaxes=True,
                          vertical_spacing=0.001,
                          subplot_titles = ('first_title', 'second_title', 'third_title'))

fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 1, 1)
fig.append_trace(trace2, 1, 2)
fig.append_trace(trace3, 1, 3)

fig['layout'].update(height=600, width=600, title='')

# rotate all the subtitles of 90 degrees
for annotation in fig['layout']['annotations']: 
        annotation['textangle']=-90

pyo.plot(fig)#, filename='file.html')

a=1