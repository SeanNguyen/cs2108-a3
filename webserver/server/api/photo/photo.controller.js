/**
 * Using Rails-like standard naming convention for endpoints.
 * GET     /things              ->  index
 * POST    /things              ->  create
 * GET     /things/:id          ->  show
 * PUT     /things/:id          ->  update
 * DELETE  /things/:id          ->  destroy
 */

'use strict';

var _ = require('lodash');
var Thing = require('./photo.model');

// Get list of things
exports.index = function(req, res) {
  var username = req.query.username;
  var tag = req.query.tag;
  var query = Thing.find();
  if(username) {
    query.where("user").equals(username);
  }
  if(tag) {
    query.where("tags").equals(tag);
  }
  query.exec()
  .then(function (things, err) {
    if(err) { return handleError(res, err); }
    return res.json(200, things);
  })
};

// Get a single thing
exports.show = function(req, res) {
  Thing.findById(req.params.id, function (err, thing) {
    if(err) { return handleError(res, err); }
    if(!thing) { return res.send(404); }
    return res.json(thing);
  });
};

// Creates a new thing in the DB.
exports.create = function(req, res) {
  Thing.create(req.body, function(err, thing) {
    if(err) { return handleError(res, err); }
    return res.json(201, thing);
  });
};

// Updates an existing thing in the DB.
exports.update = function(req, res) {
  if(req.body._id) { delete req.body._id; }

  Thing.findById(req.params.id, function (err, thing) {
    thing.update({$set: { name: req.body.name,
                          description: req.body.description,
                          user: req.body.user,
                          path: req.body.path,
                          tags: req.body.tags,
                        } 
      }, 
      { w: 1 },
      function (err, affected) {
        if (err) { return handleError(res, err); }
        thing.name = req.body.name;
        thing.description = req.body.description;
        thing.user = req.body.user;
        thing.path = req.body.path;
        thing.tags = req.body.tags;
        return res.json(200, thing);
      });
  });
};

// Deletes a thing from the DB.
exports.destroy = function(req, res) {
  Thing.findById(req.params.id, function (err, thing) {
    if(err) { return handleError(res, err); }
    if(!thing) { return res.send(404); }
    thing.remove(function(err) {
      if(err) { return handleError(res, err); }
      return res.send(204);
    });
  });
};

function handleError(res, err) {
  return res.send(500, err);
}