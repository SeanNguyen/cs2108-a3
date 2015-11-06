'use strict';

var app = angular.module('webserverApp');

app.controller('WelcomeController', WelcomeController);

function WelcomeController($scope, $state, localStorageService) {
	$scope.welcomeMessage = "Tell Us Your Name";
  	$scope.input = {username: ''};
  	$scope.logIn = logIn;

  	active();

  	function active() {
  		var username = localStorageService.get("username");
  		if(username) {
  			$scope.input.username = username;
  			$scope.welcomeMessage = "Welcome";
  		}
  	}

  	function logIn(username) {
  		localStorageService.set("username", username);
  		$state.go("main");
  	}
};