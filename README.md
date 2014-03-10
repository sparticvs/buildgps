BuildGPS
========

What is BuildGPS?
-----------------

BuildGPS is a tool that talks to Jenkins and GitLab (currently, maybe more interfaces later)
to get current build status.  BuildGPS consists of two parts.  First is a Python Tornado-based
WebSocket Service that will talk to Jenkins and GitLab JSON APIs (because of Cross-Origin
Resource Sharing) and feed information to the Second part of the project. The second is an
extremely light HTML/Javascript Package that gets information back from the server and using
Bootstrap, it displays the build status for each project that reports on WebSockets.

Why make BuildGPS?
------------------

I know that other "dashboards" for Jenkins exist.  The problem is that most of them are ugly
(sorry, but it's true). Since I wanted a useful one that was also light-weight, this was the
perfect solution I could develop.

License
--------

This is Licensed under Apache License v 2.0
