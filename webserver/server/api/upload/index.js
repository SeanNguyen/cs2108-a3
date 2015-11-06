'use strict';

var express = require('express');
var multer  = require('multer')
var upload = multer({ dest: 'uploads/' })
var controller = require('./upload.controller');

var router = express.Router();

router.post('/', upload.single('image'), controller.upload);

module.exports = router;