'use strict';

angular.module('webserverApp')
  .controller('MainCtrl', function ($scope, $http, localStorageService, $state) {
  	$scope.username;


  	active();
  	
  	//implementations
  	function active() {
  		$scope.username = localStorageService.get("username");
  		if(!$scope.username) {
  			$state.go("welcome");
  		}
  	}
  });