'use strict';

var app = angular.module('webserverApp');

app.factory('Photo', ['$resource', function($resource) {
	return $resource('/api/photo/:id', {id:'@_id'},
	    {
	        'update': { method:'PUT' }
	    });
}]);