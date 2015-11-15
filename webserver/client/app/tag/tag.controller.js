'use strict';

var app = angular.module('webserverApp');

app.controller('TagController', TagController);

function TagController($scope, $state, Photo, $stateParams) {
	$scope.loading;
	$scope.photos;
	$scope.tag;

	active();
	
	//implementations
	function active() {
		//load images of current user
		$scope.loading = true;
		$scope.tag = $stateParams.tag;

		Photo.query({tag :$scope.tag})
		.$promise.then(function(res) {
			$scope.photos = res;
			$scope.loading = false;
		})
		.catch(function(err) {
			alert("Cannot connect to server");
		});
	}
};