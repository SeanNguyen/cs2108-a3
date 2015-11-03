'use strict';

var mongoose = require('mongoose'),
    Schema = mongoose.Schema;

var PhotoSchema = new Schema({
	name: String,
	description: String,
	user: String,
	path: String,
	tags: [String]
});

module.exports = mongoose.model('Photo', PhotoSchema);