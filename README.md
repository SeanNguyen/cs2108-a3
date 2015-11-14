# cs2108-a3

###HOW TO START FRONT-END WEB SERVER
- require: nodejs, npm, mongodb
- install global npm packet if you havent have them: `npm install -g bower grunt-cli`
- start mongodb `mongod`
- go to web server folder `cd webserver`
- install bower and npm dependencies `bower install; npm install`
- start server `grunt serve`
- Enjoy!!!

###HOW TO START IMAGECLASSIFIER
- require: python 2.7.x, nltk, opencv for python, semanticFeature from assignment 1
- install python 2.7.x
- install nltk
- http://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html#gsc.tab=0 opencv for python
- start python shell "import nltk", "nltk.download()" and download WordNet corpus
- place semanticFeature in same folder as webserver
- download training data i've uploaded to http://nyanpa.su/uploads.rar and extract to webserver/uploads
- run imageclassifier.py

restful api at localhost:1111
/get_tags?=filename
/set_tags?=filename&tags={"tags": []}

test query data
http://nyanpa.su/query.csv
http://nyanpa.su/query.rar