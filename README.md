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
pip3 install -r requirements.txt
```

### MariaDB as mySQL drop-in replacement
> If you wish to apply a pipe to a database, you should establish a database somewhere. Either as a localhost or as a remoe database server.

```shell
# install MariaDB
sudo apt-get install mariadb-server

# for secure setting
sudo mysql_secure_installation

# check systemctl status 
systemctl status mysql

# to start the service
sudo systemctl start mysql

# to stop the service 
sudo systemctl stop mysql

# for login as root 
$ sudo mysql -u root -p
```

```
# inside the shell of mysql
## create a new db
CREATE DATABASE <example>;

## create a table in a db
create table <customer>(<name> varchar(10), <join_date> date) DEFAULT CHARSET=utf8;

## create a new user
CREATE USER <user>@<IP> IDENTIFIED by <password>;

## grant privilege
GRANT ALL PRIVILEGES ON <database>.<table> TO <user>@<IP>;
FLUSH PRIVILEGES;

## show grants
SHOW GRANTS FOR <user>@<IP>;
```

### .env file
You can find an example of an [.env file](https://github.com/PeterTsungYu/dev_eda/blob/dev/.env_example).
```shell
touch .env 
```

```
# inside the .env, fill in the info
db_user=''
db_pwd=''
```
> "db_user", the one you created within mysql

> "db_pwd", the one you created within mysql as the user is created

> In this project, the localhost is used as the host.

### Execute Python script in shell
With everything being employed, good luck for your ride!
```shell
python3 app.py
```
#### If start successfully
![img_0](https://i.imgur.com/S7Y0D3u.png)

If seeing the above image, you can go ahead to open a browser.
After starting the Dash as a web app, you can access the web app in a browser by visiting localhost:8050.
The browser should be the one running on your machine (like RPi) or the one on your remote computer as you are accessing your machine by remote ssh or connections.
> The default port for Dash is 8050
