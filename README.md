Just put your hostname from observium as argument and it will start the expansion from it.

You should get something like this :

![Screenshot](https://raw.githubusercontent.com/mathieupoussin/observium_map_generator/master/screen.png)

Map.php allows you to see a svg output in your browser with clickable links to your observium setup (Just adapt the links in the conf), it requires Viz.js

How to use : 

- Install mysql, pydot, and colour python libraries
- Put graph.py in your observium root and graph.php in a subdirectory in your html directory
- Place Viz.js in the map.php directory ( http://mdaines.github.io/viz.js/viz.js )
- Setup a cron that call a bash script like this one (adapt it to your setup)
- Modify map.php by changing CHANGEME.dot do your dotfile (used in the cron script

```
#!/bin/bash

cd /opt/observium/html/graph/

/usr/bin/php /opt/observium/discovery.php -h all -m discovery-protocols

python /opt/observium/graph.py CHANGEME
```
