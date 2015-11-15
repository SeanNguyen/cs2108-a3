'use strict';

var fs = require("fs");
var photo = require("../photo/photo.model");

// Creates a new thing in the DB.
exports.upload = function(req, res) {
	if(!req.file) {
		return res.send(400);
	}

	fs.readFile(req.file.path, function (err, data) {
		if(err) {
			return handleError(res, err);
		}

		console.log(req.body);

		//prepare upload folder
		var uploadFolder = __dirname + "/../../../uploads/";
	  	if (!fs.existsSync(uploadFolder)){
		    fs.mkdirSync(uploadFolder);
		}

		//create a new photo model
		var newPhoto = {
			name: req.file.originalname,
			description: "",
			user: req.body.username,
			path: "",
			tags: []
		}
		photo.create(newPhoto, function(err, model) {
			if(err) { return handleError(res, err); }

	  		model.path = "uploads/" + model._id + ".jpg"
	  		model.save(function (err) {
		      	if (err) { return handleError(res, err); }
		      	//write image to destination folder
		  		var uploadPath = uploadFolder + model._id + ".jpg";
			  	fs.writeFile(uploadPath, data, function (err) {
			  		if(err) { return handleError(res, err);	}
			  		return res.send(200, model);
				});
		    });
		});
	});
};

function handleError(res, err) {
  return res.send(500, err);
}