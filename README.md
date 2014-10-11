BuildGPS
========

What is BuildGPS?
-----------------

BuildGPS is a tool that talks to Jenkins and GitLab (currently, maybe more interfaces later)
to get current build status.  BuildGPS consists of two parts.  First is a Python Tornado-based
WebSocket Service that will talk to Jenkins and GitLab JSON APIs (because of Cross-Origin
Resource Sharing) and feed information to the Second part of the project. The second is an
extremely light HTML/Javascript Package that gets information back from the server and using
Twitter Bootstrap and Angular.JS, it displays the build status for each project that reports
on WebSockets.

Why make BuildGPS?
------------------

I know that other "dashboards" for Jenkins exist.  The problem is that most of them are ugly
(sorry, but it's true). Since I wanted a useful one that was also light-weight, this was the
perfect solution I could develop.

Why a new version number?
-------------------------

Great question. I learned about Angular.JS after a working version of this was
done. I know that the change will eliminate some bugs before they are
discovered because the code is easier to work with and read. This gets its own
version number because I think that this work needs to be differentiated in
some manner.

License
--------

This is Licensed under Apache License v 2.0
