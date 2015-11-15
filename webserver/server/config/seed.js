/**
 * Populate DB with sample data on server start
 * to disable, edit config/environment/index.js, and set `seedDB: false`
 */

'use strict';
var fs = require('fs');
var Photo = require('../api/photo/photo.model');

Photo.find({'user' : 'system'}).remove(function() {
  //read svg file
  fs.readFile('../train.csv', 'utf8', function (err,data) {
    if (err) {
      return console.log(err);
    }
    var lines = data.split("\r\n");
    for (var i = lines.length - 1; i >= 0; i--) {
      var line = lines[i];
      if(line.length == 0)
        continue;
      var args = line.split(",");
      var name = args[0];
      args.splice(0, 1)
      Photo.create({
        name: name,
        description: 'System Photo',
        user: 'system',
        path: 'uploads/' + name,
        tags: args
      });
    };
  });
})