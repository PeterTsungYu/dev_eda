# Data Analysis Dash App
## Scope
This project aims to build a visualization web app for data analysis. 
- Visualization
- Data Analysis
- Interactive web app
- Generation of research reports

## Dependencies
The web app is built under the frameworks of [Dash and Plotly](https://dash.plotly.com/?_gl=1*1ndvzch*_ga*MTE4OTc0ODE0OC4xNjYzMDYwODEz*_ga_6G7EE0JNSC*MTY2MzA2MDgxMy4xLjEuMTY2MzA2MDgyNi4wLjAuMA..). 
They are both python-native frameworks for web application and data visualization.
One would find out that it is a relatively easy way to build an interactive interface even though one is programming in Python.

Data are populated from a remote database. For instance, [python mariadb](https://pypi.org/project/mariadb/). 

With this interactive data analysis project folder, one could further visualize and analyze. 
Take a look at the [Pythonic IoT project](https://github.com/PeterTsungYu/dev_iot) and [NodeRed Dashboard](https://github.com/PeterTsungYu/flows_Reformer) that are created under the same scope of this project.   

| Features              | Links                   |
| -----------------     |:----------------------- |
| Pythonic IoT project  | [:link:][https://github.com/PeterTsungYu/dev_iot]           |
| NodeRed Dashboard     | [:link:][https://github.com/PeterTsungYu/flows_Reformer]    |

## Snaps
### Overall view
![gif](https://i.imgur.com/nA2zUYQ.gif)

### Summary table
<img src="https://i.imgur.com/30djIjp.png" width="700" height="300">

### Summary charts and plots
<img src="https://i.imgur.com/FZuTpSZ.png" width="700" height="300">

### Comparison graph
<img src="https://i.imgur.com/6soNk6A.png" width="700" height="300">

### Selection graph
<img src="https://i.imgur.com/QeoNoqJ.png" width="700" height="300">

## Quick Start
The below instructions are employed in the environment as...
- Linux-based or Linux system with the Python3 installed 
- Wifi or Intranet access

### Clone the project
```shell
git clone https://github.com/PeterTsungYu/dev_eda.git
```

### Install required packages
```shell
cd dev_eda/
pip install -r requirements.txt
```




After starting the NodeRed as a service, you can access the editor in a browser by visiting localhost:1880.
The browser should be the one running on your machine (like RPi) or the one on your remote computer as you are accessing your machine by remote ssh or connections.
> The default port for NodeRed is 1880
