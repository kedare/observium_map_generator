Just put your hostname from observium as argument and it will start the expansion from it.

You should get something like this :

![Screenshot](https://raw.githubusercontent.com/mathieupoussin/observium_map_generator/master/screen.png)

Map.php allows you to see a svg output in your browser with clickable links to your observium setup (Just adapt the links in the conf), it requires Viz.js

How to use : 

- Install mysql, pydot, and colour python libraries
- Puts graph.py in your observium root and graph.php in a subdirectory in your html directory
- Grab Viz.js in the map.php directory
- Setup a cron that call a bash script like this one (adapt it to your setup)
- Adapt map.php by changing CHANGEME.dot do your dotfile

```
#!/bin/bash

cd /usr/local/obs/html/graph/

/usr/bin/php /usr/local/obs/discovery.php -h all -m discovery-protocols

python /usr/local/obs/graph.py CHANGEME
```
