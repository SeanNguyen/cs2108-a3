'use strict';

angular.module('webserverApp')
  .controller('WelcomeController', function ($scope, $state, localStorageService) {
  	$scope.input = {username: ''};
  	$scope.logIn = logIn;

  	function logIn(username) {
  		localStorageService.set("username", username);
  		$state.go("main");
  	}
  });