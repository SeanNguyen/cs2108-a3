'use strict';

var fs = require("fs");

// Creates a new thing in the DB.
exports.upload = function(req, res, next) {
	if(!req.file) {
		return res.send(400);
	}

	fs.readFile(req.file.path, function (err, data) {
		if(err) {
			return handleError(res, err);
		}

		var uploadFolder = __dirname + "/../../../imageRepo/";
	  	var uploadPath = uploadFolder + req.body.imageName;
	  	if (!fs.existsSync(uploadFolder)){
		    fs.mkdirSync(uploadFolder);
		}
	  	fs.writeFile(uploadPath, data, function (err) {
	  		if(err) {
	  			return handleError(res, err);
	  		}
	  		res.send(200);
		});
	});
};

function handleError(res, err) {
  return res.send(500, err);
}